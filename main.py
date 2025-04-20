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
    
    nodes['X'].truck = truck_agent10
    nodes['A'].truck = truck_agent11
    nodes['L'].bin = bin_agent0
    nodes['M'].bin = bin_agent1
    
    
    # Behavior empty garbage
    
    behavior1 = EmptyGarbage()
    bin_agent0.add_behaviour(behavior1)
    bin_agent1.add_behaviour(behavior1)
    

    await wait_until_finished(bin_agent0)
    await wait_until_finished(bin_agent1)
    

if __name__ == "__main__":
    
    f = open('graph_files/proj1_edgelist', 'r')
    a = f.readlines()
    nodes_set = set()
    inc_out_set = set()
    for line in a:
        
        splited = line.split()
        nodes_set.add(splited[0])
        inc_out_set.add((splited[0], splited[1], splited[2]))
        
        
    for node in nodes_set:
        node_ = Node(node)
        nodes[node] = node_ 
    
    nodes['X'] = Node('X')
        
    
    for node_pair in inc_out_set:
       edge = Edge(node_pair[0], node_pair[1], node_pair[2])
       edges[(node_pair[0],node_pair[1])] = edge

    for key,value in edges.items():
        nodes[key[0]].edge_list.add(value)
        nodes[key[1]].edge_list.add(value)
    
    
    for key,value in nodes.items():
        print("--------")
        for edge in value.edge_list:
            print(edge.A, edge.B)
    
    
    # For first scenario
    
    #nodes['A'].bin = 
    
    spade.run(main())
