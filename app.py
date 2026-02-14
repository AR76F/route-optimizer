# app.py
# Streamlit Route Optimizer — Page 1 + Page 2 (Planning)
# FIXED:
# - Page 2 code moved into render_page_2() (no global execution)
# - Only ONE st.set_page_config()
# - Persistent session_state for: navigation, upload bytes, route_result, planning_result
# - Page 1 map (Tech Home + Entrepôts) shows permanent labels (names)
#
# CHANGE (as requested):
# - Add cache to geocode_ll() and reverse_geocode() so we don't re-geocode every rerun / every user
# - No "clear cache" button added

import os
import re
from io import BytesIO
from datetime import datetime, date, timedelta, timezone
from typing import List, Tuple, Optional

import streamlit as st
import googlemaps
import polyline
import folium
from streamlit_folium import st_folium

import pandas as pd
import requests

# ────────────────────────────────────────────────────────────────
# Optional myGeotab import (app still works if it's missing or secrets not set)
# ────────────────────────────────────────────────────────────────
GEOTAB_AVAILABLE = True
try:
    import mygeotab as myg
except Exception:
    GEOTAB_AVAILABLE = False

# ────────────────────────────────────────────────────────────────
# Page config (ONE TIME)
# ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Route Optimizer", layout="wide", initial_sidebar_state="expanded")

# ────────────────────────────────────────────────────────────────
# Navigation persisted
# ────────────────────────────────────────────────────────────────
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

# ────────────────────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────────────────────
def cummins_header():
    CANDIDATES = [
        "Cummins_Logo.png", "Cummins_Logo.jpg", "Cummins_Logo.svg",
        "assets/cummins_black.svg", "assets/cummins_black.png", "assets/cummins_black.jpg",
    ]
    col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
    with col_logo:
        shown = False
        for path in CANDIDATES:
            if os.path.exists(path):
                try:
                    st.image(path, width=300)
                    shown = True
                    break
                except Exception:
                    pass
        if not shown:
            st.markdown(
                """
                <div style="width:150px;height:150px;display:flex;align-items:center;justify-content:center;">
                  <svg viewBox="0 0 100 100" width="150" height="150"
                       xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cummins">
                    <rect x="0" y="0" width="100" height="100" fill="#000000"/>
                    <path d="M70,50a20,20 0 1,1 -20,-20" fill="#ffffff"/>
                  </svg>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_title:
        st.markdown(
            """
            <div style="margin-bottom:2px;">
              <h1 style="margin:0;color:white;font-size:54px;">Optimisation du trajet des techniciens</h1>
            </div>
            <div style="color:#9aa0a6;font-size:32px;">
              Domicile ➜ Entrepôt ➜ Clients (MAXIMUM 25 TRAJETS) — <b>Cummins Service Fleet</b>
            </div>
            """,
            unsafe_allow_html=True
        )

# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────
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

def big_number_marker(n: str, color_hex: str = "#cc3333"):
    html = f"""
    <div style="
      background:{color_hex};
      color:white;
      border-radius:18px;
      width:36px;height:36px;
      display:flex;align-items:center;justify-content:center;
      font-weight:700;font-size:16px;border:2px solid #222;">
      {n}
    </div>
    """
    return folium.DivIcon(html=html)

def recency_color(ts: Optional[str]) -> Tuple[str, str]:
    if not ts:
        return "#9e9e9e", "> 30d"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return "#9e9e9e", "unknown"
    age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
    if age <= timedelta(hours=2):
        return "#00c853", "≤ 2h"
    if age <= timedelta(hours=24):
        return "#2e7d32", "≤ 24h"
    if age <= timedelta(days=7):
        return "#fb8c00", "≤ 7d"
    return "#9e9e9e", "> 7d"

# ────────────────────────────────────────────────────────────────
# Google Maps key
# ────────────────────────────────────────────────────────────────
GOOGLE_KEY = secret("GOOGLE_MAPS_API_KEY")
if not GOOGLE_KEY:
    st.error("Missing Google Maps key. Add it in **App settings → Secrets** as `GOOGLE_MAPS_API_KEY`.")
    st.stop()
gmaps_client = googlemaps.Client(key=GOOGLE_KEY)

# ────────────────────────────────────────────────────────────────
# Geocoding helpers (CACHED)  ✅ (replacement requested)
# ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60*60*24*30, show_spinner=False, max_entries=20000)
def _geocode_cached(q: str) -> Optional[Tuple[float, float, str]]:
    """
    Cache Google Geocoding results for 30 days.
    Cache is shared for all users *on the same Streamlit Cloud instance*.
    """
    if not q:
        return None
    try:
        res = gmaps_client.geocode(q, components={"country": "CA"}, region="ca")
        if res:
            loc = res[0]["geometry"]["location"]
            addr = res[0].get("formatted_address") or q
            return float(loc["lat"]), float(loc["lng"]), addr
    except Exception:
        pass
    return None

def geocode_ll(gmaps_client: googlemaps.Client, text: str) -> Optional[Tuple[float, float, str]]:
    """
    Same signature as before, but now cached.
    """
    if not text:
        return None
    q = normalize_ca_postal(text)
    return _geocode_cached(q)

@st.cache_data(ttl=60*60*24*30, show_spinner=False, max_entries=20000)
def _reverse_geocode_cached(lat: float, lon: float) -> str:
    """
    Cache reverse geocode for 30 days.
    """
    try:
        res = gmaps_client.reverse_geocode((lat, lon))
        if res:
            return res[0].get("formatted_address", f"{lat:.5f},{lon:.5f}")
    except Exception:
        pass
    return f"{lat:.5f},{lon:.5f}"

def reverse_geocode(gmaps_client: googlemaps.Client, lat: float, lon: float) -> str:
    """
    Same signature as before, but now cached.
    """
    return _reverse_geocode_cached(float(lat), float(lon))

# ────────────────────────────────────────────────────────────────
# Shared data: TECH_HOME / ENTREPOTS
# ────────────────────────────────────────────────────────────────
TECH_HOME = {
    "Alain Duguay": "1110 rue Proulx, Les Cèdres, QC J7T 1E6",
    "Alexandre Pelletier Guay": "163 21e ave, Sabrevois, J0J 2G0",
    "Ali Reza-Sabour": "226 rue Felx, Saint-Clet, QC J0P 1S0",
    "David Robitaille": "1271 route des lac, saint-marcelline de kildare, QC J0K 2Y0",
    "Patrick Robitaille": "3365 ave laurier est, Montréal, QC H1X 1V3",
    "Benoit Charrette": "34 rue de la Digue, Saint-Jérome, QC, J7Y 5J1",
    "Benoit Larame": "12 rue de Beaudry, Mercier, J6R 2N7",
    "Christian Dubrueil": "31 rue des Roitelets, Delson, J5B 1T6",
    "Donald Lagace (IN SHOP)": "Montée Saint-Régis, Sainte-Catherine, QC, Canada",
    "Elie Rajotte-Lemay": "3700 Mnt du 4e Rang, Les Maskoutains, J0H 1S0",
    "Francois Racine": "80 rue de Beaujeu, Coteau-du-lac, J0P 1B0",
    "Fredy Diaz": "312 rue de Valcourt, Blainville, J7B 1H3",
    "George Yamna": "Rue René-Lévesque, Saint-Eustache, J7R 7L4",
    "Kevin Duranceau": "943 rue des Marquises, Beloeil, J3G 6T9",
    "Louis Lauzon": "5005 rue Domville, Saint-Hubert, J3Y 1Y2",
    "Martin Bourbonnière": "1444 rue de l'Orchidée, L'Assomption QC J5W 6B3",
    "Maxime Roy": "1407 3e Rue, Saint-Blaise-sur-Richelieu, QC J0J 1W0",
    "Michael Sulte": "2020 chem. De Covery Hill, Hinchinbrooke, QC, J0S 1E0",
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

# ────────────────────────────────────────────────────────────────
# NEW: helper to add permanent labels on the map (tech + entrepôt)
# ────────────────────────────────────────────────────────────────
def add_labeled_marker(fmap: folium.Map, lat: float, lon: float, label: str, kind: str):
    """
    kind: "tech" or "wh"
    Adds a normal marker + a permanent label next to it (always visible).
    """
    if kind == "wh":
        icon = folium.Icon(color="red", icon="building", prefix="fa")
    else:
        icon = folium.Icon(color="blue", icon="user", prefix="fa")

    folium.Marker([lat, lon], icon=icon, popup=folium.Popup(label, max_width=320), tooltip=label).add_to(fmap)

    folium.Marker(
        [lat, lon],
        icon=folium.DivIcon(
            icon_size=(260, 22),
            icon_anchor=(0, -18),
            html=f"""
            <div style="display:inline-block;padding:2px 6px;
                font-size:12px;font-weight:700;color:#111;
                background:rgba(255,255,255,.95);
                border:1px solid #ddd;border-radius:6px;
                box-shadow:0 1px 2px rgba(0,0,0,.25);white-space:nowrap;">
                {label}
            </div>
            """
        ),
    ).add_to(fmap)

# ────────────────────────────────────────────────────────────────
# PAGE 1 (Route Optimizer)
# ────────────────────────────────────────────────────────────────
def render_page_1():
    cummins_header()

    # Travel options
    st.markdown("### Travel options")
    c1, c2 = st.columns([1.2, 1.2])
    with c1:
        st.markdown("**Travel mode:** Driving")
        leave_now = st.checkbox("Leave now", value=True, key="leave_now")
        round_trip = st.checkbox("Return to home at the end (round trip)?", value=True, key="round_trip")
    with c2:
        traffic_model = st.selectbox("Traffic model", ["best_guess", "pessimistic", "optimistic"], index=0, key="traffic_model")
        planned_date = st.date_input("Planned departure date", value=date.today(), disabled=leave_now, key="planned_date")
        planned_time = st.time_input("Planned departure time", value=datetime.now().time(), disabled=leave_now, key="planned_time")

    st.markdown("<hr style='margin:30px 0; border:1px solid #444;'>", unsafe_allow_html=True)

    if leave_now:
        departure_dt = datetime.now(timezone.utc)
    else:
        naive = datetime.combine(planned_date, planned_time)
        departure_dt = naive.replace(tzinfo=timezone.utc)

    # Technician capacities
    TECHNICIANS = [
        "Louis Lauzon","Patrick Bellefleur","Martin Bourbonniere","Francois Racine",
        "Alain Duguay","Benoit Charrette-gosselin","Donald Lagace","Ali Reza-sabour",
        "Kevin Duranceau","Maxime Roy","Christian Dubreuil","Pier-luc Cote","Fredy Diaz",
        "Alexandre Pelletier guay","Sergio Mendoza caron","Benoit Laramee","Georges Yamna nghuedieu",
        "Sebastien Pepin-millette","Elie Rajotte-lemay","Michael Sulte",
    ]

    EXCEL_URL = "https://cummins365.sharepoint.com/:x:/r/sites/GRP_CC40846-AdministrationFSPG/Shared%20Documents/Administration%20FSPG/Info%20des%20techs%20pour%20booking/CapaciteTechs_CandiacEtOttawa.xlsx?d=wa4a6497bebb642849d640c57e4db82de&csf=1&web=1&e=8ltLaR"
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/AR76F/route-optimizer/main/CapaciteTechs_CandiacEtOttawa.xlsx"

    hcol, bcol = st.columns([3, 2], vertical_alignment="center")
    with hcol:
        st.markdown("### 🧰 Technician capacities")
    with bcol:
        st.link_button("📎 Informations supplémentaires sur les techniciens", EXCEL_URL)

    st.caption("Choisis le type de service. On affiche les techniciens qui ont ce training **complété**.")

    if st.button("🔄 Recharger les données des trainings (GitHub)", key="refresh_trainings"):
        st.cache_data.clear()

    def _fetch_excel_df_from_github(raw_url: str, sheet: str, header=None) -> pd.DataFrame:
        r = requests.get(raw_url, timeout=30)
        r.raise_for_status()
        return pd.read_excel(BytesIO(r.content), sheet_name=sheet, header=header, engine="openpyxl")

    def _norm_name(s: str) -> str:
        return " ".join(str(s or "").strip().lower().split())

    def _excel_col_to_idx(col_letter: str) -> int:
        col_letter = col_letter.strip().upper()
        idx = 0
        for ch in col_letter:
            idx = idx * 26 + (ord(ch) - ord('A') + 1)
        return idx - 1

    SHEET_NAME = "Trainings"
    NAMES_COL_LETTER = "C"
    HEADER_ROW = 2
    TRAINING_COL_RANGE = ("H", "X")
    DATA_ROW_START = 3
    DATA_ROW_END = 22

    @st.cache_data(ttl=300, show_spinner=False)
    def get_training_options() -> list[tuple[str, int]]:
        df = _fetch_excel_df_from_github(GITHUB_RAW_URL, sheet=SHEET_NAME, header=None)
        r = HEADER_ROW - 1
        c_start = _excel_col_to_idx(TRAINING_COL_RANGE[0])
        c_end = _excel_col_to_idx(TRAINING_COL_RANGE[1])

        options = []
        for c in range(c_start, c_end + 1):
            val = df.iat[r, c] if (r < len(df) and c < df.shape[1]) else None
            label = str(val).strip() if val is not None and str(val).strip().lower() not in ("", "nan") else ""
            if label:
                options.append((label, c))
        return options

    @st.cache_data(ttl=300, show_spinner=False)
    def get_not_completed_by_col(training_col_idx: int) -> set:
        df = _fetch_excel_df_from_github(GITHUB_RAW_URL, sheet=SHEET_NAME, header=None)
        name_col_idx = _excel_col_to_idx(NAMES_COL_LETTER)
        r_start = max(0, DATA_ROW_START - 1)
        r_end = min(len(df) - 1, DATA_ROW_END - 1)

        sub = df.iloc[r_start:r_end + 1, [name_col_idx, training_col_idx]].copy()
        sub.columns = ["name", "status"]
        sub["status_norm"] = sub["status"].astype(str).str.strip().str.lower()
        not_completed_mask = sub["status_norm"].isin({"not completed", "notcompleted", "incomplete"})
        not_completed = sub[not_completed_mask]["name"].dropna()
        return {_norm_name(n) for n in not_completed.tolist()}

    def eligible_for(training_col_idx: int):
        not_ok_norm = get_not_completed_by_col(training_col_idx)
        return [t for t in TECHNICIANS if _norm_name(t) not in not_ok_norm]

    _training_pairs = get_training_options()
    _training_labels = ["(choisir)"] + [p[0] for p in _training_pairs]
    label_to_col = {label: col for (label, col) in _training_pairs}

    sel_training = st.selectbox("Type de service requis", _training_labels, index=0, key="tech_caps_training")
    if sel_training and sel_training != "(choisir)":
        col_idx = label_to_col.get(sel_training)
        techs = eligible_for(col_idx) if col_idx is not None else []
        if techs:
            st.success(f"{len(techs)} technicien(s) disponible(s) pour **{sel_training}**")
            for t in techs:
                st.write(f"• {t}")
        else:
            st.warning("Aucun technicien avec ce training complété.")

    # Point de départ
    st.markdown("---")
    st.subheader("🎯 Point de départ")

    if "route_start" not in st.session_state:
        st.session_state.route_start = ""
    if "storage_text" not in st.session_state:
        st.session_state.storage_text = ""

    tabs = st.tabs(["🚚 Live Fleet (Geotab)", "🏠 Technician Home"])

    # TAB 1 — GEOTAB LIVE FLEET
    with tabs[0]:
        G_DB = secret("GEOTAB_DATABASE")
        G_USER = secret("GEOTAB_USERNAME")
        G_PWD = secret("GEOTAB_PASSWORD")
        G_SERVER = secret("GEOTAB_SERVER", "my.geotab.com")
        geotab_enabled_by_secrets = GEOTAB_AVAILABLE and all([G_DB, G_USER, G_PWD])

        if geotab_enabled_by_secrets:
            if "geo_refresh_key" not in st.session_state:
                st.session_state.geo_refresh_key = 0
            if st.button("🔄 Rafraîchir Geotab maintenant", key="geo_refresh_btn"):
                st.session_state.geo_refresh_key += 1

            @st.cache_resource(show_spinner=False)
            def _geotab_api_cached(user, pwd, db, server):
                api = myg.API(user, pwd, db, server)
                api.authenticate()
                return api

            @st.cache_data(ttl=900, show_spinner=False)
            def _geotab_devices_cached(user, pwd, db, server):
                api = _geotab_api_cached(user, pwd, db, server)
                devs = api.call("Get", typeName="Device", search={"isActive": True}) or []
                return [{"id": d["id"], "name": d.get("name") or d.get("serialNumber") or "unit"} for d in devs]

            @st.cache_data(ttl=75, show_spinner=False)
            def _geotab_positions_for(api_params, device_ids, refresh_key):
                user, pwd, db, server = api_params
                api = _geotab_api_cached(user, pwd, db, server)
                results = []
                for did in device_ids:
                    try:
                        dsi = api.call("Get", typeName="DeviceStatusInfo", search={"deviceSearch": {"id": did}})
                        lat = lon = when = None
                        driver_name = None
                        if dsi:
                            row = dsi[0]
                            lat, lon = row.get("latitude"), row.get("longitude")
                            when = row.get("dateTime") or row.get("lastCommunicated") or row.get("workDate")
                            if (lat is None or lon is None) and isinstance(row.get("location"), dict):
                                lat = row["location"].get("y")
                                lon = row["location"].get("x")
                            drv = row.get("driver")
                            if isinstance(drv, dict):
                                driver_name = drv.get("name")
                        if lat is not None and lon is not None:
                            results.append({"deviceId": did, "lat": float(lat), "lon": float(lon),
                                            "when": when, "driverName": driver_name})
                        else:
                            results.append({"deviceId": did, "error": "no_position"})
                    except Exception:
                        results.append({"deviceId": did, "error": "error"})
                return results

            DEVICE_TO_DRIVER_RAW = {
                "01942": "ALI-REZA SABOUR", "24735": "PATRICK BELLEFLEUR", "23731": "ÉLIE RAJOTTE-LEMAY",
                "19004": "GEORGES YAMNA", "22736": "MARTIN BOURBONNIÈRE", "23738": "PIER-LUC CÔTÉ",
                "24724": "LOUIS LAUZON", "23744": "BENOÎT CHARETTE", "23727": "FREDY DIAZ",
                "23737": "ALAIN DUGUAY", "23730": "BENOÎT LARAMÉE", "24725": "CHRISTIAN DUBREUIL",
                "23746": "MICHAEL SULTE", "24728": "FRANÇOIS RACINE", "23743": "ALEX PELLETIER-GUAY",
                "23745": "KEVIN DURANCEAU", "23739": "MAXIME ROY",
            }

            import json
            try:
                j = secret("GEOTAB_DEVICE_TO_DRIVER_JSON")
                if j:
                    DEVICE_TO_DRIVER_RAW.update(json.loads(j))
            except Exception:
                pass

            def _norm(s: str) -> str:
                return " ".join(str(s or "").strip().upper().split())

            NAME2DRIVER, ID2DRIVER = {}, {}
            for k, v in DEVICE_TO_DRIVER_RAW.items():
                nk = _norm(k)
                if not nk:
                    continue
                if len(nk) > 12 or ("-" in nk and any(c.isalpha() for c in nk)):
                    ID2DRIVER[nk] = v
                else:
                    NAME2DRIVER[nk] = v

            def _driver_from_mapping(device_id: str, device_name: str) -> Optional[str]:
                n_id, n_name = _norm(device_id), _norm(device_name)
                return NAME2DRIVER.get(n_name) or ID2DRIVER.get(n_id) or ID2DRIVER.get(n_name) or NAME2DRIVER.get(n_id)

            def _label_for_device(device_id: str, device_name: str, driver_from_api: Optional[str]) -> str:
                driver = driver_from_api or _driver_from_mapping(device_id, device_name) or "(no driver)"
                dev_label = device_name or device_id
                return f"{driver} — {dev_label}"

            devs = _geotab_devices_cached(G_USER, G_PWD, G_DB, G_SERVER)
            if not devs:
                st.info("Aucun appareil actif trouvé.")
            else:
                options, label2id = [], {}
                for d in devs:
                    lbl = _label_for_device(d["id"], d["name"], None)
                    options.append(lbl)
                    label2id[lbl] = d["id"]

                picked_labels = st.multiselect(
                    "Sélectionner un ou plusieurs véhicules/techniciens à afficher :",
                    sorted(options),
                    default=[],
                    key="geo_pick_labels",
                )
                wanted_ids = [label2id[lbl] for lbl in picked_labels]

                if wanted_ids:
                    pts = _geotab_positions_for((G_USER, G_PWD, G_DB, G_SERVER), tuple(wanted_ids), st.session_state.geo_refresh_key)
                    id2name = {d["id"]: d["name"] for d in devs}
                    valid = [p for p in pts if "lat" in p and "lon" in p]
                    if valid:
                        avg_lat = sum(p["lat"] for p in valid) / len(valid)
                        avg_lon = sum(p["lon"] for p in valid) / len(valid)
                        fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="cartodbpositron")

                        choice_labels = []
                        for p in valid:
                            device_id = p["deviceId"]
                            device_name = id2name.get(device_id, device_id)
                            label = _label_for_device(device_id, device_name, p.get("driverName"))
                            choice_labels.append(label)

                            color, lab = recency_color(p.get("when"))
                            folium.CircleMarker(
                                [p["lat"], p["lon"]],
                                radius=8,
                                color="#222",
                                weight=2,
                                fill=True,
                                fill_color=color,
                                fill_opacity=0.9
                            ).add_to(fmap)

                            folium.Marker(
                                [p["lat"], p["lon"]],
                                popup=folium.Popup(
                                    f"<b>{label}</b><br>Recency: {lab}<br>{p['lat']:.5f}, {p['lon']:.5f}",
                                    max_width=320
                                ),
                                tooltip=label,
                                icon=folium.DivIcon(
                                    icon_size=(240, 22),
                                    icon_anchor=(0, -18),
                                    html=f"""
                                    <div style="display:inline-block;padding:2px 6px;
                                        font-size:12px;font-weight:700;color:#111;
                                        background:rgba(255,255,255,.95);
                                        border:1px solid #ddd;border-radius:6px;
                                        box-shadow:0 1px 2px rgba(0,0,0,.25);white-space:nowrap;">
                                        {label.split(' — ')[0]}
                                    </div>"""
                                )
                            ).add_to(fmap)

                        st_folium(fmap, height=800, width=1800)

                        start_choice = st.selectbox("Utiliser comme point de départ :", ["(aucun)"] + choice_labels, index=0, key="geo_start_choice")
                        if start_choice != "(aucun)":
                            chosen = valid[choice_labels.index(start_choice)]
                            picked_addr = reverse_geocode(gmaps_client, chosen["lat"], chosen["lon"])
                            st.session_state.route_start = picked_addr
                            st.success(f"Départ défini depuis **{start_choice}** → {picked_addr}")
                    else:
                        st.warning("Aucune position exploitable pour les éléments sélectionnés (essayez de rafraîchir).")
                else:
                    st.info("Sélectionnez au moins un véhicule/technicien pour afficher la carte.")
        else:
            st.info("Geotab désactivé. Ajoutez `GEOTAB_DATABASE`, `GEOTAB_USERNAME`, `GEOTAB_PASSWORD` dans les Secrets.")

    # TAB 2 — TECH HOMES + ENTREPOTS (labels permanents)
    with tabs[1]:
        st.markdown("### 🏠 Domiciles des techniciens et entrepôts")
        show_map = st.checkbox("Afficher la carte (techniciens + entrepôts)", value=False, key="techhome_show_map")

        def _extract_postal(addr: str) -> str:
            if not addr:
                return ""
            m = re.search(r"\b([A-Z]\d[A-Z])\s?(\d[A-Z]\d)\b", str(addr).upper())
            return (m.group(1) + m.group(2)) if m else ""

        tech_home_df = pd.DataFrame(
            [{"tech_name": name, "home_address": addr, "postal": _extract_postal(addr)}
             for name, addr in TECH_HOME.items()]
        )
        st.session_state["tech_home"] = tech_home_df

        if show_map:
            try:
                tech_points = []
                for name, addr in TECH_HOME.items():
                    g = geocode_ll(gmaps_client, addr)
                    if g:
                        lat, lon, formatted = g
                        tech_points.append({"name": name, "address": formatted, "lat": lat, "lon": lon})

                ent_points = []
                for ent_name, addr in ENTREPOTS.items():
                    g = geocode_ll(gmaps_client, addr)
                    if g:
                        lat, lon, formatted = g
                        ent_points.append({"name": ent_name, "address": formatted, "lat": lat, "lon": lon})

                points_all = tech_points + ent_points
                if points_all:
                    avg_lat = sum(p["lat"] for p in points_all) / len(points_all)
                    avg_lon = sum(p["lon"] for p in points_all) / len(points_all)
                    fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="cartodbpositron")

                    for p in ent_points:
                        add_labeled_marker(fmap, p["lat"], p["lon"], f"🏭 {p['name']}", kind="wh")

                    for p in tech_points:
                        add_labeled_marker(fmap, p["lat"], p["lon"], p["name"], kind="tech")

                    st_folium(fmap, height=800, width=1800)
                else:
                    st.warning("Aucun point géocodé à afficher.")
            except Exception as e:
                st.error(f"Erreur lors du chargement de la carte : {e}")

        st.markdown("#### Sélectionner les sources de départ / fin")
        c1b, c2b = st.columns(2)
        with c1b:
            tech_choice = st.selectbox(
                "Technicien → définir comme **départ**",
                ["(choisir)"] + sorted(TECH_HOME.keys()),
                key="tech_choice_start_tab2"
            )
            if tech_choice != "(choisir)":
                st.session_state.route_start = TECH_HOME[tech_choice]
                st.success(f"Départ défini sur **{tech_choice}** — {TECH_HOME[tech_choice]}")
        with c2b:
            ent_choice = st.selectbox(
                "Entrepôt → définir comme **stockage**",
                ["(choisir)"] + sorted(ENTREPOTS.keys()),
                key="entrepot_choice_storage_tab2"
            )
            if ent_choice != "(choisir)":
                st.session_state.storage_text = ENTREPOTS[ent_choice]
                st.success(f"Stockage défini sur **Entrepôt — {ent_choice}** — {ENTREPOTS[ent_choice]}")

    if st.session_state.get("route_start"):
        st.info(f"📍 **Point de départ sélectionné :** {st.session_state.route_start}")

    # Route stops
    st.markdown("### Route stops")
    start_text = st.text_input("Technician home (START)", key="route_start",
                               placeholder="e.g., 123 Main St, City, Province")
    storage_text = st.text_input("Storage location (first stop)", key="storage_text",
                                 placeholder="e.g., 456 Depot Rd, City, Province")
    stops_text = st.text_area("Other stops (one ZIP/postal code or full address per line)",
                              height=140, placeholder="H0H0H0\nG2P1L4\n…", key="stops_text")
    other_stops_input = [s.strip() for s in stops_text.splitlines() if s.strip()]

    # Optimize route — DRIVING ONLY
    st.markdown("---")
    if st.button("🧭 Optimize Route", type="primary", key="optimize_btn"):
        try:
            start_text = st.session_state.get("route_start", "").strip()
            storage_query = normalize_ca_postal(storage_text.strip()) if storage_text else ""
            other_stops_queries = [normalize_ca_postal(s.strip()) for s in other_stops_input if s.strip()]

            failures = []
            start_g = geocode_ll(gmaps_client, start_text)
            if not start_g:
                failures.append(f"START: `{start_text}`")

            storage_g = geocode_ll(gmaps_client, storage_query) if storage_query else None
            if storage_query and not storage_g:
                failures.append(f"STORAGE: `{storage_text}`")

            wp_raw = []
            if storage_query:
                wp_raw.append(("Storage", storage_query))
            for i, q in enumerate(other_stops_queries, start=1):
                wp_raw.append((f"Stop {i}", q))

            wp_geocoded: List[Tuple[str, str, Tuple[float, float]]] = []
            for label, q in wp_raw:
                g = geocode_ll(gmaps_client, q)
                if not g:
                    failures.append(f"{label}: `{q}`")
                else:
                    lat, lon, addr = g
                    wp_geocoded.append((label, addr, (lat, lon)))

            if failures:
                st.error("I couldn’t geocode some locations:\n\n- " + "\n- ".join(failures) +
                         "\n\nTip: use full street addresses if a postal code fails.")
                st.stop()

            def to_ll_str(ll: Tuple[float, float]) -> str:
                return f"{ll[0]:.7f},{ll[1]:.7f}"

            start_ll = (start_g[0], start_g[1])
            start_addr = start_g[2]

            wp_addrs = [addr for (_lbl, addr, _ll) in wp_geocoded]
            wp_llstr = [to_ll_str(ll) for (_lbl, _addr, ll) in wp_geocoded]

            if len(wp_llstr) > 23:
                st.error("Too many stops. Google allows up to **25 total** (origin + destination + waypoints).")
                st.stop()

            if st.session_state.get("round_trip", True):
                destination_addr = start_addr
                destination_llstr = to_ll_str(start_ll)
                waypoints_for_api = wp_llstr[:]
            else:
                if wp_llstr:
                    destination_addr = wp_addrs[-1]
                    destination_llstr = wp_llstr[-1]
                    waypoints_for_api = wp_llstr[:-1]
                else:
                    if storage_g:
                        destination_addr = storage_g[2]
                        destination_llstr = to_ll_str((storage_g[0], storage_g[1]))
                    else:
                        destination_addr = start_addr
                        destination_llstr = to_ll_str(start_ll)
                    waypoints_for_api = []

            wp_arg = (["optimize:true"] + waypoints_for_api) if waypoints_for_api else None

            directions = gmaps_client.directions(
                origin=to_ll_str(start_ll),
                destination=destination_llstr,
                mode="driving",
                waypoints=wp_arg,
                departure_time=departure_dt,
                traffic_model=st.session_state.get("traffic_model", "best_guess"),
            )

            if not directions:
                st.error("No route returned by Google Directions (driving). Try replacing postal codes with full addresses.")
                st.json({"origin": to_ll_str(start_ll), "destination": destination_llstr, "waypoints": waypoints_for_api})
                st.stop()

            if waypoints_for_api:
                order = directions[0].get("waypoint_order", list(range(len(waypoints_for_api))))
                ordered_wp_addrs = [wp_addrs[i] for i in order]
                if not st.session_state.get("round_trip", True) and wp_addrs:
                    ordered_wp_addrs.append(destination_addr)
            else:
                ordered_wp_addrs = [] if st.session_state.get("round_trip", True) else [destination_addr]

            visit_texts = [start_addr] + ordered_wp_addrs + ([start_addr] if st.session_state.get("round_trip", True) else [destination_addr])

            legs = directions[0].get("legs", [])
            total_dist_m = sum(leg.get("distance", {}).get("value", 0) for leg in legs)
            total_sec = sum((leg.get("duration_in_traffic") or leg.get("duration") or {}).get("value", 0) for leg in legs)
            km = total_dist_m / 1000.0 if total_dist_m else 0.0
            mins = total_sec / 60.0 if total_sec else 0.0

            per_leg = []
            current_dt = departure_dt
            for i, leg in enumerate(legs, start=1):
                dur = leg.get("duration_in_traffic") or leg.get("duration") or {}
                dur_sec = int(dur.get("value", 0))
                leg_mins = round(dur_sec / 60.0)
                dist_m = int(leg.get("distance", {}).get("value", 0))
                dist_km = dist_m / 1000.0
                current_dt = current_dt + timedelta(seconds=dur_sec)
                arr_str = current_dt.astimezone().strftime("%H:%M")
                stop_addr = visit_texts[i] if i < len(visit_texts) else ""
                per_leg.append({"idx": i, "to": stop_addr, "dist_km": dist_km, "mins": leg_mins, "arrive": arr_str})

            st.session_state.route_result = {
                "visit_texts": visit_texts,
                "km": km,
                "mins": mins,
                "start_ll": start_ll,
                "wp_geocoded": wp_geocoded,
                "round_trip": st.session_state.get("round_trip", True),
                "overview": directions[0].get("overview_polyline", {}).get("points"),
                "per_leg": per_leg,
            }

        except Exception as e:
            st.error(f"Unexpected error: {type(e).__name__}: {e}")
            st.exception(e)

    # Render result
    res = st.session_state.get("route_result")
    if res:
        visit_texts = res["visit_texts"]
        km = res["km"]
        mins = res["mins"]
        start_ll = tuple(res["start_ll"])
        wp_geocoded = res["wp_geocoded"]
        round_trip_res = res["round_trip"]
        overview = res.get("overview")
        per_leg = res.get("per_leg", [])

        st.markdown("#### Optimized order (Driving)")
        for ix, addr in enumerate(visit_texts):
            if ix == 0:
                st.write(f"**START** — {addr}")
            elif ix == len(visit_texts) - 1:
                st.write(f"**END** — {addr}")
            else:
                st.write(f"**{ix}** — {addr}")

        if per_leg:
            st.markdown("#### Stop-by-stop timing")
            for leg in per_leg:
                st.write(f"**{leg['idx']}** → _{leg['to']}_  •  {leg['dist_km']:.1f} km  •  {leg['mins']} mins  •  **ETA {leg['arrive']}**")

        show_map2 = st.checkbox("Show map", value=False, key="route_show_map")
        if show_map2:
            try:
                fmap = folium.Map(location=[start_ll[0], start_ll[1]], zoom_start=9, tiles="cartodbpositron")
                if overview:
                    try:
                        path = polyline.decode(overview)
                        folium.PolyLine(path, weight=7, color="#2196f3", opacity=0.9).add_to(fmap)
                    except Exception:
                        pass

                folium.Marker(
                    start_ll,
                    icon=folium.Icon(color="green", icon="play", prefix="fa"),
                    popup=folium.Popup(f"<b>START</b><br>{visit_texts[0]}", max_width=260)
                ).add_to(fmap)

                addr2ll = {addr: ll for (_lbl, addr, ll) in wp_geocoded}
                for i, addr in enumerate(visit_texts[1:-1], start=1):
                    ll = addr2ll.get(addr)
                    if ll:
                        folium.Marker(
                            ll,
                            popup=folium.Popup(f"<b>{i}</b>. {addr}", max_width=260),
                            icon=big_number_marker(str(i))
                        ).add_to(fmap)

                end_addr = visit_texts[-1]
                end_ll = addr2ll.get(end_addr)
                if not end_ll:
                    g = geocode_ll(gmaps_client, end_addr)
                    if g:
                        end_ll = (g[0], g[1])

                if end_ll:
                    folium.Marker(
                        end_ll,
                        icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
                        popup=folium.Popup(f"<b>{'END (Home)' if round_trip_res else 'END'}</b><br>{end_addr}", max_width=260)
                    ).add_to(fmap)

                st_folium(fmap, height=800, width=1800)
            except Exception as e:
                st.warning(f"Map rendering skipped: {e}")

        st.success(f"**Total distance:** {km:.1f} km • **Total time:** {mins:.0f} mins (live traffic)")

import os
import re
import math
import calendar
from io import BytesIO
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

import streamlit as st
import pandas as pd

# ===============================================================
# PAGE 2 (Planning) — VERSION FIXED + REPAIR PASS
# + ✅ AJOUT: Integrity Check (jobs manquants à ajouter manuellement)
# (COLLER CETTE SECTION 1/2, puis la SECTION 2/2 juste après)
# ===============================================================

def render_page_2():
    import calendar
    import math
    import sqlite3
    import time
    import hashlib
    from datetime import date, timedelta
    from io import BytesIO
    from typing import List, Optional, Tuple, Dict, Any

    st.title("📅 Planning (Page 2)")

    # Load tech_home from page 1 (or build fallback)
    tech_df = st.session_state.get("tech_home")
    if tech_df is None or len(tech_df) == 0:
        def _extract_postal(addr: str) -> str:
            if not addr:
                return ""
            m = re.search(r"\b([A-Z]\d[A-Z])\s?(\d[A-Z]\d)\b", str(addr).upper())
            return (m.group(1) + m.group(2)) if m else ""

        tech_df = pd.DataFrame(
            [{"tech_name": name, "home_address": addr, "postal": _extract_postal(addr)}
             for name, addr in TECH_HOME.items()]
        )
        st.session_state["tech_home"] = tech_df

    expected_cols = {"tech_name", "home_address"}
    if not expected_cols.issubset(set(tech_df.columns)):
        st.error("tech_home doit contenir tech_name et home_address.")
        st.stop()

    # Upload Jobs Excel (persistant)
    st.subheader("📤 Jobs – Upload Excel")
    uploaded = st.file_uploader("Upload ton fichier Excel jobs", type=["xlsx"], key="jobs_uploader")
    if uploaded:
        st.session_state["jobs_file_bytes"] = uploaded.getvalue()
        st.session_state["jobs_file_name"] = uploaded.name

    if "jobs_file_bytes" not in st.session_state:
        st.info("Upload un fichier Excel pour continuer (il sera conservé même si tu changes de page).")
        st.stop()

    data = BytesIO(st.session_state["jobs_file_bytes"])
    try:
        jobs_raw = pd.read_excel(data, sheet_name="Export", engine="openpyxl")
    except Exception:
        data.seek(0)
        jobs_raw = pd.read_excel(data, sheet_name=0, engine="openpyxl")

    st.caption(f"Jobs détectés: {len(jobs_raw)}")
    st.dataframe(jobs_raw.head(20), use_container_width=True)

    # Column mapping helper
    def pick_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        cols = {c.lower().strip(): c for c in df.columns}
        for cand in candidates:
            k = cand.lower().strip()
            if k in cols:
                return cols[k]
        return None

    COL_ORDER = pick_col(jobs_raw, ["ORDER #", "ORDER#", "Order", "Job ID", "WO", "Work Order"])
    COL_CUST  = pick_col(jobs_raw, ["CUST. #", "CUST #", "CUST#", "CUSTOMER #", "CUSTOMER#", "Customer #"])
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
        st.error("Je ne trouve pas la colonne Job/Order (#). Assure-toi qu’elle existe dans ton export.")
        st.stop()

    # ✅ Clean IDs: "347762.0" -> "347762" (but keep alphanumeric IDs intact)
    def clean_id(x):
        try:
            if pd.isna(x):
                return ""
        except Exception:
            pass
        s = str(x).strip()
        if re.fullmatch(r"\d+\.0+", s):
            return s.split(".")[0]
        return s

    def build_address(row: pd.Series) -> str:
        parts = []
        for c in [COL_ADDR1, COL_ADDR2, COL_ADDR3, COL_CITY, COL_PROV, COL_POST]:
            if c and pd.notna(row.get(c)) and str(row.get(c)).strip():
                parts.append(str(row.get(c)).strip())
        return ", ".join(parts)

    def extract_postal(s: str) -> str:
        if not s:
            return ""
        m = re.search(r"\b([A-Z]\d[A-Z])\s?(\d[A-Z]\d)\b", str(s).upper())
        return (m.group(1) + m.group(2)) if m else ""

    jobs = pd.DataFrame()
    jobs["job_id"] = jobs_raw[COL_ORDER].apply(clean_id)
    jobs["cust"] = jobs_raw[COL_CUST].apply(clean_id) if COL_CUST else ""
    jobs["address"] = jobs_raw.apply(build_address, axis=1)

    desc = jobs_raw[COL_DESC].fillna("").astype(str) if COL_DESC else ""
    up   = jobs_raw[COL_UP].fillna("").astype(str) if COL_UP else ""
    jobs["description"] = (desc + " | " + up).str.strip(" |")

    ons = pd.to_numeric(jobs_raw[COL_ONS], errors="coerce") if COL_ONS else None
    srt = pd.to_numeric(jobs_raw[COL_SRT], errors="coerce") if COL_SRT else None
    if ons is not None:
        hours = ons
    elif srt is not None:
        hours = srt
    else:
        st.error("Je ne trouve pas ONSITE SRT HRS ni SRT HRS pour calculer la durée.")
        st.stop()

    jobs["job_minutes"] = (hours.fillna(0) * 60).round().astype(int)

    techs_needed = pd.to_numeric(jobs_raw[COL_TECHN], errors="coerce") if COL_TECHN else None
    jobs["techs_needed"] = techs_needed.fillna(1).astype(int) if techs_needed is not None else 1

    jobs["postal"] = jobs_raw[COL_POST].fillna("").astype(str).apply(extract_postal) if COL_POST else ""

    # Clean jobs
    jobs = jobs[(jobs["address"].astype(str).str.len() > 8) & (jobs["job_minutes"] > 0)].copy()
    jobs = jobs.drop_duplicates(subset=["job_id"]).reset_index(drop=True)

    # ✅ FIX #1 (déterminisme): ordre stable global des jobs
    jobs = jobs.sort_values(["techs_needed", "job_id"], kind="mergesort").reset_index(drop=True)

    # ────────────────────────────────────────────────────────────────
    # Shared helpers
    # ────────────────────────────────────────────────────────────────
    MONTHS_FR = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]

    def month_selector(prefix: str) -> Tuple[date, date]:
        today = date.today()
        c1, c2 = st.columns(2)
        with c1:
            year = st.selectbox("Année", list(range(today.year - 1, today.year + 3)), index=1, key=f"{prefix}_year")
        with c2:
            month_name = st.selectbox("Mois", MONTHS_FR, index=today.month - 1, key=f"{prefix}_month")
        month_num = MONTHS_FR.index(month_name) + 1
        month_start = date(year, month_num, 1)
        last_day = calendar.monthrange(year, month_num)[1]
        month_end = date(year, month_num, last_day)
        st.caption(f"📅 Période planifiée : {month_start} → {month_end} (lundi→vendredi)")
        return month_start, month_end

    def business_days(start: date, end: date) -> List[date]:
        out = []
        d = start
        while d <= end:
            if d.weekday() < 5:
                out.append(d)
            d += timedelta(days=1)
        return out

    def mm_to_hhmm(m: int) -> str:
        h = m // 60
        mm = m % 60
        return f"{h:02d}:{mm:02d}"

    # ────────────────────────────────────────────────────────────────
    # ✅ COST REDUCTION #1: Persistent SQLite cache for travel (multi-user safe)
    # ────────────────────────────────────────────────────────────────
    DB_PATH = st.session_state.get("p2_travel_cache_db", "/tmp/travel_cache.sqlite")

    st.sidebar.subheader("🧾 Coûts / Cache")
    use_traffic = st.sidebar.checkbox("Utiliser trafic (duration_in_traffic)", value=True, key="p2_use_traffic")
    cache_days = st.sidebar.number_input("Conserver cache (jours)", min_value=1, max_value=365, value=30, step=1, key="p2_cache_days")

    st.sidebar.subheader("🧭 Préfiltrage géographique")
    solo_pool = st.sidebar.slider("SOLO: nb de jobs candidats (pool)", 10, 200, 60, 10, key="p2_solo_pool")
    duo_pool = st.sidebar.slider("DUO: nb de jobs candidats (pool)", 10, 300, 80, 10, key="p2_duo_pool")
    techs_near_job = st.sidebar.slider("DUO: nb de techs proches à tester", 2, 6, 4, 1, key="p2_duo_near_techs")
    include_nearby_fsa = st.sidebar.checkbox("Inclure FSA voisins si peu de candidats", value=True, key="p2_include_nearby_fsa")  # kept for UI; no longer used

    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", str(s or "").strip().lower())

    def _key(origin: str, dest: str, traffic_flag: bool) -> str:
        raw = f"{_norm(origin)}|{_norm(dest)}|driving|traffic={int(bool(traffic_flag))}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _db():
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS travel (
                k TEXT PRIMARY KEY,
                minutes INTEGER,
                ts INTEGER
            )
        """)
        return conn

    if "p2_api_calls" not in st.session_state:
        st.session_state["p2_api_calls"] = 0
    if "p2_cache_hits" not in st.session_state:
        st.session_state["p2_cache_hits"] = 0

    def travel_min_cached(origin: str, dest: str) -> int:
        if not origin or not dest:
            return 9999

        k = _key(origin, dest, use_traffic)
        now = int(time.time())
        min_ts = now - int(cache_days) * 86400

        conn = _db()
        cur = conn.cursor()
        cur.execute("SELECT minutes, ts FROM travel WHERE k=? AND ts>=?", (k, min_ts))
        row = cur.fetchone()
        if row:
            conn.close()
            st.session_state["p2_cache_hits"] += 1
            return int(row[0])

        try:
            r = gmaps_client.distance_matrix([origin], [dest], mode="driving")
            el = r["rows"][0]["elements"][0]
            if el.get("status") != "OK":
                conn.close()
                return 9999

            if use_traffic:
                dur = el.get("duration_in_traffic") or el.get("duration") or {}
            else:
                dur = el.get("duration") or el.get("duration_in_traffic") or {}
            minutes = int(round(int(dur.get("value", 0)) / 60))
        except Exception:
            conn.close()
            return 9999

        conn.execute("INSERT OR REPLACE INTO travel(k, minutes, ts) VALUES(?,?,?)", (k, minutes, now))
        conn.commit()
        conn.close()
        st.session_state["p2_api_calls"] += 1
        return minutes

    # ────────────────────────────────────────────────────────────────
    # ✅ LAT/LON cache + haversine + sector rule
    # ────────────────────────────────────────────────────────────────
    def haversine_km(lat1, lon1, lat2, lon2) -> float:
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return 1e9
        R = 6371.0
        p1 = math.radians(float(lat1))
        p2 = math.radians(float(lat2))
        dp = math.radians(float(lat2) - float(lat1))
        dl = math.radians(float(lon2) - float(lon1))
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    if "p2_ll_cache" not in st.session_state:
        st.session_state["p2_ll_cache"] = {}
    ll_cache: Dict[str, Tuple[float, float]] = st.session_state["p2_ll_cache"]

    def get_ll_for_address(addr: str) -> Tuple[Optional[float], Optional[float]]:
        if not addr:
            return None, None
        key = _norm(addr)
        if key in ll_cache:
            return ll_cache[key][0], ll_cache[key][1]
        g = geocode_ll(gmaps_client, addr)  # cached 30 days (page 1 helper)
        if g:
            lat, lon, _ = g
            ll_cache[key] = (float(lat), float(lon))
            return float(lat), float(lon)
        ll_cache[key] = (None, None)
        return None, None

    def classify_sector(lat: Optional[float], lon: Optional[float]) -> str:
        if lat is None or lon is None:
            return "UNK"
        lat = float(lat); lon = float(lon)
        if (45.40 <= lat <= 45.72) and (-74.10 <= lon <= -73.40):
            return "MTL"
        return "NORTH" if lat >= 45.55 else "SOUTH"

    def sector_compatible(tech_sector: str, job_sector: str) -> bool:
        if tech_sector == "UNK" or job_sector == "UNK":
            return True
        if tech_sector == "MTL" or job_sector == "MTL":
            return True
        if (tech_sector == "SOUTH" and job_sector == "NORTH") or (tech_sector == "NORTH" and job_sector == "SOUTH"):
            return False
        return True

    tech_names_all = sorted(tech_df["tech_name"].astype(str).tolist())
    home_map = {t: tech_df.loc[tech_df["tech_name"] == t, "home_address"].iloc[0] for t in tech_names_all}

    tech_ll_map: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    tech_sector_map: Dict[str, str] = {}
    for t in tech_names_all:
        lat, lon = get_ll_for_address(home_map[t])
        tech_ll_map[t] = (lat, lon)
        tech_sector_map[t] = classify_sector(lat, lon)

    # Ensure columns exist
    if "job_lat" not in jobs.columns:
        jobs["job_lat"] = None
        jobs["job_lon"] = None
        jobs["job_sector"] = "UNK"

    # ✅ FIX #2: persist lat/lon/sector back into the dataframe using idx
    def ensure_job_ll_idx(df: pd.DataFrame, idx) -> Tuple[Optional[float], Optional[float], str]:
        r = df.loc[idx]
        lat = r.get("job_lat")
        lon = r.get("job_lon")
        sec = r.get("job_sector", "UNK") or "UNK"
        if pd.notna(lat) and pd.notna(lon):
            lat = float(lat); lon = float(lon)
            if sec == "UNK":
                sec = classify_sector(lat, lon)
                df.at[idx, "job_sector"] = sec
            return lat, lon, sec

        lat, lon = get_ll_for_address(r["address"])
        sec = classify_sector(lat, lon)
        df.at[idx, "job_lat"] = lat
        df.at[idx, "job_lon"] = lon
        df.at[idx, "job_sector"] = sec
        return lat, lon, sec

    # Pool by lat/lon (stable)
    def get_job_pool_for_tech(df_remaining: pd.DataFrame, tech_name: str, pool_size: int) -> pd.DataFrame:
        if df_remaining.empty:
            return df_remaining
        df_remaining = df_remaining.sort_values(["job_id"], kind="mergesort")
        tlat, tlon = tech_ll_map.get(tech_name, (None, None))
        tsec = tech_sector_map.get(tech_name, "UNK")

        dists = []
        for idx, r in df_remaining.iterrows():
            lat, lon, jsec = ensure_job_ll_idx(df_remaining, idx)
            if not sector_compatible(tsec, jsec):
                continue
            d = haversine_km(tlat, tlon, lat, lon)
            dists.append((idx, d))

        if not dists:
            return df_remaining.head(pool_size) if len(df_remaining) > pool_size else df_remaining

        dists.sort(key=lambda x: x[1])
        chosen_idx = [i for (i, _d) in dists[:int(pool_size)]]
        return df_remaining.loc[chosen_idx].copy()

    def rank_techs_for_job(tech_names: List[str], job_row: pd.Series, top_n: int) -> List[str]:
        if top_n >= len(tech_names):
            return tech_names
        jlat, jlon = get_ll_for_address(job_row.get("address", ""))
        jsec = classify_sector(jlat, jlon)

        scored = []
        for t in tech_names:
            tlat, tlon = tech_ll_map.get(t, (None, None))
            tsec = tech_sector_map.get(t, "UNK")
            if not sector_compatible(tsec, jsec):
                continue
            d = haversine_km(tlat, tlon, jlat, jlon)
            scored.append((t, d))

        if not scored:
            return tech_names[:max(2, int(top_n))]

        scored.sort(key=lambda x: x[1])
        return [t for (t, _d) in scored[:max(2, int(top_n))]]

    # ────────────────────────────────────────────────────────────────
    # Styling (unchanged)
    # ────────────────────────────────────────────────────────────────
    def style_duo(df: pd.DataFrame):
        if df is None or df.empty:
            return df

        def _row_style(row):
            ot_val = str(row.get("ot", "")).strip().lower()
            if ot_val:
                css = (
                    "background-color: #f8d7da;"
                    "color: #000000;"
                    "font-weight: 900;"
                    "border-left: 6px solid #b02a37;"
                )
                return [css] * len(row)

            if "techs_needed" not in row:
                return [""] * len(row)
            try:
                n = int(row.get("techs_needed", 1))
            except Exception:
                n = 1

            if n >= 3:
                css = (
                    "background-color: #f8d7da;"
                    "color: #000000;"
                    "font-weight: 800;"
                    "border-left: 6px solid #b02a37;"
                )
                return [css] * len(row)
            if n == 2:
                css = (
                    "background-color: #ffd966;"
                    "color: #000000;"
                    "font-weight: 700;"
                    "border-left: 6px solid #ff9800;"
                )
                return [css] * len(row)
            return [""] * len(row)

        return df.style.apply(_row_style, axis=1)

    INSPECTION_KEYWORDS = ["inspection", "generator inspection", "génératrice inspection", "inspection génératrice"]

    def filter_by_service_type(df: pd.DataFrame, mode_label: str) -> pd.DataFrame:
        if mode_label == "Inclure full service (tous les jobs)":
            return df
        if "description" not in df.columns:
            return df
        s = df["description"].fillna("").astype(str).str.lower()
        mask = False
        for kw in INSPECTION_KEYWORDS:
            mask = mask | s.str.contains(kw, na=False)
        if mode_label == "Generator inspection seulement":
            return df[mask].copy()
        if mode_label == "Exclure generator inspection":
            return df[~mask].copy()
        return df

    def compute_total_parts(job_minutes_total: int, daily_onsite_cap: int) -> int:
        if daily_onsite_cap <= 0:
            return 1
        return int(math.ceil(float(job_minutes_total) / float(daily_onsite_cap)))

    # ────────────────────────────────────────────────────────────────
    # Month scheduler with DUO booking + sequence + return home
    # ────────────────────────────────────────────────────────────────
    def schedule_month_with_duo(
        jobs_in: pd.DataFrame,
        tech_names: List[str],
        month_days: List[date],
        day_hours: float,
        lunch_min: int,
        buffer_job: int,
        max_jobs_per_day: int,
        allow_duo: bool,
        progress=None,
        progress_text=None
    ) -> dict:
        available = int(round(day_hours * 60)) - int(lunch_min)
        if available <= 0:
            return {"success": False, "rows": [], "remaining": jobs_in, "reason": "Heures/jour - pause <= 0"}

        daily_onsite_cap = int(available)
        MIN_ONSITE_CHUNK_MIN = 180

        OT_ACTIVE_CAP = int(round(14 * 60)) - int(lunch_min)
        if OT_ACTIVE_CAP < available:
            OT_ACTIVE_CAP = available

        def _choose_onsite_no_crumbs(remaining_min: int, max_onsite_today: int, min_chunk: int) -> int:
            remaining_min = int(remaining_min)
            max_onsite_today = int(max_onsite_today)
            min_chunk = int(min_chunk)
            if max_onsite_today <= 0:
                return 0

            onsite_today = min(remaining_min, max_onsite_today)
            if onsite_today >= remaining_min:
                return onsite_today

            rem_after = remaining_min - onsite_today
            if onsite_today < min_chunk:
                return 0
            if rem_after < min_chunk:
                if remaining_min <= max_onsite_today:
                    return remaining_min
                onsite_today = remaining_min - min_chunk
                onsite_today = min(onsite_today, max_onsite_today)
                if onsite_today < min_chunk:
                    return 0
                rem_after = remaining_min - onsite_today
                if rem_after > 0 and rem_after < min_chunk:
                    return 0
                return onsite_today
            return onsite_today

        remaining_all = jobs_in.copy()
        remaining_all = remaining_all.sort_values(["techs_needed", "job_id"], kind="mergesort").reset_index(drop=True)

        duo_jobs = remaining_all[remaining_all["techs_needed"] == 2].copy() if allow_duo else remaining_all.iloc[0:0].copy()
        solo_jobs = remaining_all[remaining_all["techs_needed"] <= 1].copy()
        hard_jobs = remaining_all[remaining_all["techs_needed"] > 2].copy()

        duo_jobs = duo_jobs.sort_values(["job_id"], kind="mergesort")
        solo_jobs = solo_jobs.sort_values(["job_id"], kind="mergesort")
        hard_jobs = hard_jobs.sort_values(["job_id"], kind="mergesort")

        planned_rows: List[Dict[str, Any]] = []

        _home_map = {t: home_map[t] for t in tech_names}
        _tech_sector = {t: tech_sector_map.get(t, "UNK") for t in tech_names}

        carryover_by_tech: Dict[str, Dict[str, Any]] = {}
        split_label_state: Dict[str, Dict[str, Any]] = {}

        def _register_and_relabel_split_row(base_job_id: str, new_row_idx: int, part_num: int):
            if base_job_id not in split_label_state:
                split_label_state[base_job_id] = {"total": int(part_num), "row_idxs": []}
            stt = split_label_state[base_job_id]
            if int(part_num) > int(stt["total"]):
                stt["total"] = int(part_num)
            stt["row_idxs"].append(int(new_row_idx))
            total = int(stt["total"])
            for i, ridx in enumerate(stt["row_idxs"], start=1):
                base = re.sub(r"\s*\(PART\s+\d+/\d+\)\s*$", "", str(planned_rows[ridx]["job_id"])).strip()
                planned_rows[ridx]["job_id"] = f"{base} (PART {i}/{total})"

        def _book_split_part_for_tech(
            day: date,
            t: str,
            used: Dict[str, int],
            cur_loc: Dict[str, str],
            jobs_count: Dict[str, int],
            lock_tech: Dict[str, bool],
            split_state: Dict[str, Any],
        ):
            addr = split_state["address"]
            base_job_id = split_state["base_job_id"]
            cust = split_state.get("cust", "")
            desc = split_state.get("description", "")
            techs_needed_val = int(split_state.get("techs_needed", 1))

            tsec = _tech_sector.get(t, "UNK")
            jlat, jlon = get_ll_for_address(addr)
            jsec = classify_sector(jlat, jlon)
            if not sector_compatible(tsec, jsec):
                return

            remaining_min = int(split_state["remaining_job_min"])
            part_idx = int(split_state["part_idx_next"])

            tmin = travel_min_cached(cur_loc[t], addr)
            tback = travel_min_cached(addr, _home_map[t])

            max_onsite_today = int(available) - int(used[t]) - int(tmin) - int(buffer_job) - int(tback)
            if max_onsite_today <= 0:
                return

            onsite_today = _choose_onsite_no_crumbs(remaining_min, max_onsite_today, MIN_ONSITE_CHUNK_MIN)
            if onsite_today <= 0:
                return

            jobs_count[t] += 1
            start_m = int(used[t]) + int(tmin)
            end_m = start_m + int(onsite_today) + int(buffer_job)

            planned_rows.append({
                "date": day.isoformat(),
                "technicien": t,
                "sequence": jobs_count[t],
                "job_id": f"{base_job_id} (PART {part_idx}/{max(1, int(split_state.get('total_parts', part_idx)) )})",
                "cust": cust,
                "duo": "",
                "ot": "",
                "debut": mm_to_hhmm(int(start_m)),
                "fin": mm_to_hhmm(int(end_m)),
                "adresse": addr,
                "travel_min": int(tmin),
                "job_min": int(onsite_today),
                "buffer_min": int(buffer_job),
                "techs_needed": techs_needed_val,
                "description": desc,
            })

            row_idx = len(planned_rows) - 1
            _register_and_relabel_split_row(base_job_id, row_idx, part_idx)

            used[t] = int(end_m)
            cur_loc[t] = addr

            remaining_min = int(remaining_min) - int(onsite_today)
            split_state["remaining_job_min"] = remaining_min
            split_state["part_idx_next"] = part_idx + 1

            lock_tech[t] = True if remaining_min > 0 else False

        total_steps = max(1, len(month_days))

        for di, day in enumerate(month_days):
            used = {t: 0 for t in tech_names}
            cur_loc = {t: _home_map[t] for t in tech_names}
            jobs_count = {t: 0 for t in tech_names}
            lock_tech = {t: False for t in tech_names}

            # Continue split jobs first
            for t in tech_names:
                if t in carryover_by_tech:
                    _book_split_part_for_tech(
                        day=day,
                        t=t,
                        used=used,
                        cur_loc=cur_loc,
                        jobs_count=jobs_count,
                        lock_tech=lock_tech,
                        split_state=carryover_by_tech[t],
                    )
                    if int(carryover_by_tech[t]["remaining_job_min"]) <= 0:
                        del carryover_by_tech[t]

            # ---- 1) DUO first ----
            if allow_duo and (not duo_jobs.empty) and len(tech_names) >= 2:
                while True:
                    if duo_jobs.empty:
                        break

                    best = None
                    duo_jobs = duo_jobs.sort_values(["job_id"], kind="mergesort")
                    sample = duo_jobs.head(int(duo_pool)) if len(duo_jobs) > int(duo_pool) else duo_jobs

                    for jidx, job in sample.iterrows():
                        addr = job["address"]
                        job_min_total = int(job["job_minutes"])
                        job_min_each = int(math.ceil(job_min_total / 2.0))
                        need_block = int(job_min_each) + int(buffer_job)

                        near_techs = rank_techs_for_job(tech_names, pd.Series({"address": addr}), int(techs_near_job))
                        jlat, jlon = get_ll_for_address(addr)
                        jsec = classify_sector(jlat, jlon)

                        for i in range(len(near_techs)):
                            for k in range(i + 1, len(near_techs)):
                                t1 = near_techs[i]
                                t2 = near_techs[k]

                                if lock_tech.get(t1) or lock_tech.get(t2):
                                    continue
                                if jobs_count[t1] >= int(max_jobs_per_day) or jobs_count[t2] >= int(max_jobs_per_day):
                                    continue
                                if not sector_compatible(_tech_sector.get(t1, "UNK"), jsec):
                                    continue
                                if not sector_compatible(_tech_sector.get(t2, "UNK"), jsec):
                                    continue

                                duo_is_overtime = False
                                if int(job_min_each) > int(daily_onsite_cap):
                                    if (int(job_min_each) - int(daily_onsite_cap)) < 180:
                                        if jobs_count[t1] != 0 or jobs_count[t2] != 0:
                                            continue
                                        duo_is_overtime = True
                                    else:
                                        continue

                                t1_tr = travel_min_cached(cur_loc[t1], addr)
                                t2_tr = travel_min_cached(cur_loc[t2], addr)
                                start_m = max(used[t1] + int(t1_tr), used[t2] + int(t2_tr))
                                end_m = start_m + int(need_block)

                                t1_back = travel_min_cached(addr, _home_map[t1])
                                t2_back = travel_min_cached(addr, _home_map[t2])

                                if (end_m + int(t1_back) <= available) and (end_m + int(t2_back) <= available):
                                    score = (start_m, max(int(t1_tr), int(t2_tr)))
                                    if best is None or score < best[0]:
                                        best = (
                                            score, jidx, t1, t2,
                                            start_m, end_m,
                                            int(t1_tr), int(t2_tr),
                                            duo_is_overtime,
                                            int(job_min_each)
                                        )

                    if best is None:
                        break

                    _, jidx, t1, t2, start_m, end_m, t1_tr, t2_tr, duo_is_overtime, job_min_each = best
                    job = duo_jobs.loc[jidx]

                    for tname, trv in [(t1, t1_tr), (t2, t2_tr)]:
                        jobs_count[tname] += 1
                        planned_rows.append({
                            "date": day.isoformat(),
                            "technicien": tname,
                            "sequence": jobs_count[tname],
                            "job_id": job["job_id"],
                            "cust": job.get("cust", ""),
                            "duo": "⚠️ DUO",
                            "ot": "",
                            "debut": mm_to_hhmm(int(start_m)),
                            "fin": mm_to_hhmm(int(end_m)),
                            "adresse": job["address"],
                            "travel_min": int(trv),
                            "job_min": int(job_min_each),
                            "buffer_min": int(buffer_job),
                            "techs_needed": int(job["techs_needed"]),
                            "description": job["description"],
                        })
                        used[tname] = int(end_m)
                        cur_loc[tname] = job["address"]

                    if bool(duo_is_overtime):
                        lock_tech[t1] = True
                        lock_tech[t2] = True

                    duo_jobs = duo_jobs[duo_jobs["job_id"] != job["job_id"]].copy()

            # ---- 2) SOLO greedy per tech ----
            if not solo_jobs.empty:
                made_progress = True
                while made_progress:
                    made_progress = False
                    if solo_jobs.empty:
                        break

                    solo_jobs = solo_jobs.sort_values(["job_id"], kind="mergesort")

                    for t in tech_names:
                        if solo_jobs.empty:
                            break
                        if lock_tech.get(t, False):
                            continue
                        if jobs_count[t] >= int(max_jobs_per_day):
                            continue

                        best_idx = None
                        best_cost = None
                        best_tmin = None

                        sample = get_job_pool_for_tech(solo_jobs, t, int(solo_pool))

                        # Try normal jobs that fit
                        for idx, job in sample.iterrows():
                            jlat, jlon, jsec = ensure_job_ll_idx(sample, idx)
                            if not sector_compatible(_tech_sector.get(t, "UNK"), jsec):
                                continue

                            tmin = travel_min_cached(cur_loc[t], job["address"])
                            tback = travel_min_cached(job["address"], _home_map[t])
                            need = int(tmin) + int(job["job_minutes"]) + int(buffer_job) + int(tback)
                            if need <= 0:
                                continue

                            if used[t] + need <= available:
                                if best_cost is None or int(tmin) < best_cost:
                                    best_idx = idx
                                    best_cost = int(tmin)
                                    best_tmin = int(tmin)

                        if best_idx is not None:
                            job = sample.loc[best_idx]
                            jobs_count[t] += 1
                            start_m = used[t] + int(best_tmin)
                            end_m = start_m + int(job["job_minutes"]) + int(buffer_job)

                            planned_rows.append({
                                "date": day.isoformat(),
                                "technicien": t,
                                "sequence": jobs_count[t],
                                "job_id": job["job_id"],
                                "cust": job.get("cust", ""),
                                "duo": "",
                                "ot": "",
                                "debut": mm_to_hhmm(int(start_m)),
                                "fin": mm_to_hhmm(int(end_m)),
                                "adresse": job["address"],
                                "travel_min": int(best_tmin),
                                "job_min": int(job["job_minutes"]),
                                "buffer_min": int(buffer_job),
                                "techs_needed": int(job["techs_needed"]),
                                "description": job["description"],
                            })

                            used[t] = int(end_m)
                            cur_loc[t] = job["address"]
                            solo_jobs = solo_jobs[solo_jobs["job_id"] != job["job_id"]].copy()
                            made_progress = True
                            continue

                        # OT single-job day (ONLY if first job of the day)
                        if jobs_count[t] == 0:
                            best_ot_idx = None
                            best_ot_cost = None
                            best_ot_tmin = None
                            best_ot_job = None

                            for idx, job in sample.iterrows():
                                jlat, jlon, jsec = ensure_job_ll_idx(sample, idx)
                                if not sector_compatible(_tech_sector.get(t, "UNK"), jsec):
                                    continue
                                tmin = travel_min_cached(cur_loc[t], job["address"])
                                tback = travel_min_cached(job["address"], _home_map[t])
                                need = int(tmin) + int(job["job_minutes"]) + int(buffer_job) + int(tback)

                                if need <= OT_ACTIVE_CAP:
                                    if best_ot_cost is None or int(tmin) < best_ot_cost:
                                        best_ot_idx = idx
                                        best_ot_cost = int(tmin)
                                        best_ot_tmin = int(tmin)
                                        best_ot_job = job

                            if best_ot_idx is not None:
                                job = best_ot_job
                                jobs_count[t] += 1
                                start_m = used[t] + int(best_ot_tmin)
                                end_m = start_m + int(job["job_minutes"]) + int(buffer_job)

                                planned_rows.append({
                                    "date": day.isoformat(),
                                    "technicien": t,
                                    "sequence": jobs_count[t],
                                    "job_id": job["job_id"],
                                    "cust": job.get("cust", ""),
                                    "duo": "",
                                    "ot": "🟥 OT",
                                    "debut": mm_to_hhmm(int(start_m)),
                                    "fin": mm_to_hhmm(int(end_m)),
                                    "adresse": job["address"],
                                    "travel_min": int(best_ot_tmin),
                                    "job_min": int(job["job_minutes"]),
                                    "buffer_min": int(buffer_job),
                                    "techs_needed": int(job["techs_needed"]),
                                    "description": job["description"],
                                })

                                used[t] = int(end_m)
                                cur_loc[t] = job["address"]
                                solo_jobs = solo_jobs[solo_jobs["job_id"] != job["job_id"]].copy()
                                lock_tech[t] = True
                                made_progress = True
                                continue

                        # Split long jobs (unchanged logic, stable sample)
                        best_long_idx = None
                        best_long_cost = None
                        best_long_job = None
                        best_long_is_overtime = False

                        for idx, job in sample.iterrows():
                            jm = int(job["job_minutes"])
                            if jm <= int(daily_onsite_cap):
                                continue
                            if t in carryover_by_tech:
                                continue

                            jlat, jlon, jsec = ensure_job_ll_idx(sample, idx)
                            if not sector_compatible(_tech_sector.get(t, "UNK"), jsec):
                                continue

                            is_overtime_candidate = False
                            if (jobs_count[t] == 0) and ((jm - int(daily_onsite_cap)) < 180):
                                is_overtime_candidate = True

                            addr = job["address"]
                            tmin = travel_min_cached(cur_loc[t], addr)
                            tback = travel_min_cached(addr, _home_map[t])

                            max_onsite_today = int(available) - int(used[t]) - int(tmin) - int(buffer_job) - int(tback)
                            if max_onsite_today <= 0:
                                continue
                            if jobs_count[t] > 0 and int(max_onsite_today) < int(MIN_ONSITE_CHUNK_MIN):
                                continue

                            onsite_today_candidate = _choose_onsite_no_crumbs(jm, max_onsite_today, MIN_ONSITE_CHUNK_MIN)
                            if onsite_today_candidate <= 0:
                                continue
                            if is_overtime_candidate and jm > int(max_onsite_today):
                                continue

                            if best_long_cost is None or int(tmin) < best_long_cost:
                                best_long_idx = idx
                                best_long_cost = int(tmin)
                                best_long_job = job
                                best_long_is_overtime = bool(is_overtime_candidate)

                        if best_long_idx is None:
                            continue

                        job = best_long_job
                        base_job_id = str(job["job_id"])
                        jm_total = int(job["job_minutes"])

                        if bool(best_long_is_overtime):
                            tmin = travel_min_cached(cur_loc[t], job["address"])
                            start_m = int(used[t]) + int(tmin)
                            end_m = start_m + int(jm_total) + int(buffer_job)

                            jobs_count[t] += 1
                            planned_rows.append({
                                "date": day.isoformat(),
                                "technicien": t,
                                "sequence": jobs_count[t],
                                "job_id": job["job_id"],
                                "cust": job.get("cust", ""),
                                "duo": "",
                                "ot": "",
                                "debut": mm_to_hhmm(int(start_m)),
                                "fin": mm_to_hhmm(int(end_m)),
                                "adresse": job["address"],
                                "travel_min": int(tmin),
                                "job_min": int(jm_total),
                                "buffer_min": int(buffer_job),
                                "techs_needed": int(job.get("techs_needed", 1)),
                                "description": job["description"],
                            })

                            used[t] = int(end_m)
                            cur_loc[t] = job["address"]
                            solo_jobs = solo_jobs[solo_jobs["job_id"] != job["job_id"]].copy()
                            lock_tech[t] = True
                            made_progress = True
                            continue

                        total_parts_guess = compute_total_parts(int(job["job_minutes"]), int(daily_onsite_cap))
                        carryover_by_tech[t] = {
                            "base_job_id": base_job_id,
                            "cust": job.get("cust", ""),
                            "address": job["address"],
                            "description": job["description"],
                            "techs_needed": int(job.get("techs_needed", 1)),
                            "total_parts": int(total_parts_guess),
                            "part_idx_next": 1,
                            "remaining_job_min": int(job["job_minutes"]),
                        }
                        solo_jobs = solo_jobs[solo_jobs["job_id"] != job["job_id"]].copy()

                        _book_split_part_for_tech(
                            day=day,
                            t=t,
                            used=used,
                            cur_loc=cur_loc,
                            jobs_count=jobs_count,
                            lock_tech=lock_tech,
                            split_state=carryover_by_tech[t],
                        )
                        if t in carryover_by_tech and int(carryover_by_tech[t]["remaining_job_min"]) <= 0:
                            del carryover_by_tech[t]

                        made_progress = True

            # RETURN_HOME (unchanged)
            for t in tech_names:
                if jobs_count[t] > 0:
                    tback = travel_min_cached(cur_loc[t], _home_map[t])
                    planned_rows.append({
                        "date": day.isoformat(),
                        "technicien": t,
                        "sequence": jobs_count[t] + 1,
                        "job_id": "RETURN_HOME",
                        "cust": "",
                        "duo": "",
                        "ot": "",
                        "debut": mm_to_hhmm(int(used[t])),
                        "fin": mm_to_hhmm(int(used[t]) + int(tback)),
                        "adresse": _home_map[t],
                        "travel_min": int(tback),
                        "job_min": 0,
                        "buffer_min": 0,
                        "techs_needed": 1,
                        "description": "🏠 Retour domicile (estimé)",
                    })
                    used[t] = int(used[t]) + int(tback)
                    cur_loc[t] = _home_map[t]

            if progress is not None:
                progress.progress(int(((di + 1) / total_steps) * 100))
            if progress_text is not None:
                progress_text.write(f"Planification… {di+1}/{len(month_days)} jour(s) traités")

        remaining_out = pd.concat([duo_jobs, solo_jobs, hard_jobs], ignore_index=True)
        success = remaining_out.empty and (len(carryover_by_tech) == 0)
        return {"success": bool(success), "rows": planned_rows, "remaining": remaining_out}

    # ===============================================================
    # ✅ (A) Repair pass (post-planning) — SAFETY
    # ===============================================================
    def _is_return_home(job_id: str) -> bool:
        return str(job_id).strip().upper() == "RETURN_HOME"

    def _is_split_part(job_id: str) -> bool:
        return "(PART" in str(job_id).upper()

    def _is_duo_row(row: dict) -> bool:
        return str(row.get("duo", "")).strip() != ""

    def _is_ot_row(row: dict) -> bool:
        return str(row.get("ot", "")).strip() != ""

    def rebuild_day_greedy(
        day: str,
        tech: str,
        jobs_list: List[Dict[str, Any]],
        day_available_min: int,
        buffer_job: int,
        max_jobs_per_day: int,
    ) -> Optional[List[Dict[str, Any]]]:
        home_addr = home_map[tech]
        cur = home_addr
        used = 0
        seq = 0
        remaining = list(jobs_list)
        out_rows: List[Dict[str, Any]] = []

        if len(remaining) > int(max_jobs_per_day):
            return None

        while remaining:
            best_i = None
            best_tmin = None
            for i, jb in enumerate(remaining):
                tmin = travel_min_cached(cur, jb["adresse"])
                if best_tmin is None or int(tmin) < int(best_tmin):
                    best_tmin = int(tmin)
                    best_i = i

            jb = remaining.pop(best_i)
            tmin = int(best_tmin)
            tback = int(travel_min_cached(jb["adresse"], home_addr))
            need = tmin + int(jb["job_min"]) + int(buffer_job) + tback

            if used + need > int(day_available_min):
                return None

            seq += 1
            start_m = used + tmin
            end_m = start_m + int(jb["job_min"]) + int(buffer_job)

            out_rows.append({
                "date": day,
                "technicien": tech,
                "sequence": seq,
                "job_id": jb["job_id"],
                "cust": jb.get("cust", ""),
                "duo": "",
                "ot": jb.get("ot", ""),
                "debut": mm_to_hhmm(int(start_m)),
                "fin": mm_to_hhmm(int(end_m)),
                "adresse": jb["adresse"],
                "travel_min": int(tmin),
                "job_min": int(jb["job_min"]),
                "buffer_min": int(buffer_job),
                "techs_needed": int(jb.get("techs_needed", 1)),
                "description": jb.get("description", ""),
            })

            used = int(end_m)
            cur = jb["adresse"]

            if seq >= int(max_jobs_per_day) and remaining:
                return None

        if seq > 0:
            tback = int(travel_min_cached(cur, home_addr))
            out_rows.append({
                "date": day,
                "technicien": tech,
                "sequence": seq + 1,
                "job_id": "RETURN_HOME",
                "cust": "",
                "duo": "",
                "ot": "",
                "debut": mm_to_hhmm(int(used)),
                "fin": mm_to_hhmm(int(used) + int(tback)),
                "adresse": home_addr,
                "travel_min": int(tback),
                "job_min": 0,
                "buffer_min": 0,
                "techs_needed": 1,
                "description": "🏠 Retour domicile (estimé)",
            })
        return out_rows

    def repair_month_plan(
        planned_rows: List[Dict[str, Any]],
        tech_names: List[str],
        day_available_min: int,
        buffer_job: int,
        max_jobs_per_day: int,
        threshold_travel_min: int = 50,
        candidate_techs_top_n: int = 4,
        max_moves: int = 25,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not planned_rows:
            return planned_rows, {"moves": 0, "attempts": 0, "improved": 0}

        locked: List[Dict[str, Any]] = []
        movable: List[Dict[str, Any]] = []

        # ✅ keep originals for fallback (by day/tech)
        original_rows_by_day_tech: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

        for r in planned_rows:
            day_k = str(r.get("date", "")).strip()
            tech_k = str(r.get("technicien", "")).strip()
            if _is_return_home(r.get("job_id", "")):
                locked.append(r)  # removed later, rebuilt per day
            elif _is_duo_row(r) or _is_split_part(r.get("job_id", "")) or _is_ot_row(r):
                locked.append(r)
            else:
                movable.append(r)
                original_rows_by_day_tech.setdefault((day_k, tech_k), []).append(r)

        by_day_tech: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for r in movable:
            k = (str(r.get("date", "")).strip(), str(r.get("technicien", "")).strip())
            by_day_tech.setdefault(k, []).append({
                "job_id": r["job_id"],
                "cust": r.get("cust", ""),
                "ot": r.get("ot", ""),
                "adresse": r["adresse"],
                "job_min": int(r.get("job_min", 0)),
                "techs_needed": int(r.get("techs_needed", 1)),
                "description": r.get("description", ""),
                "travel_min_orig": int(r.get("travel_min", 0)),
            })

        candidates: List[Tuple[int, str, str, Dict[str, Any]]] = []
        for (day, tech), lst in by_day_tech.items():
            for jb in lst:
                candidates.append((int(jb["travel_min_orig"]), day, tech, jb))
        candidates.sort(key=lambda x: x[0], reverse=True)

        stats = {"moves": 0, "attempts": 0, "improved": 0}
        tech_list = list(tech_names)

        for (tmin_orig, day, src_tech, jb) in candidates:
            if stats["moves"] >= int(max_moves):
                break
            if int(tmin_orig) <= int(threshold_travel_min):
                break

            stats["attempts"] += 1

            job_row = pd.Series({
                "address": jb["adresse"],
                "job_id": jb["job_id"],
                "job_minutes": int(jb["job_min"]),
            })

            near_techs = rank_techs_for_job(tech_list, job_row, int(candidate_techs_top_n))
            near_techs = [t for t in near_techs if t != src_tech]
            if not near_techs:
                continue

            best_move = None

            for dst_tech in near_techs:
                src_key = (day, src_tech)
                dst_key = (day, dst_tech)

                src_list = list(by_day_tech.get(src_key, []))
                dst_list = list(by_day_tech.get(dst_key, []))

                src_list2 = [x for x in src_list if str(x["job_id"]) != str(jb["job_id"])]
                dst_list2 = dst_list + [jb]

                if len(dst_list2) > int(max_jobs_per_day):
                    continue

                rebuilt_src = rebuild_day_greedy(day, src_tech, src_list2, day_available_min, buffer_job, max_jobs_per_day)
                rebuilt_dst = rebuild_day_greedy(day, dst_tech, dst_list2, day_available_min, buffer_job, max_jobs_per_day)
                if rebuilt_src is None or rebuilt_dst is None:
                    continue

                new_tmin = None
                for rr in rebuilt_dst:
                    if str(rr.get("job_id")) == str(jb["job_id"]):
                        new_tmin = int(rr.get("travel_min", 9999))
                        break
                if new_tmin is None:
                    continue

                delta = int(tmin_orig) - int(new_tmin)
                if delta <= 0:
                    continue

                if best_move is None or delta > best_move[0]:
                    best_move = (delta, dst_tech, rebuilt_src, rebuilt_dst, src_list2, dst_list2)

            if best_move is None:
                continue

            delta, dst_tech, rebuilt_src, rebuilt_dst, src_list2, dst_list2 = best_move
            by_day_tech[(day, src_tech)] = src_list2
            by_day_tech[(day, dst_tech)] = dst_list2
            stats["moves"] += 1
            stats["improved"] += 1

        final_rows: List[Dict[str, Any]] = []

        # Keep locked, but remove RETURN_HOME (re-created on rebuilt days)
        for r in locked:
            if _is_return_home(r.get("job_id", "")):
                continue
            final_rows.append(r)

        # Rebuild or fallback per (day,tech)
        for (day, tech), lst in by_day_tech.items():
            rebuilt = rebuild_day_greedy(day, tech, lst, day_available_min, buffer_job, max_jobs_per_day)
            if rebuilt is not None:
                final_rows.extend(rebuilt)
            else:
                # Fallback to original rows (so we NEVER lose jobs)
                orig = original_rows_by_day_tech.get((day, tech), [])
                if orig:
                    final_rows.extend(orig)
                # Re-add original RETURN_HOME for that day/tech if it existed
                for r in planned_rows:
                    if str(r.get("date", "")).strip() == day and str(r.get("technicien", "")).strip() == tech and _is_return_home(r.get("job_id", "")):
                        final_rows.append(r)
                        break

        return final_rows, stats

    # ────────────────────────────────────────────────────────────────
    # ✅ FIX AJOUTÉ: Integrity Check (helper) — jobs manquants
    # ────────────────────────────────────────────────────────────────
    def _normalize_base_job_id(jid: str) -> str:
        return re.sub(r"\s*\(PART\s+\d+/\d+\)\s*$", "", str(jid)).strip()

    def render_integrity_check(jobs_df: pd.DataFrame):
        all_initial_jobs = set(jobs_df["job_id"].astype(str).tolist())

        planned_jobs = set()
        for r in st.session_state.get("planning_month_rows", []):
            jid = r.get("job_id", "")
            if jid and str(jid).upper() != "RETURN_HOME":
                planned_jobs.add(_normalize_base_job_id(jid))

        remaining_jobs = set()
        for r in st.session_state.get("planning_month_remaining_rows", []):
            jid = r.get("job_id", "")
            if jid:
                remaining_jobs.add(str(jid))

        covered_jobs = planned_jobs.union(remaining_jobs)
        missing_jobs = sorted(list(all_initial_jobs - covered_jobs))

        st.divider()
        st.subheader("🔎 Vérification d'intégrité des jobs")

        st.write(f"Jobs initiaux : {len(all_initial_jobs)}")
        st.write(f"Jobs planifiés : {len(planned_jobs)}")
        st.write(f"Jobs restants : {len(remaining_jobs)}")
        st.write(f"Jobs couverts total : {len(covered_jobs)}")

        if missing_jobs:
            st.error(f"⚠️ Jobs manquants détectés : {len(missing_jobs)}")
            st.dataframe(
                pd.DataFrame({"Jobs à ajouter manuellement": missing_jobs}),
                use_container_width=True
            )
        else:
            st.success("✅ Aucun job perdu. Tous les jobs sont planifiés ou listés comme restants.")

    # ────────────────────────────────────────────────────────────────
    # MODE SELECTOR (unchanged)
    # ────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🧭 Mode de planification")
    mode = st.radio(
        "Choisir un mode",
        [
            "1 journée / 1 technicien (mode actuel)",
            "Mois complet — techniciens choisis par l'utilisateur",
            "Mois complet — techniciens choisis automatiquement",
        ],
        horizontal=True,
        key="p2_mode",
    )

    tech_names_all = sorted(tech_df["tech_name"].astype(str).tolist())
# ===============================================================
# PAGE 2 — SECTION 2/2
# (COLLER IMMÉDIATEMENT APRÈS LA SECTION 1/2)
# ===============================================================

    # ────────────────────────────────────────────────────────────────
    # MODE A — DAY / 1 TECH (logique identique)
    # ────────────────────────────────────────────────────────────────
    if mode == "1 journée / 1 technicien (mode actuel)":
        st.subheader("🧰 Planning 1 journée / 1 technicien")
        chosen_tech = st.selectbox("Choisir le technicien", tech_names_all, index=0, key="p2_chosen_tech")
        home_addr = tech_df.loc[tech_df["tech_name"] == chosen_tech, "home_address"].iloc[0]
        st.caption(f"🏠 Adresse domicile: {home_addr}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            day_hours = st.number_input("Heures/jour", 4.0, 14.0, 8.0, 0.5, key="p2_day_hours")
        with c2:
            lunch_min = st.number_input("Pause (min)", 0, 120, 30, 5, key="p2_lunch")
        with c3:
            buffer_job = st.number_input("Buffer/job (min)", 0, 60, 10, 5, key="p2_buffer")
        with c4:
            max_jobs = st.number_input("Max jobs/jour", 1, 25, 10, 1, key="p2_max_jobs")

        only_one = st.checkbox("Filtrer: seulement jobs à 1 technicien", value=False, key="p2_only_one")
        service_choice = st.selectbox(
            "Type de jobs",
            ["Inclure full service (tous les jobs)", "Generator inspection seulement", "Exclure generator inspection"],
            index=0,
            key="p2_service_choice",
        )

        run = st.button("🚀 Générer la journée", type="primary", key="p2_run")

        if run:
            st.session_state["p2_api_calls"] = 0
            st.session_state["p2_cache_hits"] = 0

            available = int(round(day_hours * 60)) - int(lunch_min)
            daily_onsite_cap = int(available)

            OT_ACTIVE_CAP = int(round(14 * 60)) - int(lunch_min)
            if OT_ACTIVE_CAP < available:
                OT_ACTIVE_CAP = available

            MIN_ONSITE_CHUNK_MIN = 180

            def _choose_onsite_no_crumbs(remaining_min: int, max_onsite_today: int, min_chunk: int) -> int:
                remaining_min = int(remaining_min)
                max_onsite_today = int(max_onsite_today)
                min_chunk = int(min_chunk)
                if max_onsite_today <= 0:
                    return 0

                onsite_today = min(remaining_min, max_onsite_today)
                if onsite_today >= remaining_min:
                    return onsite_today

                rem_after = remaining_min - onsite_today
                if onsite_today < min_chunk:
                    return 0
                if rem_after < min_chunk:
                    if remaining_min <= max_onsite_today:
                        return remaining_min
                    onsite_today = remaining_min - min_chunk
                    onsite_today = min(onsite_today, max_onsite_today)
                    if onsite_today < min_chunk:
                        return 0
                    rem_after = remaining_min - onsite_today
                    if rem_after > 0 and rem_after < min_chunk:
                        return 0
                    return onsite_today
                return onsite_today

            remaining = jobs.copy()
            remaining = filter_by_service_type(remaining, service_choice)
            if only_one:
                remaining = remaining[remaining["techs_needed"] <= 1].copy()

            remaining = remaining.sort_values(["job_id"], kind="mergesort")

            used = 0
            seq = 0
            cur_loc = home_addr
            day_rows = []
            carryover = None

            tsec = tech_sector_map.get(chosen_tech, "UNK")

            while True:
                if remaining.empty:
                    break
                if seq >= int(max_jobs):
                    break
                if carryover is not None and int(carryover.get("remaining_job_min", 0)) > 0:
                    break

                best_idx = None
                best_cost = None
                best_tmin = None

                sample = get_job_pool_for_tech(remaining, chosen_tech, int(solo_pool))

                for idx, job in sample.iterrows():
                    jlat, jlon, jsec = ensure_job_ll_idx(sample, idx)
                    if not sector_compatible(tsec, jsec):
                        continue

                    tmin = travel_min_cached(cur_loc, job["address"])
                    tback = travel_min_cached(job["address"], home_addr)
                    need = int(tmin) + int(job["job_minutes"]) + int(buffer_job) + int(tback)

                    if need <= 0:
                        continue

                    if used + need <= available:
                        if best_cost is None or int(tmin) < best_cost:
                            best_idx = idx
                            best_cost = int(tmin)
                            best_tmin = int(tmin)

                if best_idx is not None:
                    job = sample.loc[best_idx]
                    seq += 1
                    start_m = used + int(best_tmin)
                    end_m = start_m + int(job["job_minutes"]) + int(buffer_job)

                    day_rows.append({
                        "technicien": chosen_tech,
                        "sequence": seq,
                        "job_id": job["job_id"],
                        "cust": job.get("cust", ""),
                        "duo": "⚠️ DUO" if int(job["techs_needed"]) >= 2 else "",
                        "ot": "",
                        "debut": mm_to_hhmm(int(start_m)),
                        "fin": mm_to_hhmm(int(end_m)),
                        "adresse": job["address"],
                        "travel_min": int(best_tmin),
                        "job_min": int(job["job_minutes"]),
                        "buffer_min": int(buffer_job),
                        "techs_needed": int(job["techs_needed"]),
                        "description": job["description"],
                    })

                    used = int(end_m)
                    cur_loc = job["address"]
                    remaining = remaining[remaining["job_id"] != job["job_id"]].copy()
                    remaining = remaining.sort_values(["job_id"], kind="mergesort")
                    continue

                if seq == 0:
                    best_ot_idx = None
                    best_ot_cost = None
                    best_ot_tmin = None
                    best_ot_job = None

                    for idx, job in sample.iterrows():
                        jlat, jlon, jsec = ensure_job_ll_idx(sample, idx)
                        if not sector_compatible(tsec, jsec):
                            continue
                        tmin = travel_min_cached(cur_loc, job["address"])
                        tback = travel_min_cached(job["address"], home_addr)
                        need = int(tmin) + int(job["job_minutes"]) + int(buffer_job) + int(tback)

                        if need <= OT_ACTIVE_CAP:
                            if best_ot_cost is None or int(tmin) < best_ot_cost:
                                best_ot_idx = idx
                                best_ot_cost = int(tmin)
                                best_ot_tmin = int(tmin)
                                best_ot_job = job

                    if best_ot_idx is not None:
                        job = best_ot_job
                        seq += 1
                        start_m = used + int(best_ot_tmin)
                        end_m = start_m + int(job["job_minutes"]) + int(buffer_job)

                        day_rows.append({
                            "technicien": chosen_tech,
                            "sequence": seq,
                            "job_id": job["job_id"],
                            "cust": job.get("cust", ""),
                            "duo": "",
                            "ot": "🟥 OT",
                            "debut": mm_to_hhmm(int(start_m)),
                            "fin": mm_to_hhmm(int(end_m)),
                            "adresse": job["address"],
                            "travel_min": int(best_ot_tmin),
                            "job_min": int(job["job_minutes"]),
                            "buffer_min": int(buffer_job),
                            "techs_needed": int(job["techs_needed"]),
                            "description": job["description"],
                        })

                        used = int(end_m)
                        cur_loc = job["address"]
                        remaining = remaining[remaining["job_id"] != job["job_id"]].copy()
                    break

                best_long = None
                for idx, job in sample.iterrows():
                    jm = int(job["job_minutes"])
                    if jm <= int(daily_onsite_cap):
                        continue
                    jlat, jlon, jsec = ensure_job_ll_idx(sample, idx)
                    if not sector_compatible(tsec, jsec):
                        continue

                    tmin = travel_min_cached(cur_loc, job["address"])
                    tback = travel_min_cached(job["address"], home_addr)
                    max_onsite_today = int(available) - int(used) - int(tmin) - int(buffer_job) - int(tback)
                    if max_onsite_today <= 0:
                        continue

                    onsite_today_candidate = _choose_onsite_no_crumbs(jm, max_onsite_today, MIN_ONSITE_CHUNK_MIN)
                    if onsite_today_candidate <= 0:
                        continue

                    if best_long is None or int(tmin) < int(best_long["tmin"]):
                        best_long = {"idx": idx, "job": job, "tmin": int(tmin), "tback": int(tback)}

                if best_long is None:
                    break

                job = best_long["job"]
                base_job_id = str(job["job_id"])
                total_parts = compute_total_parts(int(job["job_minutes"]), int(daily_onsite_cap))

                carryover = {
                    "base_job_id": base_job_id,
                    "cust": job.get("cust", ""),
                    "address": job["address"],
                    "description": job["description"],
                    "techs_needed": int(job.get("techs_needed", 1)),
                    "total_parts": int(total_parts),
                    "part_idx_next": 1,
                    "remaining_job_min": int(job["job_minutes"]),
                }

                remaining = remaining[remaining["job_id"] != job["job_id"]].copy()

                tmin = best_long["tmin"]
                tback = best_long["tback"]
                max_onsite_today = int(available) - int(used) - int(tmin) - int(buffer_job) - int(tback)
                onsite_today = _choose_onsite_no_crumbs(int(carryover["remaining_job_min"]), int(max_onsite_today), MIN_ONSITE_CHUNK_MIN)
                if onsite_today <= 0:
                    break

                seq += 1
                start_m = int(used) + int(tmin)
                end_m = start_m + int(onsite_today) + int(buffer_job)

                day_rows.append({
                    "technicien": chosen_tech,
                    "sequence": seq,
                    "job_id": f"{base_job_id} (PART 1/{total_parts})",
                    "cust": carryover.get("cust", ""),
                    "duo": "",
                    "ot": "",
                    "debut": mm_to_hhmm(int(start_m)),
                    "fin": mm_to_hhmm(int(end_m)),
                    "adresse": job["address"],
                    "travel_min": int(tmin),
                    "job_min": int(onsite_today),
                    "buffer_min": int(buffer_job),
                    "techs_needed": int(job.get("techs_needed", 1)),
                    "description": job["description"],
                })

                used = int(end_m)
                cur_loc = job["address"]
                carryover["remaining_job_min"] = int(carryover["remaining_job_min"]) - int(onsite_today)
                carryover["part_idx_next"] = 2
                break

            st.session_state["planning_day_rows"] = day_rows
            st.session_state["planning_remaining_count"] = len(remaining)

        day_rows_saved = st.session_state.get("planning_day_rows", [])
        if day_rows_saved:
            st.divider()
            st.subheader("📋 Horaire de la journée (persistant)")

            day_df = pd.DataFrame(day_rows_saved)
            day_df = day_df.sort_values(["technicien", "sequence", "debut"], ascending=True).reset_index(drop=True)

            preferred = ["technicien", "sequence", "job_id", "cust", "duo", "ot", "debut", "fin", "adresse",
                         "travel_min", "job_min", "buffer_min", "techs_needed", "description"]
            cols = [c for c in preferred if c in day_df.columns] + [c for c in day_df.columns if c not in preferred]
            day_df = day_df[cols]

            st.dataframe(style_duo(day_df), use_container_width=True)

            available_active = int(round(st.session_state.get("p2_day_hours", 8.0) * 60)) - int(st.session_state.get("p2_lunch", 30))
            total_travel = int(day_df["travel_min"].sum()) if "travel_min" in day_df.columns else 0
            total_job = int(day_df["job_min"].sum()) if "job_min" in day_df.columns else 0
            total_buffer = int(day_df["buffer_min"].sum()) if "buffer_min" in day_df.columns else 0
            total_active = total_travel + total_job + total_buffer

            st.subheader("📊 Résumé")
            st.write(f"**Total travel:** {total_travel} min")
            st.write(f"**Total job:** {total_job} min")
            st.write(f"**Total buffer:** {total_buffer} min")
            st.write(f"**Total actif:** {total_active} / {available_active} min")

            st.subheader("🧾 Coûts (estimation)")
            st.write(f"**Appels API (cette run):** {st.session_state.get('p2_api_calls', 0)}")
            st.write(f"**Hits cache (cette run):** {st.session_state.get('p2_cache_hits', 0)}")

            st.subheader("🧩 Jobs non planifiés")
            st.caption(f"Reste (approx): {st.session_state.get('planning_remaining_count', '—')} job(s)")

    # ────────────────────────────────────────────────────────────────
    # MODE B — MONTH, user chooses techs (REPAIR PASS INTEGRATED)
    # ────────────────────────────────────────────────────────────────
    elif mode == "Mois complet — techniciens choisis par l'utilisateur":
        st.subheader("🗓️ Mois complet — techniciens choisis par l'utilisateur")

        month_start, month_end = month_selector("p2m_fixed")
        chosen_techs = st.multiselect(
            "Choisir les techniciens",
            options=tech_names_all,
            default=st.session_state.get("p2_month_fixed_techs", []),
            key="p2_month_fixed_techs",
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            day_hours_m = st.number_input("Heures/jour", 4.0, 14.0, 8.0, 0.5, key="p2m_day_hours")
        with c2:
            lunch_min_m = st.number_input("Pause (min)", 0, 120, 30, 5, key="p2m_lunch")
        with c3:
            buffer_job_m = st.number_input("Buffer/job (min)", 0, 60, 10, 5, key="p2m_buffer")
        with c4:
            max_jobs_m = st.number_input("Max jobs/jour/tech", 1, 25, 10, 1, key="p2m_max_jobs")

        allow_duo = st.checkbox("Autoriser booking DUO (techs_needed = 2)", value=True, key="p2m_allow_duo")

        # Repair controls (Mode B)
        st.sidebar.subheader("🛠️ Repair (post-planification)")
        do_repair = st.sidebar.checkbox("Activer repair pass (réassigne les SOLO très loin)", value=True, key="p2_repair_on")
        repair_threshold = st.sidebar.number_input("Seuil travel (min) pour réparer", min_value=20, max_value=120, value=50, step=5, key="p2_repair_thr")
        repair_top_n = st.sidebar.slider("Nb techs candidats (lat/lon)", 2, 6, 4, 1, key="p2_repair_topn")
        repair_max_moves = st.sidebar.slider("Max déplacements (moves)", 0, 80, 25, 5, key="p2_repair_moves")

        run_month = st.button("🚀 Générer le mois (techs imposés)", type="primary", key="p2_run_month_fixed")

        if run_month:
            st.session_state["p2_api_calls"] = 0
            st.session_state["p2_cache_hits"] = 0

            if len(chosen_techs) == 0:
                st.error("Choisis au moins 1 technicien.")
            else:
                if allow_duo and (jobs["techs_needed"] == 2).any() and len(chosen_techs) < 2:
                    st.error("Il y a des jobs DUO (2 techs), mais tu as sélectionné moins de 2 techniciens.")
                    st.stop()

                days = business_days(month_start, month_end)
                progress = st.progress(0)
                progress_text = st.empty()

                result = schedule_month_with_duo(
                    jobs_in=jobs,
                    tech_names=chosen_techs,
                    month_days=days,
                    day_hours=day_hours_m,
                    lunch_min=lunch_min_m,
                    buffer_job=buffer_job_m,
                    max_jobs_per_day=max_jobs_m,
                    allow_duo=allow_duo,
                    progress=progress,
                    progress_text=progress_text,
                )

                # Repair pass post-planification (Mode B)
                if do_repair and result and result.get("rows"):
                    day_available_min = int(round(day_hours_m * 60)) - int(lunch_min_m)
                    repaired_rows, rep_stats = repair_month_plan(
                        planned_rows=result["rows"],
                        tech_names=chosen_techs,
                        day_available_min=day_available_min,
                        buffer_job=int(buffer_job_m),
                        max_jobs_per_day=int(max_jobs_m),
                        threshold_travel_min=int(repair_threshold),
                        candidate_techs_top_n=int(repair_top_n),
                        max_moves=int(repair_max_moves),
                    )
                    result["rows"] = repaired_rows
                    st.sidebar.caption(
                        f"Repair: moves={rep_stats['moves']} | attempts={rep_stats['attempts']} | improved={rep_stats['improved']}"
                    )

                st.session_state["planning_month_rows"] = result["rows"]
                st.session_state["planning_month_success"] = result["success"]
                st.session_state["planning_month_mode"] = "fixed"
                st.session_state["planning_month_techs_used"] = chosen_techs

                remaining_df = result["remaining"].copy()
                cols_show = ["job_id", "cust", "address", "description", "job_minutes", "techs_needed", "postal"]
                remaining_show = remaining_df[cols_show].copy() if all(c in remaining_df.columns for c in cols_show) else remaining_df.copy()
                st.session_state["planning_month_remaining_rows"] = remaining_show.to_dict("records")

                progress.progress(100)
                progress_text.write("Terminé ✅")

        month_rows_saved = st.session_state.get("planning_month_rows", [])
        if month_rows_saved and st.session_state.get("planning_month_mode") == "fixed":
            st.divider()
            techs_used = st.session_state.get("planning_month_techs_used", [])

            if st.session_state.get("planning_month_success"):
                st.success(f"Mois complété ✅ | Techs utilisés: {len(techs_used)}")
            else:
                st.error("Impossible de compléter le mois avec le nombre de techniciens choisi ❌")
                st.warning("Ajoute des techniciens ou ajuste les paramètres (heures/jour, max jobs, buffer).")

            month_df = pd.DataFrame(month_rows_saved)
            sort_cols = [c for c in ["date", "technicien", "sequence", "debut"] if c in month_df.columns]
            month_df = month_df.sort_values(sort_cols, ascending=True).reset_index(drop=True)

            preferred = ["date", "technicien", "sequence", "job_id", "cust", "duo", "ot", "debut", "fin", "adresse",
                         "travel_min", "job_min", "buffer_min", "techs_needed", "description"]
            cols = [c for c in preferred if c in month_df.columns] + [c for c in month_df.columns if c not in preferred]
            month_df = month_df[cols]

            st.subheader("📋 Horaire du mois (tableau complet)")
            st.dataframe(style_duo(month_df), use_container_width=True)

            st.subheader("👷 Vue par technicien")
            for tech in sorted(month_df["technicien"].dropna().unique()):
                st.markdown(f"### {tech}")
                sub = month_df[month_df["technicien"] == tech].sort_values(["date", "sequence", "debut"], ascending=True)
                st.dataframe(style_duo(sub), use_container_width=True)

            st.subheader("🧾 Coûts (estimation)")
            st.write(f"**Appels API (cette run):** {st.session_state.get('p2_api_calls', 0)}")
            st.write(f"**Hits cache (cette run):** {st.session_state.get('p2_cache_hits', 0)}")

            st.subheader("🧩 Jobs non planifiés")
            remaining_rows = st.session_state.get("planning_month_remaining_rows", [])
            if remaining_rows:
                unplanned_df = pd.DataFrame(remaining_rows)
                st.dataframe(style_duo(unplanned_df), use_container_width=True)
                if "techs_needed" in unplanned_df.columns:
                    duo_left = int((unplanned_df["techs_needed"].astype(int) == 2).sum())
                    if duo_left > 0:
                        st.warning(f"⚠️ Jobs DUO restants (techs_needed=2): {duo_left}")

            # ✅ FIX AJOUTÉ ICI: Integrity check (Mode B)
            render_integrity_check(jobs)

    # ────────────────────────────────────────────────────────────────
    # MODE C — MONTH, auto techs (REPAIR PASS INTEGRATED)
    # ────────────────────────────────────────────────────────────────
    else:
        st.subheader("⚙️ Mois complet — techniciens choisis automatiquement")

        month_start, month_end = month_selector("p2m_auto")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            day_hours_m = st.number_input("Heures/jour", 4.0, 14.0, 8.0, 0.5, key="p2a_day_hours")
        with c2:
            lunch_min_m = st.number_input("Pause (min)", 0, 120, 30, 5, key="p2a_lunch")
        with c3:
            buffer_job_m = st.number_input("Buffer/job (min)", 0, 60, 10, 5, key="p2a_buffer")
        with c4:
            max_jobs_m = st.number_input("Max jobs/jour/tech", 1, 25, 10, 1, key="p2a_max_jobs")

        allow_duo = st.checkbox("Autoriser booking DUO (techs_needed = 2)", value=True, key="p2a_allow_duo")

        # Repair controls (Mode C)
        st.sidebar.subheader("🛠️ Repair (post-planification) — auto")
        do_repair = st.sidebar.checkbox("Activer repair pass (auto)", value=True, key="p2_repair_on_auto")
        repair_threshold = st.sidebar.number_input("Seuil travel (min) pour réparer (auto)", min_value=20, max_value=120, value=50, step=5, key="p2_repair_thr_auto")
        repair_top_n = st.sidebar.slider("Nb techs candidats (lat/lon) (auto)", 2, 6, 4, 1, key="p2_repair_topn_auto")
        repair_max_moves = st.sidebar.slider("Max déplacements (moves) (auto)", 0, 80, 25, 5, key="p2_repair_moves_auto")

        run_month = st.button("🚀 Générer le mois (auto)", type="primary", key="p2_run_month_auto")

        if run_month:
            st.session_state["p2_api_calls"] = 0
            st.session_state["p2_cache_hits"] = 0

            days = business_days(month_start, month_end)
            outer_progress = st.progress(0)
            outer_text = st.empty()

            best = None
            for k in range(1, len(tech_names_all) + 1):
                chosen = tech_names_all[:k]
                if allow_duo and (jobs["techs_needed"] == 2).any() and len(chosen) < 2:
                    continue

                outer_text.write(f"Essai avec {k} technicien(s)…")
                inner_progress = st.progress(0)
                inner_text = st.empty()

                result = schedule_month_with_duo(
                    jobs_in=jobs,
                    tech_names=chosen,
                    month_days=days,
                    day_hours=day_hours_m,
                    lunch_min=lunch_min_m,
                    buffer_job=buffer_job_m,
                    max_jobs_per_day=max_jobs_m,
                    allow_duo=allow_duo,
                    progress=inner_progress,
                    progress_text=inner_text,
                )

                if do_repair and result and result.get("rows"):
                    day_available_min = int(round(day_hours_m * 60)) - int(lunch_min_m)
                    repaired_rows, rep_stats = repair_month_plan(
                        planned_rows=result["rows"],
                        tech_names=chosen,
                        day_available_min=day_available_min,
                        buffer_job=int(buffer_job_m),
                        max_jobs_per_day=int(max_jobs_m),
                        threshold_travel_min=int(repair_threshold),
                        candidate_techs_top_n=int(repair_top_n),
                        max_moves=int(repair_max_moves),
                    )
                    result["rows"] = repaired_rows
                    st.sidebar.caption(
                        f"Repair(auto): moves={rep_stats['moves']} | attempts={rep_stats['attempts']} | improved={rep_stats['improved']}"
                    )

                best = {
                    "rows": result["rows"],
                    "success": result["success"],
                    "remaining": result["remaining"],
                    "techs_used": chosen,
                }

                outer_progress.progress(int((k / max(1, len(tech_names_all))) * 100))
                if result["success"]:
                    break

            st.session_state["planning_month_rows"] = best["rows"] if best else []
            st.session_state["planning_month_success"] = best["success"] if best else False
            st.session_state["planning_month_mode"] = "auto"
            st.session_state["planning_month_techs_used"] = best["techs_used"] if best else []

            remaining_df = best["remaining"].copy() if best else pd.DataFrame()
            cols_show = ["job_id", "cust", "address", "description", "job_minutes", "techs_needed", "postal"]
            remaining_show = remaining_df[cols_show].copy() if (not remaining_df.empty and all(c in remaining_df.columns for c in cols_show)) else remaining_df.copy()
            st.session_state["planning_month_remaining_rows"] = remaining_show.to_dict("records") if not remaining_show.empty else []

            outer_text.write("Terminé ✅")

        month_rows_saved = st.session_state.get("planning_month_rows", [])
        if month_rows_saved and st.session_state.get("planning_month_mode") == "auto":
            st.divider()
            techs_used = st.session_state.get("planning_month_techs_used", [])

            if st.session_state.get("planning_month_success"):
                st.success(f"Mois complété ✅ | Techs utilisés: {len(techs_used)}")
            else:
                st.error("Même en mode auto, le mois n’a pas pu être complété ❌")
                st.caption("Souvent dû à: paramètres trop restrictifs, jobs 3+ techs, ou journées pleines.")
                st.write("**Techniciens utilisés:**", ", ".join(techs_used) if techs_used else "—")

            month_df = pd.DataFrame(month_rows_saved)
            sort_cols = [c for c in ["date", "technicien", "sequence", "debut"] if c in month_df.columns]
            month_df = month_df.sort_values(sort_cols, ascending=True).reset_index(drop=True)

            preferred = ["date", "technicien", "sequence", "job_id", "cust", "duo", "ot", "debut", "fin", "adresse",
                         "travel_min", "job_min", "buffer_min", "techs_needed", "description"]
            cols = [c for c in preferred if c in month_df.columns] + [c for c in month_df.columns if c not in preferred]
            month_df = month_df[cols]

            st.subheader("📋 Horaire du mois (tableau complet)")
            st.dataframe(style_duo(month_df), use_container_width=True)

            st.subheader("👷 Vue par technicien")
            for tech in sorted(month_df["technicien"].dropna().unique()):
                st.markdown(f"### {tech}")
                sub = month_df[month_df["technicien"] == tech].sort_values(["date", "sequence", "debut"], ascending=True)
                st.dataframe(style_duo(sub), use_container_width=True)

            st.subheader("🧾 Coûts (estimation)")
            st.write(f"**Appels API (cette run):** {st.session_state.get('p2_api_calls', 0)}")
            st.write(f"**Hits cache (cette run):** {st.session_state.get('p2_cache_hits', 0)}")

            st.subheader("🧩 Jobs non planifiés")
            remaining_rows = st.session_state.get("planning_month_remaining_rows", [])
            if remaining_rows:
                unplanned_df = pd.DataFrame(remaining_rows)
                st.dataframe(style_duo(unplanned_df), use_container_width=True)
                if "techs_needed" in unplanned_df.columns:
                    duo_left = int((unplanned_df["techs_needed"].astype(int) == 2).sum())
                    if duo_left > 0:
                        st.warning(f"⚠️ Jobs DUO restants (techs_needed=2): {duo_left}")

            # ✅ FIX AJOUTÉ ICI: Integrity check (Mode C)
            render_integrity_check(jobs)

# ────────────────────────────────────────────────────────────────
# Router
# ────────────────────────────────────────────────────────────────
if page == "🏠 Route Optimizer":
    render_page_1()
else:
    render_page_2()


