import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
from consts import Tiles
from srAgente import *
from tree_search import *
import time
# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)

def get_keys(steps):
    if len(steps) <= 1:
        return []
    
    step = (steps[1][0] - steps[0][0], steps[1][1] - steps[0][1])
    
    print(step)
    if step == (1,0):
        key = 'd'
    elif step == (0,1):
        key = 's'
    elif step == (-1,0):
        key = 'a'
    else:
        key = 'w'
    return [key] + get_keys(steps[1:])

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        print(msg)

        # You can create your own map representation or use the game representation:
        mapa = Map(game_properties["map"])
        print(mapa)

        print('1++++++++++++++++++++++++++++++++++++++')
        #print(mapa._map)
        for x in mapa._map:
            print(x)
        print('1++++++++++++++++++++++++++++++++++++++')
        walls = []
        for lin in range(len(mapa._map)):
            for col in range(len(mapa._map[lin])):
                if mapa._map[lin][col] == Tiles.WALL:
                    walls.append([col,lin])
        print(walls)
        print('2++++++++++++++++++++++++++++++++++++++')

        # coordenadas = Agent(mapa.filter_tiles([Tiles.FLOOR, Tiles.GOAL, Tiles.MAN, Tiles.MAN_ON_GOAL, Tiles.BOX, Tiles.BOX_ON_GOAL]))
        
        # p = SearchProblem(coordenadas, mapa.keeper, (4,0))
        # t = SearchTree(p,'breadth')

        # print(t.search())
        # mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])
        game = Logic(mapa)
        agent = Agent(game)
        initial = {"keeper": mapa.keeper, "boxes": mapa.boxes}
        p = SearchProblem(agent, initial, mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL]))
        t = SearchTree(p,'breadth')

        print("Resultado:")
        print(t.search())
        res = t.get_path(t.solution)
        keys = get_keys(res)
        print(keys)

        # Next 3 lines are not needed for AI agent
        SCREEN = pygame.display.set_mode((299, 123))
        SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        SCREEN.blit(SPRITES, (0, 0))
        
        count2 = 0

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server

                for key in keys:
                    print(key)
                    time.sleep(0.1)
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": key})
                    )  # send key command to server - you must implement this send in the AI agent

                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            # Next line is not needed for AI agent
            pygame.display.flip()

            


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
