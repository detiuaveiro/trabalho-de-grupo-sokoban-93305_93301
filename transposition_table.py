import random
from state import *
from tree_search import *

list_pieces = ('keeper','box','empty')

class TranspositionTable:
    zobrist_table = None
    def __init__(self, area):
        TranspositionTable.zobrist_table = ZobristTable(area)
        self.__table = {}

    def put(self,state):        
        self.__table[HashableState(state)] = 1

    def in_table(self,state):
        return HashableState(state) in self.__table

class HashableState(State):
    def __init__(self, state):
        super().__init__(state.normalized_keeper, state.keeper, state.boxes)

    def __hash__(self):
        return TranspositionTable.zobrist_table.hash_zobrist(self)

class ZobristTable:
    def __init__(self, area):
        """The table is a list that represents each position of the map.

        Each position has random values for each piece.

        zobrist_table = [{"keeper": rand_number, "boxes": rand_number, 'empty': rand_number}, {"keeper": rand_number , "boxes": rand_number}, ... ]  
        """
        self.__table = []
        for p in range(area):
            self.__table.append({})
            for piece in list_pieces:
                self.__table[p][piece] = self.random_number();        
    
    def hash_zobrist(self, state):
        xor = lambda x,y: x^y

        keeper = state.normalized_keeper
        res = self.__table[keeper]['keeper']
        for boxp in state.boxes:
            res = xor(res,self.__table[boxp]['box'])

        return res

    @staticmethod
    def random_number():
        """Generate a random number with 32 bits. """
        return random.getrandbits(32)



