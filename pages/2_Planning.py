import os
import re
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List

import pandas as pd
import streamlit as st
import googlemaps


st.set_page_config(page_title="Planning mensuel", layout="wide")
st.title("📅 Planning mensuel – Journées techniciens")

# ─────────────────────────────────────────────────────────────
# Google key
# ─────────────────────────────────────────────────────────────
def secret(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

GOOGLE_KEY = secret("GOOGLE_MAPS_API_KEY")
if not GOOGLE_KEY:
    st.error("Missing Google Maps key (`GOOGLE_MAPS_API_KEY`) in Streamlit Secrets.")
    st.stop()

gmaps = googlemaps.Client(key=GOOGLE_KEY)

# ─────────────────────────────────────────────────────────────
# Techs from session_state
# ─────────────────────────────────────────────────────────────
tech_df = st.session_state.get("tech_home")
if tech_df is None or len(tech_df) == 0:
    st.warning("⚠️ Je ne trouve pas `tech_home`. Va d’abord sur la page principale (Route Optimizer).")
    st.stop()

# Expected columns: tech_name, home_address
if "tech_name" not in tech_df.columns or "home_address" not in tech_df.columns:
    st.error("`tech_home` doit contenir `tech_name` et `home_address`.")
    st.stop()

st.subheader("👷 Techniciens (depuis la page 1)")
st.dataframe(tech_df[["tech_name", "home_address"]], use_container_width=True)

st.divider()

# ─────────────────────────────────────────────────────────────
# Upload Jobs Excel
# ─────────────────────────────────────────────────────────────
st.subheader("📤 Jobs – Upload Excel (onglet Export)")
file = st.file_uploader("Upload ton fichier Excel jobs", type=["xlsx"])
if not file:
    st.info("Upload le fichier Excel pour continuer.")
    st.stop()

# Read Excel (try Export first, fallback first sheet)
try:
    jobs_raw = pd.read_excel(file, sheet_name="Export", engine="openpyxl")
except Exception:
    jobs_raw = pd.read_excel(file, sheet_name=0, engine="openpyxl")

st.caption(f"Jobs détectés: {len(jobs_raw)}")
st.dataframe(jobs_raw.head(20), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Column mapping (robust)
# ─────────────────────────────────────────────────────────────
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
    st.error("Je ne trouve pas la colonne Job/Order (#). Assure-toi qu’elle existe dans ton export.")
    st.stop()

def build_address(row: pd.Series) -> str:
    parts = []
    for c in [COL_ADDR1, COL_ADDR2, COL_ADDR3, COL_CITY, COL_PROV, COL_POST]:
        if c and pd.notna(row.get(c)) and str(row.get(c)).strip():
            parts.append(str(row.get(c)).strip())
    return ", ".join(parts)

jobs = pd.DataFrame()
jobs["job_id"] = jobs_raw[COL_ORDER].astype(str)
jobs["address"] = jobs_raw.apply(build_address, axis=1)

desc = ""
if COL_DESC: desc = jobs_raw[COL_DESC].fillna("").astype(str)
up   = ""
if COL_UP:   up   = jobs_raw[COL_UP].fillna("").astype(str)
jobs["description"] = (desc + " | " + up).str.strip(" |")

# duration minutes
ons = pd.to_numeric(jobs_raw[COL_ONS], errors="coerce") if COL_ONS else None
srt = pd.to_numeric(jobs_raw[COL_SRT], errors="coerce") if COL_SRT else None
hours = None
if ons is not None:
    hours = ons
elif srt is not None:
    hours = srt
else:
    st.error("Je ne trouve pas `ONSITE SRT HRS` ni `SRT HRS` pour calculer la durée.")
    st.stop()

jobs["job_minutes"] = (hours.fillna(0) * 60).round().astype(int)

techs_needed = pd.to_numeric(jobs_raw[COL_TECHN], errors="coerce") if COL_TECHN else None
jobs["techs_needed"] = techs_needed.fillna(1).astype(int) if techs_needed is not None else 1

# clean
jobs = jobs[(jobs["address"].astype(str).str.len() > 8) & (jobs["job_minutes"] > 0)].copy()
jobs = jobs.drop_duplicates(subset=["job_id"]).reset_index(drop=True)

st.divider()
st.subheader("🧾 Jobs nettoyés")
st.dataframe(jobs.head(30), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Zone heuristic (Nord / MTL / Sud)
# ─────────────────────────────────────────────────────────────
def zone_from_address(addr: str) -> str:
    a = (addr or "").lower()
    # very rough keywords (adjust anytime)
    rive_nord = ["laval", "terrebonne", "blainville", "mirabel", "boisbriand", "st-jérôme", "saint-jérôme"]
    rive_sud  = ["longueuil", "brossard", "candiac", "delson", "beloeil", "st-hubert", "saint-hubert", "chambly", "st-jean", "saint-jean"]
    if any(k in a for k in rive_nord): return "RIVE_NORD"
    if any(k in a for k in rive_sud):  return "RIVE_SUD"
    return "MTL_LAVAL"

jobs["zone"] = jobs["address"].apply(zone_from_address)
tech_df = tech_df.copy()
tech_df["zone"] = tech_df["home_address"].apply(zone_from_address)

# ─────────────────────────────────────────────────────────────
# Distance Matrix (cached)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60*60*24, show_spinner=False)
def travel_min(origin: str, dest: str) -> int:
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

def penalty(zone_a: str, zone_b: str, p_ns: int, p_mtl: int) -> int:
    if zone_a == zone_b:
        return 0
    if {"RIVE_NORD","RIVE_SUD"} == {zone_a, zone_b}:
        return p_ns
    # Anything involving MTL gets medium penalty
    return p_mtl

# ─────────────────────────────────────────────────────────────
# Parameters
# ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("⚙️ Paramètres")

c1, c2, c3, c4 = st.columns(4)
with c1:
    day_hours = st.number_input("Heures/jour", 6.0, 12.0, 8.0, 0.5)
with c2:
    lunch_min = st.number_input("Pause (min)", 0, 120, 30, 5)
with c3:
    buffer_job = st.number_input("Buffer/job (min)", 0, 60, 10, 5)
with c4:
    max_days = st.number_input("Max jours/tech", 1, 31, 22, 1)

p1, p2 = st.columns(2)
with p1:
    p_ns = st.number_input("Pénalité Nord↔Sud (min)", 0, 240, 90, 15)
with p2:
    p_mtl = st.number_input("Pénalité changement de zone (min)", 0, 240, 45, 15)

run = st.button("🚀 Générer le planning", type="primary")

# ─────────────────────────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────────────────────────
def mm_to_hhmm(m: int) -> str:
    h = m // 60
    mm = m % 60
    return f"{h:02d}:{mm:02d}"

if run:
    available = int(round(day_hours * 60)) - int(lunch_min)
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

                # prioritize same zone first
                pool = remaining[remaining["zone"] == tech_zone].copy()
                if pool.empty:
                    pool = remaining.copy()

                while True:
                    best_idx = None
                    best_cost = None
                    best_t = None

                    # limit candidates for cost (speed)
                    sample = pool.head(35) if len(pool) > 35 else pool

                    for idx, job in sample.iterrows():
                        tmin = travel_min(cur_loc, job["address"])
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

                    start_m = used + best_t
                    end_m = start_m + int(job["job_minutes"]) + int(buffer_job)

                    day_rows.append({
                        "technicien": tech_name,
                        "jour": day,
                        "sequence": seq,
                        "job_id": job["job_id"],
                        "zone": job["zone"],
                        "adresse": job["address"],
                        "debut": mm_to_hhmm(start_m),
                        "fin": mm_to_hhmm(end_m),
                        "travel_min": best_t,
                        "job_min": int(job["job_minutes"]),
                        "buffer_min": int(buffer_job),
                        "description": job["description"],
                        "techs_needed": int(job["techs_needed"]),
                    })

                    used = end_m
                    cur_loc = job["address"]
                    cur_zone = job["zone"]

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
        st.stop()

    st.dataframe(visits_df.sort_values(["technicien","jour","sequence"]), use_container_width=True)

    st.subheader("📊 Résumé par journée")
    st.dataframe(summary_df.sort_values(["technicien","jour"]), use_container_width=True)

    st.subheader("🧩 Jobs non planifiés")
    st.caption(f"Reste: {len(remaining)} job(s)")
    st.dataframe(remaining.head(100), use_container_width=True)

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
