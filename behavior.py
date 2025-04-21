from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from spade.behaviour import OneShotBehaviour
from central import Central
from dijkstra import dijkstra
import asyncio

STATE_ZERO = "BIN_NOT_FULL"  # Bin is not full
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
        self.available_trucks = []
        #self.fsm_added = False

    async def on_start(self):
        print("Starting announcement . . .")

    async def run(self):
        print(self.agent.jid)
        fsm = ContractNetFSMBehaviour(agent=self.agent)
        fsm.add_state(name=STATE_ONE, state=StateOne(agent=self.agent ,central=self.central , trucks=self.available_trucks), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree(agent=self.agent, trucks=self.available_trucks))
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_ONE, dest=STATE_THREE)
        #fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        #fsm.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        self.agent.add_behaviour(fsm)
        

    
        await asyncio.sleep(5)

class InformBehav(OneShotBehaviour):
        
        def __init__(self, agent, receiver_address, metadata, body, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.receiver_address = receiver_address  
            self.agent = agent
            self.body = body
            self.metadata = metadata

        async def run(self):
            print("InformBehav running")
            msg = Message(to=str(self.receiver_address))     # Instantiate the message

            if self.metadata is not None:
                for key, value in self.metadata.items():
                    msg.set_metadata(key, value)
            msg.body = self.body

            await self.send(msg)
            print("Message sent!")

            #print(msg.body)

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            

class RecvBehav(OneShotBehaviour):
        
        def __init__(self, agent, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.agent = agent
        

        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10) # wait for a message for 10 seconds
            self.agent.inbox.append(msg)

            #inbox.append(msg)

            if msg:
                #print("YES")
                print("Message received with content: {}".format(msg.body))
            else:
                print("NO")
                #print("Did not received any message after 10 seconds")

            # # stop agent from behaviour
            

class StateZero(State):
    """
    Bin is not full - Wait for the bin to be full
    """

    async def run(self):
        print(f"0️⃣ Bin \033[31m{self.agent.jid}\033[0m is not full - Wait for the bin to be full")
        #self.set_next_state(STATE_ONE)

class StateOne(State):
    """
    Bin is full - Call for trucks proposals
    """
    def __init__(self, agent, central, trucks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.central = central  # Store the agent address
        self.available_trucks = trucks

    async def run(self):
        print(f"1️⃣ Bin \033[31m{self.agent.jid}\033[0m is full - Call for trucks proposals")
        
        
        for key, value in self.central.trucks.items():

            data = {

                "location": self.agent.location

            }

            self.agent.msg_behav = InformBehav(agent=self.agent, receiver_address=value.jid, metadata=data, body="I ANNOUNCE")
            self.agent.add_behaviour(self.agent.msg_behav)

            value.rec_behav = RecvBehav(agent=value)
            value.add_behaviour(value.rec_behav)


            available_truck_position = value.isAvailable(self.agent.current_waste_lvl) 
    
            if available_truck_position :

                # self.set_next_state(STATE_THREE)

                self.available_trucks.append(value)
                

            else : 
                value.msg_behav = InformBehav(agent=value.jid, receiver_address=self.agent, metadata=None, body="REFUSE")
                value.add_behaviour(value.msg_behav)

        if len(self.available_trucks) == 0:
            self.set_next_state(STATE_TWO)
            
        else :
            self.set_next_state(STATE_THREE)
            

        '''
                if not value.isAvailable()
                else self.set_next_state(STATE_THREE)
            
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

    def __init__(self, agent, trucks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.trucks = trucks
        


    async def run(self):
        print(f"3️⃣ Bin  \033[31m{self.agent.jid}\033[0m - At least one truck is available")



        #distances = dijkstra(self.agent.location, self.central.nodes)
        #print("Distances: ", distances)


        # for truck in self.available_trucks:
        #     truck_location = self.central.trucks[truck].location
        #     truck_distance = distances[truck_location]
        #     print(f"Truck {truck} | location: {truck.location} | distance: {truck_distance}")
            
        for truck in self.trucks:
           

           data = {
                "location": truck.location,
           }

           truck.msg_behav = InformBehav(agent=truck.jid, receiver_address=self.agent.jid, metadata=data, body="I PROPOSE")
           truck.add_behaviour(truck.msg_behav)

           self.agent.rec_behav = RecvBehav(agent=self.agent)
           self.agent.add_behaviour(self.agent.rec_behav)
            


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
        
        while not truck.isAvailable(): # como ver qual era o truck responsavel
            await asyncio.sleep(1)
            
        # esvaziar o bin
        # truck deixa de estar busy


class ContractNetFSMBehaviour(FSMBehaviour):

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent  

    async def on_start(self):
        print("\n--------\n")
