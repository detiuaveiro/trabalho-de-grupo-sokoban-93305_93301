#não esquecer de mandar coisas pro server nao ir abaixo
#estar smp a consumir as msgs do servidor
#3 mil steps por nivel (maximo) linha 117 do server.py
#actions movimentos


#map._map ---> todas as coordenadas do mapa
from tree_search import *
from game_logic import *
from state import *

class Agent(SearchDomain):
    def __init__(self, logic):
        self.logic = logic
    
    #possiveis ações
    def actions(self, state):
        actlist = self.logic.possible_moves(state)

        return actlist
    
    #consequencias da açao escolhida
    def result(self, state, action):
        box_positions = state.boxes[:]

        if (self.logic.has_box(action, state)):
            box_positions.remove(action)
            box_positions.append(self.logic.new_box_position(action, state))

        box_positions.sort()
        newstate = State(action, box_positions)
        
        return newstate

    #lista das caixas vs lista dos diamantes
    def satisfies(self, state_boxes, goal):
        return state_boxes == goal

    def heuristic(self, city, goal_city):
        pass

    def cost(self, city, action):
        pass

