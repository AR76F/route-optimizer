"""
timesheet.py — BMS Timesheet (Streamlit page)
==============================================
Drop this file alongside your app.py and add it to your pages/ folder,
OR call show_timesheet() from your main app multipage routing.

Features (mirrors the Excel):
  - Employee selector (from TECHNICIANS list — update in WO_INTERNE_URL section)
  - Pay period auto-detection (same period table as Excel, weekly Saturday cutoff)
  - RT / OT / DT auto-rules:
        Mon–Fri  06:00–08:00 → OT before
        Mon–Fri  08:00–17:00 → RT
        Mon–Fri  17:00–23:00 → OT after
        Mon–Fri  23:00–06:00 → DT night
        Saturday entire day  → OT
        Sunday   entire day  → DT
  - Meal break auto (≥ 30 min unpaid lunch → meal_hrs = 0.5)
  - Pay ID / Pay Type auto from Catégorie  (RT/OT/DT/VP/SP)
  - Trans Type (WO / PM)
  - Order Ref — WO Interne dropdown OR free text for client WOs
  - Job type (Job Client / WO Interne / PM)
  - "Déjà BMS" flag per line
  - Add / remove rows dynamically
  - Previous / Next week navigation
  - Submit → writes JSON to OneDrive folder (FeuilleDeTemps/<periode>/<emp>/)
  - WO Interne list: loaded from a single JSON file on GitHub (or fallback hardcoded)
    → update ONE file, everyone gets it automatically

JSON output format is identical to what bms_watcher.py expects — no changes needed.

Configuration
─────────────
Set these env vars (or edit the constants below):
    ONEDRIVE_FOLDER   full path to the local OneDrive FeuilleDeTemps folder
                      e.g. C:\\Users\\you\\OneDrive - Cummins\\FeuilleDeTemps
    WO_JSON_URL       raw GitHub URL to your wo_interne.json  (optional)
"""

import os
import json
import math
import streamlit as st
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# ─────────────────────────── Configuration ───────────────────────────────────

ONEDRIVE_FOLDER = os.environ.get(
    "ONEDRIVE_FOLDER",
    str(Path.home() / "OneDrive - Cummins" / "FeuilleDeTemps"),
)

# Raw GitHub URL pointing to your wo_interne.json
# If blank, falls back to HARDCODED_WO below
WO_JSON_URL = os.environ.get("WO_JSON_URL", "")

TZ = ZoneInfo("America/Toronto")

# ─────────────────────────── Static data ─────────────────────────────────────

TECHNICIANS = [
    ("Alain Duguay",              "GW636"),
    ("Alexandre Pelletier Guay",  "ME964"),
    ("Ali Reza-Sabour",           "KO424"),
    ("David Robitaille",          "UZ895"),
    ("Patrick Robitaille",        "HA414"),
    ("Benoit Charrette",          "HG848"),
    ("Benoit Larame",             "SQ740"),
    ("Christian Dubrueil",        "IW666"),
    ("Donald Lagace (IN SHOP)",   "IW667"),
    ("Elie Rajotte-Lemay",        "XE270"),
    ("Francois Racine",           "GW629"),
    ("Fredy Diaz",                "MA470"),
    ("George Yamna",              "TC807"),
    ("Kevin Duranceau",           "KP275"),
    ("Louis Lauzon",              "FW688"),
    ("Martin Bourbonnière",       "GW574"),
    ("Maxime Roy",                "SO763"),
    ("Michael Sulte",             "XY100"),
    ("Patrick Bellefleur",        "GW573"),
    ("Pier-Luc Cote",             "MA213"),
    ("Sebastien Pepin (IN SHOP)", "WX094"),
    ("Sergio Mendoza",            "AT12D"),
]

# Pay code table — mirrors the Codes sheet
PAY_CODES = {
    "Regular Time":  ("RT", "RT"),
    "Overtime":      ("OT", "OT"),
    "Double Time":   ("DT", "DT"),
    "Vacances":      ("RT", "VP"),
    "Maladie":       ("RT", "SP"),
}

# Fallback WO Interne (used when WO_JSON_URL is empty / unreachable)
HARDCODED_WO = [
    ("MAINTENANCE BATIMENT",                       "350993"),
    ("RÉPARATION CAMION - FSPG",                   "350994"),
    ("SHOP SUPPLIES - FSPG",                       "351013"),
    ("EXPÉDITION PIÈCES",                          "350995"),
    ("SHOP SUPPLIES - DE Z8 À AK",                 "350996"),
    ("AJUSTEMENTS PIÈCES",                         "351012"),
    ("FORMATION -SÉCURITÉ  FSPG",                  "350997"),
    ("FORMATION EN LIGNE (QSOL - CLC) - FSPG",    "350998"),
    ("FORMATION TECHNIQUE EN CLASSE -  FSPG",      "350999"),
    ("FRAIS DE FORMATION (AUTORISÉ PAR DAN EPURE)","351000"),
    ("TEMPS NON-PRODUCTIF - FSPG",                 "351002"),
    ("OUTILLAGES",                                 "351011"),
    ("ÉQUIPEMENT DE SÉCURITÉ ET RÉUNIONS",         "351003"),
    ("SUPERVISION",                                "351004"),
    ("PMO - SHOP SUPPLIES",                        "351005"),
    ("RÉUNION D'ÉQUIPE",                           "351006"),
    ("PERTE DE TEMPS TI / ORDI",                   "351007"),
    ("DÉPLACEMENT QUÉBEC (AQ)",                    "463357"),
    ("DÉPLACEMENT OTTAWA (AK)",                    "111345"),
    ("SUPPORT TECH LEAD HAND",                     "351008"),
    ("ADMIN ISPG",                                 "351009"),
    ("PAIEMENT 4HR RT(INCITATIF TRAVAUX NUIT)",    "351010"),
]

MOIS_EN = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",
           7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}

MOIS_FR = {1:"jan",2:"fév",3:"mar",4:"avr",5:"mai",6:"jun",
           7:"jul",8:"aoû",9:"sep",10:"oct",11:"nov",12:"déc"}

DAY_FR = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]

# ─────────────────────────── Pay period helpers ───────────────────────────────

def _pay_periods_around(ref: date):
    """Generate pay period (start, end) tuples covering ref ± 3 weeks.
    Periods end on Saturday and are 7 days long."""
    # Find nearest Saturday at or before ref
    delta = (ref.weekday() + 2) % 7  # days since last Saturday (Sat=5)
    sat = ref - timedelta(days=delta)
    # Walk back 2 more periods and forward 2
    periods = []
    for i in range(-2, 4):
        end = sat + timedelta(weeks=i)
        start = end - timedelta(days=6)
        periods.append((start, end))
    return periods

def current_period(ref: date = None):
    ref = ref or date.today()
    for start, end in _pay_periods_around(ref):
        if start <= ref <= end:
            return start, end
    # Fallback: week ending next Saturday
    delta = (5 - ref.weekday()) % 7
    end = ref + timedelta(days=delta)
    return end - timedelta(days=6), end

def fmt_period(d: date):
    return f"{d.day:02d}-{MOIS_EN[d.month]}-{d.year}"

def fmt_date_fr(d: date):
    return f"{DAY_FR[d.weekday()]} {d.day} {MOIS_FR[d.month]}"

# ─────────────────────────── RT/OT/DT rules ──────────────────────────────────

def infer_category(d: date, time_in: float, time_out: float) -> str:
    """Return 'Regular Time', 'Overtime', or 'Double Time' from day + hours."""
    wd = d.weekday()  # Mon=0 … Sun=6
    if wd == 6:
        return "Double Time"
    if wd == 5:
        return "Overtime"
    # Weekday — check if entirely in RT window
    if time_in is not None and time_out is not None:
        if time_in >= 8.0 and time_out <= 17.0:
            return "Regular Time"
        if (time_in < 6.0) or (time_out > 23.0) or (time_in >= 23.0):
            return "Double Time"
        return "Overtime"
    return "Regular Time"

def compute_hours(time_in: float, time_out: float, meal_hrs: float = 0.0) -> float:
    if time_in is None or time_out is None:
        return 0.0
    h = time_out - time_in - meal_hrs
    return max(round(h, 2), 0.0)

def auto_meal(time_in: float, time_out: float) -> float:
    """0.5 if span ≥ 5h and crosses 11–13 window, else 0."""
    if time_in is None or time_out is None:
        return 0.0
    if (time_out - time_in) >= 5.0 and time_in < 13.0 and time_out > 11.0:
        return 0.5
    return 0.0

def decimal_to_hhmm(h: float) -> str:
    if h is None:
        return ""
    hh = int(h)
    mm = int(round((h - hh) * 60))
    return f"{hh:02d}:{mm:02d}"

# ─────────────────────────── WO Interne loader ───────────────────────────────

@st.cache_data(ttl=3600)
def load_wo_interne() -> list[tuple[str, str]]:
    if WO_JSON_URL:
        try:
            import urllib.request
            with urllib.request.urlopen(WO_JSON_URL, timeout=5) as r:
                data = json.loads(r.read())
            return [(item["description"], item["no_wo"]) for item in data]
        except Exception:
            pass
    return HARDCODED_WO

# ─────────────────────────── JSON / OneDrive writer ──────────────────────────

def submit_timesheet(emp_num: str, emp_nom: str, periode_fin: date, rows: list[dict]) -> tuple[bool, str]:
    """Write the JSON file to OneDrive exactly as bms_watcher.py expects."""
    if not rows:
        return False, "Aucune ligne à soumettre."

    periode_str = fmt_period(periode_fin)
    payload = {
        "employe_num":  emp_num,
        "employe_nom":  emp_nom,
        "periode_fin":  periode_str,
        "soumis_le":    datetime.now(TZ).isoformat(),
        "lignes":       rows,
    }

    try:
        base = Path(ONEDRIVE_FOLDER)
        folder = base / periode_str / f"{emp_num}"
        folder.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{emp_num}_{periode_str}_{ts}.json"
        fpath = folder / fname
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True, str(fpath)
    except Exception as e:
        return False, str(e)

# ─────────────────────────── Row state helpers ───────────────────────────────

def _blank_row(d: date) -> dict:
    return {
        "date":        d,
        "time_in":     None,
        "time_out":    None,
        "category":    "",       # auto when time_in/out set
        "job_type":    "Job Client",
        "trans_type":  "WO",
        "order_ref":   "",
        "wo_interne":  "",       # selected WO label
        "commentaire": "",
        "deja_bms":    False,
    }

def default_rows(start: date, end: date) -> list[dict]:
    rows = []
    d = start
    while d <= end:
        rows.append(_blank_row(d))
        d += timedelta(days=1)
    return rows

# ─────────────────────────── CSS ─────────────────────────────────────────────

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.ts-header {
    background: linear-gradient(135deg, #0a1628 0%, #112240 60%, #1a3a5c 100%);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
}
.ts-header h1 {
    color: #e8f4fd;
    font-size: 1.6rem;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.3px;
}
.ts-header .subtitle {
    color: #7eb8d4;
    font-size: 0.82rem;
    font-family: 'DM Mono', monospace;
    margin-top: 2px;
}

.period-badge {
    background: #1e3a5f;
    border: 1px solid #2d5a8e;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #7eb8d4;
    margin-bottom: 1rem;
    display: inline-block;
}

.day-card {
    background: #f8fafd;
    border: 1px solid #e2eaf5;
    border-left: 4px solid #2d6be4;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.day-card.weekend-sat { border-left-color: #e07b00; background: #fffbf5; }
.day-card.weekend-sun { border-left-color: #d63031; background: #fff5f5; }
.day-card.deja-bms    { opacity: 0.55; }

.day-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #4a6fa5;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
    font-family: 'DM Mono', monospace;
}
.day-label.sat { color: #e07b00; }
.day-label.sun { color: #d63031; }

.badge-rt  { background:#dff0d8; color:#2d6a2d; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-ot  { background:#fff3cd; color:#856404; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-dt  { background:#f8d7da; color:#721c24; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-vp  { background:#d1ecf1; color:#0c5460; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-sp  { background:#e2e3e5; color:#383d41; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }

.hours-display {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: #1a3a5c;
}

.submit-section {
    background: linear-gradient(135deg, #e8f4fd, #f0f8ff);
    border: 1px solid #bee3f8;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-top: 1.5rem;
}

.stButton > button {
    background: #2d6be4;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    font-weight: 500;
    font-size: 0.9rem;
    transition: background 0.2s;
}
.stButton > button:hover { background: #1a52c4; }

.wo-rule-box {
    background: #f0f4ff;
    border-left: 3px solid #2d6be4;
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    font-size: 0.78rem;
    color: #334;
    margin-bottom: 1rem;
}
</style>
"""

# ─────────────────────────── Main page function ───────────────────────────────

def show_timesheet():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Header ──
    st.markdown("""
    <div class="ts-header">
        <div>
            <h1>⏱ Feuille de temps BMS</h1>
            <div class="subtitle">Succursale Z8 · Cummins Eastern Canada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load WO Interne ──
    wo_list = load_wo_interne()
    wo_labels = [f"{desc}  ({no})" for desc, no in wo_list]
    wo_by_label = {f"{desc}  ({no})": no for desc, no in wo_list}

    # ═══════════════════════════════════════════════════════
    #  SIDEBAR — Employee + Period
    # ═══════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown("### 👤 Employé")
        tech_labels = [f"{nom}  ({num})" for nom, num in TECHNICIANS]
        sel_tech = st.selectbox("Nom", tech_labels, key="sel_tech")
        emp_nom, emp_num = sel_tech.rsplit("  (", 1)
        emp_num = emp_num.rstrip(")")

        st.markdown("---")
        st.markdown("### 📅 Période")

        today = date.today()
        p_start, p_end = current_period(today)

        if "period_offset" not in st.session_state:
            st.session_state.period_offset = 0

        col_prev, col_cur, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀", key="prev_week"):
                st.session_state.period_offset -= 1
        with col_cur:
            if st.button("Auj.", key="today_week"):
                st.session_state.period_offset = 0
        with col_next:
            if st.button("▶", key="next_week"):
                st.session_state.period_offset += 1

        offset = st.session_state.period_offset
        p_start = p_start + timedelta(weeks=offset)
        p_end   = p_end   + timedelta(weeks=offset)

        st.markdown(
            f'<div class="period-badge">📅 {fmt_period(p_start)} → {fmt_period(p_end)}</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("### ℹ️ Règles heures")
        st.markdown("""
        <div class="wo-rule-box">
        🟢 <b>RT</b> Lun–Ven 08:00–17:00<br>
        🟡 <b>OT</b> Lun–Ven 06–08 et 17–23<br>
        🔴 <b>DT</b> Lun–Ven 23–06<br>
        🟠 <b>OT</b> Samedi (toute la journée)<br>
        🔴 <b>DT</b> Dimanche (toute la journée)
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    #  Initialize / reset rows when period or employee changes
    # ═══════════════════════════════════════════════════════
    state_key = f"rows_{emp_num}_{p_end.isoformat()}"

    if state_key not in st.session_state:
        st.session_state[state_key] = default_rows(p_start, p_end)

    rows: list[dict] = st.session_state[state_key]

    # ═══════════════════════════════════════════════════════
    #  Row editor — one expander per day
    # ═══════════════════════════════════════════════════════
    st.markdown(f"**Saisie des heures — {emp_nom}**")

    total_hours = 0.0
    rows_to_delete = []

    for idx, row in enumerate(rows):
        d: date = row["date"]
        wd = d.weekday()

        day_class = "day-card"
        label_class = "day-label"
        if wd == 5:
            day_class += " weekend-sat"
            label_class += " sat"
        elif wd == 6:
            day_class += " weekend-sun"
            label_class += " sun"
        if row.get("deja_bms"):
            day_class += " deja-bms"

        day_str = fmt_date_fr(d)

        # Compute live hours for display
        ti = row.get("time_in")
        to_ = row.get("time_out")
        meal = row.get("meal_hrs", 0.0) or 0.0
        hrs  = compute_hours(ti, to_, meal)
        total_hours += hrs

        badge_html = ""
        cat = row.get("category", "")
        if cat == "Regular Time":  badge_html = '<span class="badge-rt">RT</span>'
        elif cat == "Overtime":    badge_html = '<span class="badge-ot">OT</span>'
        elif cat == "Double Time": badge_html = '<span class="badge-dt">DT</span>'
        elif cat == "Vacances":    badge_html = '<span class="badge-vp">VP</span>'
        elif cat == "Maladie":     badge_html = '<span class="badge-sp">SP</span>'

        hrs_str = f"{hrs:.2f}h" if hrs > 0 else "—"

        with st.expander(f"{day_str}   {badge_html}   {hrs_str}", expanded=(hrs == 0 and wd < 5)):
            # Allow multiple rows per day (extra job lines)
            _render_row(idx, row, wo_labels, wo_by_label, d)

            # Add / Remove line buttons
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("➕ Ajouter une ligne", key=f"add_{idx}"):
                    # Insert duplicate row for same date
                    new_row = _blank_row(d)
                    rows.insert(idx + 1, new_row)
                    st.rerun()
            with c2:
                if len([r for r in rows if r["date"] == d]) > 1:
                    if st.button("✕ Enlever", key=f"del_{idx}"):
                        rows_to_delete.append(idx)

    # Apply deletions
    if rows_to_delete:
        for i in sorted(rows_to_delete, reverse=True):
            rows.pop(i)
        st.rerun()

    # ═══════════════════════════════════════════════════════
    #  Summary + Submit
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(f"""
    <div class="submit-section">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <span style="font-size:1rem; font-weight:600; color:#1a3a5c;">
                Total semaine
            </span>
            <span class="hours-display">{total_hours:.2f} h</span>
        </div>
    """, unsafe_allow_html=True)

    # JSON preview (collapsible)
    with st.expander("🔍 Aperçu JSON (bms_watcher)"):
        preview_rows = _build_json_rows(rows)
        st.json({
            "employe_num": emp_num,
            "employe_nom": emp_nom,
            "periode_fin": fmt_period(p_end),
            "lignes": preview_rows,
        })

    col_sub, col_rst = st.columns([2, 1])
    with col_sub:
        if st.button("📤 Soumettre à BMS Watcher", type="primary", key="submit_btn"):
            json_rows = _build_json_rows(rows)
            valid = [r for r in json_rows if r.get("heures", 0) > 0]
            if not valid:
                st.warning("⚠️ Aucune ligne avec des heures à soumettre.")
            else:
                ok, msg = submit_timesheet(emp_num, emp_nom, p_end, valid)
                if ok:
                    st.success(f"✅ Soumis ! ({len(valid)} ligne(s)) → {Path(msg).name}")
                    # Mark all submitted rows as deja_bms
                    for r in rows:
                        if r.get("time_in") and r.get("time_out"):
                            r["deja_bms"] = True
                else:
                    st.error(f"❌ Erreur : {msg}")

    with col_rst:
        if st.button("🔄 Réinitialiser", key="reset_btn"):
            st.session_state[state_key] = default_rows(p_start, p_end)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────── Row renderer ────────────────────────────────────

def _render_row(idx: int, row: dict, wo_labels: list, wo_by_label: dict, d: date):
    """Render all inputs for a single time-entry row, mutating `row` in place."""

    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 1])

    with c1:
        time_in_str = st.text_input(
            "Time In (ex: 8.0)", 
            value="" if row["time_in"] is None else str(row["time_in"]),
            key=f"ti_{idx}",
            placeholder="8.0",
            help="Heure décimale : 8.0 = 8h00, 13.5 = 13h30"
        )
    with c2:
        time_out_str = st.text_input(
            "Time Out (ex: 17.0)", 
            value="" if row["time_out"] is None else str(row["time_out"]),
            key=f"to_{idx}",
            placeholder="17.0",
        )
    with c3:
        cat_options = [""] + list(PAY_CODES.keys())
        current_cat = row.get("category", "")
        try:
            cat_idx = cat_options.index(current_cat)
        except ValueError:
            cat_idx = 0
        cat = st.selectbox("Catégorie", cat_options, index=cat_idx, key=f"cat_{idx}")
    with c4:
        deja = st.checkbox("Déjà BMS", value=row.get("deja_bms", False), key=f"bms_{idx}")

    # Parse time inputs
    def _parse_time(s):
        s = s.strip().replace(",", ".")
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    ti = _parse_time(time_in_str)
    to_ = _parse_time(time_out_str)

    # Auto meal
    meal = auto_meal(ti, to_) if (ti is not None and to_ is not None) else 0.0

    # Auto category from time if not manually set
    if not cat and ti is not None and to_ is not None:
        cat = infer_category(d, ti, to_)
    elif not cat:
        # Default from weekday
        cat = infer_category(d, None, None)

    hrs = compute_hours(ti, to_, meal)

    if ti is not None and to_ is not None:
        pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
        cols_info = st.columns([1, 1, 1, 1])
        cols_info[0].metric("Heures", f"{hrs:.2f} h")
        cols_info[1].metric("Pay ID", pay_id)
        cols_info[2].metric("Pay Type", pay_type)
        if meal > 0:
            cols_info[3].metric("Repas", f"{meal:.1f} h")

    c5, c6, c7 = st.columns([1, 1, 2])
    with c5:
        job_type = st.selectbox(
            "Type de job",
            ["Job Client", "WO Interne", "PM"],
            index=["Job Client", "WO Interne", "PM"].index(row.get("job_type", "Job Client")),
            key=f"jt_{idx}",
        )
    with c6:
        trans_options = ["WO", "PM"]
        t_idx = 1 if job_type == "PM" else 0
        trans_type = st.selectbox("Trans Type", trans_options, index=t_idx, key=f"tt_{idx}")

    with c7:
        if job_type == "WO Interne":
            # Dropdown from WO Interne list
            current_wo_label = row.get("wo_interne", "")
            try:
                wo_idx = wo_labels.index(current_wo_label) + 1
            except ValueError:
                wo_idx = 0
            wo_sel = st.selectbox("Order Ref (WO Interne)", ["— choisir —"] + wo_labels, index=wo_idx, key=f"wo_{idx}")
            order_ref = wo_by_label.get(wo_sel, "") if wo_sel != "— choisir —" else ""
            wo_interne_sel = wo_sel if wo_sel != "— choisir —" else ""
        else:
            # Free text for client WO or PM
            order_ref = st.text_input("Order Ref", value=row.get("order_ref", ""), key=f"or_{idx}", placeholder="Ex: 345924")
            wo_interne_sel = ""

    commentaire = st.text_input("Commentaire", value=row.get("commentaire", ""), key=f"cm_{idx}", placeholder="Optionnel")

    # Mutate row dict in place
    row["time_in"]     = ti
    row["time_out"]    = to_
    row["meal_hrs"]    = meal
    row["category"]    = cat
    row["job_type"]    = job_type
    row["trans_type"]  = trans_type
    row["order_ref"]   = order_ref
    row["wo_interne"]  = wo_interne_sel
    row["commentaire"] = commentaire
    row["deja_bms"]    = deja


def _build_json_rows(rows: list[dict]) -> list[dict]:
    """Convert internal row dicts to the JSON format bms_watcher.py expects."""
    MOIS_EN_U = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",
                 7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}
    out = []
    for row in rows:
        d: date = row["date"]
        ti  = row.get("time_in")
        to_ = row.get("time_out")
        if ti is None or to_ is None:
            continue
        meal = row.get("meal_hrs", 0.0) or 0.0
        hrs  = compute_hours(ti, to_, meal)
        cat  = row.get("category", "Regular Time") or "Regular Time"
        pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
        out.append({
            "date":        f"{d.day:02d}-{MOIS_EN_U[d.month]}-{d.year}",
            "heures":      hrs,
            "time_in":     decimal_to_hhmm(ti),
            "time_out":    decimal_to_hhmm(to_),
            "pay_id":      pay_id,
            "pay_type":    pay_type,
            "trans_type":  row.get("trans_type", "WO"),
            "order_ref":   row.get("order_ref", ""),
            "meal_hrs":    meal,
            "commentaire": row.get("commentaire", ""),
            "deja_bms":    row.get("deja_bms", False),
        })
    return out


# ─────────────────────────── Entry point ─────────────────────────────────────

if __name__ == "__main__":
    st.set_page_config(
        page_title="Feuille de temps BMS",
        page_icon="⏱",
        layout="wide",
    )
    show_timesheet()
