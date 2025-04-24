import getpass

# from spade_bdi.bdi import BDIAgent
import spade
from spade.behaviour import OneShotBehaviour
import asyncio
from spade.agent import Agent
from helper import progress_bar


class Truck(Agent):
    CAPACITY = 80
    VELOCITY = 5
    name = None

    rec_behav = None
    msg_behav = None
    inbox = []

    is_busy = False
    trip_cycles = 0
    cycles_left = 0
    current_waste_lvl = 0

    distance_traveled = 0

    def __init__(self, jid, password, location):
        # Call parent constructor
        super().__init__(jid, password)
        self.location = location
        self.name = str(self.jid)
        # self.name = str(self.jid.resource)

    async def setup(self):
        self.variables = {
            "current_waste_lvl": self.current_waste_lvl,
            "capacity": self.CAPACITY,
            "velocity": self.VELOCITY,
        }

        self.is_busy = False

    def updateLocation(self, location):
        self.location = location

    def getLocation(self):
        assert hasattr(self, "location"), "Truck must have a location attribute"
        return self.location

    def isAvailable(self, amount):
        # print(
        #     f"🚚 {self.jid} availability: {(self.current_waste_lvl + amount) <= self.CAPACITY
        #         and self.cycles_left == 0
        #         and self.is_busy is False}"
        # )
        return (
            self.location
            if (
                (self.current_waste_lvl + amount) <= self.CAPACITY
                and self.cycles_left == 0
                and self.is_busy is False
            )
            else False
        )

    def startTrip(self, cycles, distance_to_travel):
        self.is_busy = True
        self.trip_cycles = cycles
        self.cycles_left = cycles
        self.distance_traveled += (
            distance_to_travel  # TODO: tentar passar isto para um sítio mais adequado
        )

    def update(self):
        print(f"🚚 {self.jid}: \033[34m{self.cycles_left}/ {self.trip_cycles}\033[0m")
        # print(
        #     f"🚚: \033[34m{progress_bar(1 - self.cycles_left / self.trip_cycles)}\033[0m"
        # )
        if self.is_busy and self.cycles_left > 0:
            self.cycles_left -= 1
        else:
            self.is_busy = False
