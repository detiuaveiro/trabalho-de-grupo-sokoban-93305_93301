import random
from state import *
from tree_search import *

list_pieces = ('keeper','boxes','empty')

class TranspositionTable:
    def __init__(self, measures):
        self.__zobrist_table = ZobristTable(measures)
        self.__table = {}

    def put(self,state):
        self.__table[HashableState(state, self.__zobrist_table)] = 1

    def in_table(self,state):
        return HashableState(state, self.__zobrist_table) in self.__table

class HashableState(State):
    def __init__(self, state, zobrist_table):
        super().__init__(state.keeper, state.boxes)
        self.zobrist_table = zobrist_table

    def __hash__(self):
        return self.zobrist_table.hash_zobrist(self)

class ZobristTable:
    def __init__(self, measures):
        #the table is a list that represents each position of the map
        #each position as random values for each piece 
        #zobrist_table = [{"keeper": rand_number, "boxes": rand_number, 'empty': rand_number}, {"keeper": rand_number , "boxes": rand_number}, ... ] 

        self.__table = []
        for p in range(measures):
            self.__table.append({})
            for piece in list_pieces:
                self.__table[p][piece] = self.random_number();        

        #print("TABLE: ", table)
    
    def hash_zobrist(self, state):
        xor = lambda x,y: x^y

        keeper = state.keeper
        boxes = state.boxes
        #print("keeper",keeper)
        #print("boxes",boxes)
        res = 0
        for p in self.__table:
            if p == keeper:
                #print("WE GOT THE KEEPER")
                next_operator = self.zobrist_table[p]['keeper']
                #print("HASH: ", next_operator)
            elif p in boxes:
                #print("WE GOT A BOX")
                next_operator = self.zobrist_table[p]['boxes']
                #print("HASH: ", next_operator)
            else:
                next_operator = 0#self.zobrist_table[y][x]['empty']
            res = xor(res,next_operator)

        return res

    @staticmethod
    def random_number():
        #generate random number with 32 bits
        return random.getrandbits(32)

