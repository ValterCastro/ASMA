from time import sleep

class Central():
    total_waste_collected = 0
    average_waste_level = 0
    total_distance_traveled = 0
    bins = {}
    trucks = {}
    nodes = {}
        
    def __init__(self, nodes):
        self.bins = {}
        self.trucks = {}
        self.nodes = nodes
        
    def get_moment_statistics(self):
        """
        Returns the current statistics of the central system.
        """
        self.total_distance_traveled = sum([truck.distance_traveled for truck in self.trucks.values()])
        self.average_waste_level = sum([bin.waste_level for bin in self.bins.values()]) / len(self.bins) if self.bins else 0

        return {
            "total_waste_collected": self.total_waste_collected,
            "average_waste_level": self.average_waste_level,
            "total_distance_traveled": self.total_distance_traveled
        }
    
    def add_bin(self, bin_id, bin):
        """
        Adds a bin to the central system.
        """
        self.bins[bin_id] = {
            "bin": bin,
            "waste_level": 0,
            "time_full": 0,
        }
        
    def add_truck(self, truck_id, truck):
        """
        Adds a truck to the central system.
        """
        self.trucks[truck_id] = truck
      
    
    def update_world(self, interval):
        while True:
            for key, bin in self.bins.items(): 
                bin['bin'].update()
            for _, truck in self.trucks.items():
                break
            
            print("\033[32m⊞ Updating world...\033[0m")
            
            sleep(interval)