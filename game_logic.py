from mapa import Map
from consts import Tiles
from tree_search import *

class Logic:

    #node com keeper e caixas
    #posiçoes do mapa
    def __init__(self, mapa):
        self.mapa = mapa
        self.width = self.get_map_width()                      
        self.dead_squares = self.simple_deadlocks()
        # print("Deadlocks:",self.dead_squares)
        # print(self.width)

    def get_map_width(self):
        width = 0
        for line in self.mapa._map:
            if (len(line) > width):
                width = len(line)

        return width
    
    def coordenate_to_num(self, coordenate):
        return coordenate[1] * self.width + coordenate[0]

    #retorna uma lista de moves
    def possible_moves(self, state):
        actlist_keeper = []

        for tile in self.positions_around_keeper(state):
            if self.move_is_valid(tile, state):
                actlist_keeper.append(tile)

        return actlist_keeper

    #valida o move
    def move_is_valid(self, tile, state):

        if self.has_box(tile, state):                                  
            return self.push_is_valid(tile, state)                     
                                                                
        return not self.is_wall(tile)                           
                                                                  
    def has_box(self, tile, state):
        return True if tile in state.boxes else False
    
    def push_is_valid(self, box, state):

        new_box_position = self.new_box_position(box, state)

        return not self.has_box(new_box_position, state) and not self.is_wall(new_box_position) and new_box_position not in self.dead_squares
    
    def new_box_position(self, box, state):
        return box + (box - state.keeper)

    def positions_around_keeper(self, state):
        x = state.keeper
        return [x - self.width, x + 1, x + self.width, x - 1]    #cima,dir,baixo,esq

    def map_positions(self):
        positions = self.mapa.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL])
        list = []

        for position in positions:
            list.append(self.coordenate_to_num(position))

        return list  

    def keeper(self):
        return self.coordenate_to_num(self.mapa.keeper)

    def list_walls(self):
        walls = self.mapa.filter_tiles([Tiles.WALL])
        list = []

        for wall in walls:
            list.append(self.coordenate_to_num(wall))

        return list
        
    def list_boxes(self):
        list = []
        
        for box in self.mapa.boxes:
            list.append(self.coordenate_to_num(box))
        
        return list

    def list_goal(self):
        goals = self.mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])
        list = []

        for goal in goals:
            list.append(self.coordenate_to_num(goal))
        
        return list

    def is_wall(self, tile):
        return True if tile in self.list_walls() else False

    #--------Deadlocks---------#
    def simple_deadlocks(self):

        valid_squares = []
        for g in self.list_goal():
            valid_squares += (self.__pull_block(g, [g]))
        
        return [square for square in self.map_positions() if square not in valid_squares] 

    #auxiliary function for square_deadlock
    def __pull_block(self,pull_from, visited_squares):

        x = pull_from
        #set keeper next to the box (try positions around the box) and try to pull the box
        if not self.is_wall(x+1) and not self.is_wall(x+2) and (x+1) not in visited_squares:
            visited_squares.append((x+1))
            visited_squares = self.__pull_block((x+1),visited_squares)
        
        if not self.is_wall(x-1) and not self.is_wall(x-2) and (x-1) not in visited_squares:
            visited_squares.append((x-1))
            visited_squares = self.__pull_block((x-1),visited_squares)

        if not self.is_wall(x + self.width) and not self.is_wall(x + self.width * 2) and (x + self.width) not in visited_squares:
            visited_squares.append(x + self.width)
            visited_squares = self.__pull_block((x + self.width),visited_squares)
        
        if not self.is_wall(x - self.width) and not self.is_wall(x - self.width * 2) and (x - self.width) not in visited_squares:
            visited_squares.append((x - self.width))
            visited_squares = self.__pull_block((x - self.width),visited_squares)

        return visited_squares