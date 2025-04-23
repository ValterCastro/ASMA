import getpass

# from spade_bdi.bdi import BDIAgent
import spade
from spade.behaviour import OneShotBehaviour
import asyncio
from spade.agent import Agent


class Truck(Agent):
    CAPACITY = 80
    VELOCITY = 5
    name = None

    rec_behav = None
    msg_behav = None
    inbox = []

    location = None

    is_busy = False
    cycles_to_destination = 0
    current_waste_lvl = 0

    distance_traveled = 0

    async def setup(self):
        self.variables = {
            "current_waste_lvl": self.current_waste_lvl,
            "capacity": self.CAPACITY,
            "velocity": self.VELOCITY,
        }
        self.name = str(self.jid)
        self.location = None
        self.is_busy = False

    def updateLocation(self, location):
        assert location is not None, "Location cannot be None"
        self.location = location
        # print(f"Truck {self.name} updated location to {location}")

    def getLocation(self):
        assert hasattr(self, "location"), "Truck must have a location attribute"
        return self.location

    def isAvailable(self, amount):
        return (
            self.location
            if (
                (self.current_waste_lvl + amount) <= self.CAPACITY
                and self.cycles_to_destination == 0
            )
            else False
        )

    def startTrip(self, cycles, distance_to_travel):
        self.is_busy = True
        self.cycles_to_destination = cycles
        self.distance_traveled += (
            distance_to_travel  # TODO: tentar passar isto para um sítio mais adequado
        )

    def update(self):
        if self.is_busy:
            self.cycles_to_destination -= 1
        else:
            self.is_busy = False
