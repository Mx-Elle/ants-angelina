
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