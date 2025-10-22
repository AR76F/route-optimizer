    # app.py
# Streamlit Route Optimizer — Home ➜ Storage ➜ Optimized Stops (≤ 25)
# Notes:
# - No filesystem writes (GitHub/Streamlit Cloud often block /mnt/data).
# - Optional Geotab integration guarded behind secrets + import.
# - Includes a "Download this script" button via inspect (no file creation needed).

import os
import sys
import inspect
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Tuple, Optional

import streamlit as st

# Third-party libs (make sure these are in your requirements.txt)
import googlemaps
import polyline
import folium
from streamlit_folium import st_folium


# ────────────────────────────────────────────────────────────────────────────────
# Optional myGeotab import (app still works if it's missing or secrets not set)
# ────────────────────────────────────────────────────────────────────────────────
GEOTAB_AVAILABLE = True
try:
    import mygeotab as myg
except Exception:
    GEOTAB_AVAILABLE = False

# ────────────────────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Route Optimizer", layout="wide")

# ────────────────────────────────────────────────────────────────────────────────
# Cummins Header (black logo + styled title)
# Supports both root and assets folder (PNG/JPG/SVG)
# ────────────────────────────────────────────────────────────────────────────────
def cummins_header():
    # Candidate logo file paths — checks in root and /assets
    CANDIDATES = [
        "Cummins_Logo.png",           # your current logo
        "Cummins_Logo.jpg",
        "Cummins_Logo.svg",
        "assets/cummins_black.svg",
        "assets/cummins_black.png",
        "assets/cummins_black.jpg",
    ]

    # Larger logo column balance
    col_logo, col_title = st.columns([1, 5], vertical_alignment="center")

    with col_logo:
        shown = False
        for path in CANDIDATES:
            if os.path.exists(path):
                try:
                    # Display the logo larger (150px width)
                    st.image(path, width=300)
                    shown = True
                    break
                except Exception:
                    pass

        if not shown:
            # Inline fallback logo (simple black “C” emblem)
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
              Domicile ➜ Entrepot ➜ Clients (MAXIMUM 25 TRAJETS) — <b>Cummins Service Fleet</b>
            </div>
            """,
            unsafe_allow_html=True
        )

# Render header
cummins_header()

# Single source of truth for START address (Geotab -> Route stops)
if "route_start" not in st.session_state:
    st.session_state.route_start = ""

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
def secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch from Streamlit secrets or environment."""
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)
        
def normalize_ca_postal(text: str) -> str:
    """Normalize 'J4G1A1' -> 'J4G 1A1, Canada' if it looks like a Canadian postal code."""
    if not text:
        return text
    t = str(text).strip().upper().replace(" ", "")
    if len(t) == 6 and t[:3].isalnum() and t[3:].isalnum():
        return f"{t[:3]} {t[3:]}, Canada"
    return text

def geocode_ll(gmaps_client: googlemaps.Client, text: str) -> Optional[Tuple[float, float, str]]:
    """
    Geocode a string with Canadian bias; return (lat, lon, formatted_address).
    Returns None if not found.
    """
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

def add_marker(mapobj, lat, lon, popup, icon=None):
    if icon is None:
        icon = folium.Icon(color="red", icon="map-marker", prefix="fa")
    folium.Marker([lat, lon], popup=popup, icon=icon).add_to(mapobj)

def recency_color(ts: Optional[str]) -> Tuple[str, str]:
    """Return (color, label) based on timestamp recency."""
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

# ────────────────────────────────────────────────────────────────────────────────
# Google Maps API key (secrets only)
# ────────────────────────────────────────────────────────────────────────────────
GOOGLE_KEY = secret("GOOGLE_MAPS_API_KEY")
if not GOOGLE_KEY:
    st.error("Missing Google Maps key. Add it in **App settings → Secrets** as `GOOGLE_MAPS_API_KEY`.")
    st.stop()
gmaps_client = googlemaps.Client(key=GOOGLE_KEY)

# ────────────────────────────────────────────────────────────────────────────────
# Inputs — DRIVING ONLY + traffic + round trip
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("### Travel options")

# Left column: mode, departure, round-trip
# Right column: traffic model and planned time
c1, c2 = st.columns([1.2, 1.2])

with c1:
    st.markdown("**Travel mode:** Driving")

    leave_now = st.checkbox("Leave now", value=True)
    # 🔽 moved here: round-trip toggle under "Leave now"
    round_trip = st.checkbox("Return to home at the end (round trip)?", value=True)

with c2:
    traffic_model = st.selectbox("Traffic model", ["best_guess", "pessimistic", "optimistic"], index=0)
    planned_date = st.date_input("Planned departure date", value=date.today(), disabled=leave_now)
    planned_time = st.time_input("Planned departure time", value=datetime.now().time(), disabled=leave_now)

# Departure time logic
if leave_now:
    departure_dt = datetime.now(timezone.utc)
else:
    naive = datetime.combine(planned_date, planned_time)
    departure_dt = naive.replace(tzinfo=timezone.utc)

# ────────────────────────────────────────────────────────────────────────────────
# 🎯 Point de départ : Live Fleet (Geotab) + Technician Home
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🎯 Point de départ")

if "route_start" not in st.session_state:
    st.session_state.route_start = ""

tabs = st.tabs(["🚚 Live Fleet (Geotab)", "🏠 Technician Home"])

# ===============  TAB 1 — LIVE FLEET (GEOTAB, MULTI-SÉLECTION + GRANDE CARTE)  ===============
with tabs[0]:
    G_DB = secret("GEOTAB_DATABASE")
    G_USER = secret("GEOTAB_USERNAME")
    G_PWD = secret("GEOTAB_PASSWORD")
    G_SERVER = secret("GEOTAB_SERVER", "my.geotab.com")
    geotab_enabled_by_secrets = GEOTAB_AVAILABLE and all([G_DB, G_USER, G_PWD])

    if geotab_enabled_by_secrets:

        # Rafraîchissement manuel pour éviter la saturation API
        if "geo_refresh_key" not in st.session_state:
            st.session_state.geo_refresh_key = 0
        if st.button("🔄 Rafraîchir Geotab maintenant"):
            st.session_state.geo_refresh_key += 1

        # Caches si non définis ailleurs
        if "_geotab_api_cached" not in globals():
            @st.cache_resource(show_spinner=False)
            def _geotab_api_cached(user, pwd, db, server):
                api = myg.API(user, pwd, db, server)
                api.authenticate()
                return api

        if "_geotab_devices_cached" not in globals():
            @st.cache_data(ttl=900, show_spinner=False)  # 15 min
            def _geotab_devices_cached(user, pwd, db, server):
                api = _geotab_api_cached(user, pwd, db, server)
                devs = api.call("Get", typeName="Device", search={"isActive": True}) or []
                return [{"id": d["id"], "name": d.get("name") or d.get("serialNumber") or "unit"} for d in devs]

        if "_geotab_positions_for" not in globals():
            @st.cache_data(ttl=75, show_spinner=False)   # ~1 min
            def _geotab_positions_for(api_params, device_ids, refresh_key):
                user, pwd, db, server = api_params
                api = _geotab_api_cached(user, pwd, db, server)
                results = []
                for did in device_ids:
                    try:
                        dsi = api.call("Get", typeName="DeviceStatusInfo",
                                       search={"deviceSearch": {"id": did}})
                        lat = lon = when = None
                        driver_name = None
                        if dsi:
                            row = dsi[0]
                            lat, lon = row.get("latitude"), row.get("longitude")
                            when = row.get("dateTime") or row.get("lastCommunicated") or row.get("workDate")
                            if (lat is None or lon is None) and isinstance(row.get("location"), dict):
                                lat = row["location"].get("y"); lon = row["location"].get("x")
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

        # Mapping (optionnel) pour associer un nom de conducteur si l'API ne le renvoie pas
        DEVICE_TO_DRIVER_RAW = {
            "01942": "ALI-REZA SABOUR", "24735": "PATRICK BELLEFLEUR", "23731": "ÉLIE RAJOTTE-LEMAY",
            "18010": "GEORGES YAMNA", "23736": "MARTIN BOURBONNIÈRE", "23738": "PIER-LUC CÔTÉ",
            "24724": "LOUIS LAUZON", "23744": "BENOÎT CHARETTE", "23727": "FREDY DIAZ",
            "23737": "ALAIN DUGUAY", "23730": "BENOÎT LARAMÉE", "24725": "CHRISTIAN DUBREUIL",
            "23746": "MICHAEL SULTE", "24728": "FRANÇOIS RACINE", "23743": "ALEX PELLETIER-GUAY",
            "23745": "KEVIN DURANCEAU",
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

        # Sélection multiple
        devs = _geotab_devices_cached(G_USER, G_PWD, G_DB, G_SERVER)
        if not devs:
            st.info("Aucun appareil actif trouvé.")
        else:
            options = []
            label2id = {}
            for d in devs:
                label = _label_for_device(d["id"], d["name"], None)
                options.append(label)
                label2id[label] = d["id"]

            picked_labels = st.multiselect(
                "Sélectionner un ou plusieurs véhicules/techniciens à afficher :",
                sorted(options), default=[]
            )

            wanted_ids = [label2id[lbl] for lbl in picked_labels]
            if wanted_ids:
                pts = _geotab_positions_for(
                    (G_USER, G_PWD, G_DB, G_SERVER),
                    tuple(wanted_ids),
                    st.session_state.geo_refresh_key
                )
                id2name = {d["id"]: d["name"] for d in devs}

                valid = [p for p in pts if "lat" in p and "lon" in p]
                if valid:
                    # Carte grande
                    avg_lat = sum(p["lat"] for p in valid) / len(valid)
                    avg_lon = sum(p["lon"] for p in valid) / len(valid)
                    fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="cartodbpositron")

                    # Liste pour le choix final du départ
                    choice_labels = []
                    for p in valid:
                        device_id = p["deviceId"]
                        device_name = id2name.get(device_id, device_id)
                        label = _label_for_device(device_id, device_name, p.get("driverName"))
                        choice_labels.append(label)

                        color, lab = recency_color(p.get("when"))

                        # Marqueur + étiquette avec le nom (lisible sur la carte)
                        folium.CircleMarker(
                            [p["lat"], p["lon"]],
                            radius=8, color="#222", weight=2,
                            fill=True, fill_color=color, fill_opacity=0.9
                        ).add_to(fmap)

                        folium.Marker(
                            [p["lat"], p["lon"]],
                            popup=folium.Popup(
                                f"<b>{label}</b><br>Recency: {lab}<br>{p['lat']:.5f}, {p['lon']:.5f}", max_width=320
                            ),
                            tooltip=label,
                            icon=folium.DivIcon(
                                icon_size=(240, 22),
                                icon_anchor=(0, -18),
                                html=f"""
                                <div style="
                                    display:inline-block;padding:2px 6px;
                                    font-size:12px;font-weight:700;color:#111;
                                    background:rgba(255,255,255,.95);
                                    border:1px solid #ddd;border-radius:6px;
                                    box-shadow:0 1px 2px rgba(0,0,0,.25);white-space:nowrap;">
                                    {label.split(' — ')[0]}
                                </div>
                                """
                            )
                        ).add_to(fmap)

                    st_folium(fmap, height=800, width=1800)

                    # Choix final : définir le départ à partir de la liste affichée
                    start_choice = st.selectbox(
                        "Utiliser comme point de départ :", ["(aucun)"] + choice_labels, index=0
                    )
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
        
# ============= TAB 2 – DOMICILES DES TECHNICIENS ET ENTREPÔTS =============
with tabs[1]:
    # Ensure session variables exist
    if "route_start" not in st.session_state:
        st.session_state.route_start = ""
    if "storage_text" not in st.session_state:
        st.session_state.storage_text = ""

    TECH_HOME = {
        "Alain": "1110 rue Proulx, Les Cèdres, QC J7T 1E6",
        "Alex": "163 21e ave, Sabrevois, J0J 2G0",
        "Ali": "226 rue Felx, Saint-Clet, QC J0P 1S0",
        "Ben C": "34 rue de la Digue, Saint-Jérome, QC, Canada",
        "Ben L": "12 rue de Beaudry, Mercier, J6R 2N7",
        "Christian": "31 rue des Roitelets, Delson, J5B 1T6",
        "Donald": "Montée Saint-Régis, Sainte-Catherine, QC, Canada",
        "Elie": "3700 Mnt du 4e Rang, Les Maskoutains, J0H 1S0",
        "Francois": "80 rue de Beaujeu, Coteau-du-lac, J0P 1B0",
        "Fredy": "312 rue de Valcourt, Blainville, J7B 1H3",
        "George": "Rue René-Lévesque, Saint-Eustache, J7R 7L4",
        "Kevin": "943 rue des Marquises, Beloeil, J3G 6T9",
        "Louis": "5005 rue Domville, Saint-Hubert, J3Y 1Y2",
        "Martin": "1444 rue de l'Orchidée, L'Assomption QC J5W 6B3",
        "Maxime": "3e ave, Ile aux Noix, QC, Canada",
        "Michael": "2020 chem. De Covery Hill, Hinchinbrooke, QC, Canada",
        "Patrick": "222 rue Charles-Gadiou, L'Assomption, J5W 0J4",
        "PL": "143 rue Ashby, Marieville, J3M 1P2",
        "Seb": "Saint-Valentin, QC, Canada",
        "Sergio": "791 Rue des Marquises, Beloeil, QC J3G 6M6",
    }

    ENTREPOTS = {
        "Candiac": "315 Liberté, Candiac, QC J5R 6Z7",
        "Assomption": "119 rue de la Commissaires, Assomption, QC, Canada",
        "Boisbriand": "5025 rue Ambroise-Lafortune, Boisbriand, QC, Canada",
        "Mirabel": "1600 Montée Guenette, Mirabel, QC, Canada",
    }

    st.markdown("### 🏠 Domiciles des techniciens et entrepôts")

    # Map toggle OFF by default
    show_map = st.checkbox("Afficher la carte (techniciens + entrepôts)", value=False)

    if show_map:
        try:
            points = []
            tech_name_to_addr = {}
            ent_name_to_addr = {}

            # Geocode technicians
            for name, addr in TECH_HOME.items():
                g = geocode_ll(gmaps_client, addr)
                if g:
                    lat, lon, formatted = g
                    points.append({"name": name, "address": formatted, "lat": lat, "lon": lon, "type": "technician"})
                    tech_name_to_addr[name] = formatted

            # Geocode entrepôts
            for name, addr in ENTREPOTS.items():
                g = geocode_ll(gmaps_client, addr)
                if g:
                    lat, lon, formatted = g
                    points.append({"name": name, "address": formatted, "lat": lat, "lon": lon, "type": "entrepot"})
                    ent_name_to_addr[name] = formatted

            if points:
                avg_lat = sum(p["lat"] for p in points) / len(points)
                avg_lon = sum(p["lon"] for p in points) / len(points)
                fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="cartodbpositron")

                # Markers with permanent labels
                for p in points:
                    if p["type"] == "technician":
                        m = folium.Marker(
                            [p["lat"], p["lon"]],
                            popup=folium.Popup(f"<b>{p['name']}</b><br>{p['address']}", max_width=300),
                            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
                        )
                        m.add_to(fmap)
                        folium.Tooltip(p["name"], permanent=True, direction="right").add_to(m)
                    else:
                        m = folium.Marker(
                            [p["lat"], p["lon"]],
                            popup=folium.Popup(f"<b>🏭 Entrepôt — {p['name']}</b><br>{p['address']}", max_width=300),
                            icon=folium.Icon(color="red", icon="building", prefix="fa"),
                        )
                        m.add_to(fmap)
                        folium.Tooltip(f"Entrepôt — {p['name']}", permanent=True, direction="right").add_to(m)

                st_folium(fmap, height=800, width=1800)
            else:
                st.warning("Aucun point géocodé à afficher.")

        except Exception as e:
            st.error(f"Erreur lors du chargement de la carte : {e}")

    # Selection controls (no extra input here)
    st.markdown("#### Sélectionner les sources de départ / fin")
    c1, c2 = st.columns(2)

    with c1:
        tech_choice = st.selectbox(
            "Technicien → définir comme **départ**",
            ["(choisir)"] + sorted(TECH_HOME.keys()),
            key="tech_choice_start_tab2",
        )
        if tech_choice != "(choisir)":
            # Set the Start (Route stops START field)
            st.session_state.route_start = TECH_HOME[tech_choice]
            st.success(f"Départ défini sur **{tech_choice}** — {TECH_HOME[tech_choice]}")

    with c2:
        ent_choice = st.selectbox(
            "Entrepôt → définir comme **stockage**",
            ["(choisir)"] + sorted(ENTREPOTS.keys()),
            key="entrepot_choice_storage_tab2",
        )
        if ent_choice != "(choisir)":
            # Set the single Storage input used in Route stops
            st.session_state.storage_text = ENTREPOTS[ent_choice]
            st.success(f"Stockage défini sur **Entrepôt — {ent_choice}** — {ENTREPOTS[ent_choice]}")

# Rappel visuel du départ courant
if st.session_state.route_start:
    st.info(f"📍 **Point de départ sélectionné :** {st.session_state.route_start}")

# ────────────────────────────────────────────────────────────────────────────────
# Route stops (AFTER Geotab so the start can be auto-filled)
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("### Route stops")
start_text = st.text_input(
    "Technician home (START)",
    key="route_start",  # bound to the value we set from Geotab
    placeholder="e.g., 123 Main St, City, Province"
)
storage_text = st.text_input(
    "Storage location (first stop)",
    key="storage_text",
    placeholder="e.g., 456 Depot Rd, City, Province",
)
stops_text = st.text_area(
    "Other stops (one ZIP/postal code or full address per line)",
    height=140,
    placeholder="H0H0H0\nG2P1L4\n…"
)
other_stops_input = [s.strip() for s in stops_text.splitlines() if s.strip()]

# ────────────────────────────────────────────────────────────────────────────────
# Optimize route — DRIVING ONLY (compute + persist result)
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🧭 Optimize Route", type="primary"):
    try:
        # 1) Gather inputs and normalize
        start_text = st.session_state.get("route_start", "").strip()
        storage_query = normalize_ca_postal(storage_text.strip()) if storage_text else ""
        other_stops_queries = [normalize_ca_postal(s.strip()) for s in other_stops_input if s.strip()]

        # 2) Geocode all inputs; fail with a clear list if any are bad
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
            st.error(
                "I couldn’t geocode some locations:\n\n- " + "\n- ".join(failures) +
                "\n\nTip: use full street addresses if a postal code fails."
            )
            st.stop()

        # 3) Build Directions request (DRIVING + optimize:true)
        def to_ll_str(ll: Tuple[float, float]) -> str:
            return f"{ll[0]:.7f},{ll[1]:.7f}"

        start_ll = (start_g[0], start_g[1])
        start_addr = start_g[2]

        wp_addrs = [addr for (_lbl, addr, _ll) in wp_geocoded]
        wp_llstr = [to_ll_str(ll) for (_lbl, _addr, ll) in wp_geocoded]

        if len(wp_llstr) > 23:
            st.error("Too many stops. Google allows up to **25 total** (origin + destination + waypoints).")
            st.stop()

        if round_trip:
            destination_addr = start_addr
            destination_llstr = to_ll_str(start_ll)
            waypoints_for_api = wp_llstr[:]            # include all
        else:
            if wp_llstr:
                destination_addr = wp_addrs[-1]
                destination_llstr = wp_llstr[-1]
                waypoints_for_api = wp_llstr[:-1]      # all except final destination
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
            traffic_model=traffic_model,
        )

        if not directions:
            st.error("No route returned by Google Directions (driving). Try replacing postal codes with full addresses.")
            st.json({
                "origin": to_ll_str(start_ll),
                "destination": destination_llstr,
                "waypoints": waypoints_for_api,
            })
            st.stop()

        # 4) Build visit list using Google's waypoint_order
        if waypoints_for_api:
            order = directions[0].get("waypoint_order", list(range(len(waypoints_for_api))))
            ordered_wp_addrs = [wp_addrs[i] for i in order]
            if not round_trip and wp_addrs:
                ordered_wp_addrs.append(destination_addr)
        else:
            ordered_wp_addrs = [] if round_trip else [destination_addr]

        visit_texts = [start_addr] + ordered_wp_addrs + ([start_addr] if round_trip else [destination_addr])

        # 5) Totals (duration_in_traffic preferred)
        legs = directions[0].get("legs", [])
        total_dist_m = sum(leg.get("distance", {}).get("value", 0) for leg in legs)
        total_sec = sum((leg.get("duration_in_traffic") or leg.get("duration") or {}).get("value", 0) for leg in legs)
        km = total_dist_m / 1000.0 if total_dist_m else 0.0
        mins = total_sec / 60.0 if total_sec else 0.0

        # 6) Persist everything needed to re-render after reruns (e.g., Show map toggle)
        st.session_state.route_result = {
            "visit_texts": visit_texts,
            "km": km,
            "mins": mins,
            "start_ll": start_ll,
            "wp_geocoded": wp_geocoded,
            "round_trip": round_trip,
            "overview": directions[0].get("overview_polyline", {}).get("points"),
        }

    except Exception as e:
        st.error(f"Unexpected error: {type(e).__name__}: {e}")
        st.exception(e)

# ────────────────────────────────────────────────────────────────────────────────
# Render last optimized result (persists across reruns, e.g. Show map toggle)
# ────────────────────────────────────────────────────────────────────────────────
res = st.session_state.get("route_result")
if res:
    visit_texts = res["visit_texts"]
    km = res["km"]
    mins = res["mins"]
    start_ll = tuple(res["start_ll"])
    wp_geocoded = res["wp_geocoded"]
    round_trip = res["round_trip"]
    overview = res.get("overview")

    st.markdown("#### Optimized order (Driving)")
    for ix, addr in enumerate(visit_texts):
        if ix == 0:
            st.write(f"**START** — {addr}")
        elif ix == len(visit_texts) - 1:
            st.write(f"**END** — {addr}")
        else:
            st.write(f"**{ix}** — {addr}")

    # Toggle map rendering (off by default for stability)
    show_map = st.checkbox("Show map", value=False, key="show_map_toggle")
    if show_map:
        try:
            fmap = folium.Map(location=[start_ll[0], start_ll[1]], zoom_start=9, tiles="cartodbpositron")

            # Safe polyline
            if overview:
                try:
                    path = polyline.decode(overview)
                    folium.PolyLine(path, weight=7, color="#2196f3", opacity=0.9).add_to(fmap)
                except Exception:
                    pass

            # Start marker
            folium.Marker(
                start_ll, icon=folium.Icon(color="green", icon="play", prefix="fa"),
                popup=folium.Popup(f"<b>START</b><br>{visit_texts[0]}", max_width=260)
            ).add_to(fmap)

            # Waypoint markers from cached geocodes
            addr2ll = {addr: ll for (_lbl, addr, ll) in wp_geocoded}
            for i, addr in enumerate(visit_texts[1:-1], start=1):
                ll = addr2ll.get(addr)
                if ll:
                    folium.Marker(
                        ll, popup=folium.Popup(f"<b>{i}</b>. {addr}", max_width=260),
                        icon=big_number_marker(str(i))
                    ).add_to(fmap)

            # End marker
            end_addr = visit_texts[-1]
            end_ll = addr2ll.get(end_addr)
            if not end_ll:
                g = geocode_ll(gmaps_client, end_addr)
                if g:
                    end_ll = (g[0], g[1])
            if end_ll:
                folium.Marker(
                    end_ll, icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
                    popup=folium.Popup(f"<b>{'END (Home)' if round_trip else 'END'}</b><br>{end_addr}", max_width=260)
                ).add_to(fmap)

            # ✅ Larger map display (fills most of the screen)
            st_folium(fmap, height=800, width=1800)

        except Exception as e:
            st.warning(f"Map rendering skipped: {e}")

    st.success(f"**Total distance:** {km:.1f} km • **Total time:** {mins:.0f} mins (live traffic)")
