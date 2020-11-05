import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
from consts import Tiles
from student import *
from tree_search import *

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)


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

                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                # if count2 > 33 :
                #     pygame.quit()
                #     print("adeus")
                # else:
                #     if count2 == 0:   
                #         key = "s"
                #     if count2 == 1:
                #         key = "a"
                #     if count2 == 2:
                #         key = "w"
                #     if count2 == 3:
                #         key = "d"
                #     if count2 == 4:
                #         key = "d"
                #     if count2 == 5:
                #         key = "d"
                #     if count2 == 6:
                #         key = "s"
                #     if count2 == 7:
                #         key = "a"
                #     if count2 == 8:
                #         key = "w"
                #     if count2 == 9:
                #         key = "a"
                #     if count2 == 10:
                #         key = "a"
                #     if count2 == 11:
                #         key = "s"
                #     if count2 == 12:
                #         key = "s"
                #     if count2 == 13:
                #         key = "d"
                #     if count2 == 14:
                #         key = "w"
                #     if count2 == 15:
                #         key = "a"
                #     if count2 == 16:
                #         key = "w"
                #     if count2 == 17:
                #         key = "d"
                #     if count2 == 18:
                #         key = "w"
                #     if count2 == 19:
                #         key = "w"
                #     if count2 == 20:
                #         key = "a"
                #     if count2 == 21:
                #         key = "s"
                #     if count2 == 22:
                #         key = "d"
                #     if count2 == 23:
                #         key = "s"
                #     if count2 == 24:
                #         key = "s"
                #     if count2 == 25:
                #         key = "d"
                #     if count2 == 26:
                #         key = "d"
                #     if count2 == 27:
                #         key = "w"
                #     if count2 == 28:
                #         key = "a"
                #     if count2 == 29:
                #         key = "s"
                #     if count2 == 30:
                #         key = "a"
                #     if count2 == 31:
                #         key = "w"
                #     if count2 == 32:
                #         key = "w"
                #     if count2 == 33:
                #         key = "w"
                    
                #     count2 += 1


                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            key = "w"
                        elif event.key == pygame.K_LEFT:
                            key = "a"
                        elif event.key == pygame.K_DOWN:
                            key = "s"
                        elif event.key == pygame.K_RIGHT:
                            key = "d"

                        elif event.key == pygame.K_d:
                            import pprint

                            pprint.pprint(state)
                            print(Map(f"levels/{state['level']}.xsb"))
                        await websocket.send(
                            json.dumps({"cmd": "key", "key": key})
                        )  # send key command to server - you must implement this send in the AI agent
                        break
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
