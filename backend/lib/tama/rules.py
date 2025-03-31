import numpy as np
from numba import njit, types, typeof

from lib.tama.fen import fen_to_field

mcd = np.array([[0, -1], [-1, 0], [0, 1]], dtype=np.int8)  # men directions with capture
md = np.array([[-1, -1], [-1, 1]], dtype=np.int8)  # men directions without capture
kcd = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]], dtype=np.int8)  # king directions with capture
kd = np.array([[-1, -1], [-1, 1], [1, 1], [1, -1]], dtype=np.int8)  # king directions without capture

'''
1 1


'''


@njit()
def on_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


@njit()
def find_possible_capture_for_men(field, row, col, capture, capture_low, capture_high, capture_len, max_capture):
    reverted_piece, reverted_capture_idx = 0, capture_high
    max_capture = max(max_capture, capture_len)
    if capture_high != 0:
        reverted_piece = field[capture[capture_high - 1, 0], capture[capture_high - 1, 1]]
        field[capture[capture_high - 1, 0], capture[capture_high - 1, 1]] = 0

    for i in range(mcd.shape[0]):
        row2 = row + mcd[i, 0]
        col2 = col + mcd[i, 1]
        if not on_board(row2, col2):
            continue
        if field[row2, col2] == -1:
            row3 = row2 + mcd[i, 0]
            col3 = col2 + mcd[i, 1]
            if field[row3, col3] == 0:
                capture[capture_high] = row2, col2, row3, col3
                capture_low, capture_high, max_capture = find_possible_capture_for_men(
                    field, row3, col3, capture, capture_low, capture_high + 1, capture_len + 1, max_capture
                )

    if reverted_piece:
        field[capture[reverted_capture_idx, 0], capture[reverted_capture_idx, 1]] = reverted_piece

    return capture_low, capture_high, max_capture


@njit()
def get_possible_moves(input_field: np.ndarray, side: int):
    field = np.copy(input_field) * side

    capture = np.zeros((100, 4), dtype=np.int8)  # TODO: change to empty
    capture_low, capture_high, max_capture = 0, 0, 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            if field[row, col] == 1:
                capture_low, capture_high, max_capture = find_possible_capture_for_men(
                    field, row, col, capture, capture_low, capture_high, 0, max_capture
                )

    print(capture_low, capture_high, max_capture)
    print(capture[capture_low:capture_high])


if __name__ == '__main__':
    # start_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
    start_field = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, 0, -1, 0, 0, 0],
        [-1, -1, 0, 0, 0, -1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ], dtype=np.int8)
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
