import streamlit as st
import pandas as pd
import googlemaps
from datetime import timedelta
import re

st.set_page_config(
    page_title="Planning mensuel des techniciens",
    layout="wide"
)

st.title("📅 Planning mensuel – Techniciens")

# ─────────────────────────────────────────────────────────────
# 1. Vérifier que les techniciens existent (page 1 visitée)
# ─────────────────────────────────────────────────────────────
tech_df = st.session_state.get("tech_home")

if tech_df is None or tech_df.empty:
    st.warning("⚠️ Aucun technicien trouvé. Va d’abord sur la page principale.")
    st.stop()

st.subheader("👷 Techniciens disponibles")
st.dataframe(tech_df, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# 2. Upload du fichier Jobs (Option A)
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📤 Import des jobs (Excel)")

uploaded_file = st.file_uploader(
    "Uploader le fichier Excel (onglet Export)",
    type=["xlsx"]
)

if not uploaded_file:
    st.info("📎 En attente du fichier Excel des jobs.")
    st.stop()

jobs_df = pd.read_excel(uploaded_file)

st.success(f"✅ {len(jobs_df)} jobs importés")
st.dataframe(jobs_df.head(), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# 3. Colonnes requises (adapter si besoin)
# ─────────────────────────────────────────────────────────────
REQUIRED_COLS = {
    "Job ID": "job_id",
    "Adresse client": "address",
    "Durée job (h)": "job_hours"
}

jobs_df = jobs_df.rename(columns=REQUIRED_COLS)

missing = set(REQUIRED_COLS.values()) - set(jobs_df.columns)
if missing:
    st.error(f"Colonnes manquantes dans le fichier : {missing}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# 4. Google Maps
# ─────────────────────────────────────────────────────────────
GOOGLE_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_KEY)

def get_zone(address: str) -> str:
    """Classification simple par zone géographique"""
    addr = address.lower()
    if any(x in addr for x in ["laval", "terrebonne", "blainville", "mirabel", "boisbriand"]):
        return "Rive Nord"
    if any(x in addr for x in ["longueuil", "brossard", "candiac", "beloeil", "chambly"]):
        return "Rive Sud"
    return "Montréal"

jobs_df["zone"] = jobs_df["address"].apply(get_zone)

# ─────────────────────────────────────────────────────────────
# 5. Paramètres de journée
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⏱️ Paramètres de planification")

WORKDAY_HOURS = st.number_input(
    "Heures max par jour",
    min_value=6,
    max_value=12,
    value=8
)

AVG_TRAVEL_HOURS = st.number_input(
    "Temps moyen de déplacement par job (h)",
    min_value=0.25,
    max_value=2.0,
    value=0.75,
    step=0.25
)

# ─────────────────────────────────────────────────────────────
# 6. Construction du planning
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🧠 Génération du planning")

if st.button("🚀 Générer le planning"):

    planning_rows = []

    tech_list = tech_df["tech_name"].tolist()
    zones = jobs_df["zone"].unique()

    job_queue = jobs_df.copy()

    for tech in tech_list:
        day = 1

        for zone in zones:
            zone_jobs = job_queue[job_queue["zone"] == zone]

            while not zone_jobs.empty:
                remaining = WORKDAY_HOURS
                day_jobs = []

                for idx, job in zone_jobs.iterrows():
                    job_time = job["job_hours"] + AVG_TRAVEL_HOURS
                    if job_time <= remaining:
                        day_jobs.append(job)
                        remaining -= job_time

                if not day_jobs:
                    break

                for job in day_jobs:
                    planning_rows.append({
                        "Technicien": tech,
                        "Jour": day,
                        "Zone": zone,
                        "Job ID": job["job_id"],
                        "Adresse": job["address"],
                        "Durée job (h)": job["job_hours"],
                        "Déplacement estimé (h)": AVG_TRAVEL_HOURS
                    })
                    job_queue = job_queue[job_queue["job_id"] != job["job_id"]]

                day += 1
                zone_jobs = job_queue[job_queue["zone"] == zone]

    planning_df = pd.DataFrame(planning_rows)

    st.success("✅ Planning généré")
    st.dataframe(planning_df, use_container_width=True)

    # Export
    st.download_button(
        "⬇️ Télécharger le planning (Excel)",
        data=planning_df.to_excel(index=False),
        file_name="planning_techniciens.xlsx"
    )
