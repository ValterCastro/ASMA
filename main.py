import getpass
import spade
import asyncio
import random
import copy

# from spade_bdi.bdi import BDIAgent
from central import central
from bin import Bin
from truck import Truck
import time
import logging
from spade import wait_until_finished
from behavior import EmptyGarbage
from node import Node
from edge import Edge
from simple_term_menu import TerminalMenu

NODES = {}
EDGES = {}


def main():
    while True:
        options = ["Scenario 1", "Scenario 2", "Scenario 3"]
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        selection = options[menu_entry_index]

        if selection == "Scenario 1":
            spade.run(scenario_1())
        elif selection == "Scenario 2":
            spade.run(scenario_2())
        elif selection == "Scenario 3":
            spade.run(scenario_3())


async def scenario_1():
    """
    Scenario 1:
    • Bin filling rate (time interval): every 300 seconds (ensure that the bin fills up once and only
    once)
    • Bin filling rate (quantity): 100% of the bin capacity
    • Number of Trucks: 1
    • End of simulation: 240 seconds
    """
    truck_agent10 = Truck("asma@draugr.de/10", "1234")
    await truck_agent10.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent10.setContractor(central)
    NODES["X"].truck = truck_agent10

    nodes = get_rand_bins(list(NODES.values()), 6)

    for node in nodes:
        await node.bin.start(auto_register=True)
        await asyncio.sleep(1)
        node.bin.setManager(central)

        await wait_until_finished(node.bin)


def gen_bins():
    behavior = EmptyGarbage()
    for i, bin in zip(range(16), "ABCDEFGHIJKLMNOP"):
        bin_agent = Bin(f"asma@draugr.de/{i}", "1234")
        bin_agent.add_behaviour(behavior)
        NODES[bin].bin = bin_agent


def get_rand_bins(bins, n):
    return random.sample(bins, n)


async def _():

    # First scenario hardcoded 2 trucks and 2 bins

    truck_agent10 = Truck("asma@draugr.de/10", "1234")
    await truck_agent10.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent10.setContractor(central)
    # print(f"Is {truck_agent.name} a contractor? {truck_agent.getContractor()}")

    truck_agent11 = Truck("asma@draugr.de/11", "1234")
    await truck_agent11.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent11.setContractor(central)
    # print(f"Is {truck_agent.name} a contractor? {truck_agent.getContractor()}")

    bin_agent0 = Bin("asma@draugr.de/0", "1234")
    await bin_agent0.start(auto_register=True)
    await asyncio.sleep(1)
    bin_agent0.setManager(central)
    # print(f"Is {bin_agent.name} a manager? {bin_agent.getManager()}")

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

async def scenario_2():
    # Scenario 2 logic here
    print("Executing Scenario 2...")
    # You can call the main function or any other function here
    await main()


async def scenario_3():
    # Scenario 3 logic here
    print("Executing Scenario 3...")
    # You can call the main function or any other function here
    await main()


def read_graph():
    f = open("graph_files/proj1_edgelist", "r")
    a = f.readlines()
    nodes_set = set()
    inc_out_set = set()
    for line in a:
        splited = line.split()
        nodes_set.add(splited[0])
        inc_out_set.add((splited[0], splited[1], splited[2]))

    for node in nodes_set:
        node_ = Node(node)
        NODES[node] = node_

    NODES["X"] = Node("X")

    for node_pair in inc_out_set:
        edge = Edge(node_pair[0], node_pair[1], node_pair[2])
        EDGES[(node_pair[0], node_pair[1])] = edge

    for key, value in EDGES.items():
        NODES[key[0]].edge_list.add(value)
        NODES[key[1]].edge_list.add(value)


if __name__ == "__main__":

    # Read the graph from the file and populate NODES and EDGES
    read_graph()

    # Initialize read bins from graph
    gen_bins()

    # Run the menu function
    main()
