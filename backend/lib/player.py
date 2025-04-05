from lib.tama.engines.engine1 import evaluate_node_at_depth
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
    def __init__(self, side: int, depth: int):
        super().__init__(side)
        self.depth = depth
        self._task_queue = multiprocessing.Queue()
        self._result_queue = multiprocessing.Queue()
        self._worker = multiprocessing.Process(
            target=self._worker_loop,
            args=(self._task_queue, self._result_queue),
            daemon=True
        )
        self._worker.start()

    async def get_best_move(self, field):
        """Send task to worker and await result."""
        self._task_queue.put((field, self.side, self.depth))
        return await self._poll_result()

    @staticmethod
    def _worker_loop(task_queue, result_queue):
        """Run indefinitely, processing tasks as they come."""
        while True:
            field, side, depth = task_queue.get()
            result = iterative_descent(evaluate_node_at_depth, field, side, depth)
            result_queue.put(result)

    async def _poll_result(self):
        """Check for results without blocking the event loop."""
        while True:
            if not self._result_queue.empty():
                return self._result_queue.get()
            await asyncio.sleep(0.2)  # Prevent busy-waiting

    def shutdown(self):
        if self._worker.is_alive():
            self._worker.terminate()
