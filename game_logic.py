from mapa import Map
from consts import Tiles
from tree_search import *

class Logic:

    #node com keeper e caixas
    #posiçoes do mapa
    def __init__(self, mapa):
        self.__mapa = mapa
        self.__keeper = self.__coordenate_to_num(self.mapa.keeper)
        self.__walls = [self.__coordenate_to_num(w) for w in self.mapa.filter_tiles([Tiles.WALL])]
        self.__boxes = [self.__coordenate_to_num(b) for b in mapa.boxes]
        self.__goals = [self.__coordenate_to_num(g) for g in self.mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])]            
        self.__dead_squares = self.simple_deadlocks()

    @property
    def mapa(self):
        return self.__mapa
    
    @property
    def width(self):
        width = 0
        for line in self.mapa._map:
            if (len(line) > width):
                width = len(line)

        return width

    @property
    def height(self):
        height = 0
        for line in self.mapa._map:
            height += 1

        return height

    @property
    def measures(self):
        return self.width * self.height

    @property
    def keeper(self):
        return self.__keeper

    @property
    def walls(self):
        return self.__walls

    @property
    def boxes(self):
        return self.__boxes

    @property
    def goals(self):
        return self.__goals

    #retorna uma lista de moves
    def possible_moves(self, state):
        actlist_keeper = []
        for tile in self.positions_around_tile(state.__keeper):
            if self.move_is_valid(tile, state):
                actlist_keeper.append(tile)
        return actlist_keeper

    #valida o move
    def move_is_valid(self, tile, state):
        if self.has_box(tile, state):                                  
            return self.push_is_valid(tile, state)                     
                                                                
        return not self.is_wall(tile)                           
                                                                
    
    def push_is_valid(self, box, keeper, state):
        new_box_position = self.new_box_position(box, keeper)
        return not self.has_box(new_box_position, state) and not self.is_wall(new_box_position) and new_box_position not in self.__dead_squares
    
    def new_box_position(self, box, tile):
        return box + (box - tile)

    def positions_around_tile(self, tile):
        return [tile - self.width, tile + 1, tile + self.width, tile - 1]    #cima,dir,baixo,esq

    def has_box(self, tile, state):
        return True if tile in state.boxes else False
    
    def is_wall(self, tile):
        return True if tile in self.__walls else False
    
    def __coordenate_to_num(self, coordenate):
        return coordenate[1] * self.width + coordenate[0]
    
    def __map_positions(self):
        positions = self.mapa.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL])
        return [self.__coordenate_to_num(p) for p in positions]

    #--------Deadlocks---------#
    def simple_deadlocks(self):

        valid_squares = []
        for g in self.__goals:
            valid_squares += (self.__pull_block(g, [g]))
        
        return [square for square in self.__map_positions() if square not in valid_squares] 

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