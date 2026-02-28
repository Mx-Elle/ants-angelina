from multiprocessing import Queue
from random import choice
from board import Entity, neighbors
import numpy as np
import numpy.typing as npt
import heapq
from collections import defaultdict


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
    
    """
    FRIENDLY_HILL = 1
    ENEMY_HILL = 2
    FRIENDLY_ANT = 3
    ENEMY_ANT = 4
    FOOD = 5
        """
    
    def score_land(self, vision: set[tuple[tuple[int, int], Entity]], type: str) -> set:
        #dijkstra map of values. If you're a scout, prioritize exploration (and food)
        #attacker prioritizes enemy ants and hills
        #guard prioritizes locations near the hill and food
        ...



    def choose_role(
            self, my_ants, my_hills, 
            radius: int, ant_capacity: int, food_capacity: int, food: int
            ) -> defaultdict: 
        """returns some role as an int:
        Ant Scout = 1
        Ant Guard = 2
        Ant Attack = 3
        """

        closed_list = set()
        frontier = []

        stinky = defaultdict(lambda: float(0))
        near_colony = defaultdict(lambda: float(0))

        ant_type = defaultdict(lambda: float(0))

        for hill in my_hills:        
            stinky[hill] = -radius
            near_colony[hill] = 1
            heapq.heappush(frontier, (stinky[hill], hill))

        while frontier:
            stink, current_cell = heapq.heappop(frontier)
            if current_cell in closed_list:
                continue
            if stink > 0:
                break
            for neighbor in valid_neighbors(*current_cell, self.walls):
                if neighbor in closed_list:
                    continue
                temp_s = stink + 1
                if temp_s < stinky[neighbor]:
                    stinky[neighbor] = temp_s
                    if neighbor not in closed_list:
                        heapq.heappush(
                            frontier, (stinky[neighbor], neighbor)
                        )
                        near_colony[neighbor] = 1
                        
            closed_list.add(current_cell)

        for ant in my_ants:
            if near_colony[ant]:
                ant_type[ant] = 2
            else:
                if len(my_ants) > ant_capacity and food > food_capacity:
                    ant_type[ant] = 3
                else:
                    ant_type[ant] = 1

        return ant_type
    #"choose ant function," basically meaning if the ant is farther away, it's a scout
    #closer, and it's a guard, and if you have more than a certain amount of ants+hills+food all your scouts become attackers

    def move_ants(
        self,
        vision: set[tuple[tuple[int, int], Entity]],
        stored_food: int,
    ) -> set[AntMove]:
        out = set()
        my_ants = {coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT}
        my_hills = {coord for coord, kind in vision if kind == Entity.FRIENDLY_HILL}
        claimed_destinations = my_hills

        ant_type_dict = self.choose_role(my_ants, my_hills, radius = 8, ant_capacity = 200, food_capacity = 5, food = stored_food)
        
        for ant in my_ants:
            ant_type = ant_type_dict[ant]
            valid = [
                v
                for v in valid_neighbors(*ant, self.walls)
                if v not in claimed_destinations
            ]
            if not valid:
                claimed_destinations.add(ant)
                continue

            if ant_type == 1:
                if self.scout_map == None:
                    #pick a new target
                    ...
                #do scout things
                dest = choice(valid)
                ...
            elif ant_type == 2:
                if self.guard_map == None:
                    #pick a new target
                    ...
                #do guard things
                dest = choice(valid)
                ...
            elif ant_type == 3:
                if self.guard_map == None:
                    #pick a new target
                    ...
                #do attack things
                dest = choice(valid)
                # dest = min(self.attack_map[valid])
                ...
            else:
                dest = choice(valid)

            claimed_destinations.add(dest)
            out.add((ant, dest))
        return out
    

#for returns, it should be a set of tuples like set[(ant1prevspot, new spot),(ant2prevspot, newspot)]