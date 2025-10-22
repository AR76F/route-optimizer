# app.py — Route Optimizer + Geotab live view (last-known positions with recency colors)

import os
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Tuple, Optional

import streamlit as st
import googlemaps
import polyline
import folium
from streamlit_folium import st_folium

# --- Optional Geotab imports (soft dependency) ---
GEOTAB_AVAILABLE = True
try:
    import mygeotab as myg
except Exception:
    GEOTAB_AVAILABLE = False


# =========================
# Page config & Title
# =========================
st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("📍 Route Optimizer — Home ➜ Storage ➜ Optimized Stops (≤ 25)")

# =========================
# Helpers
# =========================
def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


def geocode_latlon_from_text(gmaps: googlemaps.Client, text: str) -> Optional[Tuple[float, float]]:
    """Geocode a free-form address/ZIP → (lat, lon)."""
    if not text:
        return None
    try:
        res = gmaps.geocode(text)
        if res:
            loc = res[0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
    except Exception:
        pass
    return None


def reverse_geocode(gmaps: googlemaps.Client, lat: float, lon: float) -> str:
    """Reverse geocode (lat, lon) → human readable address (best effort)."""
    try:
        res = gmaps.reverse_geocode((lat, lon))
        if res:
            return res[0].get("formatted_address", f"{lat:.5f},{lon:.5f}")
    except Exception:
        pass
    return f"{lat:.5f},{lon:.5f}"


def big_number_marker(n: str, color_hex: str = "#cc3333"):
    """Folium DivIcon with big number bubble."""
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


# =========================
# Google Maps API key
# =========================
gmaps_key = get_secret("GOOGLE_MAPS_API_KEY")
col_key1, col_key2 = st.columns([3, 1])
with col_key1:
    if not gmaps_key:
        gmaps_key = st.text_input("Google Maps API Key", type="password", placeholder="Enter your key…")

if not gmaps_key:
    st.info("Add your Google Maps API key in **App settings → Secrets** as `GOOGLE_MAPS_API_KEY` "
            "or enter it above to enable route optimization.")
    st.stop()

gmaps = googlemaps.Client(key=gmaps_key)

# =========================
# Inputs – mode, traffic, round-trip
# =========================
colm1, colm2, colm3 = st.columns([1.2, 1.2, 2])
with colm1:
    travel_mode = st.selectbox("Travel mode", ["driving", "walking", "bicycling"])

with colm2:
    round_trip = st.checkbox("Return to home at the end (round trip)?", value=True)

st.markdown("### Traffic options (driving only)")
tc1, tc2, tc3 = st.columns([1, 1, 1])
with tc1:
    leave_now = st.checkbox("Leave now", value=True, help="If ON, departure time is now (uses live traffic).")
with tc2:
    traffic_model = st.selectbox(
        "Traffic model",
        ["best_guess", "pessimistic", "optimistic"],
        help="Only used with driving + departure time."
    )
with tc3:
    planned_date = st.date_input("Planned departure date", value=date.today(), disabled=leave_now)
    planned_time = st.time_input("Planned departure time", value=datetime.now().time(), disabled=leave_now)

# build departure time for Google
if leave_now:
    departure_dt = datetime.now(timezone.utc)
else:
    local_dt = datetime.combine(planned_date, planned_time)
    # treat as local time → naive; Google accepts naive but we convert to aware UTC to be consistent
    departure_dt = local_dt.replace(tzinfo=timezone.utc)

# =========================
# Route stops: start/storage/others
# =========================
st.markdown("### Route stops")

# These will be overridden if the user picks a Geotab driver later.
start_text = st.text_input("Technician home (START)", placeholder="e.g., 123 Main St, City, Province")
storage_text = st.text_input("Storage location (first stop)", placeholder="e.g., 456 Depot Rd, City, Province")

stops_text = st.text_area(
    "Other stops (one ZIP/postal code or full address per line)",
    height=140,
    placeholder="H0H0H0\nG2P1L4\n…"
)

# Parse user stops
other_stops_input = [s.strip() for s in stops_text.splitlines() if s.strip()]

# =========================
# Geotab block (optional)
# =========================
st.markdown("---")
st.subheader("🚚 Live Fleet (Geotab)")

enable_geotab = st.checkbox("Enable Geotab live view", value=False)
picked_driver_choice = None        # text for the selectbox
picked_driver_latlon = None        # lat, lon

def geotab_connect() -> Optional["myg.API"]:
    """Connect to MyGeotab using secrets or optional text inputs."""
    if not GEOTAB_AVAILABLE:
        st.warning("myGeotab library not available. Install `mygeotab` in requirements.txt to enable.")
        return None

    db = get_secret("GEOTAB_DATABASE")
    user = get_secret("GEOTAB_USERNAME")
    pwd = get_secret("GEOTAB_PASSWORD")
    server = get_secret("GEOTAB_SERVER", "my.geotab.com")

    with st.expander("Geotab connection (optional)"):
        c1, c2 = st.columns(2)
        with c1:
            db = st.text_input("Database", value=db or "")
            user = st.text_input("Username", value=user or "")
        with c2:
            server = st.text_input("Server", value=server or "my.geotab.com")
            pwd = st.text_input("Password", value=pwd or "", type="password")

    if not all([db, user, pwd, server]):
        st.info("Provide Geotab credentials (or set them in Secrets) to view live fleet.")
        return None

    try:
        api = myg.API(user, pwd, db, server)
        api.authenticate()
        return api
    except Exception as e:
        st.error(f"Failed to connect to Geotab: {e}")
        return None


def geotab_get_devices(api: "myg.API") -> List[dict]:
    """All devices that are active."""
    try:
        devices = api.call("Get", "Device", {"search": {"isActive": True}})
        return devices or []
    except Exception:
        return []


def geotab_load_device_position_anytime(api: "myg.API", device_id: str):
    """
    Prefer Geotab's last-known snapshot (DeviceStatusInfo).
    If not available, fall back to LogRecord look-back windows.
    Returns (lat, lon, when) or (None, None, None).
    """
    # 1) Try DeviceStatusInfo snapshot
    try:
        dsi_list = api.call("Get", "DeviceStatusInfo", {"search": {"deviceSearch": {"id": device_id}}})
        if not dsi_list:
            dsi_list = api.call("Get", "DeviceStatusInfo", {"search": {"device": {"id": device_id}}})
        if dsi_list:
            dsi = dsi_list[0]
            lat = dsi.get("latitude")
            lon = dsi.get("longitude")
            when = dsi.get("dateTime") or dsi.get("lastCommunicated") or dsi.get("workDate")
            if (lat is None or lon is None) and isinstance(dsi.get("location"), dict):
                lat = dsi["location"].get("y")
                lon = dsi["location"].get("x")
            if lat is not None and lon is not None:
                return float(lat), float(lon), when
    except Exception:
        pass

    # 2) Fallback: LogRecord with expanding windows
    windows = [timedelta(hours=2), timedelta(hours=24), timedelta(days=7), timedelta(days=30)]
    for win in windows:
        try:
            from_dt = (datetime.now(timezone.utc) - win).isoformat()
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


def recency_color(ts: Optional[str]) -> Tuple[str, str]:
    """
    Return (hex_color, label) for marker based on how recent a timestamp is.
    """
    if not ts:
        return "#7f7f7f", "> 30d"
    try:
        # Geotab returns ISO-like string; parse naively
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return "#7f7f7f", "unknown"

    age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
    if age <= timedelta(hours=2):
        return "#00c853", "≤ 2h"       # bright green
    if age <= timedelta(hours=24):
        return "#2e7d32", "≤ 24h"      # green
    if age <= timedelta(days=7):
        return "#fb8c00", "≤ 7d"       # orange
    return "#9e9e9e", "> 7d"            # grey


if enable_geotab:
    api = geotab_connect()
    if api:
        devices = geotab_get_devices(api)

        # get positions
        fleet_points = []
        for d in devices:
            lat, lon, when = geotab_load_device_position_anytime(api, d["id"])
            if lat is None or lon is None:
                continue

            # Try to get driver name if available via DeviceStatusInfo
            driver_name = None
            try:
                dsi = api.call("Get", "DeviceStatusInfo", {"search": {"deviceSearch": {"id": d["id"]}}})
                if dsi and isinstance(dsi[0].get("driver"), dict):
                    driver_name = dsi[0]["driver"].get("name")
            except Exception:
                driver_name = None

            fleet_points.append({
                "deviceId": d["id"],
                "deviceName": d.get("name") or d.get("serialNumber") or "unit",
                "driverName": driver_name,
                "lat": lat, "lon": lon,
                "when": when
            })

        # draw fleet map
        fleet_map_height = 360
        if fleet_points:
            # center map
            avg_lat = sum(p["lat"] for p in fleet_points) / len(fleet_points)
            avg_lon = sum(p["lon"] for p in fleet_points) / len(fleet_points)
            fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=7, tiles="cartodbpositron")

            for p in fleet_points:
                color, lab = recency_color(p["when"])
                name = p["driverName"] or p["deviceName"]
                popup = folium.Popup(
                    f"<b>{name}</b><br>Recency: {lab}<br>{p['lat']:.5f}, {p['lon']:.5f}",
                    max_width=260
                )
                add_marker(
                    fmap, p["lat"], p["lon"], popup,
                    icon=folium.Icon(color="green", icon="user", prefix="fa")
                )
                # overlay colored dot for recency
                folium.CircleMarker(
                    [p["lat"], p["lon"]],
                    radius=8, color="#222", weight=2,
                    fill=True, fill_color=color, fill_opacity=0.9
                ).add_to(fmap)

            st_folium(fmap, height=fleet_map_height, use_container_width=True)
        else:
            st.info("No recent positions found. (Tried last-known snapshot and up to 30-day fallback)")

        # Choose driver as route start
        name_map = []
        for p in fleet_points:
            label = p["driverName"] or p["deviceName"]
            name_map.append((label, p["lat"], p["lon"]))
        name_map.sort(key=lambda x: x[0].lower())

        picked_driver_choice = st.selectbox(
            "Use this driver as route start:",
            options=["(none)"] + [nm[0] for nm in name_map],
            index=0
        )

        if picked_driver_choice != "(none)":
            for nm in name_map:
                if nm[0] == picked_driver_choice:
                    picked_driver_latlon = (nm[1], nm[2])
                    break

            if picked_driver_latlon:
                # override start_text with reverse geocode for readability
                addr = reverse_geocode(gmaps, picked_driver_latlon[0], picked_driver_latlon[1])
                start_text = addr
                st.success(f"Start set from Geotab: **{picked_driver_choice}** → {addr}")

# =========================
# Route Optimization (Google Directions with optimize:true)
# =========================
st.markdown("---")
if st.button("🧭 Optimize Route", type="primary"):
    # Build origin/destination/waypoints
    # Resolve start
    start_ll = geocode_latlon_from_text(gmaps, start_text)
    if not start_ll:
        st.error("Could not geocode the START location.")
        st.stop()

    storage_ll = geocode_latlon_from_text(gmaps, storage_text) if storage_text else None
    if not storage_ll:
        st.error("Could not geocode the STORAGE location.")
        st.stop()

    remain_addrs = other_stops_input[:]

    # Google supports waypoints=optimize:true; we will provide them:
    # order: [storage] + others
    waypoints = []
    if storage_text:
        waypoints.append(storage_text)
    waypoints.extend(remain_addrs)

    if len(waypoints) > 23:
        st.error("Too many stops. Google allows up to 25 total (origin + destination + waypoints). "
                 "Reduce the number of waypoints.")
        st.stop()

    # destination
    if round_trip:
        destination = start_text
    else:
        destination = waypoints[-1] if waypoints else storage_text

    # If not round trip and we used last stop as destination, we must exclude it from waypoints set
    # to avoid duplication.
    optimized_waypoints = waypoints[:]
    if not round_trip and destination in optimized_waypoints:
        optimized_waypoints.remove(destination)

    # Directions request
    try:
        directions = gmaps.directions(
            origin=start_text,
            destination=destination,
            mode=travel_mode,
            waypoints=["optimize:true"] + optimized_waypoints if optimized_waypoints else None,
            departure_time=departure_dt if travel_mode == "driving" else None,
            traffic_model=traffic_model if travel_mode == "driving" else None
        )
        if not directions:
            st.error("No route found from Google Directions.")
            st.stop()
    except Exception as e:
        st.error(f"Directions API error: {e}")
        st.stop()

    # Decode optimized order
    order = []
    wp_order = directions[0].get("waypoint_order")
    if wp_order is not None:
        # Rebuild visit list based on Google's optimal order
        ordered_list = [optimized_waypoints[i] for i in wp_order]
    else:
        ordered_list = optimized_waypoints

    # Build full sequence of coordinates in visit order
    visit_texts = []
    visit_texts.append(start_text)          # 0: Start
    visit_texts.extend(ordered_list)        # 1..N-1: waypoints
    if round_trip:
        visit_texts.append(start_text)      # End = back to start
    else:
        visit_texts.append(destination)     # End

    # Build map centered roughly on start
    fmap = folium.Map(location=[start_ll[0], start_ll[1]], zoom_start=9, tiles="cartodbpositron")

    # Draw big route polyline (overview)
    overview = directions[0]["overview_polyline"]["points"]
    path = polyline.decode(overview)
    folium.PolyLine(
        locations=path,
        weight=7,
        color="#2196f3",
        opacity=0.9
    ).add_to(fmap)

    # Markers
    # Start marker
    folium.Marker(
        location=start_ll,
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
        popup=folium.Popup(f"<b>START</b><br>{start_text}", max_width=260)
    ).add_to(fmap)

    # Numbered stops (ordered_list)
    for i, addr in enumerate(ordered_list, start=1):
        ll = geocode_latlon_from_text(gmaps, addr)
        if not ll:
            continue
        folium.Marker(
            location=ll,
            popup=folium.Popup(f"<b>{i}</b>. {addr}", max_width=260),
            icon=big_number_marker(str(i))
        ).add_to(fmap)

    # End marker
    end_label = "END (Home)" if round_trip else "END"
    end_ll = geocode_latlon_from_text(gmaps, visit_texts[-1])
    if end_ll:
        folium.Marker(
            location=end_ll,
            icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
            popup=folium.Popup(f"<b>{end_label}</b><br>{visit_texts[-1]}", max_width=260)
        ).add_to(fmap)

    st_folium(fmap, height=560, use_container_width=True)

    # Show textual order + totals
    legs = directions[0]["legs"]
    total_dist_m = sum(leg["distance"]["value"] for leg in legs)
    # Prefer duration_in_traffic if present (driving + departure_time)
    total_sec = sum(leg.get("duration_in_traffic", leg["duration"])["value"] for leg in legs)
    st.markdown("#### Optimized order")
    for ix, addr in enumerate(visit_texts, start=0):
        if ix == 0:
            st.write(f"**START** — {addr}")
        elif ix == len(visit_texts) - 1:
            st.write(f"**END** — {addr}")
        else:
            st.write(f"**{ix}** — {addr}")

    km = total_dist_m / 1000.0
    mins = total_sec / 60.0
    st.success(f"**Total distance:** {km:.1f} km • **Total time:** {mins:.0f} mins "
               f"{'(live traffic)' if travel_mode=='driving' else ''}")
