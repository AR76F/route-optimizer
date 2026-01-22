# app.py — Route Optimizer + Planning (Page 2) with persistent state
import os
import re
from io import BytesIO
from datetime import datetime, date, timedelta, timezone
from typing import Optional, Tuple, List

import streamlit as st
import pandas as pd
import requests
import folium
import googlemaps
from streamlit_folium import st_folium

# ─────────────────────────────────────────────────────────────
# Page config (ONE TIME ONLY)
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Route Optimizer", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def secret(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

def normalize_ca_postal(text: str) -> str:
    if not text:
        return text
    t = str(text).strip().upper().replace(" ", "")
    if len(t) == 6 and t[:3].isalnum() and t[3:].isalnum():
        return f"{t[:3]} {t[3:]}, Canada"
    return text

def geocode_ll(gmaps_client: googlemaps.Client, text: str) -> Optional[Tuple[float, float, str]]:
    if not text:
        return None
    q = normalize_ca_postal(text)
    try:
        res = gmaps_client.geocode(q, components={"country": "CA"}, region="ca")
        if res:
            loc = res[0]["geometry"]["location"]
            addr = res[0].get("formatted_address") or q
            return float(loc["lat"]), float(loc["lng"]), addr
    except Exception:
        pass
    return None

def reverse_geocode(gmaps_client: googlemaps.Client, lat: float, lon: float) -> str:
    try:
        res = gmaps_client.reverse_geocode((lat, lon))
        if res:
            return res[0].get("formatted_address", f"{lat:.5f},{lon:.5f}")
    except Exception:
        pass
    return f"{lat:.5f},{lon:.5f}"

def zone_from_address(addr: str) -> str:
    a = (addr or "").lower()
    rive_nord = ["laval", "terrebonne", "blainville", "mirabel", "boisbriand", "st-jérôme", "saint-jérôme"]
    rive_sud  = ["longueuil", "brossard", "candiac", "delson", "beloeil", "st-hubert", "saint-hubert",
                 "chambly", "st-jean", "saint-jean"]
    if any(k in a for k in rive_nord): return "RIVE_NORD"
    if any(k in a for k in rive_sud):  return "RIVE_SUD"
    return "MTL_LAVAL"

def penalty(zone_a: str, zone_b: str, p_ns: int, p_mtl: int) -> int:
    if zone_a == zone_b:
        return 0
    if {"RIVE_NORD", "RIVE_SUD"} == {zone_a, zone_b}:
        return p_ns
    return p_mtl

def mm_to_hhmm(m: int) -> str:
    h = m // 60
    mm = m % 60
    return f"{h:02d}:{mm:02d}"

@st.cache_data(ttl=60*60*24, show_spinner=False)
def travel_min(gmaps: googlemaps.Client, origin: str, dest: str) -> int:
    if not origin or not dest:
        return 9999
    try:
        r = gmaps.distance_matrix([origin], [dest], mode="driving")
        el = r["rows"][0]["elements"][0]
        if el.get("status") != "OK":
            return 9999
        dur = el.get("duration_in_traffic") or el.get("duration") or {}
        return int(round(int(dur.get("value", 0)) / 60))
    except Exception:
        return 9999

def label_marker(lat: float, lon: float, text: str, kind: str) -> None:
    """
    Adds a marker + a permanent label next to it.
    kind: "tech" or "wh"
    """
    if kind == "wh":
        icon = folium.Icon(color="red", icon="building", prefix="fa")
        label_bg = "rgba(255,255,255,0.95)"
        label_border = "#ddd"
    else:
        icon = folium.Icon(color="blue", icon="user", prefix="fa")
        label_bg = "rgba(255,255,255,0.95)"
        label_border = "#ddd"

    m = folium.Marker([lat, lon], icon=icon, tooltip=text)
    m.add_to(st.session_state._fmap)

    # Permanent label (always visible)
    folium.Marker(
        [lat, lon],
        icon=folium.DivIcon(
            icon_size=(240, 22),
            icon_anchor=(0, -18),
            html=f"""
            <div style="
                display:inline-block;
                padding:2px 6px;
                font-size:12px;
                font-weight:700;
                color:#111;
                background:{label_bg};
                border:1px solid {label_border};
                border-radius:6px;
                box-shadow:0 1px 2px rgba(0,0,0,.25);
                white-space:nowrap;">
              {text}
            </div>
            """
        ),
    ).add_to(st.session_state._fmap)

# ─────────────────────────────────────────────────────────────
# Global constants (tech homes / warehouses)
# ─────────────────────────────────────────────────────────────
TECH_HOME = {
    "Alain Duguay": "1110 rue Proulx, Les Cèdres, QC J7T 1E6",
    "Alexandre Pelletier Guay": "163 21e ave, Sabrevois, J0J 2G0",
    "Ali Reza-Sabour": "226 rue Felx, Saint-Clet, QC J0P 1S0",
    "Benoit Charrette": "34 rue de la Digue, Saint-Jérome, QC, Canada",
    "Benoit Laramee": "12 rue de Beaudry, Mercier, J6R 2N7",
    "Christian Dubreuil": "31 rue des Roitelets, Delson, J5B 1T6",
    "Donald Lagace (IN SHOP)": "Montée Saint-Régis, Sainte-Catherine, QC, Canada",
    "Elie Rajotte-Lemay": "3700 Mnt du 4e Rang, Les Maskoutains, J0H 1S0",
    "Francois Racine": "80 rue de Beaujeu, Coteau-du-lac, J0P 1B0",
    "Fredy Diaz": "312 rue de Valcourt, Blainville, J7B 1H3",
    "Georges Yamna": "Rue René-Lévesque, Saint-Eustache, J7R 7L4",
    "Kevin Duranceau": "943 rue des Marquises, Beloeil, J3G 6T9",
    "Louis Lauzon": "5005 rue Domville, Saint-Hubert, J3Y 1Y2",
    "Martin Bourbonnière": "1444 rue de l'Orchidée, L'Assomption QC J5W 6B3",
    "Maxime Roy": "3e ave, Ile aux Noix, QC, Canada",
    "Michael Sulte": "2020 chem. De Covery Hill, Hinchinbrooke, QC, Canada",
    "Patrick Bellefleur": "222 rue Charles-Gadiou, L'Assomption, J5W 0J4",
    "Pier-Luc Cote": "143 rue Ashby, Marieville, J3M 1P2",
    "Sebastien Pepin (IN SHOP)": "Saint-Valentin, QC, Canada",
    "Sergio Mendoza": "791 Rue des Marquises, Beloeil, QC J3G 6M6",
}

ENTREPOTS = {
    "Candiac": "315 Liberté, Candiac, QC J5R 6Z7",
    "Assomption": "119 rue de la Commissaires, Assomption, QC, Canada",
    "Boisbriand": "5025 rue Ambroise-Lafortune, Boisbriand, QC, Canada",
    "Mirabel": "1600 Montée Guenette, Mirabel, QC, Canada",
}

def build_tech_home_df() -> pd.DataFrame:
    def _extract_postal(addr: str) -> str:
        if not addr:
            return ""
        m = re.search(r"\b([A-Z]\d[A-Z])\s?(\d[A-Z]\d)\b", str(addr).upper())
        return (m.group(1) + m.group(2)) if m else ""

    df = pd.DataFrame(
        [{"tech_name": name, "home_address": addr, "postal": _extract_postal(addr)}
         for name, addr in TECH_HOME.items()]
    )
    df["zone"] = df["home_address"].apply(zone_from_address)
    return df

# ─────────────────────────────────────────────────────────────
# Navigation persisted
# ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Route Optimizer"

st.sidebar.title("Menu")
st.session_state.page = st.sidebar.radio(
    "Navigation",
    ["🏠 Route Optimizer", "📅 Planning (Page 2)"],
    index=["🏠 Route Optimizer", "📅 Planning (Page 2)"].index(st.session_state.page),
    key="page_radio",
)
page = st.session_state.page

# ─────────────────────────────────────────────────────────────
# Google Maps client
# ─────────────────────────────────────────────────────────────
GOOGLE_KEY = secret("GOOGLE_MAPS_API_KEY")
if not GOOGLE_KEY:
    st.error("Missing Google Maps key. Add it in Streamlit Secrets as `GOOGLE_MAPS_API_KEY`.")
    st.stop()
gmaps = googlemaps.Client(key=GOOGLE_KEY)

# ─────────────────────────────────────────────────────────────
# Page 1
# ─────────────────────────────────────────────────────────────
def render_page_1():
    st.markdown("## Optimisation du trajet des techniciens")
    st.caption("Page 1 — garde les choix en session_state et prépare `tech_home` pour la page 2.")

    # Ensure tech_home exists for Page 2
    if "tech_home" not in st.session_state:
        st.session_state.tech_home = build_tech_home_df()

    # Persist these fields between page switches
    if "route_start" not in st.session_state:
        st.session_state.route_start = ""
    if "storage_text" not in st.session_state:
        st.session_state.storage_text = ""

    st.markdown("---")
    st.subheader("🎯 Point de départ")
    tabs = st.tabs(["🏠 Technician Home (Map + labels)", "✍️ Manual input"])

    with tabs[0]:
        st.write("Carte techniciens + entrepôts. **Les noms sont visibles sur la carte**.")
        show_map = st.checkbox("Afficher la carte", value=True, key="p1_show_map")

        if show_map:
            # Geocode once and cache into session_state to avoid re-geocoding on every rerun
            if "p1_geo_cache" not in st.session_state:
                st.session_state.p1_geo_cache = {"tech": {}, "wh": {}}

            tech_points = []
            wh_points = []

            # TECHS
            for name, addr in TECH_HOME.items():
                if name in st.session_state.p1_geo_cache["tech"]:
                    g = st.session_state.p1_geo_cache["tech"][name]
                else:
                    g = geocode_ll(gmaps, addr)
                    st.session_state.p1_geo_cache["tech"][name] = g
                if g:
                    lat, lon, formatted = g
                    tech_points.append((name, formatted, lat, lon))

            # WAREHOUSES
            for wh_name, addr in ENTREPOTS.items():
                if wh_name in st.session_state.p1_geo_cache["wh"]:
                    g = st.session_state.p1_geo_cache["wh"][wh_name]
                else:
                    g = geocode_ll(gmaps, addr)
                    st.session_state.p1_geo_cache["wh"][wh_name] = g
                if g:
                    lat, lon, formatted = g
                    wh_points.append((wh_name, formatted, lat, lon))

            points_all = tech_points + wh_points
            if points_all:
                avg_lat = sum(p[2] for p in points_all) / len(points_all)
                avg_lon = sum(p[3] for p in points_all) / len(points_all)

                st.session_state._fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="cartodbpositron")

                # Add warehouses with labels
                for wh_name, formatted, lat, lon in wh_points:
                    label_marker(lat, lon, f"🏭 {wh_name}", kind="wh")

                # Add techs with labels
                for tech_name, formatted, lat, lon in tech_points:
                    label_marker(lat, lon, tech_name, kind="tech")

                st_folium(st.session_state._fmap, height=750, width=1600)

            c1, c2 = st.columns(2)
            with c1:
                tech_choice = st.selectbox(
                    "Technicien → définir comme **départ**",
                    ["(choisir)"] + sorted(TECH_HOME.keys()),
                    key="p1_tech_choice_start",
                )
                if tech_choice != "(choisir)":
                    st.session_state.route_start = TECH_HOME[tech_choice]
                    st.success(f"Départ défini sur **{tech_choice}** — {TECH_HOME[tech_choice]}")

            with c2:
                wh_choice = st.selectbox(
                    "Entrepôt → définir comme **stockage**",
                    ["(choisir)"] + sorted(ENTREPOTS.keys()),
                    key="p1_wh_choice_storage",
                )
                if wh_choice != "(choisir)":
                    st.session_state.storage_text = ENTREPOTS[wh_choice]
                    st.success(f"Stockage défini sur **{wh_choice}** — {ENTREPOTS[wh_choice]}")

    with tabs[1]:
        st.text_input("Technician home (START)", key="route_start", placeholder="Adresse complète ou code postal")
        st.text_input("Storage location (first stop)", key="storage_text", placeholder="Adresse complète ou code postal")

    if st.session_state.route_start:
        st.info(f"📍 Point de départ actuel: {st.session_state.route_start}")
    if st.session_state.storage_text:
        st.info(f"🏭 Stockage actuel: {st.session_state.storage_text}")

    st.markdown("---")
    st.subheader("➡️ Aller à la Page 2 sans perdre l’état")
    if st.button("Ouvrir Planning (Page 2)"):
        st.session_state.page = "📅 Planning (Page 2)"
        st.rerun()

# ─────────────────────────────────────────────────────────────
# Page 2
# ─────────────────────────────────────────────────────────────
def render_page_2():
    st.title("📅 Planning mensuel – Journées techniciens")
    st.caption("Page 2 — état persistant (upload Excel + jobs + planning) via session_state.")

    # Make sure we have tech_home, otherwise create it (so Page 2 can be opened first too)
    if "tech_home" not in st.session_state:
        st.session_state.tech_home = build_tech_home_df()

    tech_df = st.session_state.tech_home.copy()
    st.subheader("👷 Techniciens (source persistante)")
    st.dataframe(tech_df[["tech_name", "home_address", "zone"]], use_container_width=True)

    st.divider()

    # Upload persisted
    st.subheader("📤 Jobs – Upload Excel (onglet Export)")
    uploaded = st.file_uploader("Upload ton fichier Excel jobs", type=["xlsx"], key="jobs_uploader")

    if uploaded is not None:
        st.session_state.jobs_file_name = uploaded.name
        st.session_state.jobs_file_bytes = uploaded.getvalue()

    if "jobs_file_bytes" not in st.session_state:
        st.info("Upload le fichier Excel pour continuer.")
        return

    file_like = BytesIO(st.session_state.jobs_file_bytes)

    # Read excel (cache on bytes hash)
    @st.cache_data(show_spinner=False)
    def read_jobs_excel(file_bytes: bytes) -> pd.DataFrame:
        bio = BytesIO(file_bytes)
        try:
            return pd.read_excel(bio, sheet_name="Export", engine="openpyxl")
        except Exception:
            bio.seek(0)
            return pd.read_excel(bio, sheet_name=0, engine="openpyxl")

    jobs_raw = read_jobs_excel(st.session_state.jobs_file_bytes)
    st.caption(f"Fichier: {st.session_state.get('jobs_file_name','(unknown)')} • Jobs détectés: {len(jobs_raw)}")
    st.dataframe(jobs_raw.head(20), use_container_width=True)

    st.divider()

    # Column mapping
    def pick_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        cols = {c.lower().strip(): c for c in df.columns}
        for cand in candidates:
            k = cand.lower().strip()
            if k in cols:
                return cols[k]
        return None

    COL_ORDER = pick_col(jobs_raw, ["ORDER #", "ORDER#", "Order", "Job ID", "WO", "Work Order"])
    COL_ADDR1 = pick_col(jobs_raw, ["ADDRESS 1", "ADDRESS1", "Address 1"])
    COL_ADDR2 = pick_col(jobs_raw, ["ADDRESS 2", "ADDRESS2", "Address 2"])
    COL_ADDR3 = pick_col(jobs_raw, ["ADDRESS 3", "ADDRESS3", "Address 3"])
    COL_CITY  = pick_col(jobs_raw, ["SITE CITY", "CITY", "City"])
    COL_PROV  = pick_col(jobs_raw, ["SITE STATE", "STATE", "Province"])
    COL_POST  = pick_col(jobs_raw, ["SITE ZIP CODE", "ZIP", "POSTAL", "Postal Code"])
    COL_DESC  = pick_col(jobs_raw, ["PM SERVICE DESC.", "DESCRIPTION", "Service Desc", "Desc"])
    COL_UP    = pick_col(jobs_raw, ["UPCOMING SERVICES", "Upcoming Services"])
    COL_ONS   = pick_col(jobs_raw, ["ONSITE SRT HRS", "ONSITE HOURS", "ONSITE HRS"])
    COL_SRT   = pick_col(jobs_raw, ["SRT HRS", "SRT HOURS", "HRS"])
    COL_TECHN = pick_col(jobs_raw, ["# OF TECHS NEEDED", "TECHS NEEDED", "Nbr Techs"])

    if not COL_ORDER:
        st.error("Je ne trouve pas la colonne Job/Order (#).")
        return

    def build_address(row: pd.Series) -> str:
        parts = []
        for c in [COL_ADDR1, COL_ADDR2, COL_ADDR3, COL_CITY, COL_PROV, COL_POST]:
            if c and pd.notna(row.get(c)) and str(row.get(c)).strip():
                parts.append(str(row.get(c)).strip())
        return ", ".join(parts)

    # Build jobs clean
    jobs = pd.DataFrame()
    jobs["job_id"] = jobs_raw[COL_ORDER].astype(str)
    jobs["address"] = jobs_raw.apply(build_address, axis=1)

    desc = jobs_raw[COL_DESC].fillna("").astype(str) if COL_DESC else ""
    up   = jobs_raw[COL_UP].fillna("").astype(str) if COL_UP else ""
    jobs["description"] = (desc + " | " + up).astype(str).str.strip(" |")

    ons = pd.to_numeric(jobs_raw[COL_ONS], errors="coerce") if COL_ONS else None
    srt = pd.to_numeric(jobs_raw[COL_SRT], errors="coerce") if COL_SRT else None
    if ons is not None:
        hours = ons
    elif srt is not None:
        hours = srt
    else:
        st.error("Je ne trouve pas `ONSITE SRT HRS` ni `SRT HRS` pour calculer la durée.")
        return

    jobs["job_minutes"] = (hours.fillna(0) * 60).round().astype(int)

    techs_needed = pd.to_numeric(jobs_raw[COL_TECHN], errors="coerce") if COL_TECHN else None
    jobs["techs_needed"] = techs_needed.fillna(1).astype(int) if techs_needed is not None else 1

    jobs = jobs[(jobs["address"].astype(str).str.len() > 8) & (jobs["job_minutes"] > 0)].copy()
    jobs = jobs.drop_duplicates(subset=["job_id"]).reset_index(drop=True)

    jobs["zone"] = jobs["address"].apply(zone_from_address)

    # Persist cleaned jobs
    st.session_state.jobs_clean = jobs

    st.subheader("🧾 Jobs nettoyés (persistant)")
    st.dataframe(jobs.head(30), use_container_width=True)

    st.divider()

    # Params (persist via keys)
    st.subheader("⚙️ Paramètres")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        day_hours = st.number_input("Heures/jour", 6.0, 12.0, 8.0, 0.5, key="p2_day_hours")
    with c2:
        lunch_min = st.number_input("Pause (min)", 0, 120, 30, 5, key="p2_lunch")
    with c3:
        buffer_job = st.number_input("Buffer/job (min)", 0, 60, 10, 5, key="p2_buffer")
    with c4:
        max_days = st.number_input("Max jours/tech", 1, 31, 22, 1, key="p2_max_days")

    p1, p2 = st.columns(2)
    with p1:
        p_ns = st.number_input("Pénalité Nord↔Sud (min)", 0, 240, 90, 15, key="p2_pns")
    with p2:
        p_mtl = st.number_input("Pénalité changement de zone (min)", 0, 240, 45, 15, key="p2_pmtl")

    # If already computed, show it (no reset)
    if "planning_visits" in st.session_state and st.session_state.planning_visits is not None:
        st.success("✅ Planning déjà généré (restauré depuis la session).")
        st.dataframe(st.session_state.planning_visits, use_container_width=True)
        with st.expander("Voir résumé + non planifiés"):
            st.dataframe(st.session_state.planning_summary, use_container_width=True)
            st.dataframe(st.session_state.planning_remaining.head(200), use_container_width=True)

    run = st.button("🚀 Générer le planning", type="primary", key="p2_run")

    if run:
        available = int(round(float(day_hours) * 60)) - int(lunch_min)
        remaining = jobs.copy()

        visits = []
        summaries = []

        with st.spinner("Calcul des journées (trajets Google Maps)…"):
            for _, tech in tech_df.iterrows():
                if remaining.empty:
                    break
                tech_name = str(tech["tech_name"])
                home = str(tech["home_address"])
                tech_zone = str(tech["zone"])

                for day in range(1, int(max_days) + 1):
                    if remaining.empty:
                        break

                    used = 0
                    seq = 0
                    cur_loc = home
                    cur_zone = tech_zone
                    day_rows = []

                    pool = remaining[remaining["zone"] == tech_zone].copy()
                    if pool.empty:
                        pool = remaining.copy()

                    while True:
                        best_idx = None
                        best_cost = None
                        best_t = None

                        sample = pool.head(35) if len(pool) > 35 else pool

                        for idx, job in sample.iterrows():
                            tmin = travel_min(gmaps, cur_loc, job["address"])
                            cost = tmin + penalty(cur_zone, job["zone"], int(p_ns), int(p_mtl))

                            need = int(tmin) + int(job["job_minutes"]) + int(buffer_job)
                            if used + need <= available:
                                if best_cost is None or cost < best_cost:
                                    best_idx = idx
                                    best_cost = cost
                                    best_t = int(tmin)

                        if best_idx is None:
                            break

                        job = pool.loc[best_idx]
                        seq += 1

                        start_m = used + int(best_t)
                        end_m = start_m + int(job["job_minutes"]) + int(buffer_job)

                        day_rows.append({
                            "technicien": tech_name,
                            "jour": day,
                            "sequence": seq,
                            "job_id": str(job["job_id"]),
                            "zone": str(job["zone"]),
                            "adresse": str(job["address"]),
                            "debut": mm_to_hhmm(int(start_m)),
                            "fin": mm_to_hhmm(int(end_m)),
                            "travel_min": int(best_t),
                            "job_min": int(job["job_minutes"]),
                            "buffer_min": int(buffer_job),
                            "description": str(job["description"]),
                            "techs_needed": int(job["techs_needed"]),
                        })

                        used = int(end_m)
                        cur_loc = str(job["address"])
                        cur_zone = str(job["zone"])

                        remaining = remaining[remaining["job_id"] != job["job_id"]].copy()
                        pool = pool[pool["job_id"] != job["job_id"]].copy()

                    if day_rows:
                        visits.extend(day_rows)
                        summaries.append({
                            "technicien": tech_name,
                            "jour": day,
                            "stops": len(day_rows),
                            "total_travel_min": sum(r["travel_min"] for r in day_rows),
                            "total_job_min": sum(r["job_min"] for r in day_rows),
                            "total_min": sum(r["travel_min"] + r["job_min"] + r["buffer_min"] for r in day_rows),
                            "zone_focus": tech_zone,
                        })

        visits_df = pd.DataFrame(visits)
        summary_df = pd.DataFrame(summaries)

        st.divider()
        st.subheader("📋 Planning détaillé")
        if visits_df.empty:
            st.warning("Aucune journée créée (essaie d’augmenter heures/jour ou diminuer pénalités).")
            return

        st.dataframe(visits_df.sort_values(["technicien", "jour", "sequence"]), use_container_width=True)

        st.subheader("📊 Résumé par journée")
        st.dataframe(summary_df.sort_values(["technicien", "jour"]), use_container_width=True)

        st.subheader("🧩 Jobs non planifiés")
        st.caption(f"Reste: {len(remaining)} job(s)")
        st.dataframe(remaining.head(200), use_container_width=True)

        # Persist results
        st.session_state.planning_visits = visits_df
        st.session_state.planning_summary = summary_df
        st.session_state.planning_remaining = remaining

        # Export
        out = BytesIO()
        fname = f"planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            visits_df.to_excel(writer, sheet_name="Visits", index=False)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            remaining.to_excel(writer, sheet_name="Unscheduled", index=False)
            jobs.to_excel(writer, sheet_name="Jobs_Input", index=False)
            tech_df.to_excel(writer, sheet_name="Tech_Input", index=False)

        st.download_button(
            "⬇️ Télécharger le planning (Excel)",
            data=out.getvalue(),
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        if (visits_df["techs_needed"] > 1).any():
            st.warning("⚠️ Certains jobs demandent >1 technicien. V1 les affiche, mais ne fait pas encore le pairing automatique.")

    st.divider()
    cA, cB = st.columns(2)
    with cA:
        if st.button("⬅️ Retour Page 1", key="p2_back"):
            st.session_state.page = "🏠 Route Optimizer"
            st.rerun()
    with cB:
        if st.button("♻️ Reset Page 2 (jobs + planning)", key="p2_reset"):
            for k in ["jobs_file_name", "jobs_file_bytes", "jobs_clean",
                      "planning_visits", "planning_summary", "planning_remaining"]:
                st.session_state.pop(k, None)
            st.rerun()

# ─────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────
if page == "🏠 Route Optimizer":
    render_page_1()
else:
    render_page_2()
