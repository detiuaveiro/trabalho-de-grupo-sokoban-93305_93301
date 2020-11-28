from abc import ABC, abstractmethod
from state import *
import asyncio
from transposition_table import *

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc

class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass

class SearchProblem:
    def __init__(self, domain, initial_state, goal):
        self.domain = domain
        self.initial_state = initial_state      # class state
        self.goal = goal                        #diamonds position
        self.goal.sort()
    
    def goal_test(self, state):
        return self.domain.satisfies(state.boxes, self.goal)

class SearchNode:

###########################################################################

    # depth_count = 0

###########################################################################


    def __init__(self, state, path, parent, depth, cost, heuristic): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.path = path

        # if SearchNode.depth_count < depth:
        #     SearchNode.depth_count = depth
        #     print("Omg we're going deeper!!!!: ", SearchNode.depth_count)

    def in_parent(self, state):
        
        if self.state.keeper == state.keeper and self.state.boxes == state.boxes:
            return True
        
        if self.parent is None:
            return False

        return self.parent.in_parent(state)

    def __str__(self):
        # return f"no(State Keeper: {self.state_keeper}, State Boxes: {self.state_boxes}, Depth: {self.depth}, Parent: {self.parent})"
        return f"no(State Keeper: {self.state.keeper}, Depth: {self.depth}, Parent: {self.parent}, Path: {self.path})"
        #return f"no(Depth: {self.depth})"
        #return "no(" + str(self.state) + "," + str(self.parent) + ")"

    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:
    # construtor
    def __init__(self, problem, strategy='breadth'): 
        self.problem = problem
        root = SearchNode(problem.initial_state, None, None, 0, 0, self.problem.domain.heuristic(problem.initial_state.boxes, problem.goal))
        self.transposition_table = TranspositionTable(problem.domain.logic.measures)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
    
    def get_path(self,node):
        if node.parent == None:
            return [node.state.keeper]
        path = self.get_path(node.parent)
        path.extend(node.path)
        return path

    @property
    def length(self):
        return self.solution.depth

    # @property
    # def cost(self):
    #     return self.solution.cost

    # procurar a solucao
    async def search(self, limit=None):
        while self.open_nodes != []:
            await asyncio.sleep(0)  #  remover pra usar threads
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.solution = node
                return self.get_path(node)
            lnewnodes = []
            # print("Estamos na profundidade", node.depth)
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state, a)
                newnode = SearchNode(newstate, a[1], node, node.depth + 1, node.cost + self.problem.domain.cost(node.state,a), self.problem.domain.heuristic(newstate.boxes, self.problem.goal))
                if not self.transposition_table.in_table(newnode.state):
                    self.transposition_table.put(newnode.state)
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda n: n.cost)
        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda n: n.cost + n.heuristic)