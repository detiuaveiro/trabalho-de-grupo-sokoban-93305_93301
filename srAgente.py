from tree_search import *
from game_logic import *
from state import *
import math

class Agent(SearchDomain):
    def __init__(self, logic):
        self.logic = logic

    def actions(self, state, reachable_positions):
        """ actions = (box , move list) 
        """
        
        boxes_paths = []
        
        for box in state.boxes:

            pos_around_box = [t for t in self.logic.positions_around_tile(box) if not self.logic.is_wall(t) and not self.logic.has_box(t,state)  and self.logic.push_is_valid(box, t, state)]

            for pos in pos_around_box:
                if reachable_positions[pos] != -1:
                    path = [pos,box]
                    next_pos = reachable_positions[pos]

                    while next_pos != state.keeper:
                        path[:0] += [next_pos]
                        next_pos = reachable_positions[next_pos]
                    
                    boxes_paths.append((box,path))

        return boxes_paths
    
    def result(self, state, action):
        """ Consequences of given action """
        box = action[0]
        keeper = action[1][-2]

        box_positions = state.boxes[:]
        box_positions.remove(box)
        box_positions.append(self.logic.new_box_position(box, keeper))
        keeper = box
        box_positions.sort()

        #find normalized keeper position
        reacheable_positions = self.logic.reacheable_positions(keeper,box_positions)
        normalized_position = 0
        while reacheable_positions[normalized_position] == -1:   
            normalized_position += 1        
        newstate = State(normalized_position, keeper, box_positions)

        return newstate, reacheable_positions

    def satisfies(self, state_boxes, goal):
        return state_boxes == goal

    def cost(self, state, action):
        return 1

    def heuristic(self, boxes, goals):
        return self.min_distance(boxes, goals)

    def min_distance(self, boxes, goals):
        visited_boxes = []
        visited_goals = []
        distances = self.distances_all_boxes_to_goals(boxes, goals)
        distance = 0

        len_boxes = len(boxes)
        len_goals = len(goals)
        
        for par in distances:
            if len(visited_boxes) == len_boxes and len(visited_goals) == len_goals:
                break
            if par[0][0] not in visited_boxes and par[0][1] not in visited_goals:
                distance += par[1]
                visited_boxes.append(par[0][0])
                visited_goals.append(par[0][1])

        return distance

    def distances_all_boxes_to_goals(self, boxes, goals):
        list = []
        for box in boxes:   
            for goal in goals:
                cost = self.logic.costs[goal][box]
                if cost != -1:
                    list.append(((box,goal), cost))

        list.sort(key=lambda n : n[1])
        return list
    

