#não esquecer de mandar coisas pro server nao ir abaixo
#estar smp a consumir as msgs do servidor
#3 mil steps por nivel (maximo) linha 117 do server.py
#actions movimentos


#map._map ---> todas as coordenadas do mapa
from tree_search import *
from game_logic import *
from state import *
import math

class Agent(SearchDomain):
    def __init__(self, logic):
        self.logic = logic
    
    #possiveis ações
    def actions(self, state):
        reachable_positions = self.__searchReachable(state)
        
        boxes_paths = []
        for box in state.boxes:

            pos_around_box = [t for t in self.logic.positions_around_tile(box) if not self.logic.is_wall(t) and self.logic.push_is_valid(box, t, state)]

            for pos in pos_around_box:
                if reachable_positions[pos] != -1:
                    path = [pos,box]
                    next_pos = reachable_positions[pos]

                    while next_pos != state.keeper:
                        path[:0] += [next_pos]
                        next_pos = reachable_positions[next_pos]
                    
                    boxes_paths.append((box,path))

        return boxes_paths
    
    #consequencias da açao escolhida
    def result(self, state, action):
        box = action[0]
        keeper = action[1][-2]

        box_positions = state.boxes[:]
        box_positions.remove(box)
        box_positions.append(self.logic.new_box_position(box, keeper))

        box_positions.sort()
        newstate = State(box, box_positions)
        
        return newstate

    #lista das caixas vs lista dos diamantes
    def satisfies(self, state_boxes, goal):
        return state_boxes == goal

    def heuristic(self, state, goal):
        return self.distance_to_boxes(state.boxes,state.keeper)

    def cost(self, state, action):
        return 1


    def distance_to_boxes(self, boxes, keeper):
        tdistance = 0
        for box in boxes:
            tdistance += self.__distance(box, keeper)


        return tdistance
    
    def __distance(self, p1, p2):
        width = self.logic.width
        tmp = math.fabs(p1 - p2)
        return tmp // width + tmp % width
    
    #perform a graph search to search for reachable positions
    #
    #returns a list containing the predecessors of each track. If predec[track] = -1 the location is unreachable
    def __searchReachable(self, state):
        #graph (Tiles (track)), predecessors)
        predec = [-1] * self.logic.measures
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
