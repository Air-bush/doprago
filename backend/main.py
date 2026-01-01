import networkx
import csv
import matplotlib.pyplot as plt

graph = networkx.MultiDiGraph()

def get_stops() -> list:
    all_stops = []
    with open("tempFiles/stops.txt", encoding="UTF-8") as file:
        reader = csv.DictReader(file)
        for line in reader:
            stop_id = line["stop_id"]
            line.pop("stop_id")
            all_stops.append((stop_id, line))
    return all_stops

def get_stations(all_stops: list) -> list:
    all_stations = []
    children = 0
    for stop_id, stop in all_stops:
        if not stop.get("parent_station"):
            all_stations.append((stop_id, stop))
        if stop.get("parent_station"):
            children += 1
    return all_stations

def get_edges() -> list:
    #[id?, weight, attr]
    pass

stops = get_stops()
stations = get_stations(stops)
edges = get_edges()
for stationid, station in stations:
    print(stationid)

graph.add_nodes_from(stops)
#graph.add_weighted_edges_from(edges)

pos = {
    stop_id: (float(attrs["stop_lon"]), float(attrs["stop_lat"]))
    for stop_id, attrs in stops
}

# Draw using those positions (no SciPy required)
networkx.draw(graph, pos=pos, with_labels=False, node_size=10)
plt.show()