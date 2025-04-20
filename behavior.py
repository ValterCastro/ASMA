from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from central import central
import asyncio

STATE_ONE = "CALL_FOR_PROPOSAL"  # Bin is full
STATE_TWO = "FAILURE"  # Every trucks refuse
STATE_THREE = "PROPOSE"  # Truck proposes to pick up the bin
STATE_FOUR = "ACCEPT_PROPOSAL"  # Bin accepts the proposal
STATE_FIVE = "INFORM:DONE"  # Bin informs the truck that the job is done
# STATE_SIX = "FAILURE"  # Bin informs the truck that the job failed


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

        self.agent.current_msg_type = (
            AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL.value
        )

        self.agent.add_behaviour(fsm)
        await asyncio.sleep(5)


class StateOne(State):
    """
    Bin is full - Call for trucks proposals
    """

    async def run(self):
        print("1️⃣ Bin is full - Call for trucks proposals")
        for key, item in central.contractors.items():
            msg = Message(to=str(key))
            msg.set_metadata(
                "type", AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL.value
            )
            msg.set_metadata("requirements", "waste_lvl<=5")
            msg.set_metadata("deadline", "5")
            msg.set_metadata(
                "eval_criteria", "waste_lvl_before,waste_lvl_after,distance"
            )
            msg.body = f"Need to drop waste from bin {self.agent.bin_number}."
            (
                self.set_next_state(STATE_TWO)
                if not item.isAvailable()
                else self.set_next_state(STATE_THREE)
            )


class StateTwo(State):
    """
    No trucks available - all refused call for proposals
    """

    async def run(self):
        print("2️⃣ No trucks available - all refused call for proposals")


class StateThree(State):
    """
    Truck proposes to pick up the bin
    """

    async def run(self):
        print("3️⃣ Truck proposes to pick up the bin")
        msg = Message(to=str(self.agent.jid))
        msg.set_metadata("type", "Proposal")
        msg.set_metadata("", "Proposal")


class StateFour(State):
    """
    Bin accepts the proposal
    """

    async def run(self):
        print("4️⃣ Bin accepts the proposal")


class StateFive(State):
    """
    Bin informs the truck that the job is done
    """

    async def run(self):
        print("5️⃣ Bin informs the truck that the job is done")


class ContractNetFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print("--------")
