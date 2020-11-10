
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
        self.dead_squares = self.simple_deadlocks()
        # print("Deadlocks:",self.dead_squares)
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
        
    #dependendo do estado atual ve se o tile tem uma caixa i guess
    def has_box(self, tile, state):
        return True if tile in state['boxes'] else False
    
    def push_is_valid(self, box, state):

        new_box_position = self.new_box_position(box, state)

        return not self.has_box(new_box_position, state) and not self.is_wall(new_box_position) and new_box_position not in self.dead_squares
    
    def new_box_position(self, box, state):
        
        direction = (box[0] - state['keeper'][0] , box[1] - state['keeper'][1])

        new_box_position = (box[0] + direction[0], box[1] + direction[1])

        return new_box_position

    def map_positions(self):
        return self.mapa.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL])

    def keeper(self):
        return self.mapa.keeper

    def list_walls(self):
        return self.mapa.filter_tiles([Tiles.WALL])
    
    def list_boxes(self):
        return self.mapa.boxes

    def list_goal(self):
        return self.mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])
    
    def is_wall(self, tile):
        return True if tile in self.list_walls() else False

    def positions_around_keeper(self, state):
        x = state['keeper'][0]
        y = state['keeper'][1]
        return [(x,y-1),(x+1,y),(x,y+1),(x-1,y)]    #cima,dir,baixo,esq


    #--------Deadlocks---------#
    def simple_deadlocks(self):

        valid_squares = []
        for g in self.list_goal():
            valid_squares += (self.__pull_block(g, [g]))
        
        return [square for square in self.map_positions() if square not in valid_squares] 

    #auxiliary function for square_deadlock
    def __pull_block(self,pull_from, visited_squares):

        x,y = pull_from
        #set keeper next to the box (try positions around the box) and try to pull the box
        if not self.is_wall((x+1,y)) and not self.is_wall((x+2,y)) and (x+1,y) not in visited_squares:
            visited_squares.append((x+1,y))
            visited_squares = self.__pull_block((x+1,y),visited_squares)
        
        if not self.is_wall((x-1,y)) and not self.is_wall((x-2,y)) and (x-1,y) not in visited_squares:
            visited_squares.append((x-1,y))
            visited_squares = self.__pull_block((x-1,y),visited_squares)

        if not self.is_wall((x,y+1)) and not self.is_wall((x,y+2)) and (x,y+1) not in visited_squares:
            visited_squares.append((x,y+1))
            visited_squares = self.__pull_block((x,y+1),visited_squares)
        
        if not self.is_wall((x,y-1)) and not self.is_wall((x,y-2)) and (x,y-1) not in visited_squares:
            visited_squares.append((x,y-1))
            visited_squares = self.__pull_block((x,y-1),visited_squares)

        return visited_squares