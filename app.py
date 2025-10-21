# app.py — Route Optimizer with optional Geotab live origin
# Start (typed or Geotab) → Storage → Optimized Stops (≤ 25 total, traffic-aware)

import os
import time
from datetime import datetime, date, time as dtime, timedelta, timezone

import streamlit as st
import googlemaps
import polyline
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Optional Geotab
try:
    import mygeotab as myg
    GEOTAB_AVAILABLE = True
except Exception:
    GEOTAB_AVAILABLE = False

# ────────────────────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("📍 Route Optimizer — Home → Storage → Optimized Stops (≤ 25)")

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
def get_gmaps_client(api_key: str | None):
    """Return a Google Maps client or raise with a helpful message."""
    key = api_key or st.secrets.get("GOOGLE_MAPS_API_KEY", "")
    if not key:
        raise RuntimeError("No Google Maps API key. Add it to Streamlit Secrets as GOOGLE_MAPS_API_KEY or enter it.")
    return googlemaps.Client(key=key)

def geocode_one(gmaps: googlemaps.Client, text_or_latlon):
    """Geocode an address string or (lat,lon) tuple into a usable string/lat/lon."""
    if isinstance(text_or_latlon, (list, tuple)) and len(text_or_latlon) == 2:
        lat, lon = float(text_or_latlon[0]), float(text_or_latlon[1])
        return {"raw": f"{lat},{lon}", "lat": lat, "lon": lon, "label": f"{lat:.5f}, {lon:.5f}"}

    q = (text_or_latlon or "").strip()
    if not q:
        return None
    res = gmaps.geocode(q)
    if not res:
        return None
    r = res[0]
    loc = r["geometry"]["location"]
    return {"raw": r["formatted_address"], "lat": loc["lat"], "lon": loc["lng"], "label": r["formatted_address"]}

def decode_distance_duration(leg):
    """Return ('12.3 km', '17 mins') from a Directions leg with/without traffic."""
    dist = leg.get("distance", {}).get("text", "—")
    # Prefer duration_in_traffic when available (driving with departure_time)
    dur = leg.get("duration_in_traffic", {}).get("text") or leg.get("duration", {}).get("text", "—")
    return dist, dur

def build_route_map(path_coords, markers, center=None, zoom=8, height=600):
    """Create a Folium map with a route polyline and numbered red markers."""
    if not center:
        center = [sum(p[0] for p in path_coords)/len(path_coords), sum(p[1] for p in path_coords)/len(path_coords)]

    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    # Route polyline
    folium.PolyLine(path_coords, weight=6, opacity=0.8, color="#2176FF").add_to(m)
    # Markers
    for i, (lat, lon, label) in enumerate(markers, start=1):
        popup = folium.Popup(f"<b>{i}.</b> {label}", max_width=300)
        folium.Marker(
            [lat, lon],
            popup=popup,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    st_folium(m, height=height, use_container_width=True, returned_objects=[])

# ────────────────────────────────────────────────────────────────────────────────
# Geotab helpers (driver names, big map, pick driver as start)
# ────────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def geotab_fetch_devices(api: "myg.API"):
    try:
        devices = api.call("Get", "Device", {"search": {"isActive": True}})
    except Exception:
        devices = []
    return [
        {
            "id": d["id"],
            "name": d.get("name", ""),
            "serialNumber": d.get("serialNumber", ""),
            "vin": d.get("vehicleIdentificationNumber", ""),
        }
        for d in devices
    ]

@st.cache_data(ttl=60)
def geotab_try_get_current_driver_diag(api: "myg.API"):
    try:
        diags = api.call("Get", "Diagnostic", {})
    except Exception:
        return None
    candidates = ["DeviceCurrentDriver", "DeviceCurrentDriverId", "Current Driver", "CurrentDriver", "DriverId", "Driver"]
    for d in diags:
        nm = (d.get("name") or "").lower()
        if any(c.lower() in nm for c in candidates):
            return d.get("id")
    return None

def geotab_latest_status_value(api: "myg.API", device_id: str, diagnostic_id: str):
    try:
        from_dt = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        sd = api.call("Get", "StatusData", {
            "deviceSearch": {"id": device_id},
            "diagnosticSearch": {"id": diagnostic_id},
            "fromDate": from_dt,
            "resultsLimit": 1,
            "sortOrder": "Descending"
        })
        if sd:
            return sd[0].get("data"), sd[0].get("dateTime")
    except Exception:
        pass
    return None, None

def geotab_latest_driverchange(api: "myg.API", device_id: str):
    try:
        from_dt = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        events = api.call("Get", "DriverChange", {
            "deviceSearch": {"id": device_id},
            "fromDate": from_dt,
            "resultsLimit": 1,
            "sortOrder": "Descending"
        })
        if events:
            return events[0].get("user", {}).get("id"), events[0].get("dateTime")
    except Exception:
        pass
    return None, None

@st.cache_data(ttl=60)
def geotab_load_user_names(api: "myg.API"):
    try:
        users = api.call("Get", "User", {"search": {"isDriver": True, "isActive": True}})
    except Exception:
        users = []
    return {
        u["id"]: (u.get("name") or (u.get("firstName", "") + " " + u.get("lastName", ""))).strip()
        for u in users
    }

@st.cache_data(ttl=60)
def geotab_load_device_position(api: "myg.API", device_id: str):
    try:
        from_dt = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        logs = api.call("Get", "LogRecord", {
            "deviceSearch": {"id": device_id},
            "fromDate": from_dt,
            "resultsLimit": 1,
            "sortOrder": "Descending"
        })
        if logs:
            lat, lon = logs[0].get("latitude"), logs[0].get("longitude")
            if lat is not None and lon is not None:
                return float(lat), float(lon), logs[0].get("dateTime")
    except Exception:
        pass
    return None, None, None

def geotab_driver_label_for_device(api: "myg.API", device: dict, diag_id: str | None, user_names: dict):
    # 1) Diagnostic value
    if diag_id:
        v, when1 = geotab_latest_status_value(api, device["id"], diag_id)
        if v and str(v) in user_names:
            return user_names[str(v)], device["name"], when1
    # 2) Latest DriverChange
    uid, when2 = geotab_latest_driverchange(api, device["id"])
    if uid and uid in user_names:
        return user_names[uid], device["name"], when2
    # 3) Fallback to device name
    return device["name"] or device["serialNumber"] or device["vin"] or "(unknown)", "", None

def render_geotab_live_block():
    """Large Geotab map; let user pick a driver as route start. Stores lat/lon in st.session_state['route_start_latlon']"""
    st.subheader("🚚 Live Fleet (Geotab)")
    if not GEOTAB_AVAILABLE:
        st.info("Geotab not installed on this server. Add `mygeotab` to requirements to enable.")
        return

    enable_geo = st.checkbox("Enable Geotab live view", value=False)
    if not enable_geo:
        st.session_state.pop("route_start_latlon", None)
        return

    # Secrets: GEOTAB_DATABASE, GEOTAB_USERNAME, GEOTAB_PASSWORD, optional GEOTAB_SERVER
    db = st.secrets.get("GEOTAB_DATABASE", "")
    un = st.secrets.get("GEOTAB_USERNAME", "")
    pw = st.secrets.get("GEOTAB_PASSWORD", "")
    srv = st.secrets.get("GEOTAB_SERVER", "my.geotab.com")
    if not (db and un and pw):
        st.error("Geotab secrets missing. Set GEOTAB_DATABASE, GEOTAB_USERNAME, GEOTAB_PASSWORD.")
        return

    try:
        api = myg.API(un, pw, db, srv)
        api.authenticate()
    except Exception as e:
        st.error(f"Geotab login failed: {e}")
        return

    devices = geotab_fetch_devices(api)
    user_names = geotab_load_user_names(api)
    driver_diag_id = geotab_try_get_current_driver_diag(api)

    # Build pin list
    pins = []
    for d in devices:
        lat, lon, when = geotab_load_device_position(api, d["id"])
        if lat is None or lon is None:
            continue
        drv_label, unit_label, when2 = geotab_driver_label_for_device(api, d, driver_diag_id, user_names)
        pins.append({
            "lat": lat, "lon": lon,
            "driver": drv_label, "unit": unit_label, "when": when2 or when
        })

    if not pins:
        st.info("No recent positions (last ~2 hours).")
        return

    # Center & draw map (big)
    avg_lat = sum(p["lat"] for p in pins)/len(pins)
    avg_lon = sum(p["lon"] for p in pins)/len(pins)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="CartoDB positron")
    cluster = MarkerCluster().add_to(m)
    for p in pins:
        html = f"""
        <div style="font-size:16px;">
         <b>Driver:</b> {p['driver']}<br/>
         <b>Unit:</b> {p['unit'] or '—'}<br/>
         <b>Last:</b> {p['when'] or '—'}
        </div>
        """
        folium.Marker(
            [p["lat"], p["lon"]],
            popup=folium.Popup(html, max_width=260),
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(cluster)

    st_folium(m, height=700, use_container_width=True, returned_objects=[])

    # Driver selector by name
    driver_list = sorted({p["driver"] for p in pins if p["driver"]})
    driver_list = ["(none)"] + driver_list
    chosen = st.selectbox("Use this driver as route start:", driver_list, index=0)
    if chosen != "(none)":
        sel_pin = next((p for p in pins if p["driver"] == chosen), None)
        if sel_pin:
            st.success(f"Using **{chosen}** as start (lat={sel_pin['lat']:.5f}, lon={sel_pin['lon']:.5f}).")
            st.session_state["route_start_latlon"] = (sel_pin["lat"], sel_pin["lon"])
        else:
            st.warning("Selected driver not found on map.")
    else:
        st.session_state.pop("route_start_latlon", None)

# ────────────────────────────────────────────────────────────────────────────────
# Inputs
# ────────────────────────────────────────────────────────────────────────────────
# API key (uses secrets by default; field allows override without displaying the key)
api_key_default = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
api_key = st.text_input("Google Maps API Key", value=api_key_default, type="password")

colA, colB = st.columns([1, 1])
with colA:
    travel_mode = st.selectbox("Travel mode", ["driving", "walking", "bicycling", "transit"])
with colB:
    round_trip = st.checkbox("Return to home at the end (round trip)?", value=True)

# Traffic (driving only)
st.markdown("### Traffic options (driving only)")
tcol1, tcol2, tcol3 = st.columns([1, 1, 1])
leave_now = tcol1.checkbox("Leave now", value=True)
traffic_model = tcol2.selectbox("Traffic model", ["best_guess", "optimistic", "pessimistic"])

# If not leaving now, pick date/time
if not leave_now:
    planned_date = tcol2.date_input("Planned departure date", value=date.today())
    planned_time = tcol3.time_input("Planned departure time", value=dtime(hour=datetime.now().hour, minute=0))
else:
    planned_date = None
    planned_time = None

# Route stops
st.markdown("### Route stops")
st.caption("First two inputs define the start & first stop. Then paste ZIP/postal codes or full addresses (one per line). Max 25 total stops (origin+destination+waypoints).")

# Geotab live section (optional) — if a driver is picked, it overrides home address as origin
render_geotab_live_block()

col1, col2 = st.columns([1, 1])
with col1:
    home_addr = st.text_input("Technician home (START)", value="")

with col2:
    storage_addr = st.text_input("Storage location (first stop)", value="")

other_stops_text = st.text_area("Other stops (one ZIP/postal code or full address per line)", height=160, placeholder="H2Y 1C6\nJ4B 5E4\n...")

# ────────────────────────────────────────────────────────────────────────────────
# Optimize Button
# ────────────────────────────────────────────────────────────────────────────────
go = st.button("Optimize Route")

if go:
    # Build client
    try:
        gmaps_client = get_gmaps_client(api_key)
    except Exception as e:
        st.error(str(e))
        st.stop()

    # Derive origin: Geotab driver pick overrides manual home if available
    origin_info = None
    if "route_start_latlon" in st.session_state:
        # Geotab chosen driver origin
        origin_info = geocode_one(gmaps_client, st.session_state["route_start_latlon"])
    else:
        origin_info = geocode_one(gmaps_client, home_addr)

    storage_info = geocode_one(gmaps_client, storage_addr)

    # Parse other stops
    raw_lines = [ln.strip() for ln in (other_stops_text or "").splitlines() if ln.strip()]
    if len(raw_lines) > 0:
        other_infos = []
        for ln in raw_lines:
            gi = geocode_one(gmaps_client, ln)
            if gi:
                other_infos.append(gi)
    else:
        other_infos = []

    # Safety checks
    if not origin_info:
        st.error("Please specify a valid Technician home (or pick a Geotab driver).")
        st.stop()
    if not storage_info:
        st.error("Please specify a valid Storage location.")
        st.stop()

    # Build sequence: origin → storage → other stops
    # Respect 25 total limit: origin + destination + waypoints ≤ 25
    # We will use optimize:true, so waypoints can be many (Google allows up to 25 including origin & destination).
    # We'll cap other stops as needed.
    max_total = 25
    # origin & destination count as 2 => waypoints ≤ 23
    leftover_waypoints = max_total - 2
