import getpass
from spade_bdi.bdi import BDIAgent
import spade
import asyncio
from spade.agent import Agent

class Truck(Agent):
    
    truck_number = 1
    waste_lvl = 0
    name = "truck"
    is_contractor = False
    is_manager = False
    
    async def setup(self):
        self.variables = {
            "waste_lvl": self.waste_lvl,  
        }
        self.name = self.name + str(self.truck_number)
        Truck.truck_number += 1
        self.name = self.name + str(Truck.truck_number)
        # Called when the agent starts
        print(f"Agent {self.name} starting...")
    
    def setManager(self, central):
        assert central is not None, "Central object cannot be None"
        assert hasattr(central, 'managers'), "Central must have a managers attribute"
        assert isinstance(central.managers, dict), "central.managers must be a dictionary"
        assert hasattr(self, 'is_manager'), "self.is_manager must be defined"
        assert isinstance(self.is_manager, bool), "self.is_manager must be a boolean"
        assert hasattr(self, 'name'), "self.name must be defined"

        if self.is_manager:
            # Remove manager
            assert self.name in central.managers, f"{self.name} not found in central.managers"
            self.is_manager = False
            central.managers.pop(self.name)
        else:
            # Add manager
            assert self.name not in central.managers, f"{self.name} is already in central.managers"
            self.is_manager = True
            central.managers.update({self.name: self})
            
    def setContractor(self, central):
        assert central is not None, "Central object cannot be None"
        assert hasattr(central, 'contractors'), "Central must have a contractors attribute"
        assert isinstance(central.contractors, dict), "central.contractors must be a dictionary"
        assert hasattr(self, 'is_contractor'), "self.is_contractor must be defined"
        assert isinstance(self.is_contractor, bool), "self.is_contractor must be a boolean"
        assert hasattr(self, 'name'), "self.name must be defined"

        if self.is_contractor:
            # Remove manager
            assert self.name in central.contractors, f"{self.name} not found in central.contractors"
            self.is_contractor = False
            central.contractors.pop(self.name)
        else:
            # Add manager
            assert self.name not in central.contractors, f"{self.name} is already in central.contractors"
            self.is_contractor = True
            central.contractors.update({self.name: self})
        
        
        
    def getManager(self):
        assert hasattr(self, 'is_manager'), "Bin must have a is_manager attribute"
        assert isinstance(self.is_manager, bool), "self.is_manager must be a boolean"
        return self.is_manager
        
    def getContractor(self):
        assert hasattr(self, 'is_contractor'), "Truck must have a is_contractor attribute"
        assert isinstance(self.is_contractor, bool), "self.is_contractor must be a boolean"
        return self.is_contractor

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

# if __name__ == "__main__":
#     spade.run(main())