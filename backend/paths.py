# Identify stations by using node and cis (e.g. to distinguish Andel from Na Knizeci)
# At each stop (Node) check if node_id matches Target and if so, then check CIS to be sure
# If CIS doesn't match just check if it comes in a couple of stops on the trip (if not just call it a day with the Node)
# Disregard check for cis ids if station names on node don't match

# For fastest route save by trips e.g. station1->station2 via Metro (7 intermediates|cca.13mins)

# Only allow metro and train to traverse the node -> switch station without transport only possible if getting of or on a metro/train
# Separate train station will be connected and not counted as node traversing

import bisect
import datetime
import heapq

from structs import *
from init import init_structures

#CURRENT RAM USAGE => 2400 MB

MINIMUM_DEPARTURE_COUNT = 5
CLOSEST_TO_LAST_DEPARTURE = 1500
LONGEST_TO_LAST_DEPARTURE = 10000

_stations, _stops, _lines, _service_ids = init_structures()

# Andel-MetroB : 1040;58759
# Amforova-Bus : 1029;47715

def console_end_nodes():
    start = input("Enter start (name-diacritics+space sensitive): ")
    start_station = get_station_by_name(start)
    if start is None:
        raise Exception("InvalidStationName")
    #start_found = False
    #for station in _stations.get(int(start[0]), []):
    #    if station.cis == int(start[1]):
    #        start_station = station
    #        start_found = True
    #if not start_found: raise Exception("InvalidStation")
    print(f"Start: {start_station.name} ({start_station.main_traffic_type}) [{",".join(start_station.zones)}]\n")

    end = input("Enter end (name-diacritics+space sensitive): ")
    end_station = get_station_by_name(end)
    if end is None:
        raise Exception("InvalidStationName")
    #end_found = False
    #for station in _stations[int(end[0])]:
    #    if station.cis == int(end[1]):
    #        end_station = station
    #        end_found = True
    #if not end_found: raise Exception("InvalidStation")
    print(f"End: {end_station.name} ({end_station.main_traffic_type}) [{",".join(end_station.zones)}]")

    if not are_ends_valid(start_station, end_station):
        raise Exception("InvalidRoute")

    return start_station,end_station


def get_temp_transfer_time(line1:Line, line2:Line):
    pass


def get_station_by_name(target_name):
    with open("stations.txt", "r", encoding="utf-8") as f:
        for line in f:
            name, node, cis = line.split(";")
            if name.lower() == target_name.lower():
                break
    for s in _stations[int(node)]:
        if s.cis == int(cis): return s
    return None


#---------------------------------------------------------------------------------------------------
def are_ends_valid(start, end):
    return not start.id == end.id


def time_to_seconds(t):
    return (t // 10000) * 3600 + ((t // 100) % 100) * 60 + (t % 100)


def seconds_to_time(s):
    return (s // 3600) * 10000 + ((s % 3600) // 60) * 100 + (s % 60)


def get_end_nodes():
    return console_end_nodes()


def find_closest_departure(station, time) -> int:
    pos = bisect.bisect_left(station.all_movements, time, key=lambda d: d["departure_time"])
    return pos


def is_departure_valid(departure:dict=None, date=None) -> bool:
    if not date:
        now = datetime.datetime.now()
        date = int(now.strftime("%Y%m%d"))
    else:
        now = datetime.datetime.strptime(str(date), "%Y%m%d")

    schedule: ServiceSchedule = departure["trip"].service
    day_of_week = int(now.strftime("%w"))-1
    if schedule.service_id[day_of_week] == "0":
        return False
    if schedule.start_date > date:
        return False
    if schedule.end_date < date:
        return False
    if date in schedule.exceptions:
        return False
    return True


def get_departure_index(station: Station|Stop, index):
    return station.all_movements[index]


def get_departure_time(station: Station|Stop, time):
    return station.all_movements[find_closest_departure(station, time)]


def get_next_departure(station: Station|Stop, index, time, date=None):
    if not date:
        now = datetime.datetime.now()
        date = int(now.strftime("%Y%m%d"))

    while True:
        if index >= len(station.all_movements):
            index = 0
            date += 1  # TODO: WARNING WONT WORK AT END OF MONTH EVENING
        departure = station.all_movements[index]
        if is_departure_valid(departure, date):
            return departure, index+1
        index += 1

def get_departures_strict(station: Station|Stop, time=None, count=10, padding=3):
    if not time:
        now = datetime.datetime.now()
        time = int(now.strftime("%H%M%S"))
    now_index = find_closest_departure(station, time+(padding*100))
    departures = []
    i = now_index
    while len(departures) < count:
        next_departure, i = get_next_departure(station, i, time)
        departures.append(next_departure)
    return departures


def get_departures(station: Station|Stop, time=None, padding=3, default_count=10):
    if not time:
        now = datetime.datetime.now()
        time = int(now.strftime("%H%M%S"))

    departures = get_departures_strict(station, time, default_count, padding)

    if time + LONGEST_TO_LAST_DEPARTURE >= departures[len(departures)-1]["departure_time"] >= time + CLOSEST_TO_LAST_DEPARTURE:
        return departures

    if departures[MINIMUM_DEPARTURE_COUNT]["departure_time"] > time + LONGEST_TO_LAST_DEPARTURE:
        pos = bisect.bisect_left(departures, time+LONGEST_TO_LAST_DEPARTURE, key=lambda d: d["departure_time"])
        return departures[:pos]
    else:
        i = find_closest_departure(station,departures[len(departures)-1]["departure_time"]) + 1
        while True:
            next_departure, i = get_next_departure(station, i, time)
            departures.append(next_departure)
            if next_departure["departure_time"] >= time + CLOSEST_TO_LAST_DEPARTURE: break
    return departures


def get_line_departures(station: Station|Stop, line: Line, time=None, padding=3, default_count=10):
    pass


def are_trips_similar(trip1:Trip, trip2:Trip) -> bool:
    #TODO: Might need rework (kind of quickly thought of sollution)
    return trip1.shape_id == trip2.shape_id


def get_unique_departures_now(station: Station|Stop, time=None, padding=3):
    # TODO: Very inefficient function (probably almost n^2)
    departures = get_departures(station,time,padding)
    unique_departures = []
    for departure in departures:
        similar = False
        for unique_departure in unique_departures:
            if are_trips_similar(departure["trip"], unique_departure["trip"]):
                similar = True
                break
        if similar: continue
        unique_departures.append(departure)
    return unique_departures


def get_all_unique_departures(station: Station|Stop):
    pass  # Gets searched from station.move from index 0 -> For easiest finding trips for fastest route calculating (uniques are assumed from station.lines)
    # Maybe search from sometime before now cause there could be services limited to daytime (e.g. night transport, substitutes, morning/evening service)


def node_traversing(arrival_trip, current_station, queued_time) -> list|None:
    extra = []
    if arrival_trip.parent_line.type == 1 or arrival_trip.parent_line.type == 2:
        for s in _stations[current_station.id]:
            if s == current_station: continue
            extra.extend(get_unique_departures_now(current_station, queued_time))
        return extra
    for s in _stations[current_station.id]:
        if s == current_station: continue
        if s.main_traffic_type == "train":
            extra.extend(get_unique_departures_now(s, queued_time))
        elif s.main_traffic_type[0] == "m":
            for sp in s.stops:
                if sp.platform[0] == "M":
                    extra.extend(get_unique_departures_now(sp, queued_time))
    return extra


def dijkstra_alfa(start: Station, end: Station, departure_time=None):
    start_time = time_to_seconds(int(datetime.datetime.now().strftime("%H%M00")) + 100)
    distances = {start: 0} #Station: relative distance
    predecessors = {start: None} #Station: movement dict (trip, arr, dep, i)
    relax_queue = [(0, 0, start)] #relative distance, distance from end, Station
    heapq.heapify(relax_queue)
    end_pos = [end.latitude, end.longitude]

    route_found = False
    while len(relax_queue) > 0:
        queued_distance, x, current_node = heapq.heappop(relax_queue)
        print("--" + current_node.name)
        if current_node == end:
            route_found = True
            break
        if queued_distance != distances[current_node]:
            continue

        queued_time = seconds_to_time(start_time+queued_distance)
        departures = get_unique_departures_now(current_node, queued_time)
        arrival = predecessors[current_node]
        if arrival:
            departures.append(arrival["departure_dict"])

        if len(_stations[current_node.id] > 1):
            extra = node_traversing(arrival["trip"], current_node, queued_time)
            if len(extra) > 0: departures.extend(extra)

        for departure in departures:
            print(departure)
            print(departure["trip"].parent_line.short_name, end="; ")
            next_stop_index = departure["stop_index"]+1
            if next_stop_index >= len(departure["trip"].stops):
                print(str(len(departure["trip"].stops)) + "ENDING")
                continue
            next_stop = departure["trip"].stops[next_stop_index]
            new_distance: int = time_to_seconds(next_stop["arrival_time"]) - start_time
            neighbour = next_stop["stop"].parent
            print(neighbour.name, end=" ")
            print(next_stop["arrival_time"], end=" ")
            if distances.get(neighbour, None) is None or new_distance < distances[neighbour]:
                print("(IN QUEUE)", end="")
                distances[neighbour] = new_distance
                predecessor_next = {
                    "trip": departure["trip"],
                    "arrival_time": next_stop["arrival_time"],
                    "departure_time": next_stop["departure_time"],
                    "stop_index": next_stop_index,
                    "stop_id": "" #TODO: Placeholder
                }
                predecessor_dict = {
                    "trip": departure["trip"],
                    "last_station": current_node,
                    "last_index": departure["stop_index"],
                    "last_departure": departure["departure_time"],
                    "current_arrival": next_stop["arrival_time"],
                    "departure_dict": predecessor_next
                }
                predecessors[neighbour] = predecessor_dict
                real_distance_index = abs(end_pos[0]-neighbour.latitude) + abs(end_pos[1]-neighbour.longitude)
                heapq.heappush(relax_queue, (new_distance, real_distance_index, neighbour))
            print()
    if not route_found:
        return {}

    print()
    raw_route = []
    current_node = end
    while current_node != start:
        print(current_node.name)
        predecessor = predecessors[current_node]
        # trip, departure stop, departure time, arrival stop, arrival time
        # previous -> current node
        edge = {
            "trip": predecessor["trip"],
            "departure_station": predecessor["last_station"],
            "departure_time": predecessor["last_departure"],
            "arrival_station": current_node,
            "arrival_time": predecessor["current_arrival"],
            "arrival_distance": distances[current_node]

        }
        raw_route.append(edge)
        current_node = predecessor["last_station"]
    print("reversing")
    raw_route.reverse()
    return raw_route


def humanize_route(raw_route):
    print("\nRoute:", end="")
    last_trip = None
    for connection in raw_route:
        if last_trip != connection["trip"]:
            print(f"\n\n{connection["trip"].parent_line.short_name} - "
                  f"{connection["departure_station"].name}", end="")
        print(f" {str(connection["departure_time"])}")
        print(f"-> {connection["arrival_station"].name} {connection["arrival_time"]}", end="")
        last_trip = connection["trip"]


if __name__ == "__main__":
    s_node, e_node = get_end_nodes()
    route = dijkstra_alfa(s_node, e_node)
    humanize_route(route)

# To implement: modular departure time, processing time saving measures, node traversing, start/end selection, fix the circulation of paths
# Check what how does program react when you arrive at terminus