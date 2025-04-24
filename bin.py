from announcement import Announcement
from announcement_types import AnnouncementType
from spade.agent import Agent
from behavior import EmptyGarbage
import asyncio


class Bin(Agent):
    current_waste_lvl = 20
    capacity = 20
    name = None
    is_manager = False
    current_message_type = ""
    msg_behav = None
    rec_behav = None
    empty_garbage_behav = None
    inbox = []
    location = None

    def __init__(self, jid, password, central, location, filling_rate_quantity):
        # Call parent constructor
        super().__init__(jid, password)
        self.central = central
        self.location = location
        self.name = str(self.jid.resource)
        self.filling_rate = self.capacity * filling_rate_quantity
        self.lock = asyncio.Lock()

    async def setup(self):
        self.empty_garbage_behav = EmptyGarbage(central=self.central)
        self.add_behaviour(self.empty_garbage_behav)

        # Called when the agent starts
        print(f"Agent {self.name} starting...")

    def empty_garbage(self):
        """
        Empties the garbage in the bin.
        """
        self.current_waste_lvl = 0
        self.current_message_type = ""

    def update(self):
        self.current_waste_lvl = min(
            self.current_waste_lvl + self.filling_rate, self.capacity
        )
