import networkx as nx
from math import radians, cos, sin, asin, sqrt

# Parameters
# bin and depot locations from the spec
locations = {
    "A": (41.1627, -8.6115),
    "B": (41.1654, -8.6110),
    "C": (41.1646, -8.6106),
    "D": (41.1603, -8.6100),
    "E": (41.1658, -8.6094),
    "F": (41.1635, -8.6089),
    "G": (41.1626, -8.6093),
    "H": (41.1622, -8.6072),
    "I": (41.1609, -8.6075),
    "J": (41.1655, -8.6062),
    "K": (41.1621, -8.6053),
    "L": (41.1600, -8.6027),
    "M": (41.1641, -8.6007),
    "N": (41.1628, -8.5997),
    "O": (41.1614, -8.6008),
    "P": (41.1597, -8.6046),
    "X": (41.1693, -8.6026)  # Depot
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    return R * c


G = nx.Graph()

# Add nodes
for name, coords in locations.items():
    G.add_node(name, pos=coords)

# Add edges with Haversine distance as weight
for src_name, src_coords in locations.items():
    for dst_name, dst_coords in locations.items():
        if src_name != dst_name:
            distance = haversine(*src_coords, *dst_coords)
            G.add_edge(src_name, dst_name, weight=distance)

# Save the graph to a file
nx.write_weighted_edgelist(G, "graph_files/proj1.edgelist")

if __name__ == "__main__":
    # Print the graph to verify
    print("Nodes of the graph:")
    print(G.nodes(data=True))
    print("\nEdges of the graph:")
    print(G.edges(data=True))
    print("\nGraph saved to porto_graph.edgelist")