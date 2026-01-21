# pages/2_Planning.py
# Planning mensuel (sans dates fixes) — optimise par zones (Rive Nord / MTL-Laval / Rive Sud)
# - Techs viennent de st.session_state["tech_home"] (créé dans app.py)
# - Jobs: upload Excel avec onglet "Export"
# - Déplacements: Google Distance Matrix via googlemaps (même lib que ta page 1)

import os
import re
import math
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st
import googlemaps


st.set_page_config(page_title="Planning techniciens", layout="wide")
st.title("📅 Planning mensuel – Journées techniciens")

# ────────────────────────────────────────────────────────────────────────────────
# Secrets / Google
# ────────────────────────────────────────────────────────────────────────────────
def secret(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

GOOGLE_KEY = secret("GOOGLE_MAPS_API_KEY")
if not GOOGLE_KEY:
    st.error("Missing Google Maps key. Add it in Secrets as `GOOGLE_MAPS_API_KEY`.")
    st.stop()

gmaps_client = googlemaps.Client(key=GOOGLE_KEY)


# ────────────────────────────────────────────────────────────────────────────────
# Helpers: postal/zone + address
# ────────────────────────────────────────────────────────────────────────────────
def normalize_postal_code(postal: str) -> str:
    if postal is None or (isinstance(postal, float) and math.isnan(postal)):
        return ""
    s = str(postal).strip().upper().replace(" ", "")
    s = re.sub(r"[^A-Z0-9]", "", s)[:6]
    return s

def extract_postal_from_text(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"\b([A-Z]\d[A-Z])\s?(\d[A-Z]\d)\b", str(text).upper())
    return (m.group(1) + m.group(2)) if m else ""

def zone_from_postal(postal: str) -> str:
    postal = normalize_postal_code(postal)
    if not postal:
        return "OTHER"
    fsa = postal[:3]
    if fsa.startswith("H"):                 # Montréal + Laval (H7...)
        return "MTL_LAVAL"
    if fsa.startswith("J3") or fsa.startswith("J4"):
        return "RIVE_SUD"
    if fsa.startswith("J5") or fsa.startswith("J6") or fsa.startswith("J7"):
        return "RIVE_NORD"
    return "OTHER"

def travel_penalty_min(zone_a: str, zone_b: str, nord_sud: int, mtl_other: int, other: int) -> int:
    if zone_a == zone_b:
        return 0
    if {"RIVE_NORD", "RIVE_SUD"} == {zone_a, zone_b}:
        return nord_sud
    if "MTL_LAVAL" in (zone_a, zone_b):
        return mtl_other
    return other

def build_full_address(row: pd.Series) -> str:
    parts = []
    for col in ["ADDRESS 1", "ADDRESS 2", "ADDRESS 3", "SITE CITY", "SITE STATE", "SITE ZIP CODE"]:
        if col in row and pd.notna(row[col]) and str(row[col]).strip():
            parts.append(str(row[col]).strip())
    return ", ".join(parts)

def minutes_to_hhmm(m: int) -> str:
    h = int(m // 60)
    mm = int(m % 60)
    return f"{h:02d}:{mm:02d}"


# ────────────────────────────────────────────────────────────────────────────────
# Google Distance Matrix (cache)
# ────────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def travel_minutes(origin: str, destination: str, departure_time: Optional[datetime] = None) -> int:
    """
    Returns driving travel time in minutes between 2 addresses.
    Uses Google Distance Matrix via googlemaps.
    Cached 24h to reduce cost.
    """
    if not origin or not destination:
        return 9999
    try:
        resp = gmaps_client.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode="driving",
            departure_time=departure_time or "now",
        )
        if resp.get("status") != "OK":
            return 9999
        el = resp["rows"][0]["elements"][0]
        if el.get("status") != "OK":
            return 9999
        dur = el.get("duration_in_traffic") or el.get("duration") or {}
        sec = int(dur.get("value", 0))
        return int(round(sec / 60))
    except Exception:
        return 9999


# ────────────────────────────────────────────────────────────────────────────────
# Load jobs from Excel (sheet Export)
# ────────────────────────────────────────────────────────────────────────────────
def load_jobs_from_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Export", engine="openpyxl")

    onsite = pd.to_numeric(df.get("ONSITE SRT HRS"), errors="coerce")
    srt = pd.to_numeric(df.get("SRT HRS"), errors="coerce")
    duration_min = (onsite.fillna(srt) * 60).round()

    df["full_address"] = df.apply(build_full_address, axis=1)

    # postal & zone
    if "SITE ZIP CODE" in df.columns:
        df["postal_norm"] = df["SITE ZIP CODE"].apply(normalize_postal_code)
    else:
        df["postal_norm"] = df["full_address"].apply(extract_postal_from_text)

    df["zone"] = df["postal_norm"].apply(zone_from_postal)
    df["duration_min"] = duration_min

    jobs = pd.DataFrame({
        "job_id": df.get("ORDER #"),
        "fa_job_id": df.get("FA JOB #"),
        "customer_name": df.get("CUSTOMER NAME"),
        "description": df.get("PM SERVICE DESC.").fillna("").astype(str),
        "upcoming_services": df.get("UPCOMING SERVICES").fillna("").astype(str),
        "address": df["full_address"],
        "city": df.get("SITE CITY"),
        "postal": df.get("SITE ZIP CODE"),
        "zone": df["zone"],
        "duration_min": df["duration_min"],
        "techs_needed": pd.to_numeric(df.get("# OF TECHS NEEDED"), errors="coerce").fillna(1).astype(int),
    })

    jobs["description_full"] = (jobs["description"] + " | " + jobs["upcoming_services"]).str.strip(" |")

    # Keep usable
    jobs = jobs.dropna(subset=["job_id", "address", "duration_min"]).copy()
    jobs = jobs[jobs["duration_min"].astype(float) > 0].copy()
    jobs["duration_min"] = jobs["duration_min"].astype(int)
    jobs["job_id"] = jobs["job_id"].astype(str)

    # Optional: drop duplicates on job_id
    jobs = jobs.drop_duplicates(subset=["job_id"], keep="first").reset_index(drop=True)
    return jobs


# ────────────────────────────────────────────────────────────────────────────────
# Scheduling (zone-aware greedy)
# ────────────────────────────────────────────────────────────────────────────────
def build_schedule(
    jobs: pd.DataFrame,
    techs: pd.DataFrame,
    day_minutes: int,
    lunch_min: int,
    buffer_per_job_min: int,
    strict_zones: bool,
    pen_nord_sud: int,
    pen_mtl_other: int,
    pen_other: int,
    max_days_per_tech: int = 31,
):
    remaining = jobs.copy()
    remaining["needs_multi_tech"] = remaining["techs_needed"].apply(lambda x: int(x) > 1)

    visits = []
    summary = []

    for _, t in techs.iterrows():
        tech_name = str(t["tech_name"])
        home = str(t["home_address"])
        tech_zone = str(t.get("zone", "OTHER"))

        for day_idx in range(1, max_days_per_tech + 1):
            if remaining.empty:
                break

            available = max(0, day_minutes - lunch_min)
            used = 0
            seq = 0
            current_loc = home
            current_zone = tech_zone

            if strict_zones:
                pool = remaining[remaining["zone"] == tech_zone].copy()
                if pool.empty:
                    pool = remaining[remaining["zone"].isin(["MTL_LAVAL", "OTHER"])].copy()
                if pool.empty:
                    pool = remaining.copy()
            else:
                pool = remaining.copy()

            day_rows = []

            while used < available and not pool.empty:
                best_idx = None
                best_score = None
                best_travel = None

                sample = pool.head(40) if len(pool) > 40 else pool

                for idx, job in sample.iterrows():
                    tmin = travel_minutes(current_loc, job["address"])
                    pen = travel_penalty_min(
                        current_zone, job["zone"],
                        nord_sud=pen_nord_sud,
                        mtl_other=pen_mtl_other,
                        other=pen_other
                    )
                    score = tmin + pen

                    needed = int(job["duration_min"]) + buffer_per_job_min + int(tmin)
                    if used + needed <= available:
                        if best_score is None or score < best_score:
                            best_idx = idx
                            best_score = score
                            best_travel = int(tmin)

                if best_idx is None:
                    break

                job = pool.loc[best_idx]
                seq += 1

                # Timing (relative day)
                travel_m = int(best_travel)
                job_m = int(job["duration_min"]) + int(buffer_per_job_min)

                start_m = used + travel_m
                end_m = start_m + job_m

                day_rows.append({
                    "tech_name": tech_name,
                    "day_number": day_idx,
                    "sequence": seq,
                    "job_id": job["job_id"],
                    "customer_name": job["customer_name"],
                    "address": job["address"],
                    "zone": job["zone"],
                    "start_hhmm": minutes_to_hhmm(start_m),
                    "end_hhmm": minutes_to_hhmm(end_m),
                    "travel_min": travel_m,
                    "job_duration_min": int(job["duration_min"]),
                    "buffer_min": int(buffer_per_job_min),
                    "needs_multi_tech": bool(job["needs_multi_tech"]),
                    "techs_needed": int(job["techs_needed"]),
                    "description": job.get("description_full", ""),
                })

                used = end_m
                current_loc = job["address"]
                current_zone = job["zone"]

                # Remove from remaining/pool
                remaining = remaining[remaining["job_id"] != job["job_id"]].copy()
                pool = pool[pool["job_id"] != job["job_id"]].copy()

            if day_rows:
                visits.extend(day_rows)
                summary.append({
                    "tech_name": tech_name,
                    "day_number": day_idx,
                    "zone_focus": tech_zone,
                    "stops": len(day_rows),
                    "total_travel_min": sum(r["travel_min"] for r in day_rows),
                    "total_job_min": sum(r["job_duration_min"] for r in day_rows),
                    "total_buffer_min": sum(r["buffer_min"] for r in day_rows),
                    "total_day_min": sum(r["travel_min"] + r["job_duration_min"] + r["buffer_min"] for r in day_rows),
                })

    return pd.DataFrame(visits), pd.DataFrame(summary), remaining


# ────────────────────────────────────────────────────────────────────────────────
# 1) Techs from session_state (created in app.py)
# ────────────────────────────────────────────────────────────────────────────────
tech_df = st.session_state.get("tech_home")
if tech_df is None:
    st.warning("Je ne trouve pas `tech_home`. Va d’abord sur la page principale (app.py) pour charger les techniciens.")
    st.stop()

# Ensure required columns
if "tech_name" not in tech_df.columns or "home_address" not in tech_df.columns:
    st.error("`tech_home` doit contenir au minimum les colonnes: `tech_name`, `home_address`.")
    st.stop()

tech_df = tech_df.copy()

# Compute tech postal/zone (postal may already exist from app.py)
if "postal" not in tech_df.columns:
    tech_df["postal"] = tech_df["home_address"].apply(extract_postal_from_text)
tech_df["postal_norm"] = tech_df["postal"].apply(normalize_postal_code)
tech_df["zone"] = tech_df["postal_norm"].apply(zone_from_postal)

st.subheader("Techniciens (depuis la page 1)")
st.dataframe(tech_df[["tech_name", "home_address", "zone"]], use_container_width=True)

st.divider()

# ────────────────────────────────────────────────────────────────────────────────
# 2) Upload Jobs Excel (Option A)
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("Jobs (upload Excel – onglet `Export`)")
jobs_file = st.file_uploader("Upload ton fichier Excel (celui avec l’onglet Export)", type=["xlsx"])
if not jobs_file:
    st.info("Upload le fichier Excel pour continuer.")
    st.stop()

try:
    jobs_df = load_jobs_from_excel(jobs_file)
except Exception as e:
    st.error(f"Impossible de lire l’onglet `Export`: {e}")
    st.stop()

st.caption(f"Jobs détectés: {len(jobs_df)}")
st.dataframe(jobs_df.head(30), use_container_width=True)

st.divider()

# ────────────────────────────────────────────────────────────────────────────────
# 3) Parameters
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("Paramètres d’optimisation")

c1, c2, c3, c4 = st.columns(4)
with c1:
    day_hours = st.number_input("Heures / jour", min_value=4.0, max_value=12.0, value=8.0, step=0.5)
with c2:
    lunch_min = st.number_input("Pause (min)", min_value=0, max_value=120, value=30, step=5)
with c3:
    buffer_min = st.number_input("Buffer / job (min)", min_value=0, max_value=60, value=10, step=5)
with c4:
    strict_zones = st.toggle("Zones strictes (évite Nord↔Sud)", value=True)

p1, p2, p3 = st.columns(3)
with p1:
    pen_ns = st.number_input("Pénalité Nord↔Sud (min)", min_value=0, max_value=240, value=90, step=15)
with p2:
    pen_mtl = st.number_input("Pénalité MTL↔autre (min)", min_value=0, max_value=240, value=45, step=15)
with p3:
    pen_other = st.number_input("Pénalité autre↔autre (min)", min_value=0, max_value=240, value=30, step=15)

run = st.button("🚀 Générer le planning", type="primary")

if run:
    day_minutes = int(round(day_hours * 60))

    with st.spinner("Calcul des trajets + génération des journées…"):
        visits_df, summary_df, remaining_df = build_schedule(
            jobs=jobs_df,
            techs=tech_df[["tech_name", "home_address", "zone"]],
            day_minutes=day_minutes,
            lunch_min=int(lunch_min),
            buffer_per_job_min=int(buffer_min),
            strict_zones=bool(strict_zones),
            pen_nord_sud=int(pen_ns),
            pen_mtl_other=int(pen_mtl),
            pen_other=int(pen_other),
            max_days_per_tech=31,
        )

    if visits_df.empty:
        st.warning("Aucune visite n’a pu être planifiée avec les contraintes actuelles.")
    else:
        st.success("Planning généré ✅")

        colA, colB = st.columns([2, 1])

        with colA:
            st.subheader("Planning détaillé (par visite)")
            st.dataframe(
                visits_df.sort_values(["tech_name", "day_number", "sequence"]),
                use_container_width=True
            )

        with colB:
            st.subheader("Résumé par journée")
            st.dataframe(
                summary_df.sort_values(["tech_name", "day_number"]),
                use_container_width=True
            )

            if visits_df["needs_multi_tech"].any():
                st.warning("⚠️ Certains jobs demandent >1 technicien. V1 les affiche mais ne force pas encore le pairing automatique.")

        st.subheader("Jobs non planifiés (reste)")
        st.caption(f"Reste: {len(remaining_df)} job(s)")
        st.dataframe(remaining_df.head(50), use_container_width=True)

        # Export Excel
        import io
        out = io.BytesIO()
        filename = f"planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            visits_df.to_excel(writer, sheet_name="Visits", index=False)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            remaining_df.to_excel(writer, sheet_name="Unscheduled", index=False)
            jobs_df.to_excel(writer, sheet_name="Jobs_Input", index=False)
            tech_df.to_excel(writer, sheet_name="Tech_Input", index=False)

        st.download_button(
            "⬇️ Télécharger le planning (Excel)",
            data=out.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

st.caption("V1 = zones + greedy nearest. V2 possible: OR-Tools (VRP) + pairing multi-tech + contraintes skills/time windows.")

