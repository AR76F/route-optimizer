"""
timesheet.py — BMS Timesheet (Streamlit page)
"""

import os
import json
import math
import streamlit as st
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ONEDRIVE_FOLDER = os.environ.get(
    "ONEDRIVE_FOLDER",
    str(Path.home() / "OneDrive - Cummins" / "FeuilleDeTemps"),
)
WO_JSON_URL = os.environ.get("WO_JSON_URL", "")
TZ = ZoneInfo("America/Toronto")

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

PAY_CODES = {
    "Regular Time":       ("RT", "RT"),
    "Overtime":           ("OT", "OT"),
    "Double Time":        ("DT", "DT"),
    "Vacances":           ("RT", "VP"),
    "Maladie":            ("RT", "SP"),
    "Férié":              ("RT", "HD"),
    "Heures en banque":   ("RT", "BTO"),
    "OT en banque":       ("OT", "OBTI"),
    "DT en banque":       ("DT", "DBTI"),
}

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

def _pay_periods_around(ref: date):
    delta = (ref.weekday() + 2) % 7
    sat = ref - timedelta(days=delta)
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
    delta = (5 - ref.weekday()) % 7
    end = ref + timedelta(days=delta)
    return end - timedelta(days=6), end

def _coerce_date(v) -> date:
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

def infer_category(d, time_in: float, time_out: float) -> str:
    d = _coerce_date(d)
    wd = d.weekday()
    if wd == 6:
        return "Double Time"
    if wd == 5:
        return "Overtime"
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

def decimal_to_hhmm(h: float) -> str:
    if h is None:
        return ""
    hh = int(h)
    mm = int(round((h - hh) * 60))
    return f"{hh:02d}:{mm:02d}"

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

def _get_gsheet_client():
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

def submit_timesheet(emp_num: str, emp_nom: str, periode_fin: date, rows: list[dict]) -> tuple[bool, str]:
    if not rows:
        return False, "Aucune ligne à soumettre."
    periode_str = fmt_period(periode_fin) if hasattr(periode_fin, 'day') else str(periode_fin)
    soumis_le   = datetime.now(TZ).isoformat()
    errors      = []
    try:
        ws = _get_sheet("Soumissions")
        if ws:
            new_rows = []
            for r in rows:
                new_rows.append([
                    str(r.get("date", "")),
                    str(emp_num),
                    str(emp_nom),
                    str(periode_str),
                    str(soumis_le),
                    str(r.get("time_in", "")),
                    str(r.get("time_out", "")),
                    str(r.get("heures", "")),
                    str(r.get("pay_id", "")),
                    str(r.get("pay_type", "")),
                    str(r.get("trans_type", "")),
                    str(r.get("order_ref", "")),
                    str(r.get("meal_hrs", "")),
                    str(r.get("commentaire", "")),
                    str(r.get("pay_type", "")),
                    "oui" if r.get("deja_bms", False) else "",
                ])
            body = {"values": new_rows}
            ws.spreadsheet.values_append(
                "Soumissions",
                params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
                body=body
            )
        else:
            detail = st.session_state.get("_gsheet_error", "raison inconnue")
            errors.append(f"Google Sheets non disponible — {detail}")
    except Exception as e:
        import traceback
        st.session_state["_gsheet_submit_error"] = traceback.format_exc()
        errors.append(f"Google Sheets: {e}")
    try:
        def _json_serial(obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
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
            json.dump(payload, f, ensure_ascii=False, indent=2, default=_json_serial)
    except Exception as e:
        errors.append(f"OneDrive: {e}")
    if len(errors) == 2:
        return False, " | ".join(errors)
    elif len(errors) == 1:
        return True, f"Soumis avec avertissement : {errors[0]}"
    return True, f"{emp_num}_{periode_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def load_week_from_gsheet(emp_num: str, p_start: date, p_end: date) -> list[dict] | None:
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
                    h, m = s.split(":")
                    return int(h) + int(m) / 60.0
                return float(s.replace(",", "."))
            except Exception:
                return None
        cat_map = {
            "RT": "Regular Time", "OT": "Overtime", "DT": "Double Time",
            "VP": "Vacances", "SP": "Maladie", "HD": "Férié",
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

def _blank_row(d: date) -> dict:
    import uuid
    return {
        "date":        d,
        "uid":         str(uuid.uuid4())[:8],
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
.day-card { background: #f8fafd; border: 1px solid #e2eaf5; border-left: 4px solid #2d6be4; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; }
.day-card.weekend-sat { border-left-color: #e07b00; background: #fffbf5; }
.day-card.weekend-sun { border-left-color: #d63031; background: #fff5f5; }
.day-card.deja-bms    { opacity: 0.55; }
.day-label { font-size: 0.78rem; font-weight: 600; color: #4a6fa5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-family: 'DM Mono', monospace; }
.day-label.sat { color: #e07b00; }
.day-label.sun { color: #d63031; }
.badge-rt  { background:#dff0d8; color:#2d6a2d; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-ot  { background:#fff3cd; color:#856404; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-dt  { background:#f8d7da; color:#721c24; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-vp  { background:#d1ecf1; color:#0c5460; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-sp  { background:#e2e3e5; color:#383d41; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.hours-display { font-family: 'DM Mono', monospace; font-size: 1.1rem; font-weight: 500; color: #1a3a5c; }
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

/* Bouton supprimer ligne — rouge plein, bien visible sur mobile */
.btn-remove > button {
    background: #c0392b !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.9rem !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}
.btn-remove > button:hover {
    background: #96281b !important;
}

/* Bannière de confirmation split — bien visible, fond coloré */
.split-banner {
    background: #fff3cd;
    border: 2px solid #f0ad4e;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    font-size: 0.95rem;
    color: #333;
    font-weight: 500;
}
.split-banner-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #856404;
    margin-bottom: 0.4rem;
}
</style>
"""


def show_timesheet():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="ts-header">
        <div>
            <h1>⏱ Feuille de temps BMS</h1>
            <div class="subtitle">Succursale Z8 · Cummins Eastern Canada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    wo_list = load_wo_interne()
    wo_labels = [f"{desc}  ({no})" for desc, no in wo_list]
    wo_by_label = {f"{desc}  ({no})": no for desc, no in wo_list}

    with st.sidebar:
        st.markdown("### 👤 Employé")
        tech_labels = [f"{nom}  ({num})" for nom, num in TECHNICIANS]
        url_emp = st.query_params.get("emp", "").strip().upper()
        default_idx = 0
        if url_emp:
            for i, (nom, num) in enumerate(TECHNICIANS):
                if num.upper() == url_emp:
                    default_idx = i
                    break
        sel_tech = st.selectbox("Nom", tech_labels, index=default_idx, key="sel_tech")
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

    state_key = f"rows_{emp_num}_{p_end.isoformat()}"
    if state_key not in st.session_state:
        loaded = load_week_from_gsheet(emp_num, p_start, p_end)
        if loaded:
            st.session_state[state_key] = loaded
            st.session_state[f"loaded_{state_key}"] = True
        else:
            st.session_state[state_key] = default_rows(p_start, p_end)
    rows: list[dict] = st.session_state[state_key]

    col_load, col_info = st.columns([1, 3])
    with col_load:
        if st.button("🔄 Rafraîchir", key="load_week_btn",
                     help="Recharger les données depuis Google Sheets"):
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

    st.markdown(f"**Saisie des heures — {emp_nom}**")

    total_hours = 0.0
    rows_to_delete = []

    from itertools import groupby
    rows_by_day = []
    for d_key, group in groupby(enumerate(rows), key=lambda x: _coerce_date(x[1]["date"])):
        rows_by_day.append((_coerce_date(d_key), list(group)))

    for d, day_rows in rows_by_day:
        wd = d.weekday()

        day_total = 0.0
        for _, row in day_rows:
            h = compute_hours(row.get("time_in"), row.get("time_out"), 0.0)
            day_total += h
            total_hours += h

        from collections import defaultdict
        hrs_by_cat = defaultdict(float)

        def _parse_time_raw(s) -> float | None:
            import re
            if not s:
                return None
            s = str(s).strip().lower().replace(",", ".")
            if not s:
                return None
            m = re.match(r'^(\d{1,2})h(\d{0,2})$', s)
            if m:
                h = int(m.group(1)); mins = int(m.group(2)) if m.group(2) else 0
                return round(h + mins / 60.0, 1)
            if re.match(r'^\d{1,2}:\d{2}$', s):
                h, mins = s.split(":")
                return round(int(h) + int(mins) / 60.0, 1)
            try:
                return round(float(s), 1)
            except Exception:
                return None

        for _, row in day_rows:
            uid = row.get("uid", "")
            absence_live = st.session_state.get(f"cat_{uid}", "")
            ti_raw = st.session_state.get(f"ti_{uid}", "")
            to_raw = st.session_state.get(f"to_{uid}", "")
            ti  = _parse_time_raw(ti_raw)  if ti_raw  else row.get("time_in")
            to_ = _parse_time_raw(to_raw) if to_raw else row.get("time_out")
            is_abs_live = absence_live in ("Vacances", "Maladie", "Férié", "Heures en banque")
            cat = absence_live if is_abs_live else (row.get("category", "") or "")
            if is_abs_live and ti is not None and to_ is not None:
                hrs_by_cat[cat] += compute_hours(ti, to_, 0.0)
                continue
            segs_ss   = st.session_state.get(f"split_segments_{uid}")
            requis_ss = st.session_state.get(f"split_client_requis_{uid}", False)
            active_segs = segs_ss if (segs_ss and requis_ss) else row.get("_split_segments")
            use_split   = bool(active_segs) and (requis_ss or row.get("_client_requis", False))
            if use_split:
                for seg in active_segs:
                    hrs_by_cat[seg["category"]] += seg["hours"]
            elif ti is not None and to_ is not None:
                effective_cat = cat if cat else infer_category(row["date"], ti, to_)
                hrs_by_cat[effective_cat] += compute_hours(ti, to_, 0.0)

        badge_map = {
            "Regular Time":     ("🟢", "RT"),
            "Overtime":         ("🟡", "OT"),
            "Double Time":      ("🔴", "DT"),
            "Vacances":         ("🔵", "VP"),
            "Maladie":          ("⚪", "SP"),
            "Férié":            ("🟣", "HD"),
            "Heures en banque": ("🏦", "BTO"),
            "OT en banque":     ("🏦", "OBTI"),
            "DT en banque":     ("🏦", "DBTI"),
        }
        cat_order = ["Regular Time", "Overtime", "Double Time", "Vacances", "Maladie", "Férié",
                     "Heures en banque", "OT en banque", "DT en banque"]

        if hrs_by_cat:
            parts = []
            for cat in cat_order:
                if cat in hrs_by_cat:
                    icon, label = badge_map.get(cat, ("•", cat))
                    parts.append(f"{icon} {hrs_by_cat[cat]:.2f}h {label}")
            title_hrs = "  ·  ".join(parts)
        else:
            title_hrs = "—"

        day_str    = fmt_date_fr(d)
        n_lines    = len(day_rows)
        line_label = f"  ({n_lines} lignes)" if n_lines > 1 else ""

        exp_key = f"exp_{state_key}_{d.isoformat()}"
        if exp_key not in st.session_state:
            st.session_state[exp_key] = (day_total == 0 and wd < 5)

        with st.expander(f"{day_str}   {title_hrs}{line_label}",
                         expanded=st.session_state[exp_key]):

            rt_accumulated = 0.0
            last_time_out  = None

            for list_pos, (idx, row) in enumerate(day_rows):

                if list_pos > 0:
                    st.markdown(
                        "<hr style='margin:2px 0 4px 0;border:none;border-top:1px solid #2d3a4a;'>",
                        unsafe_allow_html=True
                    )

                # ── Bouton supprimer — au-dessus de la ligne, bien visible sur mobile ──
                if n_lines > 1 and not row.get("deja_bms", False):
                    # Calculer les heures de cette ligne pour l'afficher dans le bouton
                    _ti_del  = row.get("time_in")
                    _to_del  = row.get("time_out")
                    _hrs_del = compute_hours(_ti_del, _to_del, 0.0)
                    if _ti_del is not None and _to_del is not None and _hrs_del > 0:
                        _ti_str  = decimal_to_hhmm(float(_ti_del))  if _ti_del  is not None else "?"
                        _to_str  = decimal_to_hhmm(float(_to_del)) if _to_del is not None else "?"
                        _del_lbl = f"🗑️ Supprimer cette ligne ({_ti_str}→{_to_str}, {_hrs_del:.2f}h)"
                    else:
                        _del_lbl = "🗑️ Supprimer cette ligne (vide)"
                    st.markdown('<div class="btn-remove">', unsafe_allow_html=True)
                    if st.button(_del_lbl, key=f"del_{idx}"):
                        rows_to_delete.append(idx)
                    st.markdown('</div>', unsafe_allow_html=True)

                _render_row(idx, row, wo_labels, wo_by_label, d, emp_num,
                            rt_already=rt_accumulated)

                ti_ = row.get("time_in")
                to__ = row.get("time_out")
                absence = row.get("category", "") in ("Vacances", "Maladie", "Férié", "Heures en banque")
                if ti_ is not None and to__ is not None and not absence:
                    raw_hrs = max(0.0, float(to__) - float(ti_))
                    rt_accumulated = min(8.0, rt_accumulated + raw_hrs)
                if row.get("time_out") is not None:
                    last_time_out = row["time_out"]

            st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
            col_add, col_reset_day = st.columns([2, 1])
            with col_add:
                if st.button("➕ Ajouter une ligne", key=f"add_day_{d.isoformat()}"):
                    new_row = _blank_row(d)
                    if last_time_out is not None:
                        new_row["time_in"] = last_time_out
                    last_idx = day_rows[-1][0]
                    rows.insert(last_idx + 1, new_row)
                    st.rerun()
            with col_reset_day:
                if st.button("🗑️ Réinitialiser", key=f"reset_day_{d.isoformat()}",
                             help="Effacer toutes les lignes de cette journée"):
                    # Retirer toutes les lignes de ce jour et les remplacer par une ligne vide
                    idxs_to_remove = [i for i, (gi, r) in enumerate(day_rows)]
                    global_idxs = [gi for gi, r in day_rows]
                    for gi in sorted(global_idxs, reverse=True):
                        rows.pop(gi)
                    # Vider session_state split pour ces lignes
                    for _, r in day_rows:
                        uid_r = r.get("uid", "")
                        for _k in (f"split_confirm_{uid_r}", f"split_segments_{uid_r}",
                                   f"split_client_requis_{uid_r}"):
                            st.session_state.pop(_k, None)
                    # Insérer une ligne vide à la bonne position
                    insert_pos = global_idxs[0]
                    rows.insert(insert_pos, _blank_row(d))
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if rows_to_delete:
        for i in sorted(rows_to_delete, reverse=True):
            rows.pop(i)
        st.rerun()

    # Summary + Submit
    from collections import defaultdict
    breakdown: dict = defaultdict(float)
    for row in rows:
        ti  = row.get("time_in")
        to_ = row.get("time_out")
        if ti is None or to_ is None:
            continue
        meal = row.get("meal_hrs", 0.0) or 0.0
        uid = row.get("uid", "")
        segs_ss   = st.session_state.get(f"split_segments_{uid}")
        requis_ss = st.session_state.get(f"split_client_requis_{uid}", False)
        active_segs = segs_ss if segs_ss and requis_ss else row.get("_split_segments")
        use_split = bool(active_segs) and (requis_ss or row.get("_client_requis", False))
        if use_split:
            for seg in active_segs:
                breakdown[seg["category"]] += seg["hours"]
        else:
            hrs = compute_hours(ti, to_, meal)
            if hrs <= 0:
                continue
            cat = row.get("category", "") or ""
            if not cat:
                cat = infer_category(row["date"], ti, to_)
            breakdown[cat] += hrs

    CAT_DISPLAY = {
        "Regular Time":     ("Régulier (RT)",           "badge-rt", "🟢"),
        "Overtime":         ("Supplémentaire (OT)",     "badge-ot", "🟡"),
        "Double Time":      ("Double (DT)",             "badge-dt", "🔴"),
        "Vacances":         ("Vacances (VP)",           "badge-vp", "🔵"),
        "Maladie":          ("Maladie (SP)",            "badge-sp", "⚪"),
        "Férié":            ("Férié (HD)",              "badge-hd", "🟣"),
        "Heures en banque": ("Banque — retraits (BTO)", "badge-sp", "🏦"),
        "OT en banque":     ("OT en banque (OBTI)",     "badge-ot", "🏦"),
        "DT en banque":     ("DT en banque (DBTI)",     "badge-dt", "🏦"),
    }

    breakdown_rows_html = ""
    for cat, hrs in sorted(breakdown.items(),
                           key=lambda x: list(PAY_CODES.keys()).index(x[0]) if x[0] in PAY_CODES else 99):
        label, badge_cls, icon = CAT_DISPLAY.get(cat, (cat, "badge-rt", "•"))
        breakdown_rows_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:4px 8px;border-radius:6px;background:rgba(255,255,255,0.5);
                    margin-bottom:4px;">
            <span style="font-size:0.85rem;color:#334;">{icon} {label}</span>
            <span class="hours-display" style="font-size:1rem;">{hrs:.2f} h</span>
        </div>"""

    st.markdown("---")
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

    with st.expander("🔍 Aperçu JSON (bms_watcher)"):
        preview_rows = _build_json_rows(rows)
        st.json({
            "employe_num": emp_num,
            "employe_nom": emp_nom,
            "periode_fin": fmt_period(p_end),
            "lignes": preview_rows,
        })

    col_sub, _ = st.columns([2, 1])
    with col_sub:
        if st.button("📤 Soumettre à BMS Watcher", type="primary", key="submit_btn"):
            json_rows = _build_json_rows(rows)
            valid = [r for r in json_rows if r.get("heures", 0) > 0]
            if not valid:
                st.warning("⚠️ Aucune ligne avec des heures à soumettre.")
            else:
                ok, msg = submit_timesheet(emp_num, emp_nom, p_end, valid)
                if ok:
                    st.success(f"✅ Soumis ! ({len(valid)} ligne(s)) → {msg}")
                else:
                    st.error(f"❌ Erreur : {msg}")



def _render_time_timeline(d: date, time_in: float, time_out: float, meal_hrs: float):
    wd = d.weekday()
    if wd == 6:
        zones = [(0, 24, "#d63031", "DT")]
    elif wd == 5:
        zones = [(0, 24, "#e07b00", "OT")]
    else:
        zones = [
            (0,  6,  "#d63031", "DT"),
            (6,  8,  "#e07b00", "OT"),
            (8,  17, "#27ae60", "RT"),
            (17, 23, "#e07b00", "OT"),
            (23, 24, "#d63031", "DT"),
        ]
    W, H = 480, 28
    bars_svg = ""
    for (zh, zend, color, zlabel) in zones:
        x = zh / 24 * W
        w = (zend - zh) / 24 * W
        bars_svg += f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="{H}" fill="{color}" opacity="0.25"/>'
    for h in [0, 6, 8, 12, 17, 23, 24]:
        x = h / 24 * W
        bars_svg += f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}" stroke="#555" stroke-width="0.7" stroke-dasharray="3,2"/>'
        if h < 24:
            bars_svg += f'<text x="{x+2:.1f}" y="10" font-size="7" fill="#555">{h:02d}h</text>'
    ti_x    = time_in  / 24 * W
    to_x    = time_out / 24 * W
    shift_w = max(to_x - ti_x, 2)
    bars_svg += (
        f'<rect x="{ti_x:.1f}" y="4" width="{shift_w:.1f}" height="{H-8}" '
        f'rx="3" fill="#2d6be4" opacity="0.85"/>'
    )
    if meal_hrs > 0:
        mid = (time_in + time_out) / 2
        mx  = mid / 24 * W
        bars_svg += (
            f'<rect x="{mx-2:.1f}" y="4" width="4" height="{H-8}" '
            f'rx="1" fill="white" opacity="0.7"/>'
        )
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


def _render_row(idx: int, row: dict, wo_labels: list, wo_by_label: dict, d: date,
                emp_num: str = "", rt_already: float = 0.0):

    DAILY_OT_EXEMPT = {"FW688"}
    apply_daily_cap = emp_num not in DAILY_OT_EXEMPT

    uid         = row.get("uid", str(idx))
    is_readonly = row.get("deja_bms", False)

    # ── Read-only ─────────────────────────────────────────────────
    if is_readonly:
        ti   = row.get("time_in")
        to_  = row.get("time_out")
        meal = row.get("meal_hrs", 0.0) or 0.0

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
        hrs = compute_hours(ti, to_, float(meal))
        cat = row.get("category", "")

        badge_map_ro = {
            "Regular Time": "🟢 RT", "Overtime": "🟡 OT", "Double Time": "🔴 DT",
            "Vacances": "🔵 VP",     "Maladie":  "⚪ SP",  "Férié":       "🟣 HD",
            "Heures en banque": "🏦 BTO", "OT en banque": "🏦 OBTI", "DT en banque": "🏦 DBTI",
        }
        badge    = badge_map_ro.get(cat, cat or "—")
        meal_txt = f" | 🍽️ {float(meal):.1f}h" if float(meal) > 0 else ""
        wo_txt   = row.get('order_ref', '') or row.get('wo_interne', '') or '—'
        comm_txt = row.get('commentaire', '') or ''

        def _fmt(h):
            if h is None: return "—"
            return f"{int(h):02d}:{int(round((h % 1) * 60)):02d}"

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
        return

    # ── Helpers ───────────────────────────────────────────────────
    def _fmt_h(h): return f"{h:.2f}h".rstrip("0").rstrip(".")

    def _parse_time(s) -> tuple[float | None, str | None]:
        import re
        if not s or not str(s).strip():
            return None, None
        s = str(s).strip().lower().replace(",", ".")
        val = None
        m = re.match(r'^(\d{1,2})h(\d{0,2})$', s)
        if m:
            val = int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0) / 60.0
        elif re.match(r'^\d{1,2}:\d{2}$', s):
            h, mins = s.split(":")
            val = int(h) + int(mins) / 60.0
        else:
            try:
                val = float(s)
            except ValueError:
                return None, f"Format non reconnu : «{s}». Essayez 8, 8.5, 8h30 ou 8:30."
        if val is None:
            return None, None
        if val < 0 or val > 24:
            return None, f"Heure invalide : {val:.2f}."
        rounded = round(val, 1)
        warn = None
        if abs(rounded - val) > 0.01:
            warn = f"Arrondi à {rounded:.1f}h"
        return rounded, warn

    def _apply_banque(segs, cat_from, cat_to):
        return [{**s, "category": cat_to} if s["category"] == cat_from else s for s in segs]

    def _persist_split(segs, requis=True):
        row["_split_segments"] = segs
        row["_client_requis"]  = requis
        st.session_state[f"split_segments_{uid}"]      = segs
        st.session_state[f"split_client_requis_{uid}"] = requis

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
        if apply_daily_cap and wd < 5:
            DAILY_RT_CAP = 8.0
            rt_consumed  = rt_already
            capped = []
            for seg in segments:
                if seg["category"] != "Regular Time":
                    capped.append(seg)
                    continue
                remaining_rt = max(0.0, DAILY_RT_CAP - rt_consumed)
                if remaining_rt <= 0:
                    capped.append({**seg, "category": "Overtime"})
                elif seg["hours"] > remaining_rt:
                    split_point = seg["time_in"] + remaining_rt
                    capped.append({"time_in": seg["time_in"], "time_out": split_point,
                                   "category": "Regular Time", "hours": round(remaining_rt, 4)})
                    capped.append({"time_in": split_point, "time_out": seg["time_out"],
                                   "category": "Overtime", "hours": round(seg["hours"] - remaining_rt, 4)})
                    rt_consumed += remaining_rt
                else:
                    capped.append(seg)
                    rt_consumed += seg["hours"]
            segments = capped
        return segments

    # ══════════════════════════════════════════════════════════════
    #  DÉTECTION SPLIT ANTICIPÉE — AVANT les champs de saisie
    #  Si In/Out déjà saisis et split non encore confirmé → bloquer
    # ══════════════════════════════════════════════════════════════
    ti_pre_raw = st.session_state.get(f"ti_{uid}", "")
    to_pre_raw = st.session_state.get(f"to_{uid}", "")

    def _quick_parse(s):
        import re
        if not s: return None
        s = str(s).strip().lower().replace(",", ".")
        m = re.match(r'^(\d{1,2})h(\d{0,2})$', s)
        if m:
            return round(int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0) / 60.0, 1)
        if re.match(r'^\d{1,2}:\d{2}$', s):
            h, mn = s.split(":")
            return round(int(h) + int(mn) / 60.0, 1)
        try:
            return round(float(s), 1)
        except Exception:
            return None

    ti_pre  = _quick_parse(ti_pre_raw)  if ti_pre_raw  else row.get("time_in")
    to_pre  = _quick_parse(to_pre_raw) if to_pre_raw else row.get("time_out")
    absence_pre = st.session_state.get(f"cat_{uid}", row.get("category", ""))
    is_absence_pre = absence_pre in ("Vacances", "Maladie", "Férié", "Heures en banque")

    # Persister ti/to dans le row dict AVANT tout st.stop() potentiel
    # pour que les valeurs survivent au rerun
    if ti_pre is not None:
        row["time_in"] = ti_pre
    if to_pre is not None:
        row["time_out"] = to_pre

    needs_split_confirmation = False
    _pre_segments = None

    if ti_pre is not None and to_pre is not None and not is_absence_pre:
        confirmed_pre = st.session_state.get(f"split_confirm_{uid}")
        if confirmed_pre is None:
            # Vérifier si un split est nécessaire
            if d.weekday() in (5, 6):
                is_sunday_pre  = d.weekday() == 6
                full_hrs_pre   = compute_hours(ti_pre, to_pre, 0.0)
                outside_cat    = "Double Time" if is_sunday_pre else "Overtime"
                banque_cat     = "DT en banque" if is_sunday_pre else "OT en banque"
                label_paye_pre = "DT payé" if is_sunday_pre else "OT payé"
                full_segs_pre  = [{"time_in": ti_pre, "time_out": to_pre,
                                    "category": outside_cat, "hours": round(full_hrs_pre, 4)}]
                needs_split_confirmation = True
                _pre_segments  = full_segs_pre
                _pre_is_we     = True
                _pre_sunday    = is_sunday_pre
                _pre_banque_cat = banque_cat
                _pre_label_paye = label_paye_pre
                _pre_full_hrs   = full_hrs_pre
                _pre_outside_cat = outside_cat
            elif d.weekday() < 5:
                segs_pre = _compute_zone_split(d, ti_pre, to_pre)
                cats_pre = {s["category"] for s in segs_pre}
                has_mixed_pre = len(cats_pre) > 1
                ot_pre = sum(s["hours"] for s in segs_pre if s["category"] == "Overtime")
                dt_pre = sum(s["hours"] for s in segs_pre if s["category"] == "Double Time")
                outside_pre = round(ot_pre + dt_pre, 2)
                daily_cap_full_pre = apply_daily_cap and rt_already >= 8.0 and not has_mixed_pre
                if (has_mixed_pre and outside_pre > 0) or daily_cap_full_pre:
                    needs_split_confirmation = True
                    _pre_segments   = segs_pre
                    _pre_is_we      = False
                    _pre_outside_hrs = outside_pre
                    _pre_daily_cap   = daily_cap_full_pre or (apply_daily_cap and any(
                        s["category"] == "Overtime" and 8 <= s["time_in"] < 17 for s in segs_pre))

    # ── Afficher la bannière de confirmation EN PREMIER si nécessaire ──────
    if needs_split_confirmation:
        if not _pre_is_we:
            # Weekday split
            _rt_pre = sum(s["hours"] for s in _pre_segments if s["category"] == "Regular Time")
            _ot_pre = round(sum(s["hours"] for s in _pre_segments if s["category"] == "Overtime"), 2)
            _dt_pre = round(sum(s["hours"] for s in _pre_segments if s["category"] == "Double Time"), 2)

            if _pre_daily_cap:
                if _rt_pre > 0:
                    titre  = f"⏰ Cap 8h atteint : {_fmt_h(_rt_pre)}h RT + {_fmt_h(_ot_pre)}h OT"
                else:
                    titre  = f"⏰ Cap 8h atteint : {_fmt_h(_ot_pre)}h en OT"
                detail = "Mettre le OT en banque ?"
            else:
                titre  = f"⚠️ Shift hors heures standard ({_fmt_h(_ot_pre + _dt_pre)}h hors 08–17h)"
                detail = "Le client a-t-il demandé de travailler en dehors des heures normales ?"

            st.markdown(f"""
            <div class="split-banner">
                <div class="split-banner-title">{titre}</div>
                <div>{detail}</div>
            </div>
            """, unsafe_allow_html=True)

            if _pre_daily_cap:
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("💰 OT payé", key=f"split_oui_{uid}", use_container_width=True):
                        st.session_state[f"split_confirm_{uid}"] = "paye"
                        _persist_split(_pre_segments)
                        st.rerun()
                with col_b:
                    if st.button("🏦 Mettre en banque (OBTI)", key=f"split_banque_{uid}", use_container_width=True):
                        st.session_state[f"split_confirm_{uid}"] = "banque"
                        _persist_split(_apply_banque(_pre_segments, "Overtime", "OT en banque"))
                        st.rerun()
            else:
                col_a, col_b, col_c = st.columns([1, 1, 1])
                with col_a:
                    if st.button("✅ OT payé", key=f"split_oui_{uid}", use_container_width=True):
                        st.session_state[f"split_confirm_{uid}"] = "oui"
                        _persist_split(_pre_segments)
                        st.rerun()
                with col_b:
                    if st.button("🏦 OT en banque", key=f"split_banque_{uid}", use_container_width=True):
                        st.session_state[f"split_confirm_{uid}"] = "banque"
                        _persist_split(_apply_banque(_pre_segments, "Overtime", "OT en banque"))
                        st.rerun()
                with col_c:
                    if st.button("❌ Garder RT seulement", key=f"split_non_{uid}", use_container_width=True):
                        st.session_state[f"split_confirm_{uid}"] = "non"
                        _persist_split(None, False)
                        row["category"] = "Regular Time"
                        st.rerun()
            # Bloquer le reste du rendu — l'utilisateur doit répondre d'abord
            st.stop()

        else:
            # Weekend
            st.markdown(f"""
            <div class="split-banner">
                <div class="split-banner-title">
                    ⚠️ {'Dimanche' if _pre_sunday else 'Samedi'} — {_fmt_h(_pre_full_hrs)}h en {_pre_label_paye}
                </div>
                <div>Mettre en banque ?</div>
            </div>
            """, unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_a:
                if st.button(f"💰 {_pre_label_paye}", key=f"split_oui_{uid}", use_container_width=True):
                    st.session_state[f"split_confirm_{uid}"] = "paye"
                    _persist_split(_pre_segments)
                    st.rerun()
            with col_b:
                if st.button("🏦 Mettre en banque", key=f"split_banque_{uid}", use_container_width=True):
                    st.session_state[f"split_confirm_{uid}"] = "banque"
                    _persist_split(_apply_banque(_pre_segments, _pre_outside_cat, _pre_banque_cat))
                    st.rerun()
            with col_c:
                if st.button("❌ Ne pas soumettre", key=f"split_non_{uid}", use_container_width=True):
                    st.session_state[f"split_confirm_{uid}"] = "non"
                    _persist_split(None, False)
                    st.rerun()
            st.stop()

    # ══════════════════════════════════════════════════════════════
    #  Champs de saisie normaux
    # ══════════════════════════════════════════════════════════════

    # Si une décision split a déjà été prise → heures figées
    split_decided = st.session_state.get(f"split_confirm_{uid}") is not None

    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.8, 0.8, 1.0, 1.0, 1.5, 1.5, 0.5])

    with c1:
        if split_decided:
            _ti_disp = decimal_to_hhmm(float(row["time_in"])) if row["time_in"] is not None else "—"
            st.markdown(
                f'<div style="padding-top:28px;font-size:0.9rem;color:#7eb8d4;">'
                f'🔒 <b>{_ti_disp}</b></div>',
                unsafe_allow_html=True)
            time_in_str = str(row["time_in"]) if row["time_in"] is not None else ""
        else:
            ti_default  = "" if row["time_in"] is None else str(row["time_in"])
            time_in_str = st.text_input("⏰ In", value=ti_default,
                                        key=f"ti_{uid}", placeholder="8.0",
                                        help="Heure décimale : 8.0 = 8h00, 13.5 = 13h30")
    with c2:
        if split_decided:
            _to_disp = decimal_to_hhmm(float(row["time_out"])) if row["time_out"] is not None else "—"
            st.markdown(
                f'<div style="padding-top:28px;font-size:0.9rem;color:#7eb8d4;">'
                f'🔒 <b>{_to_disp}</b></div>',
                unsafe_allow_html=True)
            time_out_str = str(row["time_out"]) if row["time_out"] is not None else ""
        else:
            time_out_str = st.text_input("⏰ Out",
                                         value="" if row["time_out"] is None else str(row["time_out"]),
                                         key=f"to_{uid}", placeholder="17.0")
    with c3:
        absence_options = ["—", "Vacances", "Maladie", "Férié", "Heures en banque"]
        current_cat  = row.get("category", "")
        absence_idx  = absence_options.index(current_cat) if current_cat in absence_options else 0
        absence_sel  = st.selectbox("Absence", absence_options, index=absence_idx,
                                    key=f"cat_{uid}", help="RT/OT/DT calculés automatiquement")

    # Message informatif si les heures sont figées
    if split_decided:
        st.caption("🔒 Heures figées — supprimez et recréez la ligne pour modifier.")

    ti_val, ti_warn = _parse_time(time_in_str)
    to_val, to_warn = _parse_time(time_out_str)
    if ti_warn: st.warning(f"⏰ In : {ti_warn}")
    if to_warn: st.warning(f"⏰ Out : {to_warn}")
    if time_in_str.strip()  and ti_val is None: st.error(f"⏰ In invalide : «{time_in_str}»")
    if time_out_str.strip() and to_val is None: st.error(f"⏰ Out invalide : «{time_out_str}»")

    ti  = ti_val
    to_ = to_val

    if absence_sel in ("Vacances", "Maladie", "Férié", "Heures en banque"):
        cat  = absence_sel
        meal = 0.0
        row["meal_hrs"] = 0.0
    elif ti is not None and to_ is not None:
        # Si l'utilisateur a choisi "Garder RT seulement" → respecter ce choix
        if st.session_state.get(f"split_confirm_{uid}") == "non":
            cat = "Regular Time"
        else:
            cat = infer_category(d, ti, to_)
            if apply_daily_cap and rt_already >= 8.0 and cat == "Regular Time":
                cat = "Overtime"
        meal = 0.0
    else:
        cat  = infer_category(d, None, None)
        meal = 0.0

    hrs        = compute_hours(ti, to_, meal)
    is_absence = cat in ("Vacances", "Maladie", "Férié", "Heures en banque")

    if is_absence:
        for _k in (f"split_confirm_{uid}", f"split_segments_{uid}", f"split_client_requis_{uid}"):
            st.session_state.pop(_k, None)
        row["_split_segments"] = None
        row["_client_requis"]  = False

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
                key=f"jt_{uid}")
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
                order_ref      = st.text_input("Order Ref", value=order_ref,
                                               key=f"or_{uid}", placeholder="Ex: 345924")
                wo_interne_sel = ""
        else:
            order_ref = ""
            wo_interne_sel = ""

    with c6:
        commentaire = st.text_input("Commentaire", value=row.get("commentaire", ""),
                                    key=f"cm_{uid}", placeholder="Optionnel")
    with c7:
        st.markdown("<div style='font-size:0.72rem;color:#888;margin-bottom:4px;'>BMS</div>",
                    unsafe_allow_html=True)
        deja = st.checkbox("✓", value=row.get("deja_bms", False), key=f"bms_{uid}",
                           help="Déjà entré dans BMS")

    # ── Info bar ──────────────────────────────────────────────────
    if ti is not None and to_ is not None:
        badge_map = {
            "Regular Time": "🟢 RT", "Overtime": "🟡 OT", "Double Time": "🔴 DT",
            "Vacances": "🔵 VP",     "Maladie":  "⚪ SP",  "Férié":       "🟣 HD",
            "Heures en banque": "🏦 BTO", "OT en banque": "🏦 OBTI", "DT en banque": "🏦 DBTI",
        }
        meal_txt    = f"  |  🍽️ {meal:.1f}h repas" if meal > 0 else ""
        segs_ss_ib  = st.session_state.get(f"split_segments_{uid}")
        requis_ss_ib= st.session_state.get(f"split_client_requis_{uid}", False)
        active_segs = segs_ss_ib if segs_ss_ib and requis_ss_ib else row.get("_split_segments")
        use_split   = bool(active_segs) and (requis_ss_ib or row.get("_client_requis", False))
        if use_split:
            parts  = [f"<b>{badge_map.get(s['category'], s['category'])}</b> {s['hours']:.2f}h"
                      for s in active_segs]
            detail = "  +  ".join(parts)
            st.markdown(
                f'<div style="font-size:0.78rem;color:#7eb8d4;padding:2px 0 6px 2px;">'
                f'Split → {detail}{meal_txt}</div>',
                unsafe_allow_html=True)
        else:
            pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
            st.markdown(
                f'<div style="font-size:0.78rem;color:#7eb8d4;padding:2px 0 6px 2px;">'
                f'<b>{badge_map.get(cat, cat)}</b> &nbsp;·&nbsp; {hrs:.2f} h &nbsp;·&nbsp;'
                f' Pay: {pay_id}/{pay_type}{meal_txt}</div>',
                unsafe_allow_html=True)

    if ti is not None and to_ is not None and not is_absence:
        _render_time_timeline(d, ti, to_, meal)

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
        d   = _coerce_date(row["date"])
        ti  = _to_float(row.get("time_in"))
        to_ = _to_float(row.get("time_out"))
        if ti is None or to_ is None:
            continue
        segments      = row.get("_split_segments")
        client_requis = row.get("_client_requis", False)
        if segments and client_requis:
            for seg in segments:
                cat = seg["category"]
                pay_id, pay_type = PAY_CODES.get(cat, ("RT", "RT"))
                out.append({
                    "date":          f"{d.day:02d}-{MOIS_EN_U[d.month]}-{d.year}",
                    "heures":        round(seg["hours"], 2),
                    "time_in":       decimal_to_hhmm(seg["time_in"]),
                    "time_out":      decimal_to_hhmm(seg["time_out"]),
                    "pay_id":        pay_id,
                    "pay_type":      pay_type,
                    "trans_type":    row.get("trans_type", "WO"),
                    "order_ref":     row.get("order_ref", ""),
                    "meal_hrs":      0.0,
                    "commentaire":   row.get("commentaire", ""),
                    "client_requis": cat in ("Overtime", "Double Time"),
                    "deja_bms":      row.get("deja_bms", False),
                })
        else:
            hrs = compute_hours(ti, to_, 0.0)
            cat = row.get("category", "Regular Time") or "Regular Time"
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


if __name__ == "__main__":
    st.set_page_config(page_title="Feuille de temps BMS", page_icon="⏱", layout="wide")
    show_timesheet()
