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
    
    def unseen_tiles(self, vision: set[tuple[tuple[int, int], Entity]]):
        all_cells = {(r, c) for r in range(self.walls.shape[0]) for c in range(self.walls.shape[1]) if not self.walls[r, c]}
        seen_cells = {point for point, entity in vision}
        unseen_cells = all_cells - seen_cells
        return unseen_cells
    

    def score_land(self, vision: set[tuple[tuple[int, int], Entity]], type: str) -> tuple[dict, dict]:
        #dijkstra map of values. If you're a scout, prioritize exploration (and food)
        #attacker prioritizes enemy ants and hills
        #guard prioritizes locations near the hill and food

        my_ants = {coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT}
        my_hills = {coord for coord, kind in vision if kind == Entity.FRIENDLY_HILL}
        their_ants = {coord for coord, kind in vision if kind == Entity.ENEMY_ANT}
        their_hills = {coord for coord, kind in vision if kind == Entity.ENEMY_HILL}
        seen_food = {coord for coord, kind in vision if kind == Entity.FOOD}

        attract_dijkstra = defaultdict(lambda: float('inf'))
        detract_dijkstra = defaultdict(lambda: float('inf'))

        if type == 'scout':
            for food in seen_food:
                attract_dijkstra[food] = -5            
            for tile in self.unseen_tiles(vision):
                attract_dijkstra[tile] = -1

            for ant in my_ants:
                detract_dijkstra[ant] = -1
            for hill in my_hills:
                detract_dijkstra[hill] = -7 #note this will become positive

        if type == 'guard':
            for hill in my_hills:
                attract_dijkstra[hill] = -4
            # for tile in self.unseen_tiles(vision):
            #     detract_dijkstra[tile] = -2

        if type == 'attack':
            for hill in my_hills:
                detract_dijkstra[hill] = -4 #note this will become positive
            for enemy in their_ants:      
                attract_dijkstra[enemy] = -5
            for e_hill in their_hills:      
                attract_dijkstra[e_hill] = -15
            for tile in self.unseen_tiles(vision):
                attract_dijkstra[tile] = 0
    
        return(attract_dijkstra, detract_dijkstra)
    
    
    def run_single_dijkstra(self, base_dict, all_cells):
        frontier: list[tuple[float, tuple[int, int]]] = []
        smelly = defaultdict(lambda: float('inf'), base_dict)
        
        for cell, value in base_dict.items():
            if value != float('inf'):
                heapq.heappush(frontier, (value, cell))

        while frontier:
            value, cell = heapq.heappop(frontier)
            if value > smelly[cell]:
                continue
            for neighbor in valid_neighbors(*cell, self.walls):
                if neighbor not in all_cells:
                    continue
                new_value = value + 1
                if new_value < smelly[neighbor]:
                    smelly[neighbor] = new_value
                    heapq.heappush(frontier, (smelly[neighbor], neighbor))

        return smelly

    def combine_dijkstra(self, vision: set[tuple[tuple[int, int], Entity]], type: str):
        # all_cells = {point for point, entity in vision}
        all_cells = {(r, c) for r in range(self.walls.shape[0]) for c in range(self.walls.shape[1]) if not self.walls[r, c]}
        attract_dijkstra, detract_dijkstra = self.score_land(vision, type)

        attract_dijkstra = self.run_single_dijkstra(attract_dijkstra, all_cells)
        detract_dijkstra = self.run_single_dijkstra(detract_dijkstra, all_cells)
        for cell in all_cells:
            detract_dijkstra[cell] = -1.2 * detract_dijkstra[cell]

        dijkstra = defaultdict(lambda: float('inf'))
        for cell in all_cells:
            dijkstra[cell] = attract_dijkstra[cell] + detract_dijkstra[cell]

        return dijkstra

    def choose_role(
            self, my_ants, my_hills, 
            radius: int, ant_capacity: int, food_capacity: int, food: int
            ) -> defaultdict: 
        maximum_guards = 50
        guards = 0
        maximum_attackers = 50
        attackers = 0
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
            if near_colony[ant] and guards < maximum_guards and len(my_ants) > 15:
                ant_type[ant] = 2
                guards += 1
            else:
                if len(my_ants) > ant_capacity and food > food_capacity and attackers < maximum_attackers:
                    ant_type[ant] = 3
                    attackers += 1
                else:
                    ant_type[ant] = 1

        print(f'guards: {guards}')
        print(f'scouts: {len(my_ants) - guards - attackers}')
        print(f'attackers: {attackers}')
        if attackers == 0:
            print("no attackers because:")
            print(f'food: {food}')
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

        ant_type_dict = self.choose_role(my_ants, my_hills, radius = 5, ant_capacity = 210, food_capacity = 0, food = stored_food)
        #if there's too many guards, chnge it tio a scout

        self.scout_map = self.combine_dijkstra(vision, 'scout')
        self.guard_map = self.combine_dijkstra(vision, 'guard')
        self.attack_map = self.combine_dijkstra(vision, 'attack')
        
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

            target = None
            if ant_type == 1:
                # target = min(valid, key=lambda option: self.scout_map[option])
                best_value = min(self.scout_map[option] for option in valid)
                best_cells = [option for option in valid if self.scout_map[option] == best_value]
                target = choice(best_cells)
            elif ant_type == 2:
                # target = min(valid, key=lambda option: self.guard_map[option])
                best_value = min(self.guard_map[option] for option in valid)
                best_cells = [option for option in valid if self.guard_map[option] == best_value]
                target = choice(best_cells)
            elif ant_type == 3:
                # target = min(valid, key=lambda option: self.attack_map[option])
                best_value = min(self.attack_map[option] for option in valid)
                best_cells = [option for option in valid if self.attack_map[option] == best_value]
                target = choice(best_cells)
            else:
                target = choice(valid)

            claimed_destinations.add(target)
            out.add((ant, target))
        return out
    

#for returns, it should be a set of tuples like set[(ant1prevspot, new spot),(ant2prevspot, newspot)]