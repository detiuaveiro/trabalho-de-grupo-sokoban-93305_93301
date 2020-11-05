
# possibleMove()
# hasBox()
# possiblePush()
# isDeadLock(
from mapa import Map
from consts import Tiles
from tree_search import *

class Logic:

    #node com keeper e caixas
    #posiçoes do mapa
    def __init__(self, mapa):
        self.mapa = mapa                        

    #retorna uma lista de moves
    def possible_moves(self, state):
        actlist_keeper = []

        for tile in self.positions_around_keeper(state):
            if self.move_is_valid(tile, state):
                actlist_keeper.append(tile)

        return actlist_keeper

    #valida o move
    def move_is_valid(self, tile, state):

        if self.has_box(tile, state):                                  # if tile in self.map_positions():
            return self.push_is_valid(tile, state)                     #     if (self.has_box(tile)):
                                                                #         return self.push_is_valid(tile)
        return not self.is_wall(tile)                           #     else:
                                                                #         return True

                                                                # return False
        
    #dependendo do estado atual(node) ve se o tile tem uma caixa i guess
    def has_box(self, tile, state):
        return True if tile in state['boxes'] else False
    
    def push_is_valid(self, box, state):

        new_box_position = self.new_box_position(box, state)

        return not self.has_box(new_box_position, state) and not self.is_wall(new_box_position)
    
    def new_box_position(self, box, state):
        
        direction = (box[0] - state['keeper'][0] , box[1] - state['keeper'][1])

        new_box_position = (box[0] + direction[0], box[1] + direction[1])

        return new_box_position

    #coisas que não mudam
    def map_positions(self):
        return self.mapa.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL])
    
    def list_walls(self):
        return self.mapa.filter_tiles([Tiles.WALL])

    def is_wall(self, tile):
        return True if tile in self.list_walls() else False

    def positions_around_keeper(self, state):
        x = state['keeper'][0]
        y = state['keeper'][1]
        return [(x,y-1),(x+1,y),(x,y+1),(x-1,y)]    #cima,dir,baixo,esq





    

    