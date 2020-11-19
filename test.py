from mapa import Map
from consts import Tiles
from srAgente import *
from tree_search import *


def test():
    mapa = Map("levels/2.xsb")
    game = Logic(mapa)
    agent = Agent(game)
    initial = State(game.keeper(), game.list_boxes())
    p = SearchProblem(agent, initial, game.list_goal())

    print(list(enumerate(agent.searchReachable(p.initial_state))))

    print(agent.actions(p.initial_state))
test()