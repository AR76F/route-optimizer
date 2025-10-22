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

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
def secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch from Streamlit secrets or environment."""
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

def geocode(gmaps_client: googlemaps.Client, text: str) -> Optional[Tuple[float, float]]:
    if not text:
        return None
    try:
        res = gmaps_client.geocode(text)
        if res:
            loc = res[0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
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
# Stops
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("### Route stops")
start_text = st.text_input("Technician home (START)", placeholder="e.g., 123 Main St, City, Province")
storage_text = st.text_input("Storage location (first stop)", placeholder="e.g., 456 Depot Rd, City, Province")
stops_text = st.text_area(
    "Other stops (one ZIP/postal code or full address per line)",
    height=140,
    placeholder="H0H0H0\nG2P1L4\n…"
)
other_stops_input = [s.strip() for s in stops_text.splitlines() if s.strip()]

# ────────────────────────────────────────────────────────────────────────────────
# Geotab (via secrets only) — rate-limit safe, with DRIVER NAMES
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🚚 Live Fleet (Geotab)")

G_DB = secret("GEOTAB_DATABASE")
G_USER = secret("GEOTAB_USERNAME")
G_PWD = secret("GEOTAB_PASSWORD")
G_SERVER = secret("GEOTAB_SERVER", "my.geotab.com")
geotab_enabled_by_secrets = GEOTAB_AVAILABLE and all([G_DB, G_USER, G_PWD])

# refresh key (manual)
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

@st.cache_data(ttl=75, show_spinner=False)  # ~1 min
def _geotab_positions_for(api_params, device_ids, refresh_key):
    """
    Get last position for a small set of devices.
    Returns list of dicts: {deviceId, lat, lon, when, driverName?}
    """
    user, pwd, db, server = api_params
    api = _geotab_api_cached(user, pwd, db, server)

    results = []
    calls_made = 0
    limit_per_min = 9  # headroom

    for did in device_ids:
        if calls_made >= limit_per_min:
            results.append({"deviceId": did, "error": "rate_limit_guard"})
            continue

        # 1) DeviceStatusInfo (includes current driver if assigned)
        try:
            dsi = api.call("Get", typeName="DeviceStatusInfo", search={"deviceSearch": {"id": did}})
            calls_made += 1
            lat = lon = when = None
            driver_name = None
            if dsi:
                row = dsi[0]
                lat, lon = row.get("latitude"), row.get("longitude")
                when = row.get("dateTime") or row.get("lastCommunicated") or row.get("workDate")
                # driver name (when Geotab has an assignment)
                drv = row.get("driver")
                if isinstance(drv, dict):
                    driver_name = drv.get("name")
                # fallback for location field
                if (lat is None or lon is None) and isinstance(row.get("location"), dict):
                    lat = row["location"].get("y"); lon = row["location"].get("x")
            if lat is not None and lon is not None:
                results.append({"deviceId": did, "lat": float(lat), "lon": float(lon),
                                "when": when, "driverName": driver_name})
                continue
        except Exception as e:
            results.append({"deviceId": did, "error": f"dsi:{e}"})
            continue

        # 2) Fallback: latest LogRecord (only if needed; driver unknown here)
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
            names = {d["name"]: d["id"] for d in devs}
            picked_labels = st.multiselect(
                "Select drivers/devices to show:",
                options=list(names.keys()),
                default=[],
                help="Pick a few devices, then click Refresh."
            )

            if picked_labels:
                wanted_ids = [names[n] for n in picked_labels]
                pts = _geotab_positions_for((G_USER, G_PWD, G_DB, G_SERVER), tuple(wanted_ids), st.session_state.geo_refresh_key)

                valid = [p for p in pts if "lat" in p and "lon" in p]
                id2devname = {d["id"]: d["name"] for d in devs}

                if valid:
                    avg_lat = sum(p["lat"] for p in valid) / len(valid)
                    avg_lon = sum(p["lon"] for p in valid) / len(valid)
                    fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="cartodbpositron")

                    for p in valid:
                        device_label = id2devname.get(p["deviceId"], p["deviceId"])
                        driver_label = p.get("driverName") or "(no driver)"
                        who = f"{driver_label} — {device_label}"
                        color, lab = recency_color(p.get("when"))
                        add_marker(
                            fmap, p["lat"], p["lon"],
                            popup=folium.Popup(f"<b>{who}</b><br>Recency: {lab}<br>{p['lat']:.5f}, {p['lon']:.5f}", max_width=280),
                            icon=folium.Icon(color="green", icon="user", prefix="fa")
                        )
                        folium.CircleMarker([p["lat"], p["lon"]], radius=8, color="#222", weight=2,
                                            fill=True, fill_color=color, fill_opacity=0.9).add_to(fmap)

                    st_folium(fmap, height=420)

                    # NEW: choose a start based on driver/device label
                    choice_labels = [f"{p.get('driverName') or '(no driver)'} — {id2devname.get(p['deviceId'], p['deviceId'])}"
                                     for p in valid]
                    start_choice = st.selectbox("Use this driver/device as route start:", ["(none)"] + choice_labels)
                    if start_choice != "(none)":
                        chosen = valid[choice_labels.index(start_choice)]
                        start_text = reverse_geocode(gmaps_client, chosen["lat"], chosen["lon"])
                        st.success(f"Start set from Geotab: **{start_choice}** → {start_text}")

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
# Optimize route
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🧭 Optimize Route", type="primary"):
    start_ll = geocode(gmaps_client, start_text)
    storage_ll = geocode(gmaps_client, storage_text) if storage_text else None
    if not start_ll:
        st.error("Could not geocode the START location.")
        st.stop()
    if not storage_ll:
        st.error("Could not geocode the STORAGE location.")
        st.stop()

    waypoints = []
    if storage_text:
        waypoints.append(storage_text)
    waypoints.extend(other_stops_input)

    if len(waypoints) > 23:
        st.error("Too many stops. Google allows up to **25 total** (origin + destination + waypoints).")
        st.stop()

    if round_trip:
        destination = start_text
        optimized_waypoints = waypoints[:]
    else:
        destination = waypoints[-1] if waypoints else storage_text
        optimized_waypoints = waypoints[:]
        if destination in optimized_waypoints:
            optimized_waypoints.remove(destination)

    try:
        directions = gmaps_client.directions(
            origin=start_text,
            destination=destination,
            mode=travel_mode,
            waypoints=["optimize:true"] + optimized_waypoints if optimized_waypoints else None,
            departure_time=departure_dt if travel_mode == "driving" else None,
            traffic_model=traffic_model if travel_mode == "driving" else None,
        )
    except Exception as e:
        st.error(f"Directions API error: {e}")
        st.stop()

    if not directions:
        st.error("No route found from Google Directions.")
        st.stop()

    wp_order = directions[0].get("waypoint_order")
    ordered_list = [optimized_waypoints[i] for i in wp_order] if wp_order is not None else optimized_waypoints
    visit_texts = [start_text] + ordered_list + ([start_text] if round_trip else [destination])

    fmap = folium.Map(location=[start_ll[0], start_ll[1]], zoom_start=9, tiles="cartodbpositron")

    overview = directions[0]["overview_polyline"]["points"]
    path = polyline.decode(overview)
    folium.PolyLine(path, weight=7, color="#2196f3", opacity=0.9).add_to(fmap)

    folium.Marker(
        start_ll, icon=folium.Icon(color="green", icon="play", prefix="fa"),
        popup=folium.Popup(f"<b>START</b><br>{start_text}", max_width=260)
    ).add_to(fmap)

    for i, addr in enumerate(ordered_list, start=1):
        ll = geocode(gmaps_client, addr)
        if not ll:
            continue
        folium.Marker(
            ll, popup=folium.Popup(f"<b>{i}</b>. {addr}", max_width=260),
            icon=big_number_marker(str(i))
        ).add_to(fmap)

    end_ll = geocode(gmaps_client, visit_texts[-1])
    if end_ll:
        folium.Marker(
            end_ll, icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
            popup=folium.Popup(f"<b>{'END (Home)' if round_trip else 'END'}</b><br>{visit_texts[-1]}", max_width=260)
        ).add_to(fmap)

    st_folium(fmap, height=560)

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

# ────────────────────────────────────────────────────────────────────────────────
# Download this script (no file creation; uses module source)
# ────────────────────────────────────────────────────────────────────────────────
try:
    source_text = inspect.getsource(sys.modules[__name__])
    st.download_button("💾 Download this script (app.py)", data=source_text,
                       file_name="app.py", mime="text/x-python")
except Exception:
    st.caption("Download button unavailable in this environment.")
