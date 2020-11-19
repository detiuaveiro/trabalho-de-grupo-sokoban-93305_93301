import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
from srAgente import *
from tree_search import *

def get_keys(steps, width):
    if len(steps) <= 1:
        return []
    
    step = steps[1] - steps[0]

    # print(step)
    if step == 1:
        key = 'd'
    elif step == width:
        key = 's'
    elif step == -1:
        key = 'a'
    elif step == -width:
        key = 'w'
    else:
        key = ""
    return [key] + get_keys(steps[1:],width)

async def solver(puzzle, solution):
    while True:
        game_properties = await puzzle.get()
        mapa = Map(game_properties["map"])
        print(mapa)

        game = Logic(mapa)
        agent = Agent(game)
        initial_state = State(game.keeper(), game.list_boxes())
        p = SearchProblem(agent, initial_state, game.list_goal())
        t = SearchTree(p,'breadth')
        while t.solution == None:
            await t.search()
        
        res = t.get_path(t.solution)
        
        keys = get_keys(res, game.width)

        await solution.put(keys)

async def agent_loop(puzzle, solution, server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "map" in update:
                    # we got a new level
                    game_properties = update
                    keys = ""
                    await puzzle.put(game_properties)

                if not solution.empty():
                    keys = await solution.get()

                key = ""
                if len(keys):  # we got a solution!
                    key = keys[0]
                    keys = keys[1:]

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())

puzzle = asyncio.Queue(loop=loop)
solution = asyncio.Queue(loop=loop)

net_task = loop.create_task(agent_loop(puzzle, solution, f"{SERVER}:{PORT}", NAME))
solver_task = loop.create_task(solver(puzzle, solution))

loop.run_until_complete(asyncio.gather(net_task, solver_task))
loop.close()