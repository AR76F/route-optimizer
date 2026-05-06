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

def _coerce_date(v) -> date:
    """Convert string or date to date object safely."""
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v))
    except Exception:
        return date.today()

def fmt_period(d):
    d = _coerce_date(d)
    return f"{d.day:02d}-{MOIS_EN[d.month]}-{d.year}"

def fmt_date_fr(d):
    d = _coerce_date(d)
    return f"{DAY_FR[d.weekday()]} {d.day} {MOIS_FR[d.month]}"

# ─────────────────────────── RT/OT/DT rules ──────────────────────────────────

def infer_category(d, time_in: float, time_out: float) -> str:
    """Return 'Regular Time', 'Overtime', or 'Double Time' from day + hours."""
    d = _coerce_date(d)
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

def compute_hours(time_in, time_out, meal_hrs: float = 0.0) -> float:
    if time_in is None or time_out is None:
        return 0.0
    try:
        ti = float(str(time_in).replace(",", ".")) if ":" not in str(time_in) else \
             int(str(time_in).split(":")[0]) + int(str(time_in).split(":")[1]) / 60.0
        to = float(str(time_out).replace(",", ".")) if ":" not in str(time_out) else \
             int(str(time_out).split(":")[0]) + int(str(time_out).split(":")[1]) / 60.0
    except Exception:
        return 0.0
    h = to - ti - meal_hrs
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

# ─────────────────────────── Google Sheets connection ────────────────────────

def _get_gsheet_client():
    """Returns an authorized gspread client using the service account from Streamlit secrets."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.session_state["_gsheet_error"] = f"Client: {type(e).__name__}: {e}"
        return None

def _get_sheet(sheet_name: str = "Soumissions"):
    """Returns the requested worksheet."""
    try:
        client = _get_gsheet_client()
        if not client:
            return None
        gsheet_id = st.secrets.get("GSHEET_ID", "")
        if not gsheet_id:
            st.session_state["_gsheet_error"] = "GSHEET_ID manquant dans les secrets"
            return None
        spreadsheet = client.open_by_key(gsheet_id)
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        st.session_state["_gsheet_error"] = f"Sheet: {type(e).__name__}: {e}"
        return None

# ─────────────────────────── Submit — Google Sheets + OneDrive JSON ──────────

def submit_timesheet(emp_num: str, emp_nom: str, periode_fin: date, rows: list[dict]) -> tuple[bool, str]:
    """
    Write to Google Sheets (primary — works from anywhere including iPad)
    AND write JSON to OneDrive (for bms_watcher.py compatibility).
    """
    if not rows:
        return False, "Aucune ligne à soumettre."

    periode_str = fmt_period(periode_fin)
    soumis_le   = datetime.now(TZ).isoformat()
    errors      = []

    # ── 1) Google Sheets ──────────────────────────────────────────
    try:
        ws = _get_sheet("Soumissions")
        if ws:
            # Use the JSON-transformed rows (HH:MM format, proper heures)
            json_rows = _build_json_rows(rows)
            new_rows = []
            for r in json_rows:
                new_rows.append([
                    r.get("date", ""),
                    emp_num,
                    emp_nom,
                    periode_str,
                    soumis_le,
                    r.get("time_in", ""),    # already HH:MM
                    r.get("time_out", ""),   # already HH:MM
                    r.get("heures", ""),
                    r.get("pay_id", ""),
                    r.get("pay_type", ""),
                    r.get("trans_type", ""),
                    r.get("order_ref", ""),
                    r.get("meal_hrs", ""),
                    r.get("commentaire", ""),
                    r.get("pay_type", ""),   # categorie
                ])
            ws.append_rows(new_rows, value_input_option="USER_ENTERED")
        else:
            detail = st.session_state.get("_gsheet_error", "raison inconnue")
            errors.append(f"Google Sheets non disponible — {detail}")
    except Exception as e:
        import traceback
        errors.append(f"Google Sheets: {traceback.format_exc()}")

    # ── 2) OneDrive JSON (for bms_watcher.py) ─────────────────────
    try:
        payload = {
            "employe_num": emp_num,
            "employe_nom": emp_nom,
            "periode_fin": periode_str,
            "soumis_le":   soumis_le,
            "lignes":      rows,
        }
        base   = Path(ONEDRIVE_FOLDER)
        folder = base / periode_str / emp_num
        folder.mkdir(parents=True, exist_ok=True)
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        fpath = folder / f"{emp_num}_{periode_str}_{ts}.json"
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        errors.append(f"OneDrive: {e}")

    if len(errors) == 2:
        return False, " | ".join(errors)
    elif len(errors) == 1:
        return True, f"Soumis avec avertissement : {errors[0]}"
    return True, f"{emp_num}_{periode_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


# ─────────────────────────── Load week from Google Sheets ────────────────────

def load_week_from_gsheet(emp_num: str, p_start: date, p_end: date) -> list[dict] | None:
    """
    Reads all submitted rows for this employee/period from Google Sheets.
    Returns a full week grid with submitted days as read-only.
    """
    try:
        ws = _get_sheet("Soumissions")
        if not ws:
            return None

        all_records = ws.get_all_records()
        if not all_records:
            return None

        periode_str = fmt_period(p_end)

        MOIS_NUM_R = {
            "JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
            "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12,
        }

        def _parse_date_bms(s: str) -> date | None:
            try:
                parts = str(s).strip().upper().split("-")
                return date(int(parts[2]), MOIS_NUM_R[parts[1]], int(parts[0]))
            except Exception:
                return None

        def _to_float(v) -> float | None:
            try:
                s = str(v).strip()
                if not s or s == "None":
                    return None
                if ":" in s:
                    # HH:MM format → decimal
                    h, m = s.split(":")
                    return int(h) + int(m) / 60.0
                return float(s.replace(",", "."))
            except Exception:
                return None

        cat_map = {
            "RT": "Regular Time", "OT": "Overtime", "DT": "Double Time",
            "VP": "Vacances",     "SP": "Maladie",
        }

        from collections import defaultdict
        lignes_by_date: dict = defaultdict(list)

        for rec in all_records:
            if str(rec.get("employe_num", "")).strip() != emp_num:
                continue
            if str(rec.get("periode_fin", "")).strip() != periode_str:
                continue
            d = _parse_date_bms(str(rec.get("date", "")))
            if d is None or not (p_start <= d <= p_end):
                continue

            pay_type = str(rec.get("pay_type", "RT")).strip()
            lignes_by_date[d].append({
                "date":        d,
                "time_in":     _to_float(rec.get("time_in")),
                "time_out":    _to_float(rec.get("time_out")),
                "category":    cat_map.get(pay_type, "Regular Time"),
                "job_type":    "Job Client",
                "trans_type":  str(rec.get("trans_type", "WO")).strip(),
                "order_ref":   str(rec.get("order_ref", "")).strip(),
                "wo_interne":  "",
                "commentaire": str(rec.get("commentaire", "")).strip(),
                "deja_bms":    True,
                "meal_hrs":    float(rec.get("meal_hrs", 0) or 0),
            })

        if not lignes_by_date:
            return None

        result = []
        d = p_start
        while d <= p_end:
            if d in lignes_by_date:
                result.extend(lignes_by_date[d])
            else:
                result.append(_blank_row(d))
            d += timedelta(days=1)
        return result

    except Exception:
        return None

# ─────────────────────────── Row state helpers ───────────────────────────────

def _blank_row(d: date) -> dict:
    import uuid
    return {
        "date":        d,
        "uid":         str(uuid.uuid4())[:8],  # stable key across reruns
        "time_in":     None,
        "time_out":    None,
        "category":    "",
        "job_type":    "Job Client",
        "trans_type":  "WO",
        "order_ref":   "",
        "wo_interne":  "",
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
    #  Charger la semaine depuis OneDrive
    # ═══════════════════════════════════════════════════════

    def _charger_semaine_onedrive(emp_num: str, p_end: date) -> list[dict] | None:
        """
        Lit tous les JSON soumis pour cet employé/période depuis OneDrive
        et retourne les lignes fusionnées, prêtes à remplir la grille.
        Retourne None si rien trouvé.
        """
        periode_str = fmt_period(p_end)
        folder = Path(ONEDRIVE_FOLDER) / periode_str / emp_num
        if not folder.exists():
            return None

        # Lire tous les JSON (y compris dans traites/)
        all_files = list(folder.glob("*.json"))
        traites_folder = folder / "traites"
        if traites_folder.exists():
            all_files += list(traites_folder.glob("*.json"))

        if not all_files:
            return None

        # Regrouper toutes les lignes par date (date → liste de lignes)
        from collections import defaultdict
        MOIS_NUM_R = {
            "JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
            "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12,
        }

        def _parse_date_bms(s: str) -> date | None:
            try:
                parts = str(s).strip().upper().split("-")
                return date(int(parts[2]), MOIS_NUM_R[parts[1]], int(parts[0]))
            except Exception:
                return None

        def _hhmm_to_decimal(s: str) -> float | None:
            try:
                h, m = str(s).strip().split(":")
                return int(h) + int(m) / 60.0
            except Exception:
                return None

        lignes_by_date: dict = defaultdict(list)

        for f in sorted(all_files):
            try:
                with open(f, encoding="utf-8-sig") as fp:
                    data = json.load(fp)
                for ligne in data.get("lignes", []):
                    d = _parse_date_bms(ligne.get("date", ""))
                    if d is None:
                        continue
                    ti = _hhmm_to_decimal(ligne.get("time_in", ""))
                    to_ = _hhmm_to_decimal(ligne.get("time_out", ""))
                    pay_type = ligne.get("pay_type", "RT")
                    # Reverse-map pay_type → category
                    cat_map = {"RT": "Regular Time", "OT": "Overtime", "DT": "Double Time",
                               "VP": "Vacances", "SP": "Maladie"}
                    cat = cat_map.get(pay_type, "Regular Time")
                    lignes_by_date[d].append({
                        "date":        d,
                        "time_in":     ti,
                        "time_out":    to_,
                        "category":    cat,
                        "job_type":    "WO Interne" if ligne.get("trans_type") == "WO"
                                       and not ligne.get("order_ref", "").isdigit()
                                       else "Job Client",
                        "trans_type":  ligne.get("trans_type", "WO"),
                        "order_ref":   ligne.get("order_ref", ""),
                        "wo_interne":  "",
                        "commentaire": ligne.get("commentaire", ""),
                        "deja_bms":    True,   # déjà soumis = lecture seule
                        "meal_hrs":    ligne.get("meal_hrs", 0.0),
                    })
            except Exception:
                continue

        if not lignes_by_date:
            return None

        # Rebuilder la grille complète de la semaine en fusionnant
        result = []
        d = p_start
        while d <= p_end:
            if d in lignes_by_date:
                result.extend(lignes_by_date[d])
            else:
                result.append(_blank_row(d))
            d += timedelta(days=1)
        return result

    # Bouton charger + indicateur
    col_load, col_info = st.columns([1, 3])
    with col_load:
        if st.button("📂 Charger ma semaine", key="load_week_btn",
                     help="Relit les temps déjà soumis depuis Google Sheets"):
            loaded = load_week_from_gsheet(emp_num, p_start, p_end)
            if loaded:
                st.session_state[state_key] = loaded
                st.session_state[f"loaded_{state_key}"] = True
                st.rerun()
            else:
                st.warning("Aucune soumission trouvée pour cette période.")
    with col_info:
        if st.session_state.get(f"loaded_{state_key}"):
            nb_deja = sum(1 for r in rows if r.get("deja_bms"))
            st.info(f"✅ {nb_deja} ligne(s) chargée(s) depuis Google Sheets — affichées en grisé.")

    # ═══════════════════════════════════════════════════════
    #  Row editor — one expander per DAY, all lines inside
    # ═══════════════════════════════════════════════════════
    st.markdown(f"**Saisie des heures — {emp_nom}**")

    total_hours = 0.0
    rows_to_delete = []

    # Group rows by date to render all lines of a day inside one expander
    from itertools import groupby
    rows_by_day = []
    for d_key, group in groupby(enumerate(rows), key=lambda x: _coerce_date(x[1]["date"])):
        rows_by_day.append((_coerce_date(d_key), list(group)))

    for d, day_rows in rows_by_day:
        wd = d.weekday()

        # Compute total hours for this day (all lines combined)
        day_total = 0.0
        day_cats = []
        for _, row in day_rows:
            ti  = row.get("time_in")
            to_ = row.get("time_out")
            cat = row.get("category", "")
            meal = 0.0
            h = compute_hours(ti, to_, meal)
            day_total += h
            total_hours += h
            cat = row.get("category", "")
            if cat and cat not in day_cats:
                day_cats.append(cat)

        # Build title — show hours per category instead of total
        from collections import defaultdict
        hrs_by_cat = defaultdict(float)
        for _, row in day_rows:
            ti  = row.get("time_in")
            to_ = row.get("time_out")
            cat = row.get("category", "")
            if ti is not None and to_ is not None and cat:
                hrs_by_cat[cat] += compute_hours(ti, to_, 0.0)

        badge_map = {
            "Regular Time": ("🟢", "RT"), "Overtime": ("🟡", "OT"),
            "Double Time":  ("🔴", "DT"), "Vacances": ("🔵", "VP"), "Maladie": ("⚪", "SP"),
        }
        cat_order = ["Regular Time", "Overtime", "Double Time", "Vacances", "Maladie"]

        if hrs_by_cat:
            parts = []
            for cat in cat_order:
                if cat in hrs_by_cat:
                    icon, label = badge_map.get(cat, ("•", cat))
                    parts.append(f"{icon} {hrs_by_cat[cat]:.2f}h {label}")
            title_hrs = "  ·  ".join(parts)
        else:
            title_hrs = "—"

        day_str  = fmt_date_fr(d)
        n_lines  = len(day_rows)
        line_label = f"  ({n_lines} lignes)" if n_lines > 1 else ""

        exp_key = f"exp_{state_key}_{d.isoformat()}"
        if exp_key not in st.session_state:
            st.session_state[exp_key] = (day_total == 0 and wd < 5)

        with st.expander(f"{day_str}   {title_hrs}{line_label}",
                         expanded=st.session_state[exp_key]):

            rt_accumulated = 0.0  # RT hours consumed so far in this day
            for idx, row in day_rows:
                # Separator between lines within the same day
                if idx != day_rows[0][0]:
                    st.markdown(
                        "<hr style='margin:4px 0;border:none;border-top:1px solid #2d3a4a;'>",
                        unsafe_allow_html=True
                    )

                _render_row(idx, row, wo_labels, wo_by_label, d, emp_num, rt_already=rt_accumulated)

                # Update accumulated RT for next line using raw hours
                # (category not reliable yet during render — use time delta)
                ti_ = row.get("time_in")
                to__ = row.get("time_out")
                absence = row.get("category", "") in ("Vacances", "Maladie")
                if ti_ is not None and to__ is not None and not absence:
                    raw_hrs = max(0.0, float(to__) - float(ti_))
                    rt_accumulated = min(8.0, rt_accumulated + raw_hrs)

                # Add / Remove buttons for each line
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("➕ Ajouter une ligne", key=f"add_{idx}"):
                        new_row = _blank_row(d)
                        if row.get("time_out") is not None:
                            new_row["time_in"] = row["time_out"]
                        rows.insert(idx + 1, new_row)
                        st.rerun()
                with c2:
                    if n_lines > 1:
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

    # Build breakdown by category
    from collections import defaultdict
    breakdown: dict = defaultdict(float)
    for row in rows:
        ti  = row.get("time_in")
        to_ = row.get("time_out")
        if ti is None or to_ is None:
            continue
        meal = row.get("meal_hrs", 0.0) or 0.0
        hrs  = compute_hours(ti, to_, meal)
        if hrs <= 0:
            continue
        cat = row.get("category", "") or ""
        if not cat:
            cat = infer_category(row["date"], ti, to_)
        breakdown[cat] += hrs

    # Config: label, badge CSS class, icon
    CAT_DISPLAY = {
        "Regular Time": ("Régulier (RT)",  "badge-rt",  "🟢"),
        "Overtime":     ("Supplémentaire (OT)", "badge-ot", "🟡"),
        "Double Time":  ("Double (DT)",    "badge-dt",  "🔴"),
        "Vacances":     ("Vacances (VP)",  "badge-vp",  "🔵"),
        "Maladie":      ("Maladie (SP)",   "badge-sp",  "⚪"),
    }

    # Build breakdown HTML rows
    breakdown_rows_html = ""
    for cat, hrs in sorted(breakdown.items(), key=lambda x: list(PAY_CODES.keys()).index(x[0]) if x[0] in PAY_CODES else 99):
        label, badge_cls, icon = CAT_DISPLAY.get(cat, (cat, "badge-rt", "•"))
        breakdown_rows_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:4px 8px;border-radius:6px;background:rgba(255,255,255,0.5);
                    margin-bottom:4px;">
            <span style="font-size:0.85rem;color:#334;">{icon} {label}</span>
            <span class="hours-display" style="font-size:1rem;">{hrs:.2f} h</span>
        </div>"""

    st.markdown("---")

    # Summary box
    with st.container():
        st.markdown(f"""
        <div class="submit-section">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
                <span style="font-size:1rem;font-weight:600;color:#1a3a5c;">Total semaine</span>
                <span class="hours-display">{total_hours:.2f} h</span>
            </div>
            {breakdown_rows_html}
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


# ─────────────────────────── Row renderer ────────────────────────────────────

def _render_time_timeline(d: date, time_in: float, time_out: float, meal_hrs: float):
    """
    Renders a compact visual 24h timeline showing when the shift falls,
    color-coded by RT / OT / DT zone. Read-only, purely informational.
    """
    wd = d.weekday()  # Mon=0 … Sun=6

    # Build color zones for this day type
    # Each zone: (start_h, end_h, color, label)
    if wd == 6:  # Sunday — all DT
        zones = [(0, 24, "#d63031", "DT")]
    elif wd == 5:  # Saturday — all OT
        zones = [(0, 24, "#e07b00", "OT")]
    else:  # Weekday
        zones = [
            (0,  6,  "#d63031", "DT"),
            (6,  8,  "#e07b00", "OT"),
            (8,  17, "#27ae60", "RT"),
            (17, 23, "#e07b00", "OT"),
            (23, 24, "#d63031", "DT"),
        ]

    # Build SVG bar — 24h = 480px wide, 28px tall
    W, H = 480, 28
    bars_svg = ""
    labels_svg = ""

    for (zh, zend, color, zlabel) in zones:
        x = zh / 24 * W
        w = (zend - zh) / 24 * W
        bars_svg += f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="{H}" fill="{color}" opacity="0.25"/>'

    # Hour tick marks every 6h
    for h in [0, 6, 8, 12, 17, 23, 24]:
        x = h / 24 * W
        label = f"{h:02d}h"
        bars_svg += f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}" stroke="#555" stroke-width="0.7" stroke-dasharray="3,2"/>'
        if h < 24:
            bars_svg += f'<text x="{x+2:.1f}" y="10" font-size="7" fill="#555">{label}</text>'

    # Shift overlay
    ti_x  = time_in  / 24 * W
    to_x  = time_out / 24 * W
    shift_w = max(to_x - ti_x, 2)

    bars_svg += (
        f'<rect x="{ti_x:.1f}" y="4" width="{shift_w:.1f}" height="{H-8}" '
        f'rx="3" fill="#2d6be4" opacity="0.85"/>'
    )

    # Meal break marker
    if meal_hrs > 0:
        mid = (time_in + time_out) / 2
        mx = mid / 24 * W
        bars_svg += (
            f'<rect x="{mx-2:.1f}" y="4" width="4" height="{H-8}" '
            f'rx="1" fill="white" opacity="0.7"/>'
        )

    # In/Out labels on the bar
    in_label  = f"{int(time_in):02d}:{int(round((time_in  % 1)*60)):02d}"
    out_label = f"{int(time_out):02d}:{int(round((time_out % 1)*60)):02d}"
    bars_svg += (
        f'<text x="{ti_x+3:.1f}" y="{H//2+4}" font-size="8" font-weight="bold" fill="white">{in_label}</text>'
        f'<text x="{to_x-28:.1f}" y="{H//2+4}" font-size="8" font-weight="bold" fill="white">{out_label}</text>'
    )

    svg = f"""
    <svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;max-width:{W}px;height:{H}px;border-radius:4px;
                background:#1e2533;display:block;margin:4px 0 8px 0;">
      {bars_svg}
    </svg>
    <div style="display:flex;gap:12px;font-size:0.7rem;color:#888;margin-bottom:6px;">
      <span><span style="display:inline-block;width:10px;height:10px;background:#27ae60;opacity:0.7;border-radius:2px;"></span> RT 08–17h</span>
      <span><span style="display:inline-block;width:10px;height:10px;background:#e07b00;opacity:0.7;border-radius:2px;"></span> OT 06–08h / 17–23h</span>
      <span><span style="display:inline-block;width:10px;height:10px;background:#d63031;opacity:0.7;border-radius:2px;"></span> DT nuit / dim.</span>
      <span><span style="display:inline-block;width:10px;height:10px;background:#2d6be4;opacity:0.9;border-radius:2px;"></span> Shift</span>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def _render_row(idx: int, row: dict, wo_labels: list, wo_by_label: dict, d: date, emp_num: str = "", rt_already: float = 0.0):
    """Render all inputs for a single time-entry row, mutating `row` in place."""

    # Louis Lauzon (FW688) is part-time — no automatic daily OT cap
    DAILY_OT_EXEMPT = {"FW688"}
    apply_daily_cap = emp_num not in DAILY_OT_EXEMPT

    # Use stable uid so widget state survives row insertions/deletions
    uid = row.get("uid", str(idx))
    is_readonly = row.get("deja_bms", False)

    # ── Read-only view for already-submitted rows ─────────────────
    if is_readonly:
        ti  = row.get("time_in")
        to_ = row.get("time_out")
        meal = row.get("meal_hrs", 0.0) or 0.0

        # Convert to float if stored as string (from Google Sheets)
        def _to_float(v):
            if v is None: return None
            try:
                s = str(v).strip()
                if ":" in s:
                    h, m = s.split(":")
                    return int(h) + int(m) / 60.0
                return float(s) if s else None
            except Exception:
                return None

        ti  = _to_float(ti)
        to_ = _to_float(to_)

        hrs  = compute_hours(ti, to_, float(meal))
        cat  = row.get("category", "")
        pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))

        badge_map = {
            "Regular Time": "🟢 RT", "Overtime": "🟡 OT",
            "Double Time":  "🔴 DT", "Vacances": "🔵 VP", "Maladie": "⚪ SP",
        }
        badge = badge_map.get(cat, cat or "—")

        def _fmt(h):
            if h is None: return "—"
            return f"{int(h):02d}:{int(round((h % 1) * 60)):02d}"

        meal_txt = f" | 🍽️ {float(meal):.1f}h" if float(meal) > 0 else ""
        wo_txt   = row.get('order_ref', '') or row.get('wo_interne', '') or '—'
        comm_txt = row.get('commentaire', '') or ''

        st.markdown(f"""
        <div style="background:#1a2a4a;border-left:3px solid #2d6be4;border-radius:6px;
                    padding:8px 14px;font-size:0.85rem;color:#c8d8f0;
                    display:flex;gap:16px;align-items:center;flex-wrap:wrap;">
            🔒&nbsp;<b style="color:#7eb8d4;">Déjà soumis</b>
            &nbsp;|&nbsp; <b>{_fmt(ti)} → {_fmt(to_)}</b>
            &nbsp;|&nbsp; <b style="color:#fff;">{hrs:.2f} h</b>
            &nbsp;|&nbsp; {badge}
            &nbsp;|&nbsp; WO: <b>{wo_txt}</b>
            {f"&nbsp;|&nbsp; {comm_txt}" if comm_txt else ""}
            {f"&nbsp;|&nbsp; {meal_txt}" if meal_txt else ""}
        </div>
        """, unsafe_allow_html=True)
        if ti is not None and to_ is not None:
            _render_time_timeline(d, ti, to_, float(meal))
        return  # no editable fields

    # ── Compact single-row layout ─────────────────────────────────
    # All fields on one line: In | Out | Absence | Job Type | Order Ref | Commentaire | BMS
    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.8, 0.8, 1.0, 1.0, 1.5, 1.5, 0.5])

    with c1:
        ti_default = "" if row["time_in"] is None else str(row["time_in"])
        time_in_str = st.text_input(
            "⏰ In", value=ti_default,
            key=f"ti_{uid}", placeholder="8.0",
            help="Heure décimale : 8.0 = 8h00, 13.5 = 13h30"
        )
    with c2:
        time_out_str = st.text_input(
            "⏰ Out", value="" if row["time_out"] is None else str(row["time_out"]),
            key=f"to_{uid}", placeholder="17.0",
        )
    with c3:
        absence_options = ["—", "Vacances", "Maladie"]
        current_cat = row.get("category", "")
        absence_idx = absence_options.index(current_cat) if current_cat in ("Vacances", "Maladie") else 0
        absence_sel = st.selectbox(
            "Absence", absence_options, index=absence_idx, key=f"cat_{uid}",
            help="RT/OT/DT calculés automatiquement"
        )

    # Parse times first so we can set job_type default
    def _parse_time(s):
        s = s.strip().replace(",", ".")
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    ti  = _parse_time(time_in_str)
    to_ = _parse_time(time_out_str)

    if absence_sel in ("Vacances", "Maladie"):
        cat  = absence_sel
        meal = 0.0
        row["meal_hrs"] = 0.0
    elif ti is not None and to_ is not None:
        cat  = infer_category(d, ti, to_)
        meal = 0.0
        # Override to OT if daily cap already reached by previous lines
        if apply_daily_cap and rt_already >= 8.0 and cat == "Regular Time":
            cat = "Overtime"
    else:
        cat  = infer_category(d, None, None)
        meal = 0.0

    hrs = compute_hours(ti, to_, meal)
    is_absence = cat in ("Vacances", "Maladie")

    job_type       = row.get("job_type", "Job Client")
    trans_type     = row.get("trans_type", "WO")
    order_ref      = row.get("order_ref", "")
    wo_interne_sel = row.get("wo_interne", "")

    with c4:
        if not is_absence:
            job_type = st.selectbox(
                "Type", ["Job Client", "WO Interne", "PM"],
                index=["Job Client", "WO Interne", "PM"].index(job_type)
                      if job_type in ["Job Client", "WO Interne", "PM"] else 0,
                key=f"jt_{uid}",
            )
            trans_type = "PM" if job_type == "PM" else "WO"
        else:
            st.markdown("<div style='padding-top:28px;font-size:0.75rem;color:#888;'>🏖️ Absence</div>",
                        unsafe_allow_html=True)

    with c5:
        if not is_absence:
            if job_type == "WO Interne":
                try:
                    wo_idx = wo_labels.index(wo_interne_sel) + 1
                except ValueError:
                    wo_idx = 0
                wo_sel = st.selectbox("WO Interne", ["— choisir —"] + wo_labels,
                                      index=wo_idx, key=f"wo_{uid}")
                order_ref      = wo_by_label.get(wo_sel, "") if wo_sel != "— choisir —" else ""
                wo_interne_sel = wo_sel if wo_sel != "— choisir —" else ""
            else:
                order_ref = st.text_input("Order Ref", value=order_ref,
                                          key=f"or_{uid}", placeholder="Ex: 345924")
                wo_interne_sel = ""
        else:
            order_ref = ""
            wo_interne_sel = ""

    with c6:
        commentaire = st.text_input("Commentaire", value=row.get("commentaire", ""),
                                    key=f"cm_{uid}", placeholder="Optionnel")

    with c7:
        st.markdown("<div style='font-size:0.72rem;color:#888;margin-bottom:4px;'>BMS</div>", unsafe_allow_html=True)
        deja = st.checkbox("✓", value=row.get("deja_bms", False), key=f"bms_{uid}",
                           help="Déjà entré dans BMS")

    # ── Auto-computed info bar ────────────────────────────────────
    if ti is not None and to_ is not None:
        pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
        badge_map = {
            "Regular Time": "🟢 RT", "Overtime": "🟡 OT",
            "Double Time":  "🔴 DT", "Vacances": "🔵 VP", "Maladie": "⚪ SP",
        }
        badge = badge_map.get(cat, cat)
        meal_txt = f"  |  🍽️ {meal:.1f}h repas" if meal > 0 else ""
        st.markdown(
            f'<div style="font-size:0.78rem;color:#7eb8d4;padding:2px 0 6px 2px;">'
            f'<b>{badge}</b> &nbsp;·&nbsp; {hrs:.2f} h &nbsp;·&nbsp; '
            f'Pay: {pay_id}/{pay_type}{meal_txt}</div>',
            unsafe_allow_html=True
        )

    # ── Detect mixed RT/OT/DT zones in the shift ─────────────────
    def _compute_zone_split(d: date, ti: float, to_: float) -> list[dict]:
        wd = d.weekday()
        if wd == 6:
            boundaries = [(0, 24, "Double Time")]
        elif wd == 5:
            boundaries = [(0, 24, "Overtime")]
        else:
            boundaries = [
                (0,  6,  "Double Time"),
                (6,  8,  "Overtime"),
                (8,  17, "Regular Time"),
                (17, 23, "Overtime"),
                (23, 24, "Double Time"),
            ]

        # Build raw segments by time zone
        segments = []
        for zstart, zend, zcat in boundaries:
            overlap_start = max(ti, zstart)
            overlap_end   = min(to_, zend)
            if overlap_end > overlap_start:
                segments.append({
                    "time_in":  overlap_start,
                    "time_out": overlap_end,
                    "category": zcat,
                    "hours":    round(overlap_end - overlap_start, 4),
                })

        # Apply daily 8h cap — hours beyond 8h total become OT
        # (only on weekdays, and only for non-exempt employees)
        if apply_daily_cap and wd < 5:
            DAILY_RT_CAP = 8.0
            rt_consumed = rt_already  # ← account for previous lines in same day
            capped = []
            for seg in segments:
                if seg["category"] != "Regular Time":
                    capped.append(seg)
                    continue
                remaining_rt = max(0.0, DAILY_RT_CAP - rt_consumed)
                if remaining_rt <= 0:
                    # All RT becomes OT
                    capped.append({**seg, "category": "Overtime"})
                elif seg["hours"] > remaining_rt:
                    # Split: first part RT, rest OT
                    split_point = seg["time_in"] + remaining_rt
                    capped.append({
                        "time_in":  seg["time_in"],
                        "time_out": split_point,
                        "category": "Regular Time",
                        "hours":    round(remaining_rt, 4),
                    })
                    capped.append({
                        "time_in":  split_point,
                        "time_out": seg["time_out"],
                        "category": "Overtime",
                        "hours":    round(seg["hours"] - remaining_rt, 4),
                    })
                    rt_consumed += remaining_rt
                else:
                    capped.append(seg)
                    rt_consumed += seg["hours"]
            segments = capped

        return segments

    split_triggered = False
    if ti is not None and to_ is not None and not is_absence and d.weekday() < 5:
        segments = _compute_zone_split(d, ti, to_)
        cats_in_shift = {s["category"] for s in segments}
        has_mixed = len(cats_in_shift) > 1
        ot_hrs = sum(s["hours"] for s in segments if s["category"] == "Overtime")
        dt_hrs = sum(s["hours"] for s in segments if s["category"] == "Double Time")
        outside_hrs = round(ot_hrs + dt_hrs, 2)

        # Also trigger if daily cap was applied (rt_already >= 8h, whole line becomes OT)
        daily_cap_full = apply_daily_cap and rt_already >= 8.0 and not has_mixed

        if (has_mixed and outside_hrs > 0) or daily_cap_full:
            def _fmt_h(h): return f"{h:.2f}h".rstrip("0").rstrip(".")

            # Check if it's purely a daily cap OT (within normal hours)
            daily_cap_ot = daily_cap_full or (apply_daily_cap and any(
                s["category"] == "Overtime" and 8 <= s["time_in"] < 17
                for s in segments
            ))

            if daily_cap_ot:
                rt_hrs = sum(s["hours"] for s in segments if s["category"] == "Regular Time")
                ot_only = round(sum(s["hours"] for s in segments if s["category"] == "Overtime"), 2)
                if rt_hrs > 0:
                    msg = f"ℹ️ Cap quotidien 8h atteint — **{_fmt_h(rt_hrs)}h RT** + **{_fmt_h(ot_only)}h OT** seront créés automatiquement."
                else:
                    msg = f"ℹ️ Cap quotidien 8h déjà atteint — cette ligne (**{_fmt_h(ot_only)}h**) sera en **OT** automatiquement."
                st.info(msg)
                row["_split_segments"] = segments
                row["_client_requis"]  = True
                split_triggered = True
            else:
                st.warning(
                    f"⚠️ Ce shift contient **{_fmt_h(outside_hrs)}** en dehors des heures "
                    f"régulières (08:00–17:00). **Le client a-t-il demandé de travailler "
                    f"en dehors des heures normales ?**"
                )
                col_oui, col_non = st.columns([1, 1])
                with col_oui:
                    if st.button("✅ Oui — Requis client", key=f"split_oui_{uid}"):
                        st.session_state[f"split_confirm_{uid}"] = "oui"
                        st.rerun()
                with col_non:
                    if st.button("❌ Non — Garder une seule ligne", key=f"split_non_{uid}"):
                        st.session_state[f"split_confirm_{uid}"] = "non"
                        st.rerun()

                confirmed = st.session_state.get(f"split_confirm_{uid}")
                if confirmed == "oui":
                    st.success(
                        f"✅ Requis client confirmé — {len(segments)} ligne(s) seront créées "
                        f"automatiquement à la soumission."
                    )
                    row["_split_segments"] = segments
                    row["_client_requis"]  = True
                    split_triggered = True
                elif confirmed == "non":
                    st.info("Une seule ligne sera soumise en OT.")
                    row["_split_segments"] = None
                    row["_client_requis"]  = False
        else:
            row["_split_segments"] = None
            row["_client_requis"]  = False

    # ── Visual RT/OT/DT timeline (compact, shown below the row) ──
    if ti is not None and to_ is not None and not is_absence:
        _render_time_timeline(d, ti, to_, meal)

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
    """Convert internal row dicts to the JSON format bms_watcher.py expects.
    If a row has _split_segments (client-requested OT), expands into multiple lines.
    """
    MOIS_EN_U = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",
                 7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}

    def _to_float(v) -> float | None:
        if v is None: return None
        try:
            s = str(v).strip()
            if ":" in s:
                h, m = s.split(":")
                return int(h) + int(m) / 60.0
            return float(s.replace(",", ".")) if s else None
        except Exception:
            return None

    out = []
    for row in rows:
        d: date = _coerce_date(row["date"])
        ti  = _to_float(row.get("time_in"))
        to_ = _to_float(row.get("time_out"))
        if ti is None or to_ is None:
            continue

        segments = row.get("_split_segments")
        client_requis = row.get("_client_requis", False)

        if segments and client_requis:
            for seg in segments:
                cat = seg["category"]
                pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
                out.append({
                    "date":           f"{d.day:02d}-{MOIS_EN_U[d.month]}-{d.year}",
                    "heures":         round(seg["hours"], 2),
                    "time_in":        decimal_to_hhmm(seg["time_in"]),
                    "time_out":       decimal_to_hhmm(seg["time_out"]),
                    "pay_id":         pay_id,
                    "pay_type":       pay_type,
                    "trans_type":     row.get("trans_type", "WO"),
                    "order_ref":      row.get("order_ref", ""),
                    "meal_hrs":       0.0,
                    "commentaire":    row.get("commentaire", ""),
                    "client_requis":  cat in ("Overtime", "Double Time"),
                    "deja_bms":       row.get("deja_bms", False),
                })
        else:
            hrs  = compute_hours(ti, to_, 0.0)
            cat  = row.get("category", "Regular Time") or "Regular Time"
            pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
            out.append({
                "date":          f"{d.day:02d}-{MOIS_EN_U[d.month]}-{d.year}",
                "heures":        hrs,
                "time_in":       decimal_to_hhmm(ti),
                "time_out":      decimal_to_hhmm(to_),
                "pay_id":        pay_id,
                "pay_type":      pay_type,
                "trans_type":    row.get("trans_type", "WO"),
                "order_ref":     row.get("order_ref", ""),
                "meal_hrs":      0.0,
                "commentaire":   row.get("commentaire", ""),
                "client_requis": False,
                "deja_bms":      row.get("deja_bms", False),
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
