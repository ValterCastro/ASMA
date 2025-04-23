from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from announcement_types import AnnouncementType
from spade.behaviour import OneShotBehaviour
from central import Central
from dijkstra import dijkstra
import asyncio
import numpy as np


STATE_ZERO = "INTERVAL" # Interval in empty garbage behavior
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
        self.add_transition(source=STATE_ONE, dest=STATE_TWO)
        self.add_transition(source=STATE_ONE, dest=STATE_THREE)
        self.add_transition(source=STATE_TWO, dest=STATE_ZERO)
        self.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        self.add_transition(source=STATE_FOUR, dest=STATE_FIVE)
        self.add_transition(source=STATE_FIVE, dest=STATE_ZERO)
        
        
        # self.agent.inbox = []
        
        # for truck in self.central.trucks.values():
        #     truck.inbox = []
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
    Bin is empty - Interval between bin being empty and full/supplied
    """
    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav
        
    async def run(self):
        print(f"0 Bin \033[31m{self.behav.agent.jid}\033[0m is empty - Waiting to be refilled")
        
        await asyncio.sleep(5)
        
        self.set_next_state(STATE_ONE)

class StateOne(State):
    """
    Bin is full - Call for trucks proposals
    """
    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):
        print(f"1️⃣ Bin \033[31m{self.behav.agent.jid}\033[0m is full - Call for trucks proposals")
        
        recv_behaviors = []
        
        for key, value in self.behav.central.trucks.items():

            data = {

                "location": self.agent.location

            }

            self.behav.agent.msg_behav = InformBehav(agent=self.behav.agent, receiver_address=value.jid, metadata=data, body="I ANNOUNCE")
            self.behav.agent.add_behaviour(self.behav.agent.msg_behav)

            value.rec_behav = RecvBehav(agent=value)
            value.add_behaviour(value.rec_behav)
            recv_behaviors.append(value.rec_behav)


            available_truck_position = value.isAvailable(self.behav.agent.current_waste_lvl) 
    
            if available_truck_position :

                # self.set_next_state(STATE_THREE)

                self.behav.available_trucks[str(value.jid)] = value
                print(self.behav.available_trucks)
                

            else : 
                value.msg_behav = InformBehav(agent=value.jid, receiver_address=self.behav.agent, metadata=None, body="REFUSE")
                value.add_behaviour(value.msg_behav)
                
        for behav in recv_behaviors:
            await behav.join()  

        if len(self.behav.available_trucks) == 0:
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
        
        self.set_next_state(STATE_ZERO)


class StateThree(State):
    """
    Truck proposes to pick up the bin
    """

    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav
        


    async def run(self):
        print(f"3️⃣ Bin \033[31m{self.behav.agent.jid}\033[0m - At least one truck is available")
        
        recv_behaviors = []
            
        for key , truck in self.behav.central.trucks.items():
           

           data = {
                "location": truck.location,
           }

           truck.msg_behav = InformBehav(agent=truck.jid, receiver_address=self.behav.agent.jid, metadata=data, body="I PROPOSE")
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
        print(f" 4️⃣ Bin \033[31m{self.behav.agent.jid}\033[0m - Bin accepts the proposal")
        
        
        best_distance = np.inf
        
        available_truck_nodes = {}
        
        recv_behaviors = []
        
        for msg in self.behav.agent.inbox:
            
            print(msg)
            
            if len(self.behav.central.trucks) > 0:
                
                print(self.behav.central.trucks[str(msg.sender)])
            
                available_truck_nodes[self.behav.central.trucks[str(msg.sender)].location] = self.behav.central.trucks[str(msg.sender)]
                
                
            
        
        for key , value in available_truck_nodes.items():
            distance = dijkstra(key, self.behav.agent.location, self.behav.central.nodes)
            if best_distance > distance:
                
                best_distance = distance
                self.behav.winner = value
                print("Winner", self.behav.winner)
                
        self.behav.agent.msg_behav = InformBehav(agent=self.behav.agent, receiver_address=self.behav.winner.jid, metadata=None, body="I ACCEPT PROPOSE")
        self.behav.agent.add_behaviour(self.behav.agent.msg_behav)

        self.behav.winner.rec_behav = RecvBehav(agent=self.behav.winner)
        self.behav.winner.add_behaviour(self.behav.winner.rec_behav)
        recv_behaviors.append(self.behav.winner.rec_behav)
            
            
        for behav in recv_behaviors:
            await behav.join()  
        
        
        self.set_next_state(STATE_FIVE)
        
        



class StateFive(State):
    """
    Bin informs the truck that the job is done
    """
    
    
    def __init__(self, behav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behav = behav

    async def run(self):
        print(f"5 \033[31m{self.behav.agent.jid}\033[0m - Inform Done")
        print("State 5", self.behav.winner)
        
        self.set_next_state(STATE_ZERO)
        
        


class ContractNetFSMBehaviour(FSMBehaviour):

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent  

    async def on_start(self):
        print("\n--------\n")
