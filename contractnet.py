import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from dijkstra import dijkstra
from main import nodes, edges
import asyncio

STATE_ONE = "STATE_ONE"
STATE_TWO = "STATE_TWO"
STATE_MOVE = "STATE_MOVE"
STATE_THREE = "STATE_THREE"


class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


class StateOne(State):
    async def run(self):
        print("I'm at state one (initial state)")
        msg = Message(to=str(self.agent.jid))
        msg.body = "msg_from_state_one_to_state_three"
        await self.send(msg)
        self.set_next_state(STATE_TWO)


class StateTwo(State):
    async def run(self):
        print("I'm at state two")
        self.set_next_state(STATE_MOVE)


class MoveToBinState(State):
    async def run(self):
        print("STATE MOVE: Moving to target bin.")

        # Calculate time using Dijkstra
        start_node = self.agent.getLocation().id if self.agent.getLocation() else "X"
        target_node = self.agent.target_bin_id

        dist_map = dijkstra(start_node, nodes)
        distance = dist_map[target_node]
        travel_time = distance / self.agent.velocity

        print(f"{self.agent.name} traveling from {start_node} to {target_node}: {distance:.2f}m, ETA: {travel_time:.2f}s")
        await asyncio.sleep(travel_time)

        # Update location
        self.agent.updateLocation(nodes[target_node])
        print(f"{self.agent.name} arrived at {target_node}")
        self.set_next_state(STATE_THREE)



class StateThree(State):
    async def run(self):
        print("I'm at state three (final state)")
        msg = await self.receive(timeout=5)
        print(f"State Three received message {msg.body}")
        # no final state is setted, since this is a final state


class FSMAgent(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_MOVE, state=MoveToBinState())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_MOVE)
        fsm.add_transition(source=STATE_MOVE, dest=STATE_THREE)
        self.add_behaviour(fsm)


async def main():
    fsmagent = FSMAgent("asma@yax.im", "1234")
    await fsmagent.start()

    await spade.wait_until_finished(fsmagent)
    await fsmagent.stop()
    print("Agent finished")

if __name__ == "__main__":
    spade.run(main())