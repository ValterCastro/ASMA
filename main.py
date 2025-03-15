import getpass
import spade
import asyncio
from spade_bdi.bdi import BDIAgent
from central import Central
from bin import Bin
from truck import Truck
import time
import logging
from spade import wait_until_finished
from behavior import EmptyGarbage

# Enable logging to see SPADE internals


# server = "asma@yax.im"
# password = "1234"

# async def main():
#     truck = BDIAgent(server, password, "truck.asl")
#     bin = BDIAgent(server, password, "bin.asl")
#     print("Starting agent...")
#     await truck.start()
#     await bin.start()
#     print("Agent started!")
    
#     await asyncio.sleep(1)

#     print("Setting belief: car(blue)")
#     await truck.bdi.set_belief("car", "blue")
    
#     print("Beliefs after set:")
#     truck.bdi.print_beliefs()

#     await asyncio.sleep(5)

async def main():
    # logging.basicConfig(level=logging.INFO)
    central = Central()
    # bin1 = Bin()
    # bin2 = Bin()
    #truck1 = Truck()
    
    # bin1.setManager(central)
    # truck1.setContractor(central)
    # print(central.managers.items())
    # print(central.contractors.items())
    
    truck_agent = Truck("ms_proj@macaw.me/1", "1234", )  # Replace with your XMPP server details
    await truck_agent.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent.setContractor(central)
    print(f"Is {truck_agent.name} a contractor? {truck_agent.getContractor()}")
    
    bin_agent = Bin("ms_proj@macaw.me/0", "1234")  # Replace with your XMPP server details
    await bin_agent.start(auto_register=True)
    await asyncio.sleep(1)  # Give the agent time to start
    bin_agent.setManager(central)
    print(f"Is {bin_agent.name} a manager? {bin_agent.getManager()}")
    behavior1 = EmptyGarbage()
    bin_agent.add_behaviour(behavior1)
    
    
    

    await wait_until_finished(bin_agent)
    
    # for ann in bin1.announcements:
    #     print(ann)


if __name__ == "__main__":
    spade.run(main())
    #main()