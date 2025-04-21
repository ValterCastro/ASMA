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
    msg_behav = None
    rec_behav = None
    inbox = []
    filling_rate = 1
    location = None

    
    async def setup(self):
        self.variables = {
            "current_waste_lvl": self.current_waste_lvl,  
        }
        self.announcements = [Announcement(AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL, "current_waste_lvl", 5)]
        self.name = self.name + str(Bin.bin_number)
        Bin.bin_number += 1
        
        # Called when the agent starts
        print(f"Agent {self.name} starting...")
        
    def update(self):
        self.current_waste_lvl = min(self.current_waste_lvl + self.filling_rate, self.capacity)
