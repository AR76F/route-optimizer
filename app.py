# app.py — Route Optimizer for Home ➜ Storage ➜ Optimized Stops (≤ 25)
# Works on Streamlit Cloud: reads API key from st.secrets["GOOGLE_MAPS_API_KEY"]

import streamlit as st
import googlemaps
import polyline
import folium
from streamlit.components.v1 import html
from datetime import datetime, time, timedelta

st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("📍 Optimisation des trajets (≤ 25 trajets)")

# ─────────────────────────────
# Secrets-aware API key input
# ─────────────────────────────
api_key_default = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
api_key = st.text_input("Google Maps API Key", value=api_key_default, type="password")

# ─────────────────────────────
# Inputs
# ─────────────────────────────
col0, col1 = st.columns(2)
travel_mode = col0.selectbox("Travel mode", ["driving", "walking", "bicycling"])
round_trip  = col1.checkbox("Return to home at the end (round trip)?", value=True)

st.markdown("### Traffic options (driving only)")
tcol1, tcol2, tcol3 = st.columns([1,1,2])
leave_now = tcol1.checkbox(
    "Leave now", value=True,
    help="If on, uses current live traffic. If off, pick a date/time below for predicted traffic."
)
traffic_model = tcol2.selectbox(
    "Traffic model",
    ["best_guess", "pessimistic", "optimistic"],
    help="Used only with driving."
)

# Default start time = now rounded to next 15 minutes
now = datetime.now().astimezone()
default_date = now.date()
rounded_min = ((now.minute // 15) + 1) * 15
default_time = time(hour=now.hour, minute=(0 if rounded_min == 60 else rounded_min))
if rounded_min == 60:
    default_date = (now + timedelta(hours=1)).date()

d = tcol3.date_input("Planned departure date", value=default_date, disabled=leave_now)
t = tcol3.time_input("Planned departure time", value=default_time, step=300, disabled=leave_now)

st.markdown("### Route stops")
home = st.text_input("Technician home (START)", placeholder="123 Main St, City, Province")
storage = st.text_input("Storage location (first stop)", placeholder="456 Depot Rd, City, Province")
stops_input = st.text_area(
    "Other stops (one ZIP/postal code or full address per line)",
    height=200,
    placeholder="H2Y1C6\nJ8X3X4\n123 Example Ave, City\n..."
)

# ─────────────────────────────
# Helpers
# ─────────────────────────────
def fmt_hm(seconds: int) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h} h {m} min" if h else f"{m} min"

def add_polyline_to_map(map_obj, overview_polyline_points, color="#1E90FF"):
    pts = polyline.decode(overview_polyline_points)
    folium.PolyLine(pts, color=color, weight=6, opacity=0.9).add_to(map_obj)
    return pts

def base_dir_kwargs():
    kwargs = dict(mode=travel_mode)
    if travel_mode == "driving":
        if leave_now:
            kwargs["departure_time"] = "now"  # live traffic
        else:
            chosen_dt = datetime.combine(d, t).astimezone()
            kwargs["departure_time"] = chosen_dt  # predicted traffic
        kwargs["traffic_model"] = traffic_model
    return kwargs

# ─────────────────────────────
# Action
# ─────────────────────────────
if st.button("Optimize Route") and api_key and home and storage:
    try:
        # Parse “other stops”
        raw_stops = [s.strip() for s in stops_input.splitlines() if s.strip()]
        # Remove accidental duplicates of home/storage
        other_stops = [s for s in raw_stops if s.lower() not in {home.lower(), storage.lower()}]

        # Validate total count (home + storage + other + home-if-roundtrip ≤ 25)
        total_planned_stops = 2 + len(other_stops) + (1 if round_trip else 0)
        if total_planned_stops > 25:
            st.error(f"Too many total stops ({total_planned_stops}). The limit is 25 (including start/end).")
            st.stop()

        gmaps = googlemaps.Client(key=api_key)

        # 1) Home ➜ Storage (fixed)
        kwargs1 = base_dir_kwargs()
        directions1 = gmaps.directions(origin=home, destination=storage, **kwargs1)
        if not directions1:
            st.error("No route found from Home to Storage. Please check the addresses.")
            st.stop()
        route1 = directions1[0]
        legs1 = route1["legs"]

        # 2) Storage ➜ optimized remaining ➜ (Home if round trip)
        route2 = None
        legs2 = []
        if other_stops or round_trip:
            if round_trip:
                dest2 = home
                waypoints2 = other_stops
            else:
                if len(other_stops) == 0:
                    dest2 = storage
                    waypoints2 = []
                elif len(other_stops) == 1:
                    dest2 = other_stops[0]
                    waypoints2 = []
                else:
                    dest2 = other_stops[-1]
                    waypoints2 = other_stops[:-1]

            kwargs2 = base_dir_kwargs()
            if len(waypoints2) > 0:
                directions2 = gmaps.directions(
                    origin=storage, destination=dest2,
                    waypoints=waypoints2, optimize_waypoints=True, **kwargs2
                )
            else:
                directions2 = gmaps.directions(
                    origin=storage, destination=dest2, **kwargs2
                )

            if not directions2:
                st.error("No route found after Storage. Please check the stops.")
                st.stop()

            route2 = directions2[0]
            legs2 = route2["legs"]

        # Combine legs & totals
        all_legs = legs1 + legs2
        total_distance_m = sum(leg["distance"]["value"] for leg in all_legs)
        total_distance_km = total_distance_m / 1000
        total_duration_s = sum(leg["duration"]["value"] for leg in all_legs)

        total_traffic_s = None
        if travel_mode == "driving":
            vals = [leg.get("duration_in_traffic", {}).get("value") for leg in all_legs]
            if all(v is not None for v in vals):
                total_traffic_s = sum(vals)

        st.success(f"Total distance: {total_distance_km:.1f} km")
        st.success(f"Total duration (typical): {fmt_hm(total_duration_s)}")
        if total_traffic_s is not None:
            label_time = "now" if leave_now else datetime.combine(d, t).strftime("%Y-%m-%d %H:%M")
            st.success(f"Total duration (traffic @ {label_time}): {fmt_hm(total_traffic_s)}  •  model: {traffic_model}")

        # ── Build map
        # Center from first polyline
        pts1 = polyline.decode(route1["overview_polyline"]["points"])
        avg_lat = sum(p[0] for p in pts1) / len(pts1)
        avg_lon = sum(p[1] for p in pts1) / len(pts1)
        fmap = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="OpenStreetMap")

        # Draw polylines (first leg in blue, second leg in purple)
        add_polyline_to_map(fmap, route1["overview_polyline"]["points"], color="#1E90FF")
        if route2 is not None:
            add_polyline_to_map(fmap, route2["overview_polyline"]["points"], color="#8A2BE2")  # blueviolet

        # Build markers from all legs
        markers = []
        for i, leg in enumerate(all_legs, start=1):
            s = leg["start_location"]
            markers.append((i, s["lat"], s["lng"], leg["start_address"]))
        end = all_legs[-1]["end_location"]
        markers.append((len(all_legs)+1, end["lat"], end["lng"], all_legs[-1]["end_address"]))

        # Draw markers:
        # idx 1 = Home (START), idx 2 = STORAGE, middle = numbered red, last = END (if not round trip)
        for idx, (lat, lon, name) in enumerate([(m[1], m[2], m[3]) for m in markers], start=1):
            is_first = (idx == 1)
            is_last  = (idx == len(markers))

            if is_first:
                # START (Home)
                folium.CircleMarker(
                    [lat, lon], radius=16, color="#006400", weight=2,
                    fill=True, fill_color="#32CD32", fill_opacity=1.0,
                    popup=f"START: {name}",
                ).add_to(fmap)
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=(
                        '<div style="font-size:16px;font-weight:800;'
                        'color:white;text-shadow:0 0 3px black;'
                        'text-align:center;transform:translate(-50%,-60%);">START</div>'
                    ))
                ).add_to(fmap)

            elif idx == 2:
                # STORAGE
                folium.CircleMarker(
                    [lat, lon], radius=16, color="#FF8C00", weight=2,
                    fill=True, fill_color="#FFA500", fill_opacity=1.0,
                    popup=f"STORAGE: {name}",
                ).add_to(fmap)
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=(
                        '<div style="font-size:16px;font-weight:800;'
                        'color:white;text-shadow:0 0 3px black;'
                        'text-align:center;transform:translate(-50%,-60%);">STORAGE</div>'
                    ))
                ).add_to(fmap)

            elif is_last and not round_trip:
                # END (only when not round trip)
                folium.CircleMarker(
                    [lat, lon], radius=16, color="#8B0000", weight=2,
                    fill=True, fill_color="#FF0000", fill_opacity=1.0,
                    popup="END: " + name,
                ).add_to(fmap)
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=(
                        '<div style="font-size:16px;font-weight:800;'
                        'color:white;text-shadow:0 0 3px black;'
                        'text-align:center;transform:translate(-50%,-60%);">END</div>'
                    ))
                ).add_to(fmap)

            else:
                # Middle waypoints (numbered)
                num = idx - 1  # since Stop 1 is STORAGE
                folium.CircleMarker(
                    [lat, lon], radius=14, color="#000000", weight=1,
                    fill=True, fill_color="#DC143C", fill_opacity=1.0,
                    popup=f"Stop {num}: {name}" if idx > 2 else f"Stop {idx}: {name}",
                ).add_to(fmap)
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=(
                        f'<div style="font-size:18px;font-weight:800;'
                        'color:white;text-shadow:0 0 3px black;'
                        'text-align:center;transform:translate(-50%,-60%);">'
                        f'{num if idx>2 else idx}</div>'
                    ))
                ).add_to(fmap)

        if round_trip:
            st.info("Round trip enabled: route returns to Home. START and END are the same location.")

        html(fmap._repr_html_(), height=600)

        # Ordered itinerary text
        st.subheader("Ordered itinerary")
        st.write(f"**START (Home):** {legs1[0]['start_address']}")
        st.write(f"**Stop 1 (STORAGE):** {legs1[0]['end_address']} ({legs1[0]['distance']['text']}, {legs1[0]['duration'].get('text','')})")
        if legs2:
            for i, leg in enumerate(legs2, start=2):
                line = f"**Stop {i}:** {leg['end_address']} ({leg['distance']['text']}, {leg['duration']['text']})"
                if travel_mode == "driving" and "duration_in_traffic" in leg:
                    line += f" • traffic: {leg['duration_in_traffic']['text']}"
                st.write(line)
        if not round_trip and legs2:
            st.write(f"**END:** {legs2[-1]['end_address']}")

    except googlemaps.exceptions.ApiError as e:
        st.error(f"Google Maps API error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
