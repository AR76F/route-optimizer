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
st.title("📍 Route Optimizer — Home ➜ Storage ➜ Optimized Stops (≤ 25)")

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
# Inputs — mode, traffic, round trip
# ────────────────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1.2, 1.2, 2])
with c1:
    travel_mode = st.selectbox("Travel mode", ["driving", "walking", "bicycling"])
with c2:
    round_trip = st.checkbox("Return to home at the end (round trip)?", value=True)

st.markdown("### Traffic options (driving only)")
t1, t2, t3 = st.columns([1, 1, 1])
with t1:
    leave_now = st.checkbox("Leave now", value=True)
with t2:
    traffic_model = st.selectbox("Traffic model", ["best_guess", "pessimistic", "optimistic"])
with t3:
    planned_date = st.date_input("Planned departure date", value=date.today(), disabled=leave_now)
    planned_time = st.time_input("Planned departure time", value=datetime.now().time(), disabled=leave_now)

if leave_now:
    departure_dt = datetime.now(timezone.utc)
else:
    naive = datetime.combine(planned_date, planned_time)
    departure_dt = naive.replace(tzinfo=timezone.utc)

# ────────────────────────────────────────────────────────────────────────────────
# Geotab (via secrets only) — rate-limit safe, with DRIVER NAMES (id OR name mapped)
# (Placed ABOVE Route stops so the START field can be auto-filled.)
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🚚 Live Fleet (Geotab)")

G_DB = secret("GEOTAB_DATABASE")
G_USER = secret("GEOTAB_USERNAME")
G_PWD = secret("GEOTAB_PASSWORD")
G_SERVER = secret("GEOTAB_SERVER", "my.geotab.com")
geotab_enabled_by_secrets = GEOTAB_AVAILABLE and all([G_DB, G_USER, G_PWD])

# --- Driver mapping (works by device NAME or device ID) ------------------------
# You can also add/override via secret GEOTAB_DEVICE_TO_DRIVER_JSON
DEVICE_TO_DRIVER_RAW = {
    "01942": "ALI-REZA SABOUR",
    "24735": "PATRICK BELLEFLEUR",
    "23731": "ÉLIE RAJOTTE-LEMAY",
    "18010": "GEORGES YAMNA",
    "23736": "MARTIN BOURBONNIÈRE",
    "23738": "PIER-LUC CÔTÉ",
    "24724": "LOUIS LAUZON",
    "23744": "BENOÎT CHARETTE",
    "23727": "FREDY DIAZ",
    "23737": "ALAIN DUGUAY",
    "23730": "BENOÎT LARAMÉE",
    "24725": "CHRISTIAN DUBREUIL",
    "23746": "MICHAEL SULTE",
    "24728": "FRANÇOIS RACINE",
    "23743": "ALEX PELLETIER-GUAY",
    "23745": "KEVIN DURANCEAU",
}
import json
try:
    j = secret("GEOTAB_DEVICE_TO_DRIVER_JSON")
    if j:
        DEVICE_TO_DRIVER_RAW.update(json.loads(j))
except Exception:
    pass

def _norm(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return " ".join(str(s).strip().upper().split())

# Build two maps: by name and by id (both normalized)
NAME2DRIVER, ID2DRIVER = {}, {}
for k, v in DEVICE_TO_DRIVER_RAW.items():
    nk = _norm(k)
    if not nk:
        continue
    if len(nk) > 12 or "-" in nk and any(c.isalpha() for c in nk):  # likely an ID/GUID/long
        ID2DRIVER[nk] = v
    else:
        NAME2DRIVER[nk] = v

def _driver_from_mapping(device_id: Optional[str], device_name: Optional[str]) -> Optional[str]:
    n_name = _norm(device_name)
    if n_name and n_name in NAME2DRIVER:
        return NAME2DRIVER[n_name]
    n_id = _norm(device_id)
    if n_id and n_id in ID2DRIVER:
        return ID2DRIVER[n_id]
    if n_name and n_name in ID2DRIVER:
        return ID2DRIVER[n_name]
    if n_id and n_id in NAME2DRIVER:
        return NAME2DRIVER[n_id]
    return None

def _label_for_device(device_id: str, device_name: str, driver_from_api: Optional[str]) -> str:
    driver = driver_from_api or _driver_from_mapping(device_id, device_name) or "(no driver)"
    dev_label = device_name or device_id
    return f"{driver} — {dev_label}"

# manual refresh key to avoid rate limits
if "geo_refresh_key" not in st.session_state:
    st.session_state.geo_refresh_key = 0
if st.button("🔄 Refresh Geotab now"):
    st.session_state.geo_refresh_key += 1

@st.cache_resource(show_spinner=False)
def _geotab_api_cached(user, pwd, db, server):
    api = myg.API(user, pwd, db, server)
    api.authenticate()
    return api

@st.cache_data(ttl=900, show_spinner=False)  # 15 min
def _geotab_devices_cached(user, pwd, db, server):
    api = _geotab_api_cached(user, pwd, db, server)
    devs = api.call("Get", typeName="Device", search={"isActive": True}) or []
    return [{"id": d["id"], "name": d.get("name") or d.get("serialNumber") or "unit"} for d in devs]

@st.cache_data(ttl=75, show_spinner=False)   # ~1 min
def _geotab_positions_for(api_params, device_ids, refresh_key):
    user, pwd, db, server = api_params
    api = _geotab_api_cached(user, pwd, db, server)
    results, calls_made, limit_per_min = [], 0, 9
    for did in device_ids:
        if calls_made >= limit_per_min:
            results.append({"deviceId": did, "error": "rate_limit_guard"})
            continue
        try:
            dsi = api.call("Get", typeName="DeviceStatusInfo", search={"deviceSearch": {"id": did}})
            calls_made += 1
            lat = lon = when = None
            driver_name = None
            if dsi:
                row = dsi[0]
                lat, lon = row.get("latitude"), row.get("longitude")
                when = row.get("dateTime") or row.get("lastCommunicated") or row.get("workDate")
                drv = row.get("driver")
                if isinstance(drv, dict):
                    driver_name = drv.get("name")
                if (lat is None or lon is None) and isinstance(row.get("location"), dict):
                    lat = row["location"].get("y"); lon = row["location"].get("x")
            if lat is not None and lon is not None:
                results.append({"deviceId": did, "lat": float(lat), "lon": float(lon),
                                "when": when, "driverName": driver_name})
                continue
        except Exception as e:
            results.append({"deviceId": did, "error": f"dsi:{e}"})
            continue
        if calls_made >= limit_per_min:
            results.append({"deviceId": did, "error": "rate_limit_guard"})
            continue
        try:
            from_dt = datetime.now(timezone.utc) - timedelta(days=7)
            logs = api.call("Get", typeName="LogRecord", search={
                "deviceSearch": {"id": did},
                "fromDate": from_dt,
                "resultsLimit": 1,
                "sortOrder": "Descending",
            })
            calls_made += 1
            if logs:
                lat, lon = logs[0].get("latitude"), logs[0].get("longitude")
                if lat is not None and lon is not None:
                    results.append({"deviceId": did, "lat": float(lat), "lon": float(lon),
                                    "when": logs[0].get("dateTime"), "driverName": None})
                    continue
            results.append({"deviceId": did, "error": "no_position"})
        except Exception as e:
            results.append({"deviceId": did, "error": f"log:{e}"})
    return results

if geotab_enabled_by_secrets:
    try:
        devs = _geotab_devices_cached(G_USER, G_PWD, G_DB, G_SERVER)
        if not devs:
            st.info("No active devices found.")
        else:
            # Build friendly labels for the selector BEFORE querying positions
            options, label2id = [], {}
            for d in devs:
                label = _label_for_device(d["id"], d["name"], None)  # mapping-only at this stage
                options.append(label)
                label2id[label] = d["id"]

            picked_labels = st.multiselect(
                "Select drivers/devices to show:",
                options=sorted(options),
                default=[],
                help="Pick a few devices, then click Refresh."
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
                        add_marker(
                            fmap, p["lat"], p["lon"],
                            popup=folium.Popup(f"<b>{label}</b><br>Recency: {lab}<br>{p['lat']:.5f}, {p['lon']:.5f}", max_width=300),
                            icon=folium.Icon(color="green", icon="user", prefix="fa")
                        )
                        folium.CircleMarker([p["lat"], p["lon"]], radius=8, color="#222", weight=2,
                                            fill=True, fill_color=color, fill_opacity=0.9).add_to(fmap)

                    st_folium(fmap, height=420)

                    # Use driver/device as route start — auto-fill the START address
                    start_choice = st.selectbox("Use this driver/device as route start:",
                                                ["(none)"] + choice_labels, key="geo_start_choice")
                    if start_choice != "(none)":
                        chosen = valid[choice_labels.index(start_choice)]
                        picked_addr = reverse_geocode(gmaps_client, chosen["lat"], chosen["lon"])
                        st.session_state.route_start = picked_addr
                        st.success(f"Start set from Geotab: **{start_choice}** → {picked_addr}")

                guarded = [p for p in pts if p.get("error") == "rate_limit_guard"]
                if guarded:
                    st.warning("Hit the per-minute safety cap. Click **Refresh** in ~60–90 seconds to load remaining devices.")
                missing = [p for p in pts if p.get("error") not in (None, "rate_limit_guard") and "error" in p]
                if missing:
                    st.caption("Some devices returned no recent position or hit a fallback error.")
            else:
                st.info("Select one or more devices, then click **Refresh** to load positions.")
    except Exception as e:
        st.info(f"Geotab disabled due to authentication error: {e}")
else:
    st.caption("Geotab live view is disabled. Add `GEOTAB_DATABASE`, `GEOTAB_USERNAME`, and `GEOTAB_PASSWORD` in Secrets.")

# ────────────────────────────────────────────────────────────────────────────────
# Route stops (AFTER Geotab so the start can be auto-filled)
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("### Route stops")
start_text = st.text_input(
    "Technician home (START)",
    key="route_start",  # bound to the value we set from Geotab
    placeholder="e.g., 123 Main St, City, Province"
)
storage_text = st.text_input("Storage location (first stop)", placeholder="e.g., 456 Depot Rd, City, Province")
stops_text = st.text_area(
    "Other stops (one ZIP/postal code or full address per line)",
    height=140,
    placeholder="H0H0H0\nG2P1L4\n…"
)
other_stops_input = [s.strip() for s in stops_text.splitlines() if s.strip()]

# ────────────────────────────────────────────────────────────────────────────────
# Optimize route
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🧭 Optimize Route", type="primary"):
    # 1) Read inputs and normalize
    start_text = st.session_state.get("route_start", "")
    storage_query = normalize_ca_postal(storage_text) if storage_text else storage_text
    other_stops_queries = [normalize_ca_postal(s) for s in other_stops_input]

    # 2) Geocode ALL points up front (fail fast with clear message)
    failures = []

    start_g = geocode_ll(gmaps_client, start_text)
    if not start_g:
        failures.append(f"START: `{start_text}`")

    storage_g = geocode_ll(gmaps_client, storage_query) if storage_query else None
    if not storage_g:
        failures.append(f"STORAGE: `{storage_text}`")

    wp_raw = []
    if storage_query:
        wp_raw.append(("Storage", storage_query))
    for i, q in enumerate(other_stops_queries, start=1):
        wp_raw.append((f"Stop {i}", q))

    wp_geocoded: List[Tuple[str, str, Tuple[float, float]]] = []  # (label, pretty_addr, (lat,lon))
    for label, q in wp_raw:
        g = geocode_ll(gmaps_client, q)
        if not g:
            failures.append(f"{label}: `{q}`")
        else:
            lat, lon, addr = g
            wp_geocoded.append((label, addr, (lat, lon)))

    if failures:
        st.error("I couldn’t geocode some locations:\n\n- " + "\n- ".join(failures) +
                 "\n\nTip: try full street addresses instead of postal codes for those lines.")
        st.stop()

    # 3) Build waypoints list for Google Directions as 'lat,lon' strings
    def to_ll_str(ll: Tuple[float, float]) -> str:
        return f"{ll[0]:.7f},{ll[1]:.7f}"

    start_ll = (start_g[0], start_g[1])
    start_addr = start_g[2]

    optimized_waypoints_addrs = [addr for (_label, addr, _ll) in wp_geocoded]
    optimized_waypoints_llstr = [to_ll_str(ll) for (_label, _addr, ll) in wp_geocoded]

    if len(optimized_waypoints_llstr) > 23:
        st.error("Too many stops. Google allows up to **25 total** (origin + destination + waypoints).")
        st.stop()

    if round_trip:
        destination_addr = start_addr
        destination_llstr = to_ll_str(start_ll)
        waypoints_for_api = optimized_waypoints_llstr[:]  # keep all
    else:
        if optimized_waypoints_llstr:
            destination_addr = optimized_waypoints_addrs[-1]
            destination_llstr = optimized_waypoints_llstr[-1]
            waypoints_for_api = optimized_waypoints_llstr[:-1]  # every waypoint except the last (destination)
        else:
            destination_addr = storage_g[2] if storage_g else start_addr
            destination_llstr = to_ll_str(storage_g[:2]) if storage_g else to_ll_str(start_ll)
            waypoints_for_api = []

    # 4) Call Directions with lat,lng strings (unambiguous)
    #    IMPORTANT: optimize:true ONLY for DRIVING (other modes don't support it)
    if travel_mode == "driving" and waypoints_for_api:
        wp_arg = ["optimize:true"] + waypoints_for_api
    else:
        wp_arg = waypoints_for_api if waypoints_for_api else None

    try:
        directions = gmaps_client.directions(
            origin=to_ll_str(start_ll),
            destination=destination_llstr,
            mode=travel_mode,
            waypoints=wp_arg,
            departure_time=departure_dt if travel_mode == "driving" else None,
            traffic_model=traffic_model if travel_mode == "driving" else None,
        )
    except Exception as e:
        st.error(f"Directions API error: {e}")
        st.stop()

    if not directions:
        st.error(
            "No route returned by Directions. If you’re not **Driving**, try changing mode to Driving "
            "or replace postal codes with full addresses."
        )
        # Debug info to help diagnose
        with st.expander("Debug (no route)"):
            st.write({
                "mode": travel_mode,
                "round_trip": round_trip,
                "origin": to_ll_str(start_ll),
                "destination": destination_llstr,
                "waypoints_count": len(waypoints_for_api),
                "waypoints_sample": waypoints_for_api[:5],
            })
        st.stop()

    # 5) Reconstruct the visit order as readable addresses
    if travel_mode == "driving" and waypoints_for_api:
        wp_order = directions[0].get("waypoint_order", list(range(len(waypoints_for_api))))
        ordered_wp_addrs = [optimized_waypoints_addrs[i] for i in wp_order]
        if not round_trip and optimized_waypoints_addrs:  # add destination back if we removed it
            ordered_wp_addrs.append(destination_addr)
    else:
        # For non-driving modes we keep the user-entered order (no optimization)
        ordered_wp_addrs = optimized_waypoints_addrs[:] if round_trip else optimized_waypoints_addrs[:] + [destination_addr]

    visit_texts = [start_addr] + ordered_wp_addrs + ([start_addr] if round_trip else [destination_addr])

    # 6) Draw map
    fmap = folium.Map(location=[start_ll[0], start_ll[1]], zoom_start=9, tiles="cartodbpositron")
    overview = directions[0]["overview_polyline"]["points"]
    path = polyline.decode(overview)
    folium.PolyLine(path, weight=7, color="#2196f3", opacity=0.9).add_to(fmap)

    folium.Marker(
        start_ll, icon=folium.Icon(color="green", icon="play", prefix="fa"),
        popup=folium.Popup(f"<b>START</b><br>{start_addr}", max_width=260)
    ).add_to(fmap)

    # Put numbered markers at the optimized waypoints
    addr2ll = {addr: ll for (_label, addr, ll) in wp_geocoded}
    for i, addr in enumerate(ordered_wp_addrs, start=1):
        ll = addr2ll.get(addr)
        if ll:
            folium.Marker(
                ll, popup=folium.Popup(f"<b>{i}</b>. {addr}", max_width=260),
                icon=big_number_marker(str(i))
            ).add_to(fmap)

    # End marker
    end_g = geocode_ll(gmaps_client, visit_texts[-1])
    if end_g:
        end_ll = (end_g[0], end_g[1])
        folium.Marker(
            end_ll, icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
            popup=folium.Popup(f"<b>{'END (Home)' if round_trip else 'END'}</b><br>{visit_texts[-1]}", max_width=260)
        ).add_to(fmap)

    st_folium(fmap, height=560)

    # 7) Totals
    legs = directions[0]["legs"]
    total_dist_m = sum(leg["distance"]["value"] for leg in legs)
    total_sec = sum(leg.get("duration_in_traffic", leg["duration"])["value"] for leg in legs)
    km = total_dist_m / 1000.0
    mins = total_sec / 60.0

    st.markdown("#### Optimized order")
    for ix, addr in enumerate(visit_texts):
        if ix == 0:
            st.write(f"**START** — {addr}")
        elif ix == len(visit_texts) - 1:
            st.write(f"**END** — {addr}")
        else:
            st.write(f"**{ix}** — {addr}")

    st.success(
        f"**Total distance:** {km:.1f} km • **Total time:** {mins:.0f} mins "
        f"{'(live traffic)' if travel_mode=='driving' else ''}"
    )


