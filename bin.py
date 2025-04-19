from announcement import Announcement
from announcement_types import AnnouncementType 
from spade.agent import Agent

class Bin(Agent):
    
    bin_number = 1
    current_waste_lvl = 0
    capacity = 20
    name = "bin"
    is_manager = False     
    current_message_type = ""
        
    async def setup(self):
        self.variables = {
            "current_waste_lvl": self.current_waste_lvl,  
        }
        self.announcements = [Announcement(AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL, "current_waste_lvl", 5)]
        self.name = self.name + str(Bin.bin_number)
        Bin.bin_number += 1
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
        
        
    def getManager(self):
        assert hasattr(self, 'is_manager'), "Bin must have a is_manager attribute"
        assert isinstance(self.is_manager, bool), "self.is_manager must be a boolean"
        return self.is_manager
    
