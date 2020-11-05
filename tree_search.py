from abc import ABC, abstractmethod

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
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial      # dicionario keeper_position e #caixas
        # self.initial_boxes = boxes  
        self.goal = goal            #diamonds position
    def goal_test(self, state):     #state -- posiçao das caixas
        return self.domain.satisfies(state,self.goal)

class SearchNode:

###########################################################################

    # depth_count = 0

###########################################################################


    def __init__(self, state, parent, depth): 
        # self.state_keeper = state_keeper
        # self.state_boxes = state_boxes
        self.state = state
        self.parent = parent
        self.depth = depth
        # if SearchNode.depth_count < depth:
        #     SearchNode.depth_count = depth
        #     print("Omg we're going deeper!!!!: ", SearchNode.depth_count)
        # self.cost = cost

    def in_parent(self, state):
        self.state['boxes'].sort()
        state['boxes'].sort()
        if self.state['keeper'] == state['keeper'] and self.state['boxes'] == state['boxes']:
            return True
        
        if self.parent is None:
            return False

        return self.parent.in_parent(state)


###########################################################################

    # def state_keeper_to_array(self, current_keeper):
    #     if current_keeper is None:
    #         return []

    #     array = self.state_keeper_to_array(current_keeper.parent)
    #     array.append(current_keeper.state_keeper)

    #     return array

    # def is_debug_test(self):                                                                                                                                                                     ##
    #     success_array = [(2,3),(2, 4), (1, 4), (1, 3), (2, 3), (3, 3), (4, 3), (4, 4), (3, 4), (3, 3), (2, 3), (1, 3), (1, 4), (1, 5), (2, 5), (2, 4), (1, 4), (1, 3), (2, 3), (2, 2), (2, 1), (1, 1), (1, 2), (2, 2), (2, 3), (2, 4), (3, 4), (4, 4), (4, 3), (3, 3), (3, 4), (2, 4), (2, 3), (2, 2), (2, 1)]
    #     state_keeper_array = self.state_keeper_to_array(self)

    #     count = 0
    #     for i in state_keeper_array:
    #         if i == success_array[count]:
    #             count+=1
    #         else:
    #             return False
    #     print("State Keeper Array: ", state_keeper_array)
    #     return True

###########################################################################

    def __str__(self):
        # return f"no(State Keeper: {self.state_keeper}, State Boxes: {self.state_boxes}, Depth: {self.depth}, Parent: {self.parent})"
        return f"no(State Keeper: {self.state['keeper']}, Depth: {self.depth}, Parent: {self.parent})"
        #return f"no(Depth: {self.depth})"
        #return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self, problem, strategy='breadth'): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.terminals = 1
        self.non_terminals = 0

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state['keeper']]
        path = self.get_path(node.parent)
        path += [node.state['keeper']]
        return(path)
    
    @property
    def length(self):
        return self.solution.depth

    @property
    def avg_ramification(self):
        return (self.terminals + self.non_terminals - 1) / self.non_terminals

    # @property
    # def cost(self):
    #     return self.solution.cost

    # procurar a solucao
    def search(self, limit=None):
        array = [(2,3),(2, 4), (1, 4), (1, 3), (2, 3), (3, 3), (4, 3), (4, 4), (3, 4), (3, 3), (2, 3), (1, 3), (1, 4), (1, 5), (2, 5), (2, 4), (1, 4), (1, 3), (2, 3), (2, 2), (2, 1), (1, 1), (1, 2), (2, 2), (2, 3), (2, 4), (3, 4), (4, 4), (4, 3), (3, 3), (3, 4), (2, 4), (2, 3), (2, 2), (2, 1)]
        current_depth = 0
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.non_terminals += 1
            if self.problem.goal_test(node.state['boxes']):
                self.solution = node
                self.terminals = len(self.open_nodes)
                return self.get_path(node)
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state, a)
                # newstate_keeper = newstate[0]
                # newstate_boxes = newstate[1]
                newnode = SearchNode(newstate, node, node.depth + 1)
                
                # if newnode.is_debug_test():
                #     print("Newnode",newnode)

                if not node.in_parent(newnode.state) and (limit is None or newnode.depth <= limit):
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