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

async def solver(puzzle, solution, steps):
    while True:
        game_properties = await puzzle.get()
        map = Map(game_properties["map"])
        game = Logic(map)
        agent = Agent(game)
        initial_state = State(game.keeper,game.keeper, game.boxes)
        p = SearchProblem(agent, initial_state, game.goals)
        t = SearchTree(p,'a*')
        while t.solution == None:
            res = await t.search(steps)
        res = t.get_path(t.solution)
        # print("resultado", res)
        keys = get_keys(res, game.width)
        await solution.put(keys)

async def agent_loop(puzzle, solution, steps, server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": "SrAgente"}))

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
                
                step = 0
                if 'step' in update:
                    #print(update["step"])
                    step = update["step"]
                    await steps.put(update["step"])

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
steps = asyncio.Queue(loop=loop)

net_task = loop.create_task(agent_loop(puzzle, solution, steps, f"{SERVER}:{PORT}", NAME))
solver_task = loop.create_task(solver(puzzle, solution, steps))

loop.run_until_complete(asyncio.gather(net_task, solver_task))
loop.close()
