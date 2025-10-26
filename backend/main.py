import networkx
import csv

graph = networkx.Graph()

def get_nodes() -> list:
    nodes = []
    with open("gtfs_nodatabase_test/stops.txt", encoding="UTF-8") as file:
        reader = csv.reader(file)
        for line in reader:
            print(line)
            break

get_nodes()
