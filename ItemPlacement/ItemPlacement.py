import argparse
import csv
import math
import struct
import sys

from dataclasses import dataclass
from matplotlib import animation
from typing import Callable, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

# hacky setup for the import
sys.path.insert(0, '../RNG')
from RugratsRand import RugratsRand

def get_linear_dist(x1, y1, z1, x2, y2, z2):
    return math.sqrt(abs(x2-x1)**2 + (abs(y2-y1)**2) + abs(z2-z1))

# note Y and Z are swapped compared to the graph (and Z, labeled Y on the graph, is inverted)
def glasses_filter(x, y, z):
    valid = True
    # filter upstairs
    if y < 0:
        valid = False
    # filter bathroom and nearby rooms
    if (x > 35000 and z < 10000):
        valid = False
    return valid

def spike_outside_filter(x, y, z):
    valid = True
    # filter upstairs
    if y < 0:
        valid = False
    return valid

def spike_upstairs_filter(x, y, z):
    valid = True
    # filter outside
    if y > 0:
        valid = False
    # only left side of stairs
    if z > 0:
        valid = False
    # immediately after the stairs
    if x > 10000:
        valid = False
    return valid


@dataclass
class LevelInfo():
    level_name: str
    object_name: str
    dump_filename: str
    num_objects: int
    spawn: Tuple[int, int, int]
    placement_filter: Callable
    rng_preincrement: int

GLASSES_LEVEL_INFO = LevelInfo(
    level_name="glasses",
    object_name="NPC Hiding",
    dump_filename="./hidingLocations.dmp",
    num_objects=3,
    spawn=(3309, 670, 16563),
    placement_filter=glasses_filter,
    rng_preincrement=7
)

SPIKE_LEVEL_INFO = LevelInfo(
    level_name="spike",
    object_name="Spike",
    dump_filename="./spikeLocations.dmp",
    num_objects=1,
    spawn=(28657, 779, 13322),
    placement_filter=spike_upstairs_filter,
    rng_preincrement=0
)

#TODO(Lazy) add info for Cynthia

@dataclass
class Placements():
    iteration: int
    rng_value: int
    # list of (x, y, z) location tuples
    locations: List[Tuple[int, int, int]]

class ObjectLocation():
    def __init__(self, x, y, z, info):
        self.x = x
        self.y = y
        self.z = z
        self.chance = (info >> 8) & 0xFF
        self.in_use = (info >> 24) & 0xFF

    def __str__(self):
        def _le_hex(i):
            return f"0x{i.to_bytes(4, 'little', signed=True).hex()}"

        return f"x: {self.x:<8} | {_le_hex(self.x)}\n" \
               f"y: {self.y:<8} | {_le_hex(self.y)}\n" \
               f"z: {self.z:<8} | {_le_hex(self.z)}\n" \
               f"Chance: {self.chance}\n" \
               f"In use: {self.in_use}"

# TODO(lazy) add comments and typing
def parse_locations(location_file):
    def _unpack(packed_str):
        return struct.unpack('i', bytearray.fromhex(packed_str))[0]

    location_objs = []
    with open(location_file, "r") as locations:
        csv_reader = csv.reader(locations)

        for line_count, row in enumerate(csv_reader):
            if line_count == 0:
                # just skip the header
                continue

            elif len(row) == 0:
                # stop parsing after any blank newline
                break

            else:
                _x, _y, _z, _data = row
                location_objs.append(ObjectLocation(_unpack(_x), _unpack(_y), _unpack(_z), _unpack(_data)))

    return location_objs

# surprisingly, this is actually refactored to be _easier_ to understand than the original code
def get_obj_locations(starting_seed, obj_locations, num_to_place, location_offset=0):
    assert num_to_place > 0
    processed_count = 0
    placed_tracker = [False] * len(obj_locations)
    rand = RugratsRand(seed=starting_seed)
    selected_locations = []

    while processed_count < num_to_place:
        location_index = location_offset
        placed = False
        attempts = 5 # it is not know why the original developers did this
        rand99 = (rand.next8() & 0xff) % 100

        while not placed and attempts >= 0:
            attempts = attempts - 1

            if location_index < len(obj_locations):

                while location_index < len(obj_locations) and not placed:
                    possible_location = obj_locations[location_index]
                    if rand99 < possible_location.chance and not(placed_tracker[location_index]):
                        placed_tracker[location_index] = True
                        possible_location.in_use = True
                        selected_locations.append((possible_location.x, possible_location.y, possible_location.z))
                        placed = True
                    location_index = location_index + 1

            # TODO(lazy) Determine what actually happens if an object is not placed in max attempts
            # For now just return an empty list an have the caller check for this case
            if attempts < 0:
                return []
            rand99 = 0

        processed_count = processed_count + 1

    return selected_locations

# returns a list of tuples where each entry is (iteration number, rng value used, locations)
def generate_placements(possible_locations,
                        num_objs_to_place,
                        iterations=1,
                        starting_seed=RugratsRand.DEFAULT_SEED,
                        rng_preincrement=0):
    rugrats_rand = RugratsRand(starting_seed)
    resulting_placements = []

    # start the RNG value at the starting seed passed in and increment by the preincrement amount to get to the real starting seed
    rng_value = rugrats_rand.seed
    for i in range(rng_preincrement):
        rng_value = rugrats_rand.next32()

    # Begin generating the placements using the current RNG value and continue to increment it every loop
    for i in range(iterations):
        placed_locations = get_obj_locations(rng_value, possible_locations, num_objs_to_place)
        placements = Placements(i, rng_value, placed_locations)
        # filter out failed placements
        if len(placements.locations) > 0:
            resulting_placements.append(placements)
        # Finish this iteration by grabbing the next seed
        rng_value = rugrats_rand.next32()

    return resulting_placements

def graph_placements(placements,
                     possible_coords,
                     object_name="Object",
                     player_location=None,
                     show_graph=True,
                     animate_graph=False,
                     save_graph=False):
    possible_xs, possible_ys, possible_zs = possible_coords
    placed_xs, placed_ys, placed_zs = list(map(list, zip(*placements.locations)))

    fig = plt.figure(figsize=(16,9))
    ax = plt.axes(projection='3d')
    if player_location is not None:
        player_x, player_y, player_z = player_location
        ax.scatter3D(player_x, player_z, player_y, c='r', label="Player's Location")
    ax.scatter3D(possible_xs, possible_zs, possible_ys, label=f"Possible {object_name} Locations")
    ax.scatter3D(placed_xs, placed_zs, placed_ys, c='g', s=100, label=f"Actual {object_name} Locations")
    subtitle = f"Number of RNG Calls to Reach: {placements.iteration}"
    ax.set_title(f"Hiding Locations When Starting with Seed: 0x{placements.rng_value:08X}\n{subtitle}")
    ax.legend(bbox_to_anchor=(1.60, 0.5), loc='right')
    label_pad = 20
    ax.axes.set_xlabel('X - Positive Towards Garage', labelpad=label_pad)
    ax.axes.set_ylabel('Z - Negative Towards Living Room', labelpad=label_pad)
    ax.axes.set_zlabel('Y', labelpad=label_pad)
    plt.gca().invert_zaxis()
    ax.set_xlim([-10000, 50000])
    ax.set_ylim([-25000, 35000])
    ax.set_zlim([1000, -6000])

    def rotate_iso(angle):
        ax.view_init(azim=angle, elev=45)

    if animate_graph or save_graph:
        angle = 1
        ani = animation.FuncAnimation(fig, rotate_iso, frames=np.arange(0, 360, angle), interval=40)
        if save_graph:
            graph_name = f'{object_name}_optimal_seed_0x{placements.rng_value:08X}.gif'
            print(f"Saving graph: {graph_name}\nThis may take a minute...")
            ani.save(graph_name, writer=animation.PillowWriter(fps=20))

    if show_graph:
        plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--start_seed", help="Seed to start with. Overridden by hex_start_seed", type=int, default=RugratsRand.DEFAULT_SEED)
    parser.add_argument("-x", "--hex_start_seed", help="Seed to start with expected in LE order. Overrides (int) start_seed", type=str, default=None)
    parser.add_argument("-i", "--iterations", help="Number of placements to generate", type=int, default=1)
    parser.add_argument("-l", "--level_selection", const="all", nargs="?", required=True, choices=[f"{GLASSES_LEVEL_INFO.level_name}", f"{SPIKE_LEVEL_INFO.level_name}"], help="The level for which placements shall be generated")
    parser.add_argument("-d", "--display_graph", help="If True, displays graph(s) when generated", default=False, action="store_true")
    parser.add_argument("-s", "--sort", help="If not None, sorts the placements by linear distance from character spawn and filters all but the top N provided via this argument (negative for all)", type=int, nargs='?', const=-1)
    parser.add_argument("--animate_graph", help="If True, adds a rotation animation to the graph", default=False, action="store_true")
    parser.add_argument("--save_graph", help="If True, saves graph(s) to the current directory", default=False, action="store_true")
    parser.add_argument("--filter", help="If True, applies level specific, code-defined, filter before generating graphs", default=False, action="store_true")
    args = parser.parse_args()

    # hacky override of the start_seed parameter to provide the option of int or hex
    if args.hex_start_seed is not None:
        args.start_seed =  int(args.hex_start_seed, 16)

    # Configure for the requested object type
    level_info = None
    if args.level_selection == SPIKE_LEVEL_INFO.level_name:
        level_info = SPIKE_LEVEL_INFO
    elif args.level_selection == GLASSES_LEVEL_INFO.level_name:
        level_info = GLASSES_LEVEL_INFO
    # TODO(lazy) add cynthia level
    else:
        raise RuntimeError(f"Unknown selector group: '{args.level_selection}'. Use --help to display options for --level_selection")

    # find all possible placements for the specified range given the starting RNG seed
    possible_locations = parse_locations(level_info.dump_filename)
    possible_xs = [obj.x for obj in possible_locations]
    possible_ys = [obj.y for obj in possible_locations]
    possible_zs = [obj.z for obj in possible_locations]
    possible_coords = (possible_xs, possible_ys, possible_zs)
    all_placements = generate_placements(possible_locations=possible_locations,
                                         num_objs_to_place=level_info.num_objects,
                                         iterations=args.iterations,
                                         starting_seed=args.start_seed,
                                         rng_preincrement=level_info.rng_preincrement)

    # filter placements
    filtered_placements = all_placements
    if args.filter:
        def _is_acceptable_placement(placement):
            acceptable = True
            for (object_x, object_y, object_z) in placement.locations:
                if not level_info.placement_filter(object_x, object_y, object_z):
                    acceptable = False
                    break
            return acceptable
        filtered_placements = [i for i in filtered_placements if _is_acceptable_placement(i)]

    # sort remaining placements
    sorted_placements = filtered_placements
    if args.sort is not None:
        def _score_function(placement):
            score = 0
            for (object_x, object_y, object_z) in placement.locations:
                player_x, player_y, player_z = level_info.spawn
                score += get_linear_dist(object_x, object_y, object_z,
                                         player_x, player_y, player_z)
            return (score, placement.iteration)
        sorted_placements.sort(key=_score_function)
        if args.sort > 0:
            sorted_placements = sorted_placements[:args.sort]

    # graph placements
    for placements in sorted_placements:
        graph_placements(placements=placements,
                         possible_coords=possible_coords,
                         object_name=level_info.object_name,
                         player_location=level_info.spawn,
                         show_graph=args.display_graph,
                         animate_graph=args.animate_graph,
                         save_graph=args.save_graph)


if __name__ == "__main__":
    main()
