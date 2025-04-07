from typing import Callable, Awaitable, Any
import lib.tama.engines.engine1 as engine1
import lib.tama.engines.engine2 as engine2
import lib.tama.engines.engine3 as engine3
import multiprocessing
import asyncio
from lib.tama.iterative_descent import iterative_descent


class Player:
    def __init__(self, side: int):
        self.side = side  # 1 for white, -1 for black, 0 for spectator


class HumanPlayer(Player):
    def __init__(self, side: int, sid: str):
        super().__init__(side)
        self.sid = sid


class ComputerPlayer(Player):
    def __init__(self, side: int, think_time: int, engine: int):
        super().__init__(side)
        self.think_time = think_time
        self.engine = engine
        self._task_queue = multiprocessing.Queue()
        self._result_queue = multiprocessing.Queue()
        self._worker = multiprocessing.Process(
            target=self._worker_loop,
            args=(self._task_queue, self._result_queue),
            daemon=True
        )
        self._worker.start()

    async def get_best_move(self, field, callback: Callable[[Any], Awaitable]):
        """Send task to worker and await result."""
        self._task_queue.put((field, self.side, self.think_time, self.engine))
        return await self._poll_result(callback)

    @staticmethod
    def _worker_loop(task_queue, result_queue):
        """Run indefinitely, processing tasks as they come."""

        def callback(val):
            result_queue.put(('callback', val))

        while True:
            field, side, think_time, engine = task_queue.get()
            result = 1
            if engine == 1:
                result = iterative_descent(engine1.evaluate_node_at_depth, field, side, think_time, callback)
            elif engine == 2:
                result = iterative_descent(engine2.evaluate_node_at_depth, field, side, think_time, callback)
            elif engine == 3:
                result = iterative_descent(engine3.evaluate_node_at_depth, field, side, think_time, callback)
            result_queue.put(('result', result))

    async def _poll_result(self, callback: Callable[[Any], Awaitable]):
        """Check for results without blocking the event loop."""
        while True:
            if not self._result_queue.empty():
                kind, val = self._result_queue.get()
                if kind == 'callback':
                    await callback(val)
                elif kind == 'result':
                    return val

            await asyncio.sleep(0.05)  # Prevent busy-waiting

    def shutdown(self):
        if self._worker.is_alive():
            self._worker.terminate()

    def __del__(self):
        print('shutdown worker')
        self.shutdown()
