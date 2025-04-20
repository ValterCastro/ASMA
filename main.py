import getpass
import spade
import asyncio
#from spade_bdi.bdi import BDIAgent
from central import central
from bin import Bin
from truck import Truck
import time
import logging
from spade import wait_until_finished
from behavior import EmptyGarbage
from node import Node
from edge import Edge
from dijkstra import dijkstra

nodes = {}
edges = {}



async def main():
    
    # First scenario hardcoded 2 trucks and 2 bins
    
    truck_agent10 = Truck("asma@draugr.de/10", "1234")
    await truck_agent10.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent10.setContractor(central)
    #print(f"Is {truck_agent.name} a contractor? {truck_agent.getContractor()}")
    
    truck_agent11 = Truck("asma@draugr.de/11", "1234")
    await truck_agent11.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent11.setContractor(central)
    #print(f"Is {truck_agent.name} a contractor? {truck_agent.getContractor()}")
    
    bin_agent0 = Bin("asma@draugr.de/0", "1234")
    await bin_agent0.start(auto_register=True)
    await asyncio.sleep(1)  
    bin_agent0.setManager(central)
    #print(f"Is {bin_agent.name} a manager? {bin_agent.getManager()}")
    
    bin_agent1 = Bin("asma@draugr.de/1", "1234")
    await bin_agent1.start(auto_register=True)
    await asyncio.sleep(1)  
    bin_agent1.setManager(central)
    #print(f"Is {bin_agent.name} a manager? {bin_agent.getManager()}")
    
    
    
    
    
    # Add agents to graph 
    
    truck_agent10.latest_location = nodes['X']
    truck_agent11.latest_location = nodes['A']
    nodes['L'].bin = bin_agent0
    nodes['M'].bin = bin_agent1
    
    
    # Behavior empty garbage
    
    behavior1 = EmptyGarbage()
    bin_agent0.add_behaviour(behavior1)
    bin_agent1.add_behaviour(behavior1)
    

    await wait_until_finished(bin_agent0)
    await wait_until_finished(bin_agent1)
    

def build_graph_from_file(path='graph_files/proj1_edgelist'):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    nodes_set = set()
    inc_out_set = set()

    for line in lines:
        splited = line.split()
        nodes_set.add(splited[0])
        inc_out_set.add((splited[0], splited[1], float(splited[2])))

    for node in nodes_set:
        nodes[node] = Node(node)
    nodes['X'] = Node('X')

    for a, b, w in inc_out_set:
        edge = Edge(a, b, w)
        edges[(a, b)] = edge

    for (a, b), edge in edges.items():
        nodes[a].edge_list.add(edge)
        nodes[b].edge_list.add(edge)


if __name__ == "__main__":
    build_graph_from_file()
    spade.run(main())
