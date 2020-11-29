from mapa import Map
from consts import Tiles
from tree_search import *
import time

class Logic:

    #node com keeper e caixas
    #posiçoes do mapa
    def __init__(self, mapa):
        self.__mapa = mapa
        self.__width = max([len(line) for line in mapa._map])
        self.__height = len(mapa._map)
        self.__measures = self.__width * self.__height
        self.__keeper = self.__coordenate_to_num(mapa.keeper)
        self.__walls = [self.__coordenate_to_num(w) for w in mapa.filter_tiles([Tiles.WALL])]
        self.__boxes = [self.__coordenate_to_num(b) for b in mapa.boxes]
        self.__goals = [self.__coordenate_to_num(g) for g in mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])]
        self.__valid_squares, self.__costs = self.get_valid_squares_and_costs()
        self.__dead_squares = self.simple_deadlocks()
        self.__valid_squares_for_tunnels = [square for square in self.__valid_squares if square not in self.__goals]
        self.__valid_squares_for_tunnels.sort()
        self.__tunnels = self.get_tunnels()

    @property
    def mapa(self):
        return self.__mapa
    
    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def measures(self):
        return self.__measures

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

    @property
    def tunnels(self):
        return self.__tunnels

    @property
    def costs(self):
        return self.__costs
    
    #retorna uma lista de moves
    #nao usado
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
        #first condition bug!
        return not self.has_box(keeper, state) and not self.has_box(new_box_position, state) and not self.is_wall(new_box_position) and new_box_position not in self.__dead_squares and not self.freeze_deadlock(state, box, new_box_position)
    
    def new_box_position(self, box, keeper):
        return box + (box - keeper)

    def positions_around_tile(self, tile):
        return [tile - self.__width, tile + 1, tile + self.__width, tile - 1]    #cima,dir,baixo,esq

    def has_box(self, tile, state):
        return True if tile in state.boxes else False
    
    def is_wall(self, tile):
        return True if tile in self.__walls else False
    
    def __coordenate_to_num(self, coordenate):
        return coordenate[1] * self.__width + coordenate[0]
    
    def __map_positions(self):
        positions = self.mapa.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL])
        return [self.__coordenate_to_num(p) for p in positions]

    def get_valid_squares_and_costs(self):

        valid_squares = []
        costs = [-1] * self.measures
        dict = {}
        for g in self.__goals:
            starting_costs = costs[:]
            starting_costs[g] = 0
            visited, calculated_costs = (self.__pull_block(g, [g], starting_costs))
            valid_squares += visited
            dict[g] = calculated_costs

        valid_squares = list((valid_squares))
        # print("custos",dict)   #na posiçao x, index x ---> custo costs[x]
        
        return valid_squares, dict

    #--------Deadlocks---------#
    #----predetermined deadlocks
    def simple_deadlocks(self):
        return [square for square in self.__map_positions() if square not in self.__valid_squares]

    #auxiliary function for square_deadlock
    def __pull_block(self, pull_from, visited_squares, costs):

        x = pull_from
        #set keeper next to the box (try positions around the box) and try to pull the box
        if not self.is_wall(x+1) and not self.is_wall(x+2) and (x+1) not in visited_squares:
            visited_squares.append((x+1))
            costs[x+1] = costs[x] + 1
            visited_squares , costs = self.__pull_block((x+1), visited_squares, costs)
        
        if not self.is_wall(x-1) and not self.is_wall(x-2) and (x-1) not in visited_squares:
            visited_squares.append((x-1))
            costs[x-1] = costs[x] + 1
            visited_squares , costs = self.__pull_block((x-1), visited_squares, costs)

        if not self.is_wall(x + self.__width) and not self.is_wall(x + self.__width * 2) and (x + self.__width) not in visited_squares:
            visited_squares.append((x + self.__width))
            costs[x+self.width] = costs[x] + 1
            visited_squares , costs = self.__pull_block((x + self.__width), visited_squares, costs)
        
        if not self.is_wall(x - self.__width) and not self.is_wall(x - self.__width * 2) and (x - self.__width) not in visited_squares:
            visited_squares.append((x - self.__width))
            costs[x-self.width] = costs[x] + 1
            visited_squares , costs= self.__pull_block((x - self.__width), visited_squares, costs)

        return visited_squares, costs

    #----Run time deadlocks
    #detect immoveable boxes
    #if a box gets frozen without being on a goal there is no solution
    def freeze_deadlock(self, state, box, new_box_position):
        newBoxState = state.boxes[:]
        newBoxState.remove(box)
        newBoxState.append(new_box_position)

        #print("old", box)
        #print("new", new_box_position)
        potential_immoveable = newBoxState
        limit = len(potential_immoveable)
        #print("potential_immoveable",potential_immoveable)
        
        #print("----newState---")
        froze = False
        while potential_immoveable != [] and froze == False:

            box = potential_immoveable.pop(0)
            reinsert = False
            lBoxes = []
            lWalls = []
        
            for pos in self.positions_around_tile(box):
                if pos in self.walls:
                    lWalls += [pos]
                if pos in newBoxState and pos in potential_immoveable:
                    lBoxes += [pos]

            # print("Box: ",box)            
            # if lBoxes != []:
            #     print("-------")
            #     print("lWalls",lWalls)
            #     print("lBoxes",lBoxes)

            #this condition insures that box is moveable
            if lBoxes == [] or (len(lBoxes) == 1 and len(lWalls) == 0) or box in self.goals:
                continue

            #verify if adjacent box/wall are in the same line/colun 
            #if not (box is potencially immoveable), we need to check immobility of adjacent box 
            while reinsert != True and lBoxes != []:
                adj = lBoxes.pop(0) 
                #print("here")
                wall_idx = 0
                while reinsert != True and wall_idx < len(lWalls): 
                    wall = lWalls[wall_idx]
                    #print("wall box", adj)
                    if (adj // self.width) != (wall // self.width) and (adj % self.width) != (wall % self.width):
                        #print("reinsert in walls")
                        reinsert = True
                    else:
                        #print("not reinserting in walls")
                        wall_idx += 1
                
                b_idx = 0
                while reinsert != True and b_idx < len(lBoxes):
                    b = lBoxes[b_idx]
                    if (adj // self.width) != (b // self.width) and (adj % self.width) != (b % self.width):
                        reinsert = True
                        #print("reinsert in boxes")
                    else:
                        #print("not reinserting in boxes")
                        b_idx += 1

            if reinsert:
                #print("reinsert")
                potential_immoveable.append(box)
                limit -= 1
                if limit == 0:
                    froze = True
            else:
                limit = len(potential_immoveable)

        return froze

    def is_tunnel(self, box):

        #vertical
        if self.is_wall(box - 1) and self.is_wall(box + 1):
            return -1

        #horizontal
        if self.is_wall(box - self.__width) and self.is_wall(box + self.__width):
            return 1
        
        return 0

    def get_tunnels(self):

        tunnels = []
        visited_squares = []

        for square in self.__valid_squares_for_tunnels:
            if square not in visited_squares:
                tunnel =  self.tunnel(square)
                if len(tunnel) > 1:
                    tunnels.append(tunnel)
                    visited_squares.extend(tunnel)

        return tunnels
            
    def tunnel(self, square):
        tunnel = []
        is_tunnel = self.is_tunnel(square)
        
        offset = 1
        if is_tunnel == -1:
            offset = self.__width

        if is_tunnel != 0:
            tunnel += [square]
            tunnel.extend(self.find_tunnel_exit(square, offset, -1))
            tunnel.extend(self.find_tunnel_exit(square, offset, 1))

        return tunnel

    #direction = posição a seguir - atual
    def directed_tunnel(self, tunnel, direction):
        tunnel_copy = tunnel[:]
        
        if direction < 0:
            tunnel_copy.reverse()

        return tunnel_copy

    def find_tunnel_exit(self, square, offset, direction_modifier):
        tunnel = []
        entrance = square
        if (square + direction_modifier * offset) in self.__valid_squares_for_tunnels:
            entrance = square + direction_modifier * offset
            while self.is_tunnel(entrance) != 0 and entrance not in tunnel:
                tunnel += [entrance]
                if (entrance + direction_modifier * offset) in self.__valid_squares_for_tunnels:
                    entrance += direction_modifier * offset
        return tunnel