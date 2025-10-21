# app.py — Route Optimizer with optional Geotab live origin
# Start (typed or Geotab) ➜ Storage ➜ Optimized Stops (≤ 25 total, traffic-aware)

import streamlit as st
import googlemaps
import polyline
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, time as dtime, timezone, timedelta
import mygeotab

# ────────────────────────────────────────────────────────────────────────────────
# Page config & title
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("📍 Route Optimizer — Start ➜ Storage ➜ Optimized Stops (≤ 25)")

# ────────────────────────────────────────────────────────────────────────────────
# Secrets-only Google Maps API key (fully hidden — no UI field)
# ────────────────────────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
except KeyError:
    st.error("❌ Google Maps API key missing. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

gmaps = googlemaps.Client(key=api_key)

# ────────────────────────────────────────────────────────────────────────────────
# Geotab helpers
# ────────────────────────────────────────────────────────────────────────────────
def geotab_connect():
    """Authenticate to Geotab using secrets and return an API instance."""
    try:
        db = st.secrets["GEOTAB_DATABASE"]
        user = st.secrets["GEOTAB_USERNAME"]
        pwd = st.secrets["GEOTAB_PASSWORD"]
        server = st.secrets.get("GEOTAB_SERVER", "my.geotab.com")
    except KeyError as e:
        raise RuntimeError(f"Geotab secret missing: {e}")

    api = mygeotab.API(username=user, password=pwd, database=db, server=server)
    api.authenticate()
    return api

@st.cache_data(ttl=300)
def geotab_list_devices():
    """Return list of active devices (id + name) for a dropdown."""
    api = geotab_connect()
    devices = api.get("Device", search={"isActive": True})
    options = [{"id": d["id"], "name": d.get("name", d.get("serialNumber", d["id"]))} for d in devices]
    options.sort(key=lambda x: x["name"].lower())
    return options

def geotab_device_location(device_id: str):
    """
    Return latest (lat, lon, timestamp) for a device using DeviceStatusInfo.
    """
    api = geotab_connect()
    dsi = api.call("Get", typeName="DeviceStatusInfo",
                   search={"deviceSearch": {"id": device_id}})
    if not dsi:
        raise RuntimeError("No DeviceStatusInfo found for this device.")
    info = dsi[0]
    lat = info.get("latitude")
    lon = info.get("longitude")
    ts = info.get("dateTime")  # ISO UTC string
    return lat, lon, ts

# ────────────────────────────────────────────────────────────────────────────────
# Inputs — travel, round-trip, traffic planning
# ────────────────────────────────────────────────────────────────────────────────
col0, col1 = st.columns([1, 1])
travel_mode = col0.selectbox("Travel mode", ["driving", "walking", "bicycling"])
round_trip = col1.checkbox("Return to start (round trip)?", value=True)

st.markdown("### Traffic options (driving only)")
tcol1, tcol2, tcol3 = st.columns([1, 1, 1])
leave_now = tcol1.checkbox("Leave now", value=True,
                           help="If on: live traffic. If off: pick a date/time for predicted traffic.")
traffic_model = tcol2.selectbox("Traffic model", ["best_guess", "pessimistic", "optimistic"])

# default time rounded to next 15 min
now = datetime.now()
rounded_min = ((now.minute // 15) + 1) * 15
default_time = dtime(hour=now.hour + (1 if rounded_min == 60 else 0),
                     minute=(0 if rounded_min == 60 else rounded_min))
default_date = (now + timedelta(hours=1)).date() if rounded_min == 60 else now.date()

dep_date = tcol2.date_input("Departure date", value=default_date, disabled=leave_now)
dep_time = tcol3.time_input("Departure time", value=default_time, step=300, disabled=leave_now)

# compute departure_time param (server local time is fine for Google)
departure_time = None
if travel_mode == "driving":
    departure_time = "now" if leave_now else datetime.combine(dep_date, dep_time)

# ────────────────────────────────────────────────────────────────────────────────
# Route stops — origin (typed or Geotab), storage, other stops
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("## Route stops")

# Origin
st.markdown("### Technician start (origin)")
use_geotab = st.toggle("Use Geotab live location", value=False,
                       help="ON: Pick a device and fetch its current GPS as origin.")

origin_value = None  # what we send to Google (can be 'lat,lon' or an address)
origin_label = ""    # nice label for UI

if use_geotab:
    with st.spinner("Connecting to Geotab…"):
        devices = []
        try:
            devices = geotab_list_devices()
        except Exception as e:
            st.error(f"Could not connect to Geotab: {e}")

    if devices:
        names = [d["name"] for d in devices]
        choice = st.selectbox("Geotab device", names, index=0)
        chosen_id = devices[names.index(choice)]["id"]
        if st.button("Fetch device location"):
            try:
                lat, lon, ts = geotab_device_location(chosen_id)
                origin_value = f"{lat},{lon}"  # Directions API accepts "lat,lon"
                when = ts
                try:
                    when = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                except Exception:
                    pass
                st.success(f"Using Geotab position for **{choice}** at **{when}** → `{origin_value}`")
                origin_label = f"Geotab: {choice}"
            except Exception as e:
                st.error(f"Failed to read location: {e}")
    else:
        st.info("No active devices found or access denied. Turn OFF Geotab toggle to type an origin manually.")

if not use_geotab or (use_geotab and origin_value is None):
    typed_origin = st.text_input("Start address/ZIP (if not using Geotab)",
                                 placeholder="123 Main St, City")
    if typed_origin.strip():
        origin_value = typed_origin.strip()
        origin_label = typed_origin.strip()

# Storage
storage = st.text_input("Storage location (first stop)", placeholder="456 Depot Rd, City")
# Other stops
stops_text = st.text_area("Other stops (one ZIP/postal code or full address per line)",
                          height=160, placeholder="H2Y1C6\nJ8X3X4\n123 Example Ave, City\n...")

# Validate minimal inputs
if not origin_value:
    st.warning("Please set an origin (Geotab live location or typed address).")
    st.stop()

if not storage.strip():
    st.warning("Please enter the storage location.")
    st.stop()

raw_stops = [s.strip() for s in stops_text.splitlines() if s.strip()]
# total waypoint count: start + storage + (stops) + (start again if round trip)
total_count = 2 + len(raw_stops) + (1 if round_trip else 0)
if total_count > 25:
    st.error(f"Too many total stops ({total_count}). Google Directions limit is 25 including start/end.")
    st.stop()

# ────────────────────────────────────────────────────────────────────────────────
# Google Directions helpers
# ────────────────────────────────────────────────────────────────────────────────
def call_directions(origin, destination, waypoints=None):
    """Wrap googlemaps directions call with traffic options."""
    kwargs = dict(origin=origin, destination=destination, mode=travel_mode)
    if waypoints:
        kwargs["waypoints"] = waypoints
    if travel_mode == "driving":
        kwargs["departure_time"] = departure_time  # "now" or datetime
        kwargs["traffic_model"] = traffic_model
    return gmaps.directions(**kwargs)

def decode_overview_polyline(route):
    return polyline.decode(route["overview_polyline"]["points"])

def legs_totals(route):
    """Return total meters and seconds (respect 'duration_in_traffic' if present)."""
    meters = 0
    seconds = 0
    for leg in route[0]["legs"]:
        meters += leg["distance"]["value"]
        if travel_mode == "driving" and "duration_in_traffic" in leg:
            seconds += leg["duration_in_traffic"]["value"]
        else:
            seconds += leg["duration"]["value"]
    return meters, seconds

def fmt_hm(seconds: int) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h} h {m} min" if h else f"{m} min"

# ────────────────────────────────────────────────────────────────────────────────
# Build route: Origin ➜ Storage, then Storage ➜ optimized(other stops) ➜ (Origin if round trip)
# ────────────────────────────────────────────────────────────────────────────────
# Leg A: Origin ➜ Storage
dir_A = call_directions(origin_value, storage)
if not dir_A:
    st.error("No route from origin to storage. Check addresses and API quotas.")
    st.stop()

# Leg B: Storage ➜ optimized(other stops) ➜ (Origin if round trip) | with fixed destination (required by optimize)
if round_trip:
    destination_B = origin_value
else:
    destination_B = raw_stops[-1] if raw_stops else storage

wp_opt_list = []
if raw_stops:
    wp_opt_list = ["optimize:true"] + (raw_stops if not round_trip else raw_stops)

dir_B = call_directions(
    storage,
    destination_B,
    waypoints="|".join(wp_opt_list) if wp_opt_list else None
)
if not dir_B:
    st.error("No route after storage. Check stops and quotas.")
    st.stop()

# Waypoint order for the optimized portion
wp_order = dir_B[0].get("waypoint_order", list(range(len(raw_stops))))
ordered_stops = [raw_stops[i] for i in wp_order] if raw_stops else []
if not round_trip and raw_stops:
    # Ensure the fixed destination (last raw stop) is last in display
    if raw_stops[-1] not in ordered_stops:
        ordered_stops.append(raw_stops[-1])

# Totals
mA, sA = legs_totals(dir_A)
mB, sB = legs_totals(dir_B)
km_total = (mA + mB) / 1000.0
st.subheader("Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Origin → Storage", f"{mA/1000:.1f} km", fmt_hm(sA))
c2.metric("Storage → Optimized stops" + (" → Start" if round_trip else ""), f"{mB/1000:.1f} km", fmt_hm(sB))
c3.metric("Total distance", f"{km_total:.1f} km")

# ────────────────────────────────────────────────────────────────────────────────
# Map (Folium)
# ────────────────────────────────────────────────────────────────────────────────
def center_from_route(route):
    pts = decode_overview_polyline(route[0])
    if not pts:
        return 45.5, -73.6  # fallback
    mid = pts[len(pts)//2]
    return mid[0], mid[1]

fmap = folium.Map(location=center_from_route(dir_A), zoom_start=8, tiles="cartodb dark_matter")

# Draw polylines
ptsA = decode_overview_polyline(dir_A[0])
ptsB = decode_overview_polyline(dir_B[0])
folium.PolyLine(ptsA, color="#00d1ff", weight=6, opacity=0.9).add_to(fmap)  # A: light blue
folium.PolyLine(ptsB, color="#8A2BE2", weight=6, opacity=0.9).add_to(fmap)  # B: blue-violet

# Marker helper (large badge)
def add_badge_marker(lat, lon, label, color="#ff4d4d"):
    html = f"""
    <div style="
         background:{color};
         color:white;
         border-radius:50%;
         width:36px;height:36px;
         display:flex;align-items:center;justify-content:center;
         font-weight:800;font-size:18px;border:2px solid white;">
      {label}
    </div>"""
    folium.Marker([lat, lon], icon=folium.DivIcon(html=html)).add_to(fmap)

# Simple geocode-to-latlng helper (handles "lat,lon" too)
def to_latlng(query: str):
    # Accept "lat,lon"
    if "," in query:
        try:
            lat_s, lon_s = [p.strip() for p in query.split(",", 1)]
            lat_f, lon_f = float(lat_s), float(lon_s)
            return lat_f, lon_f
        except Exception:
            pass
    # Otherwise geocode
    res = gmaps.geocode(query)
    if not res:
        return None
    loc = res[0]["geometry"]["location"]
    return loc["lat"], loc["lng"]

# Place markers:
#  1 = Origin, 2 = Storage, 3.. = optimized stops (order), last = Start if round-trip (we do not duplicate marker)
orig_ll = to_latlng(origin_value)
stor_ll = to_latlng(storage)
if orig_ll: add_badge_marker(orig_ll[0], orig_ll[1], "1", color="#2ecc71")   # green
if stor_ll: add_badge_marker(stor_ll[0], stor_ll[1], "2", color="#f39c12")   # orange

# Optimized stops after storage
for i, stop in enumerate(ordered_stops, start=3):
    ll = to_latlng(stop)
    if ll:
        add_badge_marker(ll[0], ll[1], str(i), color="#e74c3c")  # red

st_folium(fmap, height=600, width=None)

# ────────────────────────────────────────────────────────────────────────────────
# Text itinerary
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("Ordered Itinerary")
st.write(f"**START:** {origin_label or origin_value}")
st.write(f"**Stop 1 (STORAGE):** {dir_A[0]['legs'][0]['end_address']} ({dir_A[0]['legs'][0]['distance']['text']}, {dir_A[0]['legs'][0]['duration']['text']})")

# List the optimized leg B nicely
for idx, leg in enumerate(dir_B[0]["legs"], start=2):  # start=2 because stop 1 is storage
    end_addr = leg["end_address"]
    dist = leg["distance"]["text"]
    dur = (leg.get("duration_in_traffic") or leg["duration"])["text"] if travel_mode == "driving" else leg["duration"]["text"]
    if round_trip and idx == (2 + len(ordered_stops)):  # last leg returning to start
        st.write(f"**END (return to START):** {end_addr} ({dist}, {dur})")
    else:
        st.write(f"**Stop {idx}:** {end_addr} ({dist}, {dur})")

# Notes
with st.expander("Notes"):
    if travel_mode == "driving":
        when_label = "now" if leave_now else datetime.combine(dep_date, dep_time).strftime("%Y-%m-%d %H:%M")
        st.caption(f"Traffic model: **{traffic_model}** • Departure: **{when_label}**")
    st.caption("Waypoints are optimized after the storage stop. Total of start + storage + stops + (start again if round-trip) must be ≤ 25.")
