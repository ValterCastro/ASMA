import networkx as nx
import random
import os

# Parameters
n = 10  # Number of nodes
m = 15  # Number of edges (adjustable, but must be >= n-1 for connectivity)
num_graphs = 10  # Number of different graphs to generate

# Ensure the output directory exists
output_dir = "graph_files"
os.makedirs(output_dir, exist_ok=True)

# Function to generate a connected random graph
def generate_connected_graph(nodes, edges, seed):
    while True:
        # Set the random seed for reproducibility
        random.seed(seed)
        G = nx.gnm_random_graph(nodes, edges, seed=seed)
        # Check if the graph is connected
        if nx.is_connected(G):
            return G
        # If not connected, increment seed and try again
        seed += 1

# Generate and save 10 different graphs
graphs = []
base_seed = 42  # Starting seed for reproducibility

for i in range(num_graphs):
    seed = base_seed + i  # Unique seed for each graph
    G = generate_connected_graph(n, m, seed)
    graphs.append(G)
    
    # Get reachability info (adjacency list: which nodes each node can reach directly)
    reachability = {node: list(G.neighbors(node)) for node in G.nodes()}
    
    # Save the graph as an edge list
    filename = f"{output_dir}/graph_{i+1}.edgelist"
    nx.write_edgelist(G, filename, data=False)
    
    # Optionally save reachability info to a separate file
    reachability_filename = f"{output_dir}/graph_{i+1}_reachability.txt"
    with open(reachability_filename, 'w') as f:
        for node, neighbors in reachability.items():
            f.write(f"Node {node}: {neighbors}\n")
    
    print(f"Generated graph {i+1} with seed {seed}, saved to {filename}")
    print(f"Reachability info saved to {reachability_filename}")
    print(f"Number of edges: {G.number_of_edges()}, Connected: {nx.is_connected(G)}")
    print("-" * 50)

# Example: How to read a graph back from a file
# G_loaded = nx.read_edgelist("graph_files/graph_1.edgelist", nodetype=int)
# print("Loaded graph 1 edges:", list(G_loaded.edges()))
