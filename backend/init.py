import csv

from structs import *
import requests

GTFS_LOCATION = "tempFiles/"


def init_stations() -> dict[int,list[Station]]:  # node:object/list
    all_stations = {}  # key: node_id, value: Station !!!! VALUE MIGHT BE A LIST (IN CASE MULTIPLE STATIONS PER NODE)
    response = requests.get("https://data.pid.cz/stops/json/stops.json")
    raw_stations = response.json()["stopGroups"]
    for raw_station in raw_stations:
        node_id = raw_station["node"]
        gtfs_id = f"U{node_id}"
        cis = int(raw_station["cis"])
        name = raw_station["name"]
        latitude = raw_station["avgLat"]
        longitude = raw_station["avgLon"]
        main_traffic_type = raw_station["mainTrafficType"]
        station = Station(gtfs_id, node_id, cis, name, latitude, longitude, main_traffic_type)
        station_lines: list  # TODO: Implement
        stops: list[Stop] = []
        for stop in raw_station["stops"]:
            stops.append(init_stop(stop, station))
        station.stops = stops
        station_zones = []
        for stop in stops:
            for zone in stop.zones:
                if zone not in station_zones:
                    station_zones.append(zone)
        station.zones = station_zones
        transfers: dict  # Key: (fromStop, toStop) Value: minTransferTime TODO: Implement
        if all_stations.get(node_id, None) is not None:
            all_stations[node_id].append(station)
        else:
            all_stations[node_id] = [station]
    return all_stations


def init_stop(stop_data: dict, parent_station: Station) -> Stop:
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
    stop_lines: dict  # key: Line, val: Line direction indexes stopping at this stations TODO: implement
    return stop


def init_lines(all_stations) -> dict[str,Line]:
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
        directions: dict  # key: direction_id, val: head_sign/last_stop  # TODO: Implement -> May not be possible due to variable route length
        trips: dict  # key: direction_id, val: list of trips per direction  # TODO: Implement
        all_routes[route_id] = route

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

    return all_routes


if __name__ == "__main__":
    stations = init_stations()
    lines = init_lines(stations)

    #for s in stations[2704]:
    #    print(s.to_string())

    #print(lines["L993"].short_name + " -> " + lines["L993"].long_name)

    #for d in lines["L993"].stops:
    #    print(d + ": ", end="")
    #    for s in lines["L993"].stops[d]:
    #        print(s.alternative_name, end=", ")
    #    print()
