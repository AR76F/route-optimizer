# app.py – Route Optimizer with optional Geotab live map
# Works on Streamlit Cloud (Python 3.11 recommended)

import streamlit as st
import googlemaps
import polyline
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta, timezone
import mygeotab

# ======================================================================
# PAGE CONFIG
# ======================================================================
st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("📍 Route Optimizer — Home ➜ Storage ➜ Optimized Stops (≤ 25)")

# ======================================================================
# SECRETS: Google Maps API Key
# ======================================================================
api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
if not api_key:
    st.error("❌ Missing Google Maps API key in secrets.")
    st.stop()

gmaps = googlemaps.Client(key=api_key)

# ======================================================================
# GEOtab Helper Functions
# ======================================================================
@st.cache_resource(show_spinner=False)
def geotab_connect():
    """Connect once per session using Streamlit secrets."""
    server   = st.secrets.get("GEOTAB_SERVER")
    db       = st.secrets.get("GEOTAB_DATABASE")
    user     = st.secrets.get("GEOTAB_USERNAME")
    password = st.secrets.get("GEOTAB_PASSWORD")

    if not all([server, db, user, password]):
        raise RuntimeError("Missing one or more GEOTAB_* secrets.")

    api = mygeotab.API(server=server, database=db, username=user, password=password)
    api.authenticate()
    return api


def get_active_devices(api):
    """Return dict: device_id -> device (active only)."""
    devices = api.get("Device", search={"isActive": True})
    return {d["id"]: d for d in devices}


def get_drivers(api):
    """Return dict: driver_id -> user (drivers only)."""
    drivers = api.get("User", search={"isDriver": True, "isActive": True})
    return {u["id"]: u for u in drivers}


def get_latest_positions(api, hours=6):
    """Return latest GPS position per device."""
    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(hours=hours)
    logs = api.get("LogRecord", search={"fromDate": from_dt.isoformat(), "toDate": to_dt.isoformat()})
    latest = {}
    for r in logs:
        did = r.get("device", {}).get("id")
        if not did:
            continue
        lat, lon, dt = r.get("latitude"), r.get("longitude"), r.get("dateTime")
        if lat is None or lon is None:
            continue
        if did not in latest or dt > latest[did]["dateTime"]:
            latest[did] = r
    return latest


def driver_display_name(record, drivers, devices):
    """Show driver name first, fallback to device."""
    drv = record.get("driver")
    if isinstance(drv, dict):
        drv_id = drv.get("id")
        if drv_id and drv_id in drivers:
            return drivers[drv_id].get("name") or drivers[drv_id].get("firstName") or "Driver"
    did = record.get("device", {}).get("id")
    if did and did in devices:
        return devices[did].get("name") or "Device"
    return "Unknown"


def geotab_live_block():
    """Streamlit block showing live driver map & selector."""
    st.markdown("### 🚚 Live Fleet (Geotab)")
    enable = st.checkbox("Enable Geotab live view", value=False)
    start_latlng = None

    if not enable:
        return None

    try:
        api = geotab_connect()
    except Exception as e:
        st.error(f"⚠️ Could not connect to Geotab: {e}")
        return None

    with st.spinner("Fetching live driver positions..."):
        devices = get_active_devices(api)
        drivers = get_drivers(api)
        latest = get_latest_positions(api, hours=6)

    if not latest:
        st.warning("No recent GPS logs found.")
        return None

    # Prepare data
    rows = []
    for did, rec in latest.items():
        lat, lon, dt = rec["latitude"], rec["longitude"], rec["dateTime"]
        name = driver_display_name(rec, drivers, devices)
        dev_name = devices.get(did, {}).get("name", "Device")
        rows.append({
            "deviceId": did,
            "driverOrDeviceName": name,
            "deviceName": dev_name,
            "lat": lat,
            "lon": lon,
            "timestamp": dt
        })

    if not rows:
        st.warning("No positions found.")
        return None

    # Map
    avg_lat = sum(r["lat"] for r in rows) / len(rows)
    avg_lon = sum(r["lon"] for r in rows) / len(rows)
    fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=7, tiles="cartodbpositron")

    for r in rows:
        popup_html = f"""
            <b>{r['driverOrDeviceName']}</b><br/>
            <small>Unit: {r['deviceName']}</small><br/>
            <small>Updated: {r['timestamp']}</small>
        """
        folium.Marker(
            location=[r["lat"], r["lon"]],
            tooltip=r["driverOrDeviceName"],
            popup=folium.Popup(popup_html, max_width=280),
            icon=folium.Icon(color="red", icon="user", prefix="fa"),
        ).add_to(fmap)

    st_folium(fmap, height=480)

    names = [f"{r['driverOrDeviceName']} (unit: {r['deviceName']})" for r in rows]
    selection = st.selectbox("Use this driver as route start:", ["(none)"] + names)
    if selection != "(none)":
        idx = names.index(selection)
        sel = rows[idx]
        start_latlng = (sel["lat"], sel["lon"])
        st.success(f"✅ Route will start from {sel['driverOrDeviceName']}.")

    return start_latlng

# ======================================================================
# INPUTS SECTION
# ======================================================================
st.markdown("---")
start_from_driver = geotab_live_block()

col1, col2 = st.columns(2)
with col1:
    travel_mode = st.selectbox("Travel mode", ["driving", "walking", "bicycling"])
    round_trip = st.checkbox("Return home at end", value=True)
with col2:
    leave_now = st.checkbox("Leave now", value=True)

st.markdown("### Route stops")
home = st.text_input("Technician home (if not using Geotab)")
storage = st.text_input("Storage location")
stops = st.text_area("Other stops (one per line, max 23):")

if st.button("Optimize Route"):
    if not storage or (not home and not start_from_driver):
        st.error("Please specify at least a storage and home or a driver start.")
        st.stop()

    # Prepare waypoints
    waypoints = [s for s in stops.splitlines() if s.strip()]
    if len(waypoints) > 23:
        st.error("Too many stops! Max 23 waypoints.")
        st.stop()

    # Origin
    if start_from_driver:
        origin = start_from_driver
    else:
        origin = home

    # Directions
    try:
        directions = gmaps.directions(
            origin,
            storage,
            waypoints=waypoints,
            mode=travel_mode,
            optimize_waypoints=True
        )
    except Exception as e:
        st.error(f"Error fetching directions: {e}")
        st.stop()

    if not directions:
        st.warning("No route found.")
        st.stop()

    route = directions[0]
    leg = route["legs"]
    total_distance = sum([x["distance"]["value"] for x in leg]) / 1000
    total_duration = sum([x["duration"]["value"] for x in leg]) / 60

    st.success(f"✅ Route optimized: {total_distance:.1f} km, {total_duration:.1f} min")

    # Map
    m = folium.Map(location=[leg[0]["start_location"]["lat"], leg[0]["start_location"]["lng"]], zoom_start=10)
    for step in route["legs"]:
        points = polyline.decode(step["steps"][0]["polyline"]["points"])
        folium.PolyLine(points, color="blue", weight=3).add_to(m)
    st_folium(m, height=600)
