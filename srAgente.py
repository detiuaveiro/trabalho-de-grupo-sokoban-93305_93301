from tree_search import *
from game_logic import *
from state import *
import math

class Agent(SearchDomain):
    def __init__(self, logic):
        self.logic = logic

    #possiveis ações

    # actions = (box , move list)
    def actions(self, state):
        
        reachable_positions = self.__searchReachable(state)
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

                    if self.logic.tunnels != [] and box not in self.logic.goals:
                        box_new = self.logic.new_box_position(box, pos)
                        direction = box - pos
                        extra_path = []
                        # print("tunnels", self.logic.tunnels())
                        for tunnel in self.logic.tunnels:
                            if box_new in tunnel:
                                extra_path = self.logic.directed_tunnel(tunnel, direction)
                                # print("extra path", extra_path)
                                for box_state in state.boxes:
                                    # print("box", box)
                                    if box_state ==  (extra_path[-1] + direction):
                                        # print("extra path errado com a caixa", extra_path)
                                        extra_path = extra_path[:-1]
                                        # print("new extra path", extra_path)
                                    
                            # print("extra_path", extra_path)
                        if extra_path != []:
                            # print("encontrou um tunel")
                            # print("tunel", extra_path)
                            # print("path antes", path)
                            path.extend(extra_path)
                            # print("path depois", path)
                    
                    boxes_paths.append((box,path))

        # print(boxes_paths)
        # print("------------------------")
        return boxes_paths
    
    #consequencias da açao escolhida
    def result(self, state, action):
        box = action[0]
        # print("initial box", box)
        keeper = action[1][-2]
        # print("keeper", keeper)

        box_positions = state.boxes[:]
        box_positions.remove(box)
        # print("box_positions dps do remove", box_positions)
        if box != action[1][-1]:
            box = action[1][-1]
        # print("print box", box)
        box_positions.append(self.logic.new_box_position(box, keeper))

        box_positions.sort()
        # print("box postions",box_positions)
        newstate = State(box, box_positions)
        # print("newstate", newstate)
        # print("---------------//----------------")
        
        return newstate

    #lista das caixas vs lista dos diamantes
    def satisfies(self, state_boxes, goal):
        return state_boxes == goal

    def cost(self, state, action):
        return 1

        #heuristica numero 1
    
    # def heuristic(self, boxes, goals):
    #     min = self.min_distance(boxes, goals)
    #     return min

    # def min_distance(self, boxes, goals):
    #     distances = self.distances_all_boxes_to_goals(boxes, goals)
    #     distance = 0
    #     for box in distances:
    #         distance += min(distances[box].values())

    #     return distance

    # def distances_all_boxes_to_goals(self, boxes, goals):
    #     distances = {}
    #     for box in boxes:
    #         distances[box] = self.distances_to_goals(box, goals)

    #     return distances

    # def distances_to_goals(self, box, goals):
    #     distance = {}
    #     for goal in goals:
    #         distance[goal] = self.__distance(box, goal)
    #     return distance

    #heuristica numero 2 (melhor ate agr)
    # def heuristic(self, boxes, goals):
    #     return self.min_distance(boxes, goals)

    # def min_distance(self, boxes, goals):
    #     visited_boxes = []
    #     visited_goals = []
    #     distances = self.distances_all_boxes_to_goals(boxes, goals)
    #     distance = 0
        
    #     for par in distances:
    #         if par[0][0] not in visited_boxes and par[0][1] not in visited_goals:
    #             distance += par[1]
    #             visited_boxes.append(par[0][0])
    #             visited_goals.append(par[0][1])

    #     return distance

    # def distances_all_boxes_to_goals(self, boxes, goals):
    #     list = []
    #     for box in boxes:   
    #         for goal in goals:
    #             list.append(((box,goal),self.__distance(box, goal)))

    #     list.sort(key=lambda n : n[1])
    #     return list
    
    # def __distance(self, p1, p2):
        # width = self.logic.width
        # tmp = math.fabs(p1 - p2)
        # return tmp // width + tmp % width

    # heuristica numero 3 (em desenvolvimento)
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
    
    #perform a graph search to search for reachable positions
    #
    #returns a list containing the predecessors of each track. If predec[track] = -1 the location is unreachable
    def __searchReachable(self, state):
        #graph (Tiles (track)), predecessors)
        predec = [-1] * self.logic.area
        initial = state.keeper
        queue = [initial]
        visited = [initial]
        predec[initial] = initial

        while queue != []:
            v = queue[0]
            queue = queue[1:]
            adjs = self.__getAdjs(v,state)

            for adj in adjs:
                if adj not in visited:
                    queue.append(adj)
                    visited.append(adj)
                    predec[adj] = v

        return predec

    def __getAdjs(self, tile, state):
        return [t for t in self.logic.positions_around_tile(tile) if t not in state.boxes and not self.logic.is_wall(t)]
