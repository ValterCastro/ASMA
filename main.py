import getpass
import spade
import asyncio
import random
import threading

# from spade_bdi.bdi import BDIAgent
from central import Central
from bin import Bin
from truck import Truck
from helper import clear

import time
import logging
from spade import wait_until_finished
from behavior import EmptyGarbage
from node import Node
from edge import Edge
from simple_term_menu import TerminalMenu


NODES = {}
EDGES = {}
BINS = []


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


async def gen_bins(central):
    for i, node in zip(range(1), "ABCDEFGHIJKLMNOP"):
        bin_agent = Bin(f"asma@draugr.de/{i}", "1234", central=central, location=node)
        central.add_bin(bin_agent.name, bin_agent)
        NODES[node].bin = bin_agent
        BINS.append(bin_agent)
        
        
async def gen_trucks(central):
    for i, node in zip(range(1), "XABCDEFGHIJKLMNOP"):
        truck_agent = Truck(f"asma@draugr.de/{i+100}", "1234", location=node)
        central.add_truck(truck_agent.name, truck_agent)


# def get_rand_bins(bins, n):
#     return random.sample(bins, n)


async def scenario_1():
    """
    Scenario 1:
    • Bin filling rate (time interval): every 300 seconds (ensure that the bin fills up once and only
    once)
    • Bin filling rate (quantity): 100% of the bin capacity
    • Number of Trucks: 1
    • End of simulation: 240 seconds
    """

    central = Central(NODES, 215)

    await gen_trucks(central)
    
    await asyncio.gather(*(truck.start() for truck in central.trucks.values()))

    await gen_bins(central)

    await asyncio.gather(*(bin["bin"].start() for bin in central.bins.values()))

    # thread = threading.Thread(target=central.update_world, daemon=True)
    # thread.start()
    
    update_task = asyncio.create_task(central.update_world())
    await update_task

    # while central.running:
    #     pass

    await asyncio.gather(*(bin["bin"].stop() for bin in central.bins.values()))
    await asyncio.gather(*(truck.stop() for truck in central.trucks.values()))

    input(">")
    clear()


async def scenario_2(central):
    # Scenario 2 logic here
    print("Executing Scenario 2...")
    # You can call the main function or any other function here
    await main()


async def scenario_3(central):
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

    # Run the menu function
    main()
