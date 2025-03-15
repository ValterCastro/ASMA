from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import asyncio

STATE_ONE = "STATE_ONE"
STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"

class EmptyGarbage(CyclicBehaviour):
        async def on_start(self):
            print("Starting announcement . . .")
            fsm = ContractNetFSMBehaviour()
            fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
            fsm.add_state(name=STATE_TWO, state=StateTwo())
            fsm.add_state(name=STATE_THREE, state=StateThree())
            fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
            fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
            self.agent.add_behaviour(fsm)
            self.counter = 0

        async def run(self):
            print("Counter: {}".format(self.counter))
            self.counter += 1
            await asyncio.sleep(5)
            
class ContractNetFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        #await self.agent.stop()
        
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
        self.set_next_state(STATE_THREE)


class StateThree(State):
    async def run(self):
        print("I'm at state three (final state)")
        msg = await self.receive(timeout=5)
        print(f"State Three received message {msg.body}")
        # no final state is setted, since this is a final state

        
