from multiprocessing import Queue
from random import choice
from board import Entity, neighbors
import numpy as np
import numpy.typing as npt


AntMove = tuple[tuple[int, int], tuple[int, int]]


def valid_neighbors(
    row: int, col: int, walls: npt.NDArray[np.int_]
) -> list[tuple[int, int]]:
    return [n for n in neighbors((row, col), walls.shape) if not walls[n]]


class DyingBot:

    def __init__(
        self,
        walls: npt.NDArray[np.int_],
        harvest_radius: int,
        vision_radius: int,
        battle_radius: int,
        max_turns: int,
        time_per_turn: float,
    ) -> None:
        self.walls = walls
        self.collect_radius = harvest_radius
        self.vision_radius = vision_radius
        self.battle_radius = battle_radius
        self.max_turns = max_turns
        self.time_per_turn = time_per_turn

        self.scout_map = None
        self.attack_map = None
        self.guard_map = None

    @property
    def name(self):
        return "dying_ant"
    
    def score_land(self, vision) -> set:
        #dijkstra map of 
        ...

    def move_ants(
        self,
        vision: set[tuple[tuple[int, int], Entity]],
        stored_food: int,
    ) -> set[AntMove]:
        out = set()
        my_ants = {coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT}
        my_hills = {coord for coord, kind in vision if kind == Entity.FRIENDLY_HILL}
        claimed_destinations = my_hills
        for ant in my_ants:
            valid = [
                v
                for v in valid_neighbors(*ant, self.walls)
                if v not in claimed_destinations
            ]
            if not valid:
                claimed_destinations.add(ant)
                continue
            dest = choice(valid)
            #this is where the choice is randomized, by the way
            claimed_destinations.add(dest)
            out.add((ant, dest))
        return out
    

#for returns, it should be a set of tuples like set[(ant1prevspot, new spot),(ant2prevspot, newspot)]