from mapa import Map
from consts import Tiles
from tree_search import *
import time

class Logic:

    def __init__(self, map):
        self.__map = map
        self.__width = max([len(line) for line in map._map])
        self.__height = len(map._map)
        self.__area = self.__width * self.__height
        self.__keeper = self.__coordenate_to_num(map.keeper)
        self.__walls = [self.__coordenate_to_num(w) for w in map.filter_tiles([Tiles.WALL])]
        self.__boxes = [self.__coordenate_to_num(b) for b in map.boxes]
        self.__goals = [self.__coordenate_to_num(g) for g in map.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])]
        self.__valid_tiles, self.__costs = self.__get_valid_tiles_and_costs()
        self.__dead_tiles = self.__simple_deadlocks()
        # self.__valid_tiles_for_tunnels = [tile for tile in self.__valid_tiles if tile not in self.__goals]
        # self.__valid_tiles_for_tunnels.sort()
        # self.__tunnels = self.__get_tunnels()

    @property
    def map(self):
        """Current map."""
        return self.__map
    
    @property
    def width(self):
        """Width of the current map."""
        return self.__width

    @property
    def height(self):
        """Height of the current map."""
        return self.__height

    @property
    def area(self):
        """Area of the current map."""
        return self.__area

    @property
    def keeper(self):
        """Keeper position."""
        return self.__keeper

    @property
    def walls(self):
        """List of the positions of walls."""
        return self.__walls

    @property
    def boxes(self):
        """List of the positions of boxes."""
        return self.__boxes

    @property
    def goals(self):
        """List of the positions of goals."""
        return self.__goals

    @property
    def tunnels(self):
        """List of the positions of tunnels."""
        return self.__tunnels

    @property
    def costs(self):
        """Dictionary with the costs of each position to the each goal."""
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
        return not self.has_box(new_box_position, state) and not self.is_wall(new_box_position) and new_box_position not in self.__dead_tiles and not self.__freeze_deadlock(state, box, new_box_position)
    
    def new_box_position(self, box, tile):
        """Position of box after beeing pushed from tile."""
        return box + (box - tile)

    def positions_around_tile(self, tile):
        """List of positions around tile."""
        return [tile - self.__width, tile + 1, tile + self.__width, tile - 1]

    def has_box(self, tile, state):
        """Check if tile has box."""
        return True if tile in state.boxes else False
    
    def is_wall(self, tile):
        """Chech if tile is wall."""
        return True if tile in self.__walls else False
    
    def directed_tunnel(self, tunnel, direction):
        """Return the tunnel ordered based on the direction.

        Preconditions:

        tunnel should be ordered, left to right or top to bottom.

        direction given by the diference between next position and current position.
        """
        tunnel_copy = tunnel[:]
        
        if direction < 0:
            tunnel_copy.reverse()

        return tunnel_copy

    def __coordenate_to_num(self, coordenate):
        """Turn a coordenate to a number."""
        return coordenate[1] * self.__width + coordenate[0]
    
    def __map_positions(self):
        """List of all map positions without walls."""
        positions = self.__map.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL])
        return [self.__coordenate_to_num(p) for p in positions]

    def __get_valid_tiles_and_costs(self):
        """ Returns a tuple.

        tuple[0] - valid tiles for boxes.

        tuple[1] - is a dictionary where the keys are the goals and the values are arrays with the costs.

        example: for goal x if box in y --> cost = tuple[x][y]
        """

        valid_tiles = []
        costs = [-1] * self.__area
        dict = {}
        for g in self.__goals:
            starting_costs = costs[:]
            starting_costs[g] = 0
            visited, calculated_costs = (self.__pull_block(g, [g], starting_costs))
            valid_tiles += visited
            dict[g] = calculated_costs

        valid_tiles = list(set(valid_tiles))
        
        return valid_tiles, dict

    def __simple_deadlocks(self):
        """Return tiles that are not valid."""
        return [tile for tile in self.__map_positions() if tile not in self.__valid_tiles]

    #auxiliary function for tile_deadlock
    def __pull_block(self, pull_from, visited_tiles, costs):

        x = pull_from
        #set keeper next to the box (try positions around the box) and try to pull the box
        if not self.is_wall(x+1) and not self.is_wall(x+2) and (x+1) not in visited_tiles:
            visited_tiles.append((x+1))
            costs[x+1] = costs[x] + 1
            visited_tiles , costs = self.__pull_block((x+1), visited_tiles, costs)
        
        if not self.is_wall(x-1) and not self.is_wall(x-2) and (x-1) not in visited_tiles:
            visited_tiles.append((x-1))
            costs[x-1] = costs[x] + 1
            visited_tiles , costs = self.__pull_block((x-1), visited_tiles, costs)

        if not self.is_wall(x + self.__width) and not self.is_wall(x + self.__width * 2) and (x + self.__width) not in visited_tiles:
            visited_tiles.append((x + self.__width))
            costs[x+self.__width] = costs[x] + 1
            visited_tiles , costs = self.__pull_block((x + self.__width), visited_tiles, costs)
        
        if not self.is_wall(x - self.__width) and not self.is_wall(x - self.__width * 2) and (x - self.__width) not in visited_tiles:
            visited_tiles.append((x - self.__width))
            costs[x-self.__width] = costs[x] + 1
            visited_tiles , costs = self.__pull_block((x - self.__width), visited_tiles, costs)

        return visited_tiles, costs

    #----Run time deadlocks----
    #detect immoveable boxes
    #if a box gets frozen without being on a goal there is no solution
    def __freeze_deadlock(self, state, box, new_box_position):
        newBoxState = state.boxes[:]
        newBoxState.remove(box)
        newBoxState.append(new_box_position)
        
        #print("----newState---")
        #print("old", box)
        #print("new", new_box_position)
        potential_immoveable = newBoxState
        limit = len(potential_immoveable)
        
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
                    if (adj // self.__width) != (wall // self.__width) and (adj % self.__width) != (wall % self.__width):
                        #print("reinsert in walls")
                        reinsert = True
                    else:
                        #print("not reinserting in walls")
                        wall_idx += 1
                
                b_idx = 0
                while reinsert != True and b_idx < len(lBoxes):
                    b = lBoxes[b_idx]
                    if (adj // self.__width) != (b // self.__width) and (adj % self.__width) != (b % self.__width):
                        reinsert = True
                        #print("reinsert in boxes")
                    else:
                        #print("not reinserting in boxes")
                        b_idx += 1

            if reinsert:
                potential_immoveable.append(box)
                if limit == 0:
                    froze = True
                limit -= 1
            else:
                limit = len(potential_immoveable)

        return froze

    def __in_tunnel(self, box):
        """ Check if box is in a tunnel.

        Return values:

        0 - not in a tunnel.

        1 - horizontal tunnel.

        -1 - vertical tunnel.
        """

        if self.is_wall(box - 1) and self.is_wall(box + 1):
            return -1

        if self.is_wall(box - self.__width) and self.is_wall(box + self.__width):
            return 1
        
        return 0

    def __get_tunnels(self):
        """Return all existing tunnels.

        A tunnel must have length > 1.

        Returns [] if there's no tunnels.
        """

        tunnels = []
        visited_tiles = []

        #Check in valid_tiles_for_tunnels if there could be a tunnel
        for tile in self.__valid_tiles_for_tunnels:
            if tile not in visited_tiles:
                tunnel =  self.__tunnel(tile)
                if len(tunnel) > 1:
                    tunnels.append(tunnel)
                    visited_tiles.extend(tunnel)

        return tunnels
            
    def __tunnel(self, tile):
        """Return a tunnel if tile is part of it.
        
        Returns [] if there's no tunnel.
        """
        tunnel = []
        is_tunnel = self.__in_tunnel(tile)
        
        offset = 1
        if is_tunnel == -1:
            offset = self.__width

        #Check both sides
        if is_tunnel != 0:
            tunnel += [tile]
            tunnel.extend(self.__find_tunnel_exit(tile, offset, -1))
            tunnel.extend(self.__find_tunnel_exit(tile, offset, 1))

        return tunnel

    def __find_tunnel_exit(self, tile, tile_jump_modifier, direction_modifier):
        """Search for the end of a tunnel.
        
        Arguments:

        tile: start of the search.

        tile_jump_modifier: 1 for horizontal movement; map width for vertical movement.

        direction_modifier: direction to search. -1 for up or left; 1 for down or right.

        Returns [] if there's no tunnel.
        """
        tunnel = []
        entrance = tile

        #Check if next position is still in the tunnel
        if (tile + direction_modifier * tile_jump_modifier) in self.__valid_tiles_for_tunnels:
            entrance = tile + direction_modifier * tile_jump_modifier
            while self.__in_tunnel(entrance) != 0 and entrance not in tunnel:
                tunnel += [entrance]
                if (entrance + direction_modifier * tile_jump_modifier) in self.__valid_tiles_for_tunnels:
                    entrance += direction_modifier * tile_jump_modifier
        return tunnel
