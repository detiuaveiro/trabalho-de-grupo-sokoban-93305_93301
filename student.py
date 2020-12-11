import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
from srAgente import *
from tree_search import *

class SobokanSolver:

    def __init__(self, SERVER, PORT, NAME):
        self.SERVER = SERVER
        self.PORT = PORT
        self.NAME = NAME
        self.loop = asyncio.get_event_loop()
        self.puzzle = asyncio.Queue(loop=self.loop)
        self.solution = asyncio.Queue(loop=self.loop)
        self.steps = asyncio.Queue(loop=self.loop)

    def get_keys(self,steps, width):
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
        return [key] + self.get_keys(steps[1:],width)

    async def solver(self):
        while True:
            game_properties = await self.puzzle.get()
            map = Map(game_properties["map"])
            game = Logic(map)
            agent = Agent(game)
            initial_state = State(game.keeper,game.keeper, game.boxes)
            p = SearchProblem(agent, initial_state, game.goals)
            t = SearchTree(p, A_STAR_STRATEGY)
            while t.solution == None:
                res = await t.search(self.steps)
            res = t.get_path(t.solution)
            keys = self.get_keys(res, game.width)
            await self.solution.put(keys)

    async def agent_loop(self, server_address="localhost:8000", agent_name="student"):
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
                        del self.steps
                        self.steps = asyncio.Queue()
                        await self.puzzle.put(game_properties)
                    
                    if 'step' in update:
                        await self.steps.put(update["step"])

                    if not self.solution.empty():
                        keys = await self.solution.get()

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
    def start(self):
        net_task = self.loop.create_task(self.agent_loop( f"{self.SERVER}:{self.PORT}", self.NAME))
        solver_task = self.loop.create_task(self.solver())

        self.loop.run_until_complete(asyncio.gather(net_task, solver_task))
        self.loop.close()

solver = SobokanSolver(os.environ.get("SERVER", "localhost"), os.environ.get("PORT", "8000"), os.environ.get("NAME", getpass.getuser()))
solver.start()
