import numpy as np
from numba import njit, types, typeof

from lib.tama.fen import fen_to_field

mcd = np.array([[0, -1], [-1, 0], [0, 1]], dtype=np.int8)  # men directions with capture
md = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]], dtype=np.int8)  # men directions without capture
kcd = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]], dtype=np.int8)  # king directions with capture
kd = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]],
              dtype=np.int8)  # king directions without capture


@njit()
def on_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


@njit()
def find_capture_for_piece(field, side, row, col):
    if field[row, col] * side == 1:
        for i in range(mcd.shape[0]):
            row2 = row + mcd[i, 0]
            col2 = col + mcd[i, 1]
            if not on_board(row2, col2):
                continue
            if field[row2, col2] * side == -1:
                row3 = row2 + mcd[i, 0]
                col3 = col2 + mcd[i, 1]
                if not on_board(row3, col3):
                    continue
                if field[row3, col3] == 0:
                    yield row2, col2, row3, col3, (side == 1 and row3 == 0) or (side == -1 and row3 == 7)


@njit()
def find_moves_for_piece(field, side, row, col):
    if field[row, col] * side == 1:
        for i in range(md.shape[0]):
            row2 = row + md[i, 0]
            col2 = col + md[i, 1]
            if not on_board(row2, col2) or field[row2, col2] != 0:
                continue

            yield row2, col2


# TODO: men promoted to king and continue capture
@njit()
def find_capture_for_piece_with_capture(field, side, row, col):
    for row2, col2, row3, col3, promoted in find_capture_for_piece(field, side, row, col):
        captured_piece = field[row2, col2]
        piece = field[row, col]

        field[row3, col3] = (2 if promoted else 1) * side
        field[row, col] = 0
        field[row2, col2] = 0

        yield row2, col2, row3, col3, promoted

        field[row2, col2] = captured_piece
        field[row, col] = piece
        field[row3, col3] = 0


@njit()
def find_capture_max_depth(field, side, row, col, depth):
    max_depth = depth
    for _, _, row3, col3, _ in find_capture_for_piece_with_capture(field, side, row, col):
        max_depth = max(max_depth, find_capture_max_depth(field, side, row3, col3, depth + 1))

    return max_depth


@njit()
def find_field_capture_max_depth(field, side):
    max_capture = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            max_capture = max(max_capture, find_capture_max_depth(field, side, row, col, 0))

    return max_capture


@njit()
def find_possible_capture(field, side, row, col, depth, max_depth, piece_idx, moves):
    if depth == max_depth:
        return 1

    piece_offset = piece_idx
    for row2, col2, row3, col3, promoted in find_capture_for_piece_with_capture(field, side, row, col):
        cnt = find_possible_capture(field, side, row3, col3, depth + 1, max_depth, piece_idx, moves)
        for i in range(cnt):
            moves[(piece_idx + i) * max_depth + depth + 1] = row2, col2, row3, col3, 0

        piece_idx += cnt

    return piece_idx - piece_offset


@njit()
def find_field_possible_capture(field, side, max_capture, moves):
    piece_idx = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            cnt = find_possible_capture(field, side, row, col, 0, max_capture, piece_idx, moves)
            for i in range(cnt):
                moves[(piece_idx + i) * max_capture] = row, col, max_capture, 0, 0

            piece_idx += cnt

    return piece_idx


@njit()
def find_field_possible_moves(field, side, moves):
    piece_idx = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            for row2, col2 in find_moves_for_piece(field, side, row, col):
                moves[piece_idx] = row, col, row2, col2, 0
                piece_idx += 1
    return piece_idx


@njit()
def get_possible_moves(field: np.ndarray, side: int):
    # # dimensions: 0 - idx of sequence, 1 - move idx in sequence, 2 - move (captured_row, captured_col, new_row, new_col)
    # # first "move" in every sequence (row, col, capture_depth, promoted)
    # capture = np.zeros((20, 16, 4), dtype=np.int8)
    # captured_idx = 0
    # # dimensions: 0 - idx of move, 1 - move (from_row, from_col, to_row, to_col, promoted)
    # non_capture = np.zeros((168, 5), dtype=np.int8)
    # non_capture_idx = 0

    # moves array has two purposes: 1) save non capture moves 2) save capture moves
    # structure for two cases:
    # 1) saving move (from_row, from_col, to_row, to_col, promoted)
    # 2) saving sequences of captures
    # first element in every sequence:
    # (row, col, capture_depth, 0, 0)
    # other elements are elements of sequence itself size of capture_depth:
    # (captured_row, captured_col, new_row, new_col, promoted)

    moves = np.zeros((200, 5), dtype=np.int8)

    max_capture = find_field_capture_max_depth(field, side)
    if max_capture > 0:
        moves_idx = find_field_possible_capture(field, side, max_capture, moves) * max_capture
    else:
        moves_idx = find_field_possible_moves(field, side, moves)

    for i in range(moves_idx):
        print(moves[i])

    return moves_idx, moves


if __name__ == '__main__':
    # start_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
    start_field = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, -1, 0, -1, 0, 0, 0],
        [-1, -1, 0, 0, 0, -1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ], dtype=np.int8)
    print(start_field)
    get_possible_moves(start_field, 1)

'''
3
[[5 1 3 0]
 [4 1 3 1]
 [3 2 3 3]
 [3 4 3 5]]
[[5 5 3 0]
 [4 5 3 5]
 [3 4 3 3]
 [3 2 3 1]]
'''
'''
Цель игры
Целью игры Тама является захват всех шашек противника или лишение их возможности хода.
Процесс игры
Игроки ходят по очереди. Начинает игрок, играющий белыми шашками.

Обычные шашки могут перемещаться вперед, вперед по диагонали, вправо или влево на одну клетку за ход.

Когда обычная шашка завершает свой ход на последней линии доски, она превращается в дамку.

Дамки могут перемещаться на любое количество клеток по вертикали, горизонтали или диагонали в любом направлении (также, как ходит ферзь в шахматах). Дамки не могут прыгать через свои фигуры, а также через две или более фигур противника, стоящих друг за другом.

Ни дамка, ни обычная шашка не могут перемещаться на клетки, занятые другими фигурами.

Захват шашек
Обычная шашка может сбить фигуру противника, стоящую на соседней клетке слева, справа или спереди, если следующая клетка в том же направлении является пустой. В процессе боя шашка игрока прыгает через фигуру противника и становится на следующую за фигурой противника пустую клетку. При этом фигура противника снимается с доски. Если та же самая шашка игрока может сбить еще одну фигуру противника, она должна это сделать.

Дамка может сбить фигуру противника, находящуюся на той же горизонтали или вертикали, если между ними нет других фигур и если следующая за фигурой противника в том же направлении клетка (или клетки)  является пустой. В процессе боя дамка игрока прыгает через фигуру противника и становится на одной из следующих пустых клеток. При этом фигура противника снимается с доски. Если та же самая дамка игрока может сбить еще одну фигуру противника, она должна это сделать.

При сбивании нескольких фигур противника подряд в течение одного хода запрещено совершать последовательные прыжки в противоположных направлениях.

Сбивание фигур противника является обязательным. Т.е. если игрок в свою очередь может сбить одну или несколько фигур противника, то он обязан это сделать.

Если у игрока есть несколько вариантов боя, он обязан выбрать тот вариант, при котором сбивается наибольшее количество фигур противника.
'''
