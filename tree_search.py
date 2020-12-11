from abc import ABC, abstractmethod
from state import *
import asyncio
from transposition_table import *
from queue import PriorityQueue

A_STAR_STRATEGY = True
GREEDY_STRATEGY = False

class SearchDomain(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def actions(self, state):
        pass

    @abstractmethod
    def result(self, state, action):
        pass

    @abstractmethod
    def cost(self, state, action):
        pass

    @abstractmethod
    def heuristic(self, state, goal):
        pass

    @abstractmethod
    def satisfies(self, state, goal):
        pass

class SearchProblem:
    def __init__(self, domain, initial_state, goal):
        self.domain = domain
        self.initial_state = initial_state
        self.goal = goal                   
        self.goal.sort()
    
    def goal_test(self, state):
        return self.domain.satisfies(state.boxes, self.goal)

class SearchNode:

    def __init__(self, state, path, parent, depth, cost, heuristic, reacheable_positions): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.path = path
        self.reacheable_positions = reacheable_positions
        self.priority = heuristic + cost

    def __str__(self):
        return f"no(State Keeper: {self.state_keeper}, State Boxes: {self.state_boxes}, Depth: {self.depth}, Parent: {self.parent})"
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __repr__(self):
        return str(self)

class SearchNodeGreedy(SearchNode):

        def __init__(self, state, path, parent, depth, cost, heuristic, reacheable_positions): 
            super().__init__(state, path, parent, depth, cost, heuristic, reacheable_positions)
            self.priority = heuristic

class SearchTree:

    def __init__(self, problem, strategy=A_STAR_STRATEGY): 
        self.strategy = strategy
        self.problem = problem
        root = SearchNode(problem.initial_state, None, None, 0, 0, self.problem.domain.heuristic(problem.initial_state.boxes, problem.goal),  self.problem.domain.logic.reacheable_positions(problem.initial_state.keeper, problem.initial_state.boxes))
        self.transposition_table = TranspositionTable(problem.domain.logic.area)
        self.open_nodes = PriorityQueue()
        self.open_nodes.put( root )
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

    async def search(self, steps):
        step = 0
        while not self.open_nodes.empty():
            if (not steps.empty()):
                step = await steps.get()
            
            await asyncio.sleep(0)
            
            node = self.open_nodes.get()
            
            if self.problem.goal_test(node.state):
                self.solution = node
                return self.get_path(node)
            
            lnewnodes = []
            if(self.strategy != GREEDY_STRATEGY and step >=1500):
                self.strategy = GREEDY_STRATEGY
                nQueue = PriorityQueue()
                while not self.open_nodes.empty():
                    await asyncio.sleep(0)
                    node = self.open_nodes.get()
                    nQueue.put(SearchNodeGreedy(node.state, node.path, node.parent, node.depth, node.cost, node.heuristic, node.reacheable_positions))

                self.open_nodes = nQueue
                
            for a in self.problem.domain.actions(node.state, node.reacheable_positions):
                newstate, reacheable_positions = self.problem.domain.result(node.state, a)
                if(self.strategy == GREEDY_STRATEGY):
                    newnode = SearchNodeGreedy(newstate, a[1], node, node.depth + 1, node.cost + self.problem.domain.cost(node.state,a), self.problem.domain.heuristic(newstate.boxes, self.problem.goal), reacheable_positions)
                else:
                    newnode = SearchNode(newstate, a[1], node, node.depth + 1, node.cost + self.problem.domain.cost(node.state,a), self.problem.domain.heuristic(newstate.boxes, self.problem.goal), reacheable_positions)
                if not self.transposition_table.in_table(newnode.state):
                    self.transposition_table.put(newnode.state)
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)

        return self.get_path(node)
        
    def add_to_open(self,lnewnodes):            
        for node in lnewnodes:
            self.open_nodes.put(node)
