# Identify stations by using node and cis (e.g. to distinguish Andel from Na Knizeci)
# At each stop (Node) check if node_id matches Target and if so, then check CIS to be sure
# If CIS doesn't match just check if it comes in a couple of stops on the trip (if not just call it a day with the Node)
# Disregard check for cis ids if station names on node don't match

# For fastest route save by trips e.g. station1->station2 via Metro (7 intermediates|cca.13mins)

# Only allow metro and train to traverse the node

import bisect
import datetime

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


def get_temp_transfer_time(line1:Line, line2:Line):
    pass


#---------------------------------------------------------------------------------------------------
def get_end_nodes():
    return console_end_nodes()


def find_closest_departure(station, time=None) -> int:
    if not time:
        now = datetime.datetime.now()
        time = int(now.strftime("%H%M%S"))
    pos = bisect.bisect_left(station.all_movements, time, key=lambda d: d["departure_time"])
    return pos


def is_departure_valid(departure:dict=None, date=None) -> bool:
    if not date:
        now = datetime.datetime.now()
        date = int(now.strftime("%Y%m%d"))
    else:
        now = datetime.datetime.strptime(date, "%Y%m%d")

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


def get_next_departure(station: Station|Stop, index, date=None):
    while True:
        departure = station.all_movements[index]
        if is_departure_valid(departure):
            return departure, index+1
        index += 1
        if index >= len(station.all_movements):
            index = 0


def get_departures_strict(station: Station|Stop, time=None, count=10, padding=3):
    now_index = find_closest_departure(station, time)
    departures = []
    i = now_index
    while len(departures) < count:
        next_departure, i = get_next_departure(station, i)
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
            next_departure, i = get_next_departure(station, i)
            departures.append(next_departure)
            if next_departure["departure_time"] >= time + CLOSEST_TO_LAST_DEPARTURE: break
    return departures


def get_line_departures(station: Station|Stop, line: Line, time=None, padding=3, default_count=10):
    pass


def are_trips_similar(trip1:Trip, trip2:Trip) -> bool:
    pass


def get_unique_departures_now(station: Station|Stop, time=None, padding=3, search_pool_size=20):
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


def get_all_unique_departures(station: Station|Stop):
    pass  # Gets searched from station.move from index 0 -> For easiest finding trips for fastest route calculating (uniques are assumed from station.lines)
    # Maybe search from sometime before now cause there could be services limited to daytime (e.g. night transport, substitutes, morning/evening service)


def djisktra_alfa(start: Station, end: Station):
    start_time = int(datetime.datetime.now().strftime("%H%M00")) + 100


if __name__ == "__main__":
    #s_node, e_node = get_end_nodes()
    s_node = _stations[1040][0]
