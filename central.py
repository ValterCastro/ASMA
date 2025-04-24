from time import sleep
from time import time
from helper import progress_bar
import asyncio
from datetime import datetime
import os


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
            sum([bin["waste_level"] for bin in self.bins.values()]) / len(self.bins)
            if self.bins
            else 0
        )

        statistics = {
            "total_waste_collected": self.total_waste_collected,
            "average_waste_level": self.average_waste_level,
            "waste_full_times": {
                bin_id: bin.get("time_full", "Unknown")
                for bin_id, bin in self.bins.items()
            },
            # "waste_outside_bin": self.total_waste_outside,
            "truck_distances": {
                truck_id: truck.distance_traveled
                for truck_id, truck in self.trucks.items()
            },
            "total_distance_traveled": self.total_distance_traveled,
        }

        return statistics

    def write_statistics(self):
        """
        Writes the current system statistics to stats.txt in a human-readable format.
        """
        stats = self.get_moment_statistics()

        lines = []
        lines.append(f"Timestamp: {datetime.now().isoformat()}")
        lines.append(f"Total waste collected: {stats['total_waste_collected']:.2f}")

        lines.append("• Average waste level for each bin:")
        for bin_id, bin in self.bins.items():
            lines.append(f"  - Bin {bin_id}: {bin['waste_level']:.2f}")

        lines.append("• Time each waste bin was full:")
        for bin_id, bin in self.bins.items():
            full_time = bin.get("time_full", "Unknown")
            lines.append(f"  - Bin {bin_id}: {full_time}")

        # total_waste_left_outside = sum(bin.get("waste_left_outside", 0) for bin in self.bins.values())
        # lines.append(f"• Total waste left outside the bin: {total_waste_left_outside:.2f}")

        lines.append("• Distance traveled by each truck agent:")
        for truck_id, truck in self.trucks.items():
            lines.append(f"  - Truck {truck_id}: {truck.distance_traveled:.2f}")

        lines.append(f"Total distance: {stats['total_distance_traveled']:.2f}")
        lines.append("")  # Blank line for separation

        with open("stats.txt", "w") as f:
            f.write("\n".join(lines) + "\n")

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

    async def update_world(self, filling_rate_interval):
        self.start = time()
        self.next_update = self.start + filling_rate_interval

        while time() - self.start < self.duration:
            for key, bin in self.bins.items():
                if self.start >= self.next_update:
                    bin["bin"].update()
                    self.next_update += filling_rate_interval
            for _, truck in self.trucks.items():
                truck.update()

            print(
                f"\n\033[32m⊞ [{round(time() - self.start)} / {self.duration} seconds] Updating world...\033[0m\n"
                + "".join(
                    f"\033[34mBin {bin['bin'].name}: {progress_bar(bin['bin'].current_waste_lvl / bin['bin'].capacity)}\033[0m\n"
                    for bin in self.bins.values()
                )
            )

            # self.get_moment_statistics()
            self.write_statistics()
            await asyncio.sleep(1)
        self.running = False
