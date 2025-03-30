import numpy as np

char_to_piece = {'w': 1, 'W': 2, 'b': -1, 'B': -2}
piece_to_char = {v: k for k, v in char_to_piece.items()}
side_to_fen = ['', 'w', 'b']  # 1 - white, -1 - black


def fen_to_side(fen: str) -> int:
    return 1 if fen.split()[1] == 'w' else -1


def fen_to_field(fen: str):
    field = np.zeros((8, 8), dtype=np.int8)
    row, col = 7, 0
    for char in fen.split()[0]:
        if char == '/':
            row -= 1
            col = 0
        else:
            if char.isdigit():
                col += int(char)
                continue

            field[row, col] = char_to_piece[char]
            col += 1

    return field


def field_to_fen(field: np.ndarray, side: int):
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

            fen += piece_to_char[int(field[row, col])]

        if empty:
            fen += str(empty)

        fen += '/'

    return f"{fen} {side_to_fen[side]}"
