# app.py — Route Optimizer with optional Geotab live origin
# Start (typed or Geotab) → Storage → Optimized Stops (≤ 25 total, traffic-aware)

from __future__ import annotations

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
        raise RuntimeError(
            "No Google Maps API key. Add it in Streamlit Secrets as `GOOGLE_MAPS_API_KEY` or paste it above."
        )
    return googlemaps.Client(key=key)

def geocode_one(gmaps: googlemaps.Client, text_or_latlon):
    """Geocode an address string or (lat,lon) tuple into usable dict."""
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
    dur = leg.get("duration_in_traffic", {}).get("text") or leg.get("duration", {}).get("text", "—")
    return dist, dur

def build_route_map(path_coords, markers, center=None, zoom=8, height=700):
    """Create a Folium map with a route polyline and numbered red markers."""
    if not center and path_coords:
        center = [sum(p[0] for p in path_coords)/len(path_coords),
                  sum(p[1] for p in path_coords)/len(path_coords)]
    elif not center:
        center = [45.5, -73.6]  # fallback: Montreal-ish

    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    if path_coords:
        folium.PolyLine(path_coords, weight=6, opacity=0.9, color="#1E6CFF").add_to(m)

    for i, (lat, lon, label) in enumerate(markers, start=1):
        popup = folium.Popup(f"<b>{i}.</b> {label}", max_width=320)
        folium.Marker(
            [lat, lon],
            popup=popup,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    st_folium(m, height=height, use_container_width=True, returned_objects=[])

# ────────────────────────────────────────────────────────────────────────────────
# Geotab helpers (NO caching function takes the API object to avoid UnhashableParamError)
# ────────────────────────────────────────────────────────────────────────────────
def geotab_connect_from_secrets():
    db = st.secrets.get("GEOTAB_DATABASE", "")
    un = st.secrets.get("GEOTAB_USERNAME", "")
    pw = st.secrets.get("GEOTAB_PASSWORD", "")
    srv = st.secrets.get("GEOTAB_SERVER", "my.geotab.com")
    if not (db and un and pw):
        st.error("Geotab secrets missing. Set GEOTAB_DATABASE, GEOTAB_USERNAME, GEOTAB_PASSWORD.")
        return None
    try:
        api = myg.API(un, pw, db, srv)
        api.authenticate()
        return api
    except Exception as e:
        st.error(f"Geotab login failed: {e}")
        return None

def geotab_fetch_devices(api: "myg.API"):
    try:
        return api.call("Get", "Device", {"search": {"isActive": True}})
    except Exception:
        return []

def geotab_try_get_current_driver_diag(api: "myg.API"):
    """Try to find a 'current driver' diagnostic id if present."""
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

def geotab_load_user_names(api: "myg.API"):
    try:
        users = api.call("Get", "User", {"search": {"isDriver": True, "isActive": True}})
    except Exception:
        users = []
    return {
        u["id"]: (u.get("name") or (u.get("firstName", "") + " " + u.get("lastName", ""))).strip()
        for u in users
    }

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
            return user_names[str(v)], device.get("name", ""), when1
    # 2) Latest DriverChange
    uid, when2 = geotab_latest_driverchange(api, device["id"])
    if uid and uid in user_names:
        return user_names[uid], device.get("name", ""), when2
    # 3) Fallback to device name
    return device.get("name") or device.get("serialNumber") or device.get("vehicleIdentificationNumber") or "(unknown)", "", None

def render_geotab_live_block():
    """Large Geotab map; let user pick a driver as route start. Stores (lat,lon) in st.session_state['route_start_latlon']"""
    st.subheader("🚚 Live Fleet (Geotab)")

    if not GEOTAB_AVAILABLE:
        st.info("Geotab not installed on this server. Add `mygeotab` to requirements to enable.")
        return

    enable_geo = st.checkbox("Enable Geotab live view", value=False)
    if not enable_geo:
        st.session_state.pop("route_start_latlon", None)
        return

    api = geotab_connect_from_secrets()
    if not api:
        return

    devices = geotab_fetch_devices(api)
    user_names = geotab_load_user_names(api)
    driver_diag_id = geotab_try_get_current_driver_diag(api)

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

    avg_lat = sum(p["lat"] for p in pins)/len(pins)
    avg_lon = sum(p["lon"] for p in pins)/len(pins)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=7, tiles="CartoDB positron")
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
    driver_list = ["(none)"] + sorted({p["driver"] for p in pins if p["driver"]})
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

other_stops_text = st.text_area("Other stops (one ZIP/postal code or full address per line)", height=170, placeholder="H2Y 1C6\nJ4B 5E4\n...")

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

    # Determine origin: Geotab chosen driver overrides manual home
    if "route_start_latlon" in st.session_state:
        origin_info = geocode_one(gmaps_client, st.session_state["route_start_latlon"])
    else:
        origin_info = geocode_one(gmaps_client, home_addr)

    storage_info = geocode_one(gmaps_client, storage_addr)

    # Parse other stops
    raw_lines = [ln.strip() for ln in (other_stops_text or "").splitlines() if ln.strip()]
    other_infos = []
    for ln in raw_lines:
        gi = geocode_one(gmaps_client, ln)
        if gi: 
            other_infos.append(gi)

    # Safety checks
    if not origin_info:
        st.error("Please specify a valid Technician home (or pick a Geotab driver).")
        st.stop()
    if not storage_info:
        st.error("Please specify a valid Storage location.")
        st.stop()

    # Combine a maximum of 25 (origin + destination + waypoints <= 25 for a single call)
    # We'll do two calls: A) origin→storage, B) storage→others (+ optional return).
    max_total = 25

    # Departure time (Google only uses traffic for driving)
    departure_time = None
    if travel_mode == "driving":
        if leave_now:
            departure_time = datetime.now()
        else:
            # naive local dt is fine for Google client
            departure_time = datetime.combine(planned_date, planned_time)

    # ── LEG A: origin → storage ────────────────────────────────────────────────
    try:
        resp_a = gmaps_client.directions(
            origin=origin_info["raw"],
            destination=storage_info["raw"],
            mode=travel_mode,
            departure_time=departure_time if travel_mode == "driving" else None,
            traffic_model=traffic_model if travel_mode == "driving" else None
        )
    except Exception as e:
        st.error(f"Directions (origin → storage) failed: {e}")
        st.stop()

    if not resp_a:
        st.error("No route found from origin to storage.")
        st.stop()

    # Decode path
    path_coords = []
    if "overview_polyline" in resp_a[0]["overview_polyline"]:
        path_coords += polyline.decode(resp_a[0]["overview_polyline"]["points"])

    markers = [
        (origin_info["lat"], origin_info["lon"], f"START — {origin_info['label']}"),
        (storage_info["lat"], storage_info["lon"], f"Storage — {storage_info['label']}")
    ]

    total_distance_text = []
    total_duration_text = []
    for leg in resp_a[0]["legs"]:
        dist, dur = decode_distance_duration(leg)
        total_distance_text.append(dist)
        total_duration_text.append(dur)

    # ── LEG B: storage → others (+ return) with optimization ───────────────────
    if other_infos or round_trip:
        waypoints = []
        if other_infos:
            waypoints = ["optimize:true"] + [o["raw"] for o in other_infos]

        if round_trip:
            destination_b = origin_info["raw"]
        else:
            # If there's at least one other stop, make the last item the destination
            if other_infos:
                destination_b = other_infos[-1]["raw"]
                # waypoints already contains all others; remove the last from waypoints set:
                if len(waypoints) > 1:
                    waypoints = ["optimize:true"] + [o["raw"] for o in other_infos[:-1]]
            else:
                # no other stops, and no round trip: end at storage
                destination_b = storage_info["raw"]

        try:
            resp_b = gmaps_client.directions(
                origin=storage_info["raw"],
                destination=destination_b,
                mode=travel_mode,
                waypoints=waypoints if waypoints else None,
                departure_time=departure_time if travel_mode == "driving" else None,
                traffic_model=traffic_model if travel_mode == "driving" else None
            )
        except Exception as e:
            st.error(f"Directions (storage → rest) failed: {e}")
            st.stop()

        if not resp_b:
            st.error("No route found for the second leg (storage → stops).")
            st.stop()

        # Build waypoint order for markers if optimization was used
        ordered_others = other_infos[:]
        if waypoints and waypoints[0] == "optimize:true":
            # When optimize:true is used, the API returns `waypoint_order`
            wpo = resp_b[0].get("waypoint_order") or []
            if round_trip:
                ordered_others = [other_infos[i] for i in wpo]
            else:
                # destination fixed to the last other
                ordered_others = [other_infos[i] for i in wpo] + ([other_infos[-1]] if other_infos else [])

        # Decode path and append (avoid double-adding start point)
        if "overview_polyline" in resp_b[0]["overview_polyline"]:
            coords_b = polyline.decode(resp_b[0]["overview_polyline"]["points"])
            if path_coords and coords_b:
                if path_coords[-1] == coords_b[0]:
                    coords_b = coords_b[1:]
            path_coords += coords_b

        # Add markers for ordered others
        for o in ordered_others:
            markers.append((o["lat"], o["lon"], o["label"]))

        # If round trip, add home again
        if round_trip:
            markers.append((origin_info["lat"], origin_info["lon"], f"END — {origin_info['label']}"))

        # Add leg B distance/duration
        for leg in resp_b[0]["legs"]:
            dist, dur = decode_distance_duration(leg)
            total_distance_text.append(dist)
            total_duration_text.append(dur)

    # ───────────────────────────────────────────────────────────────────────────
    # Output: totals + big map
    # ───────────────────────────────────────────────────────────────────────────
    colm1, colm2 = st.columns(2)
    with colm1:
        st.metric("Legs distance (sum of displayed legs)", " + ".join(total_distance_text))
    with colm2:
        st.metric("Legs duration (traffic-aware if driving)", " + ".join(total_duration_text))

    st.markdown("#### Optimized route")
    build_route_map(path_coords, markers, height=700)
