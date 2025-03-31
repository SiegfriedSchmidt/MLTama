import numpy as np
from numba import njit, types, typeof

from lib.tama.fen import fen_to_field

mcd = np.array([[0, -1], [-1, 0], [0, 1]], dtype=np.int8)  # men directions with capture
md = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]], dtype=np.int8)  # men directions without capture
kcd = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]], dtype=np.int8)  # king directions with capture
kd = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]],
              dtype=np.int8)  # king directions without capture

'''
1 1


'''


@njit()
def on_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


@njit()
def find_capture_for_piece(field, row, col):
    for i in range(mcd.shape[0]):
        row2 = row + mcd[i, 0]
        col2 = col + mcd[i, 1]
        if not on_board(row2, col2):
            continue
        if field[row2, col2] == -1:
            row3 = row2 + mcd[i, 0]
            col3 = col2 + mcd[i, 1]
            if not on_board(row3, col3):
                continue
            if field[row3, col3] == 0:
                yield row2, col2, row3, col3


# TODO: men promoted to king and continue capture
@njit()
def find_capture_for_piece_with_capture(field, row, col):
    for row2, col2, row3, col3 in find_capture_for_piece(field, row, col):
        captured_piece = field[row2, col2]
        field[row2, col2] = 0
        yield row2, col2, row3, col3
        field[row2, col2] = captured_piece


@njit()
def find_capture_max_depth(field, row, col, depth):
    max_depth = depth

    for row2, col2, row3, col3 in find_capture_for_piece_with_capture(field, row, col):
        max_depth = max(max_depth, find_capture_max_depth(field, row3, col3, depth + 1))

    return max_depth


@njit()
def find_field_capture_max_depth(field):
    max_capture = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            if field[row, col] == 1:
                max_capture = max(max_capture, find_capture_max_depth(field, row, col, 0))

    return max_capture


@njit()
def find_possible_capture_for_men(field, row, col, depth, max_depth, piece_idx, capture):
    if depth == max_depth:
        return 1

    piece_offset = piece_idx
    for row2, col2, row3, col3 in find_capture_for_piece_with_capture(field, row, col):
        cnt = find_possible_capture_for_men(field, row3, col3, depth + 1, max_depth, piece_idx, capture)
        for i in range(cnt):
            capture[piece_idx + i, depth + 1] = row2, col2, row3, col3

        piece_idx += cnt

    return piece_idx - piece_offset


@njit()
def find_field_possible_capture(field, max_capture, capture):
    piece_idx = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            if field[row, col] == 1:
                cnt = find_possible_capture_for_men(field, row, col, 0, max_capture, piece_idx, capture)
                for i in range(cnt):
                    capture[piece_idx + i, 0] = row, col, max_capture, 0

                piece_idx += cnt

    return piece_idx


@njit()
def find_field_possible_moves(field, non_capture):
    piece_idx = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            if field[row, col] == 1:
                for i in range(md.shape[0]):
                    row2 = row + md[i, 0]
                    col2 = col + md[i, 1]
                    if not on_board(row2, col2) or field[row2, col2] != 0:
                        continue
                    non_capture[piece_idx] = row, col, row2, col2, 0
                    piece_idx += 1

    return piece_idx


@njit()
def get_possible_moves(input_field: np.ndarray, side: int):
    field = np.copy(input_field) * side

    # dimensions: 0 - idx of sequence, 1 - move idx in sequence, 2 - move (captured_row, captured_col, new_row, new_col)
    # first "move" in every sequence (row, col, capture_depth, promoted)
    capture = np.zeros((20, 16, 4), dtype=np.int8)
    captured_idx = 0
    # dimensions: 0 - idx of move, 1 - move (from_row, from_col, to_row, to_col, promoted)
    non_capture = np.zeros((168, 5), dtype=np.int8)
    non_capture_idx = 0

    max_capture = find_field_capture_max_depth(field)
    if max_capture > 0:
        captured_idx = find_field_possible_capture(field, max_capture, capture)
        for i in range(captured_idx):
            print(capture[i, 0: capture[i, 0, 2] + 1])
    else:
        non_capture_idx = find_field_possible_moves(field, non_capture)
        for i in range(non_capture_idx):
            print(non_capture[i])

    return capture, captured_idx, non_capture, non_capture_idx


if __name__ == '__main__':
    start_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
    # start_field = np.array([
    #     [0, 0, 0, 0, 0, 0, 0, 0],
    #     [-1, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, -1, -1, -1, -1],
    #     [0, 0, -1, 0, -1, 0, 0, 0],
    #     [-1, -1, 0, 0, 0, -1, 0, 0],
    #     [1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 0, 0, 0, 0],
    # ], dtype=np.int8)
    print(start_field)
    get_possible_moves(start_field, 1)

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
