from lib.tama.engine import find_best_moves
import multiprocessing
import asyncio


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
        self._queue = multiprocessing.Queue()
        self._process: multiprocessing.Process | None = None

    async def get_best_move(self, field):
        if self._process and self._process.is_alive():
            self._process.terminate()  # Kill previous if still running

        self._process = multiprocessing.Process(
            target=self._get_best_move_worker,
            args=(field, self.side, self.depth, self._queue),
            daemon=True
        )
        self._process.start()
        return await self._poll_queue_for_result()

    @staticmethod
    def _get_best_move_worker(field, side, depth, queue):
        best_idx, stats = find_best_moves(field, side, depth)
        queue.put((best_idx, stats))

    async def _poll_queue_for_result(self) -> str:
        """Check the queue periodically without blocking the event loop."""
        while True:
            if not self._queue.empty():
                return self._queue.get()  # Return the result
            await asyncio.sleep(0.2)  # Yield control to the event loop

    def shutdown(self):
        """Cleanup resources (call when exiting)."""
        if self._process:
            self._process.terminate()
