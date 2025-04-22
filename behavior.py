from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from spade.behaviour import OneShotBehaviour
from central import Central
from dijkstra import dijkstra
import asyncio
import numpy as np

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
        self.available_trucks = {}
        self.winner = None

    async def on_start(self):
        print("Starting announcement . . .")
    
        

    async def run(self):
        
        fsm = ContractNetFSMBehaviour(agent=self.agent)
        fsm.add_state(name=STATE_ONE, state=StateOne(agent=self.agent ,central=self.central , trucks=self.available_trucks), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo(agent=self.agent))
        fsm.add_state(name=STATE_THREE, state=StateThree(agent=self.agent, trucks=self.available_trucks, central=self.central))
        fsm.add_state(name=STATE_FOUR, state=StateFour(agent=self.agent, central=self.central, trucks=self.available_trucks, winner=self.winner, behav=self))
        fsm.add_state(name=STATE_FIVE, state=StateFive(agent=self.agent, central=self.central, winner=self.winner))
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_ONE, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_FIVE)
        self.agent.add_behaviour(fsm)
        
        self.agent.inbox = []
        
        for truck in self.central.trucks.values():
            truck.inbox = []
            
        
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

            self.exit_code = "Job Finished!"

            

class RecvBehav(OneShotBehaviour):
        
        def __init__(self, agent, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.agent = agent
        

        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10) # wait for a message for 10 seconds
            self.agent.inbox.append(msg)

            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")

            

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
        
        recv_behaviors = []
        
        for key, value in self.central.trucks.items():

            data = {

                "location": self.agent.location

            }

            self.agent.msg_behav = InformBehav(agent=self.agent, receiver_address=value.jid, metadata=data, body="I ANNOUNCE")
            self.agent.add_behaviour(self.agent.msg_behav)

            value.rec_behav = RecvBehav(agent=value)
            value.add_behaviour(value.rec_behav)
            recv_behaviors.append(value.rec_behav)


            available_truck_position = value.isAvailable(self.agent.current_waste_lvl) 
    
            if available_truck_position :

                # self.set_next_state(STATE_THREE)

                self.available_trucks[str(value.jid)] = value
                

            else : 
                value.msg_behav = InformBehav(agent=value.jid, receiver_address=self.agent, metadata=None, body="REFUSE")
                value.add_behaviour(value.msg_behav)
                
        for behav in recv_behaviors:
            await behav.join()  

        if len(self.available_trucks) == 0:
            self.set_next_state(STATE_TWO)
            
        else :
            self.set_next_state(STATE_THREE)
            


class StateTwo(State):
    """
    No trucks available - all refused call for proposals
    """
    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
    
    
    async def run(self):
        print(f"2️⃣ \033[31m{self.agent.jid}\033[No trucks available - all refused call for proposals")


class StateThree(State):
    """
    Truck proposes to pick up the bin
    """

    def __init__(self, agent, trucks, central, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.trucks = trucks
        self.central = central
        


    async def run(self):
        print(f"3️⃣ Bin \033[31m{self.agent.jid}\033[0m - At least one truck is available")
        
        recv_behaviors = []
            
        for key , truck in self.trucks.items():
           

           data = {
                "location": truck.location,
           }

           truck.msg_behav = InformBehav(agent=truck.jid, receiver_address=self.agent.jid, metadata=data, body="I PROPOSE")
           truck.add_behaviour(truck.msg_behav)

           self.agent.rec_behav = RecvBehav(agent=self.agent)
           self.agent.add_behaviour(self.agent.rec_behav)
           recv_behaviors.append(self.agent.rec_behav)
           
        for behav in recv_behaviors:
            await behav.join()  
           
        self.set_next_state(STATE_FOUR)
            
            


class StateFour(State):
    """
    Bin accepts the proposal
    """
    
    def __init__(self, agent, central, trucks, winner, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.central = central
        self.trucks = trucks
        self.winner = winner
        self.behav = behav

    async def run(self):
        print(f" 4️⃣ Bin \033[31m{self.agent.jid}\033[0m - Bin accepts the proposal")
        
        
        best_distance = np.inf
        
        available_truck_nodes = {}
        
        recv_behaviors = []
        
        for msg in self.agent.inbox:
            
            if len(self.trucks) > 0:
            
                available_truck_nodes[self.trucks[str(msg.sender)].location] = self.trucks[str(msg.sender)]
            
        
        for key , value in available_truck_nodes.items():
            distance = dijkstra(key, self.agent.location, self.central.nodes)
            if best_distance > distance:
                
                best_distance = distance
                self.behav.winner = value
                print("Winner", self.winner)
                
        self.agent.msg_behav = InformBehav(agent=self.agent, receiver_address=str(self.winner.jid), metadata=None, body="I ACCEPT PROPOSE")
        self.agent.add_behaviour(self.agent.msg_behav)

        self.behav.winner.rec_behav = RecvBehav(agent=self.winner)
        self.behav.winner.add_behaviour(self.winner.rec_behav)
        recv_behaviors.append(self.winner.rec_behav)
            
            
        for behav in recv_behaviors:
            await behav.join()  
        
        
        self.set_next_state(STATE_FIVE)
        
        



class StateFive(State):
    """
    Bin informs the truck that the job is done
    """
    
    
    def __init__(self, agent, central, winner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.central = central
        self.winner = winner

    async def run(self):
        print(f"5 \033[31m{self.agent.jid}\033[0m - Inform Done")
        print("State 5", self.winner)
        
        


class ContractNetFSMBehaviour(FSMBehaviour):

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent  

    async def on_start(self):
        print("\n--------\n")
