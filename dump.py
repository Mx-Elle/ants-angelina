
# while frontier:
#             stink, current_cell = heapq.heappop(frontier)
#             if current_cell in closed_list:
#                 continue
#             if all_cells.issubset(closed_list):
#                 break

#             for neighbor in valid_neighbors(*current_cell, self.walls):
#                 best_mag = 0
#                 for score_neighbor in valid_neighbors(*neighbor, self.walls):
#                     neighbor_stink = dijkstra[score_neighbor]
#                     if abs(best_mag) < abs(neighbor_stink):
#                         best_mag = neighbor_stink
#                 if best_mag > 0:
#                     dijkstra[neighbor] = best_mag - 1
#                 if best_mag < 0:
#                     dijkstra[neighbor] = best_mag + 1
#                 # full_map.add((neighbor, dijkstra[neighbor]))
#                 if neighbor not in closed_list:
#                     heapq.heappush(
#                         frontier, (dijkstra[neighbor], neighbor)
#                     )        
#             closed_list.add(current_cell)

# if type == 'scout':
#             for hill in my_hills:
#                 detract_dijkstra[hill] = -7 #note this will become positive
#                 heapq.heappush(frontier, (detract_dijkstra[hill], hill))
#             for food in seen_food:
#                 attract_dijkstra[food] = -5
#                 heapq.heappush(frontier, (attract_dijkstra[food], food))
#         if type == 'guard':
#             for hill in my_hills:
#                 attract_dijkstra[hill] = -4
#                 heapq.heappush(frontier, (attract_dijkstra[hill], hill))
#         if type == 'attack':
#             for hill in my_hills:
#                 detract_dijkstra[hill] = -4 #note this will become positive
#                 heapq.heappush(frontier, (detract_dijkstra[hill], hill))
#             for enemy in their_ants:      
#                 attract_dijkstra[enemy] = -5
#                 heapq.heappush(frontier, (attract_dijkstra[enemy], enemy))
#             for e_hill in their_hills:      
#                 attract_dijkstra[e_hill] = -15
#                 heapq.heappush(frontier, (attract_dijkstra[e_hill], e_hill))

                # target = min(self.attack_map[option] for option in valid)
                # for option in valid:
                #     if target_val < self.attack_map[option]:
                #         target_val = self.attack_map[option]
                #         target = option


 def run_single_dijkstra(self, base_dict, all_cells):
        frontier = []
        smelly = base_dict.copy()
        
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
        all_cells = {point for point, entity in vision}
        attract_dijkstra, detract_dijkstra = self.score_land(vision, type)

        attract_dijkstra = self.run_single_dijkstra(attract_dijkstra, all_cells)
        detract_dijkstra = self.run_single_dijkstra(detract_dijkstra, all_cells)
        for cell in all_cells:
            detract_dijkstra[cell] = -1.2 * detract_dijkstra[cell]

        dijkstra = defaultdict(lambda: float('inf'))
        for cell in all_cells:
            dijkstra[cell] = attract_dijkstra[cell] + detract_dijkstra[cell]

        return dijkstra

    def run_dijkstra(self, vision: set[tuple[tuple[int, int], Entity]], type: str):
        
        all_cells = {point for point, entity in vision}
        attract_dijkstra, detract_dijkstra = self.score_land(vision, type)

        #attract
        changed = True
        while changed:
            changed = False
            for cell in all_cells:
                min_neighbor = min(attract_dijkstra[neighbor] for neighbor in valid_neighbors(*cell, self.walls))
                if min_neighbor + 1 < attract_dijkstra[cell]:
                    attract_dijkstra[cell] = min_neighbor + 1
                    changed = True 
        #detract
        changed = True
        while changed:
            changed = False
            for cell in all_cells:
                min_neighbor = min(detract_dijkstra[neighbor] for neighbor in valid_neighbors(*cell, self.walls))
                if min_neighbor + 1 < detract_dijkstra[cell]:
                    detract_dijkstra[cell] = min_neighbor + 1
                    changed = True
        for cell in all_cells:
            detract_dijkstra[cell] = -1.2 * detract_dijkstra[cell]
            min_neighbor = min(detract_dijkstra[neighbor] for neighbor in valid_neighbors(*cell, self.walls))
            if min_neighbor + 1 < detract_dijkstra[cell]:
                detract_dijkstra[cell] = min_neighbor + 1
    
        dijkstra = defaultdict(lambda: float('inf'))
        for cell in all_cells:
            dijkstra[cell] = attract_dijkstra[cell] + detract_dijkstra[cell]

        return dijkstra

        # self.scout_map = self.run_dijkstra(vision, 'scout')
        # self.guard_map = self.run_dijkstra(vision, 'guard')
        # self.attack_map = self.run_dijkstra(vision, 'attack')