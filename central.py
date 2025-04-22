from time import sleep
from time import time
from helper import progress_bar


class Central:
    total_waste_collected = 0
    average_waste_level = 0
    total_distance_traveled = 0
    bins = {}
    trucks = {}
    nodes = {}

    duration = 0
    start = None

    running = True

    def __init__(self, nodes, duration):
        self.bins = {}
        self.trucks = {}
        self.nodes = nodes
        self.duration = duration

    def get_moment_statistics(self):
        """
        Returns the current statistics of the central system.
        """
        self.total_distance_traveled = sum(
            [truck.distance_traveled for truck in self.trucks.values()]
        )
        self.average_waste_level = (
            sum([bin.waste_level for bin in self.bins.values()]) / len(self.bins)
            if self.bins
            else 0
        )

        return {
            "total_waste_collected": self.total_waste_collected,
            "average_waste_level": self.average_waste_level,
            "total_distance_traveled": self.total_distance_traveled,
        }

    def add_bin(self, bin_id, bin):
        """
        Adds a bin to the central system.
        """
        self.bins[bin_id] = bin

    def add_truck(self, truck_id, truck):
        """
        Adds a truck to the central system.
        """
        self.trucks[truck_id] = truck

    def update_world(self, interval):
        self.start = time()
        while self.running:
            for key, bin in self.bins.items():
                bin.update()
            for _, truck in self.trucks.items():
                break

            print(
                f"\n\033[32m⊞ [{round(time() - self.start)} seconds] Updating world...\033[0m\n"
                + "".join(
                    f"\033[34mBin {bin.name}: {progress_bar(bin.current_waste_lvl / bin.capacity)}\033[0m\n"
                    for bin in self.bins.values()
                    )
                )


            sleep(interval)
