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



async def main():
    logging.basicConfig(level=logging.DEBUG)
    
    truck_agent = Truck("asma@draugr.de/1", "1234")  
    await truck_agent.start(auto_register=True)
    await asyncio.sleep(1)
    truck_agent.setContractor(central)
    print(f"Is {truck_agent.name} a contractor? {truck_agent.getContractor()}")
    
    bin_agent = Bin("asma@draugr.de/0", "1234")  
    await bin_agent.start(auto_register=True)
    await asyncio.sleep(1)  
    bin_agent.setManager(central)
    print(f"Is {bin_agent.name} a manager? {bin_agent.getManager()}")
    behavior1 = EmptyGarbage()
    bin_agent.add_behaviour(behavior1)
    
    
    

    await wait_until_finished(bin_agent)
    

if __name__ == "__main__":
    spade.run(main())
