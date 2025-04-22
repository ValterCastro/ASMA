from announcement import Announcement
from announcement_types import AnnouncementType
from spade.agent import Agent
from behavior import EmptyGarbage


class Bin(Agent):
    bin_number = 1
    current_waste_lvl = 0
    capacity = 20
    name = None

    current_message_type = ""
    msg_behav = None
    rec_behav = None
    empty_garbage_behav = None
    inbox = []
    filling_rate = 1
    location = None

    def __init__(self, jid, password, central, location):
        # Call parent constructor
        super().__init__(jid, password)
        self.central = central
        self.location = location
        self.name = str(self.jid.resource)

    async def setup(self):
        self.variables = {
            "current_waste_lvl": self.current_waste_lvl,
        }
        self.announcements = [
            Announcement(
                AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL, "current_waste_lvl", 5
            )
        ]

        Bin.bin_number += 1

        # self.central.add_bin(self.name, self)

        self.empty_garbage_behav = EmptyGarbage(central=self.central)
        self.add_behaviour(self.empty_garbage_behav)

        # Called when the agent starts
        print(f"Agent {self.name} starting...")

    def update(self):
        self.current_waste_lvl = min(
            self.current_waste_lvl + self.filling_rate, self.capacity
        )
