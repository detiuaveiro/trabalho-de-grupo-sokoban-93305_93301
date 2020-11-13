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
import threading
import queue

my_queue = queue.Queue()

def try_get_result_from_queue():
    try:
        # print("Queue size: ", my_queue.qsize())
        result = my_queue.get(False)
        # print("Obtained from queue: ", result)
        return result
    except queue.Empty:
        return None

def get_keys(steps, witdh):
    if len(steps) <= 1:
        return []
    
    step = steps[1] - steps[0]
    
    # print(step)
    if step == 1:
        key = 'd'
    elif step == witdh:
        key = 's'
    elif step == -1:
        key = 'a'
    else:
        key = 'w'
    return [key] + get_keys(steps[1:],witdh)

def result(mapa):
    game = Logic(mapa)
    agent = Agent(game)
    initial_state = State(game.keeper(), game.list_boxes())
    # initial = {"keeper": mapa.keeper, "boxes": mapa.boxes}
    p = SearchProblem(agent, initial_state, game.list_goal())
    t = SearchTree(p,'breadth')
    t.search()          
    res = t.get_path(t.solution)
    
    keys = get_keys(res, game.width)
    # print("keys: ", keys)
    for key in keys:
        my_queue.put(key)

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                # print("sincronizado")
                if "map" in update:
                    # we got a new level
                    game_properties = update
                    mapa = Map(update["map"])
                    print("new level")
                    state = None
                    threading.Thread(target=result, args=(mapa,)).start()
                    # res = await result(mapa)
                    # print(res)
                else:
                    # we got a current map state update
                    state = update
                    # print("consumir")

                res = None
                if not my_queue.empty():
                    res = try_get_result_from_queue() # my_queue.get(False) 

                if res != None and res != []:
                    # print(res[0])
                    # time.sleep(0.1)
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": res[0]})
                    )  # send key command to server - you must implement this send in the AI agent
                    # print("aqui")
                else:
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": ""})
                    )
                    # print("enviou nada")

                # if state != None:
                #     print(state)

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
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))