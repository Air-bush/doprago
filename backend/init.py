import csv

from structs import *
import requests

GTFS_LOCATION = "tempFiles/"
raw_stations = requests.get("https://data.pid.cz/stops/json/stops.json").json()["stopGroups"]

def init_stations(all_lines) -> dict[int,list[Station]]:  # node:object/list
    all_stations = {}  # key: node_id, value: Station !!!! VALUE MIGHT BE A LIST (IN CASE MULTIPLE STATIONS PER NODE)
    for raw_station in raw_stations:
        node_id = raw_station["node"]
        gtfs_id = f"U{node_id}"
        cis = int(raw_station["cis"])
        name = raw_station["name"]
        latitude = raw_station["avgLat"]
        longitude = raw_station["avgLon"]
        main_traffic_type = raw_station["mainTrafficType"]
        station = Station(gtfs_id, node_id, cis, name, latitude, longitude, main_traffic_type)
        stops: list[Stop] = []
        for stop in raw_station["stops"]:
            stops.append(init_stop(stop, station, all_lines))
        station.stops = stops
        station_zones = []
        station_lines = []
        for stop in stops:
            for zone in stop.zones:
                if zone not in station_zones:
                    station_zones.append(zone)
            for line in stop.lines.keys():
                if line not in station_lines:
                    station_lines.append(line)
        station.zones = station_zones
        station.lines = station_lines
        transfers: dict  # Key: (fromStop, toStop) Value: minTransferTime TODO: Implement
        if all_stations.get(node_id, None) is not None:
            all_stations[node_id].append(station)
        else:
            all_stations[node_id] = [station]
    return all_stations


def init_stop(stop_data: dict, parent_station: Station, all_lines) -> Stop:
    parent = parent_station
    gtfs_ids = stop_data["gtfsIds"]
    node_id = stop_data["id"]
    name = stop_data["altIdosName"]
    latitude = stop_data["lat"]
    longitude = stop_data["lon"]
    zones = stop_data["zone"].split(",")
    platform_code = stop_data.get("platform", UNDEFINED)
    main_traffic_type = stop_data["mainTrafficType"]
    stop = Stop(parent, gtfs_ids, node_id, name, latitude, longitude, zones, platform_code, main_traffic_type)
    wheelchair = stop_data["wheelchairAccess"]
    if wheelchair == "possible":
        stop.wheelchair_boarding = POSSIBLE
    elif wheelchair == "notPossible":
        stop.wheelchair_boarding = NOT_POSSIBLE
    stop_lines = {}  # key: Line, val: Line direction indexes stopping at this stations/end stations TODO: implement
    for line_data in stop_data["lines"]:
        line = all_lines[f"L{line_data["id"]}"]
        direction = line_data["direction"]
        direction2 = line_data.get("direction2", None)
        terminus = None
        terminus2 = None
        for raw_station in raw_stations:  # TODO: TEST AND FINISH -> FIX FIX FIX
            if raw_station["name"] == direction:
                terminus = raw_station["node"]
                if direction2 is None or terminus2 is not None:
                    break
            if direction2 is None:
                continue
            if raw_station["name"] == direction2:
                terminus2 = raw_station["node"]
                if terminus is not None:
                    break
        stop_lines[line] = [direction]
        if direction not in line.directions:
            line.directions.append(direction)
        if not direction2:
            continue
        stop_lines[line].append(direction2)
        if direction2 not in line.directions:
            line.directions.append(direction2)
    stop.lines = stop_lines
    return stop

def init_lines() -> dict[str,Line]:
    all_routes = {}  # key: route_id, val: Line
    with open(GTFS_LOCATION + "routes.txt", encoding="UTF-8") as routes_file:
        routes_reader = csv.DictReader(routes_file, delimiter=",")
        routes_data = list(routes_reader)
    for route_data in routes_data:
        route_id = route_data["route_id"]
        short_name = route_data.get("route_short_name", None)
        long_name = route_data.get("route_long_name", None)
        route_type = int(route_data["route_type"])
        color = route_data["route_color"]
        text_color = route_data["route_text_color"]
        is_night = bool(int(route_data["is_night"]))
        is_regional = bool(int(route_data["is_regional"]))
        is_substitute = bool(int(route_data["is_substitute_transport"]))
        route = Line(route_id, short_name, long_name, route_type, color,
                     text_color, is_night, is_regional, is_substitute)
        trips: dict  # key: direction_id, val: list of trips per direction  # TODO: Implement
        all_routes[route_id] = route
    return all_routes


def init_line_stations(all_routes: dict, all_stations: dict):
    with open(GTFS_LOCATION + "route_stops.txt", encoding="UTF-8") as sequence_file:  # Line.stops -> Sequence == index + 1
        sequence_reader = csv.DictReader(sequence_file, delimiter=",")
        sequence_data = list(sequence_reader)
    current_route = sequence_data[0]["route_id"]
    current_sequence = {}
    for stop_line in sequence_data:
        if current_route != stop_line["route_id"]:
            all_routes[current_route].stops = current_sequence
            current_sequence = {}
            current_route = stop_line["route_id"]
        if current_sequence.get(stop_line["direction_id"], None) is None:
            current_sequence[stop_line["direction_id"]] = []
        for station in all_stations[int(stop_line["stop_id"][1:].split("Z")[0])]:
            for stop in station.stops:
                if stop_line["stop_id"] in stop.gtfs_ids:
                    current_sequence[stop_line["direction_id"]].append(stop)

def find_station_by_name(name, all_stations) -> Station|None:
    for node in all_stations.values():
        for station in node:
            if station.name == name:
                return station

def init_structures():
    all_lines = init_lines()
    all_stations = init_stations(all_lines)
    init_line_stations(all_lines, all_stations)
    return all_stations, all_lines


if __name__ == "__main__":
    stations, lines = init_structures()

    for s in stations[1029]:
        for ss in s.stops:
            for l in ss.lines:
                print(l.short_name)
    #    for l in s.lines:
    #        print(f"{l.short_name}")
    #    print(s.to_string())

    #print(lines["L993"].short_name + " -> " + lines["L993"].long_name)

    #for d in lines["L993"].stops:
    #    print(d + ": ", end="")
    #    for s in lines["L993"].stops[d]:
    #        print(s.alternative_name, end=", ")
    #    print()
