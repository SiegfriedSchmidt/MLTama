import numpy as np
from numba import njit


@njit()
def field_to_fen_numba(field: np.ndarray, side: int):
    fen = ''
    for row in range(field.shape[0] - 1, -1, -1):
        empty = 0
        for col in range(field.shape[1]):
            if field[row, col] == 0:
                empty += 1
                continue

            if empty:
                fen += str(empty)
                empty = 0

            piece = int(field[row, col])
            if piece == 1:
                fen += 'w'
            elif piece == 2:
                fen += 'W'
            elif piece == -1:
                fen += 'b'
            elif piece == -2:
                fen += 'B'

        if empty:
            fen += str(empty)

        fen += '/'

    return f"{fen} {'w' if side == 1 else 'b'}"
