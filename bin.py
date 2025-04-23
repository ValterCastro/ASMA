from announcement import Announcement
from announcement_types import AnnouncementType
from spade.agent import Agent
from behavior import EmptyGarbage


class Bin(Agent):
    current_waste_lvl = 0
    capacity = 20
    name = None
    is_manager = False
    current_message_type = ""
    msg_behav = None
    rec_behav = None
    empty_garbage_behav = None
    inbox = []
    filling_rate = 10
    location = None

    def __init__(self, jid, password, central, location):
        # Call parent constructor
        super().__init__(jid, password)
        self.central = central
        self.location = location
        self.name = str(self.jid.resource)

    async def setup(self):
        self.empty_garbage_behav = EmptyGarbage(central=self.central)
        self.add_behaviour(self.empty_garbage_behav)

        # Called when the agent starts
        print(f"Agent {self.name} starting...")

    def update(self):
        self.current_waste_lvl = min(
            self.current_waste_lvl + self.filling_rate, self.capacity
        )
