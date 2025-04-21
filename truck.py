import getpass
#from spade_bdi.bdi import BDIAgent
import spade
from spade.behaviour import OneShotBehaviour
import asyncio
from spade.agent import Agent



class Truck(Agent):
    truck_number = 1
    current_waste_lvl = 0
    capacity = 80
    velocity = 5
    name = "truck"
    is_contractor = False
    is_manager = False
    latest_location = None
    rec_behav = None
    inbox = []
    
    
    async def setup(self):
        self.variables = {
            "current_waste_lvl": self.current_waste_lvl,
            "capacity": self.capacity, 
            "velocity": self.velocity
        }
        self.name = self.name + str(self.truck_number)
        self.latest_location = None
        Truck.truck_number += 1
        self.name = self.name + str(Truck.truck_number)
        # Called when the agent starts
        #print(f"Agent {self.name} starting...")
    
    def isAvailable(self):
        return True
    
    def updateLocation(self, location):
        assert location is not None, "Location cannot be None"
        self.latest_location = location
        #print(f"Truck {self.name} updated location to {location}")

    def getLocation(self):
        assert hasattr(self, 'latest_location'), "Truck must have a latest_location attribute"
        return self.latest_location

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


# async def check_inbox(truck):
#     while True:
#         print("Current inbox:")
#         for msg in truck.inbox:  # Access truck's inbox
#             print("Message received with content: {}".format(msg))
#             print("--------------------")
#         await asyncio.sleep(5)  # Wait 5 seconds asynchronously

# async def main():
#     # Start the Truck agent
#     #truck = Truck("truckagent@your_xmpp_server", "password")
#     await truck.start(auto_register=True)

#     # Run the inbox checker
#     await check_inbox(truck)

#     # Keep the program running (optional cleanup)
#     try:
#         await asyncio.Future()  # Run forever until interrupted
#     finally:
#         await truck.stop()

# if __name__ == "__main__":
#     asyncio.run(main())