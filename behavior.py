from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from central import central
import asyncio

STATE_ONE = "CALL_FOR_PROPOSAL"
STATE_TWO = "REFUSE"
STATE_THREE = "PROPOSE"
STATE_FOUR = "ACCEPT_PROPOSAL"
STATE_FIVE = "INFORM:DONE"
STATE_SIX = "FAILURE"


class EmptyGarbage(CyclicBehaviour):
        async def on_start(self):
            print("Starting announcement . . .")
            
        async def run(self):
            fsm = ContractNetFSMBehaviour()
            fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
            fsm.add_state(name=STATE_TWO, state=StateTwo())
            fsm.add_state(name=STATE_THREE, state=StateThree())
            fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
            fsm.add_transition(source=STATE_ONE, dest=STATE_THREE)
            fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
            fsm.add_transition(source=STATE_THREE, dest=STATE_FOUR)
            
            
            self.agent.current_msg_type = AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL.value

            self.agent.add_behaviour(fsm)
            await asyncio.sleep(5)
            
class StateOne(State):
    async def run(self):
        print("I'm at state one")
        for key, item in central.contractors.items():    
            msg = Message(to=str(key))
            msg.set_metadata("type", AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL.value)
            msg.set_metadata("requirements", "waste_lvl<=5")
            msg.set_metadata("deadline", "5")
            msg.set_metadata("eval_criteria", "waste_lvl_before,waste_lvl_after,distance")
            msg.body = f"Need to drop waste from bin {self.agent.bin_number}."
            self.set_next_state(STATE_TWO) if not item.isAvailable() else self.set_next_state(STATE_THREE)         
                
        

class StateTwo(State):
    async def run(self):
        print("I REFUSE")
        

class StateThree(State):
    async def run(self):
        print("I PROPOSE")
        msg = Message(to=str(self.agent.jid))
        msg.set_metadata("type", "Proposal")
        msg.set_metadata("", "Proposal")
        
class StateFour(State):
    async def run(self):
        print("I ACCEPT PROPOSAL")
        
class StateFive(State):
    async def run(self):
        print("INFORM:DONE")
        
class StateSix(State):
    async def run(self):
        print("FAILURE")

class ContractNetFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print("FSM starting")