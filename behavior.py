from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from spade.behaviour import OneShotBehaviour
from central import Central
from dijkstra import dijkstra
import asyncio
import numpy as np


STATE_ZERO = "INTERVAL"  # Interval in empty garbage behavior
STATE_ONE = "CALL_FOR_PROPOSAL"  # Bin is full
STATE_TWO = "FAILURE"  # Every trucks refuse
STATE_THREE = "PROPOSE"  # Trucks propose to pick up the bins trash
STATE_FOUR = "ACCEPT_PROPOSAL"  # Bin accepts the proposal
STATE_FIVE = "INFORM:DONE"  # Truck informs the bin that the job is done


class EmptyGarbage(FSMBehaviour):

    def __init__(self, central, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.central = central  #
        self.available_trucks = {}
        self.winner = None

    async def on_start(self):

        self.add_state(name=STATE_ZERO, state=StateZero(behav=self), initial=True)

        print(f"FSM starting at initial state {self.current_state}")
        print("Starting announcement . . .")
        self.add_state(name=STATE_ONE, state=StateOne(behav=self))
        self.add_state(name=STATE_TWO, state=StateTwo(agent=self.agent))
        self.add_state(name=STATE_THREE, state=StateThree(behav=self))
        self.add_state(name=STATE_FOUR, state=StateFour(behav=self))
        self.add_state(name=STATE_FIVE, state=StateFive(behav=self))

        self.add_transition(source=STATE_ZERO, dest=STATE_ONE)
        self.add_transition(source=STATE_ZERO, dest=STATE_ZERO)
        self.add_transition(source=STATE_ONE, dest=STATE_TWO)
        self.add_transition(source=STATE_ONE, dest=STATE_THREE)
        self.add_transition(source=STATE_TWO, dest=STATE_ZERO)
        self.add_transition(source=STATE_TWO, dest=STATE_ONE)
        self.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        self.add_transition(source=STATE_FOUR, dest=STATE_FIVE)
        self.add_transition(source=STATE_FIVE, dest=STATE_ZERO)

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


class InformBehav(OneShotBehaviour):

    def __init__(self, agent, receiver_address, metadata, body, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver_address = receiver_address
        self.agent = agent
        self.body = body
        self.metadata = metadata

    async def run(self):
        print(
            f"\033[34m💬 {self.agent.jid} ➡️  {self.receiver_address.jid}: {self.body}\033[0m"
        )

        msg = Message(to=str(self.receiver_address))  # Instantiate the message

        if self.metadata is not None:
            for key, value in self.metadata.items():
                msg.set_metadata(key, value)
        msg.body = self.body

        await self.send(msg)

        self.exit_code = "Job Finished!"


class RecvBehav(OneShotBehaviour):

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent

    async def run(self):

        msg = await self.receive(timeout=3)  # wait for a message for 3 seconds
        self.agent.inbox.append(msg)

        # print(f"\033[34m💬 {self.agent.jid} ⬅️ o : {msg}\033[0m")


class StateZero(State):
    """
    Bin is empty - Interval between bin being empty and full/supplied
    """

    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):

        # async with self.behav.agent.lock:
        if self.behav.agent.current_waste_lvl >= self.behav.agent.capacity:
            print(f"0️⃣  🗑️ \033[31m{self.behav.agent.jid}\033[0m needs to be emptied")

            self.behav.agent.inbox = []

            for truck in self.behav.central.trucks.values():
                truck.inbox = []

            self.set_next_state(STATE_ONE)
        else:
            print(f"0️⃣  🗑️ \033[31m{self.behav.agent.jid}\033[0m waiting to be full")
            await asyncio.sleep(3)
            self.set_next_state(STATE_ZERO)


class StateOne(State):
    """
    Bin is full - Call for trucks proposals
    """

    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):
        print(
            f"1️⃣  🗑️ \033[31m{self.behav.agent.jid}\033[0m is full - Call for trucks proposals"
        )

        recv_behaviors = []

        for key, value in self.behav.central.trucks.items():

            data = {"location": self.agent.location}

            self.behav.agent.msg_behav = InformBehav(
                agent=self.behav.agent,
                receiver_address=value.jid,
                metadata=data,
                body="I ANNOUNCE",
            )
            self.behav.agent.add_behaviour(self.behav.agent.msg_behav)

            value.rec_behav = RecvBehav(agent=value)
            value.add_behaviour(value.rec_behav)
            recv_behaviors.append(value.rec_behav)

            available_truck_position = value.isAvailable(
                self.behav.agent.current_waste_lvl
            )

            if available_truck_position:
                self.behav.available_trucks[str(value.jid)] = value
            else:
                value.msg_behav = InformBehav(
                    agent=value.jid,
                    receiver_address=self.behav.agent.jid,
                    metadata=None,
                    body="REFUSE",
                )
                value.add_behaviour(value.msg_behav)

        for behav in recv_behaviors:
            await behav.join()

        if len(self.behav.available_trucks) == 0:
            self.set_next_state(STATE_TWO)

        else:
            self.set_next_state(STATE_THREE)


class StateTwo(State):
    """
    No trucks available - all refused call for proposals
    """

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent

    async def run(self):
        print(
            f"2️⃣  \033[31m{self.agent.jid}\033[0m - No trucks available - all refused call for proposals"
        )

        await asyncio.sleep(3)
        self.set_next_state(STATE_ONE)


class StateThree(State):
    """
    Truck proposes to pick up the bin
    """

    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):
        print(
            f"3️⃣  🗑️  \033[31m{self.behav.agent.jid}\033[0m - At least one truck is available"
        )

        recv_behaviors = []

        for key, truck in self.behav.central.trucks.items():

            data = {
                "location": truck.location,
            }

            print(f"🔨💬    🚚  \033[31m{truck.jid}\033[0m")
            truck.msg_behav = InformBehav(
                agent=truck.jid,
                receiver_address=self.behav.agent.jid,
                metadata=data,
                body=f"I PROPOSE",
            )
            truck.add_behaviour(truck.msg_behav)

            self.behav.agent.rec_behav = RecvBehav(agent=self.behav.agent)
            self.behav.agent.add_behaviour(self.behav.agent.rec_behav)
            recv_behaviors.append(self.behav.agent.rec_behav)

        for behav in recv_behaviors:
            await behav.join()

        self.set_next_state(STATE_FOUR)


class StateFour(State):
    """
    Bin accepts the proposal
    """

    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):
        print(f"4️⃣  🗑️  \033[31m{self.behav.agent.jid}\033[0m - Checking proposals... ⏳")

        best_distance = np.inf

        available_truck_nodes = {}

        recv_behaviors = []

        print(
            f"\n📥 Received messages: {[f"{x.sender}: {x.body} " for x in self.behav.agent.inbox]}\n"
        )

        for msg in self.behav.agent.inbox:
            if str(msg.body).startswith("I PROPOSE"):
                print(
                    f"4️⃣  🗑️  \033[31m{self.behav.agent.jid}\033[0m received proposal from 🚚 \033[31m{self.behav.central.trucks[str(msg.sender)].jid}\033[0m"
                )
                if len(self.behav.central.trucks) > 0:
                    available_truck_nodes[
                        self.behav.central.trucks[str(msg.sender)].location
                    ] = self.behav.central.trucks[str(msg.sender)]

        distance = 0
        for key, value in available_truck_nodes.items():
            print(f"DIJKSTRA CYCLE: {value.jid}")
            distance = dijkstra(
                key, self.behav.agent.location, self.behav.central.nodes
            )
            if best_distance > distance and not value.is_busy:
                best_distance = distance
                self.behav.winner = value
                self.behav.winner.is_busy = True

        self.behav.agent.msg_behav = InformBehav(
            agent=self.behav.agent,
            receiver_address=self.behav.winner.jid,
            metadata=None,
            body="I ACCEPT PROPOSE",
        )
        self.behav.agent.add_behaviour(self.behav.agent.msg_behav)

        self.behav.winner.rec_behav = RecvBehav(agent=self.behav.winner)
        self.behav.winner.add_behaviour(self.behav.winner.rec_behav)
        recv_behaviors.append(self.behav.winner.rec_behav)

        for behav in recv_behaviors:
            await behav.join()

        self.behav.winner.startTrip(
            np.floor(best_distance / self.behav.winner.VELOCITY),
            best_distance,
        )
        self.behav.agent.empty_garbage()

        self.set_next_state(STATE_FIVE)


class StateFive(State):
    """
    Bin informs the truck that the job is done
    """

    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):
        print(
            f"5️⃣  \033[31m{self.behav.agent.jid}\033[0m - Assigned 🚚 {self.behav.winner.jid} to: {self.behav.winner.location} ➡️  {self.behav.agent.location}"
        )

        while self.behav.winner.cycles_left > 0:
            print(
                f"5️⃣  \033[31m{self.behav.agent.jid}\033[0m - Truck has not reached the destination yet"
            )
            await asyncio.sleep(2)

        await asyncio.sleep(1)

        if self.behav.winner.is_busy is False:
            self.behav.winner.location = self.behav.agent.location

        print(f"\033[31m[DEBUG]\033[0m - Location after: {self.behav.winner.location}")

        self.set_next_state(STATE_ZERO)
