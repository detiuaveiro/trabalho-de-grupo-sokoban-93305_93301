from mapa import Map
from consts import Tiles
from srAgente import *
from tree_search import *


def test():
    mapa = Map("levels/2.xsb")
    game = Logic(mapa)
    agent = Agent(game)
    initial = {"keeper": mapa.keeper, "boxes": mapa.boxes}
    p = SearchProblem(agent, initial, mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL]))

test()