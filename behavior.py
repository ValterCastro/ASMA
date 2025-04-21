from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from spade.behaviour import OneShotBehaviour
from central import Central
import asyncio

STATE_ONE = "CALL_FOR_PROPOSAL"  # Bin is full
STATE_TWO = "FAILURE"  # Every trucks refuse
STATE_THREE = "PROPOSE"  # Truck proposes to pick up the bin
STATE_FOUR = "ACCEPT_PROPOSAL"  # Bin accepts the proposal
STATE_FIVE = "INFORM:DONE"  # Bin informs the truck that the job is done
# STATE_SIX = "FAILURE"  # Bin informs the truck that the job failed


class EmptyGarbage(CyclicBehaviour):

    def __init__(self, central, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.central = central  #
        #self.fsm_added = False

    async def on_start(self):
        print("Starting announcement . . .")

    async def run(self):
        print(self.agent.jid)
        fsm = ContractNetFSMBehaviour(agent=self.agent)
        fsm.add_state(name=STATE_ONE, state=StateOne(agent=self.agent ,central=self.central), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_ONE, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        self.agent.add_behaviour(fsm)
        self.fsm_added = True

    
        await asyncio.sleep(5)

class InformBehav(OneShotBehaviour):
        
        def __init__(self, agent, receiver_address, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.receiver_address = receiver_address  #
            self.agent = agent

        async def run(self):
            print("InformBehav running")
            msg = Message(to=str(self.receiver_address))     # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")       # Set the language of the message content
            msg.body = "Hello World"

            await self.send(msg)
            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviour
            #await self.agent.stop()

class RecvBehav(OneShotBehaviour):
        
        def __init__(self, agent, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.agent = agent
        

        async def run(self):
            print("RecvBehav running")

            print("here")

            msg = await self.receive(timeout=10) # wait for a message for 10 seconds

            #inbox.append(msg)

            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")

            # # stop agent from behaviour
            #await self.agent.stop()


class StateOne(State):
    """
    Bin is full - Call for trucks proposals
    """
    def __init__(self, agent, central, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.central = central  # Store the agent address

    async def run(self):
        print("1️⃣ Bin is full - Call for trucks proposals")
        for key, value in self.central.trucks.items():

            self.agent.msg_behav = InformBehav(agent=self.agent, receiver_address=value["truck"].jid)
            self.agent.add_behaviour(self.agent.msg_behav)

            value["truck"].rec_behav = RecvBehav(agent=value["truck"])
            value["truck"].add_behaviour(value["truck"].rec_behav)

            
            
            '''
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
                if not value.isAvailable()
                else self.set_next_state(STATE_THREE)
            )
            '''


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

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent  #

    async def on_start(self):
        print("--------")
