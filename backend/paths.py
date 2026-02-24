# Identify stations by using node and cis (e.g. to distinguish Andel from Na Knizeci)
# At each stop (Node) check if node_id matches Target and if so, then check CIS to be sure
# If CIS doesnt match just check if it comes in a couple of stops on the trip (if not just call it a day with the Node)
# Disregard check for cis ids if station names on node dont match

import bisect
import datetime
import requests

from structs import *
from init import init_structures

#CURRENT RAM USAGE => 2400 MB

_stations, _stops, _lines, _service_ids = init_structures()

# Andel-MetroB : 1040;58759
# Amforova-Bus : 1029;47715

def console_end_nodes():
    print("Enter start (node;cis): ", end="")
    start = input().split(';')
    start_station = None
    try:
        start_found = False
        for station in _stations[int(start[0])]:
            if station.cis == int(start[1]):
                start_station = station
                start_found = True
        if not start_found: raise Exception("InvalidStation")
    except KeyError: raise Exception("InvalidStation")
    print(f"Start: {start_station.name} ({start_station.main_traffic_type}) [{",".join(start_station.zones)}]\n")

    print("Enter end (node;cis): ", end="")
    end = input().split(';')
    end_station = None
    try:
        end_found = False
        for station in _stations[int(end[0])]:
            if station.cis == int(end[1]):
                end_station = station
                end_found = True
        if not end_found: raise Exception("InvalidStation")
    except KeyError:
        raise Exception("InvalidStation")
    print(f"End: {end_station.name} ({end_station.main_traffic_type}) [{",".join(end_station.zones)}]")

    return start_station,end_station


#---------------------------------------------------------------------------------------------------

def get_end_nodes():
    return console_end_nodes()


def find_closest_departure(station, time=None) -> int:
    if not time:
        now = datetime.datetime.now()
        time = int(now.strftime("%H%M%S"))
    pos = bisect.bisect_left(station.all_movements, time, key=lambda d: d["departure_time"])
    return pos


def get_departures(station: Station|Stop, time=None, padding=3, default_count=10):
    now_index = find_closest_departure(station, time)


def get_line_departures(station: Station|Stop, line: Line, time=None, padding=3, default_count=10):
    pass


def get_unique_departures_now(station: Station|Stop, time=None, padding=3, search_pool_size=20):
    pass


def get_all_unique_departures(station: Station|Stop):
    pass  # Gets searched from station.move from index 0 -> For easiest finding trips for fastest route calculating (uniques are assumed from station.lines)
    # Maybe search from sometime before now cause there could be services limited to daytime (e.g. night transport, substitutes, morning/evening service)


if __name__ == "__main__":
    #s_node, e_node = get_end_nodes()
    s_node = _stations[1040][0]
    print(find_closest_departure(s_node))