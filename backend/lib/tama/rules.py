import numpy as np
from numba import njit
from lib.tama.fen import fen_to_field

# men directions with capture
mcd = np.array([
    [[0, 0], [0, 0], [0, 0]],  # stub
    [[0, -1], [-1, 0], [0, 1]],  # for white
    [[0, -1], [1, 0], [0, 1]],  # for black
], dtype=np.int8)

# men directions without capture
md = np.array([
    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],  # stub
    [[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]],  # for white
    [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1]],  # for black
], dtype=np.int8)

# king directions with capture
kcd = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]], dtype=np.int8)

# king directions without capture
kd = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]], dtype=np.int8)


@njit()
def on_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


@njit()
def is_promoted(side, row):
    return (side == 1 and row == 0) or (side == -1 and row == 7)


# TODO: king cannot capture backwards
# future idea, keeping possible moves while searching capture, if capture detected alter saving moves
@njit()
def find_capture_for_piece(field, side, row, col, pr_dir):
    if field[row, col] * side == 1:
        for i in range(mcd[side].shape[0]):
            row2 = row + mcd[side, i, 0]
            col2 = col + mcd[side, i, 1]
            if on_board(row2, col2) and field[row2, col2] * side < 0:
                row3 = row2 + mcd[side, i, 0]
                col3 = col2 + mcd[side, i, 1]
                if on_board(row3, col3) and field[row3, col3] == 0:
                    yield row2, col2, row3, col3, is_promoted(side, row3), 0

    elif field[row, col] * side == 2:
        for i in range(kcd.shape[0]):
            if pr_dir and i == (pr_dir + 1) % 4:
                continue

            row2 = row
            col2 = col
            while True:
                row2 += kcd[i, 0]
                col2 += kcd[i, 1]
                if not on_board(row2, col2) or field[row2, col2] * side > 0:
                    break

                if field[row2, col2] * side < 0:
                    row3 = row2
                    col3 = col2
                    while True:
                        row3 += kcd[i, 0]
                        col3 += kcd[i, 1]
                        if not on_board(row3, col3) or field[row3, col3] * side != 0:
                            break

                        yield row2, col2, row3, col3, 0, i + 1
                    break


@njit()
def find_moves_for_piece(field, side, row, col):
    if field[row, col] * side == 1:
        for i in range(md[side].shape[0]):
            row2 = row + md[side, i, 0]
            col2 = col + md[side, i, 1]
            if on_board(row2, col2) and field[row2, col2] == 0:
                yield row2, col2, is_promoted(side, row2)

    elif field[row, col] * side == 2:
        for i in range(kd.shape[0]):
            row2 = row
            col2 = col
            while True:
                row2 += kd[i, 0]
                col2 += + kd[i, 1]
                if not on_board(row2, col2) or field[row2, col2] != 0:
                    break

                yield row2, col2, 0


@njit()
def make_move_without_capture(field, row, col, row2, col2, promoted):
    field[row2, col2] = field[row, col] * (2 if promoted else 1)
    field[row, col] = 0


@njit()
def make_move_with_capture(field, row, col, row2, col2, row3, col3, promoted):
    make_move_without_capture(field, row, col, row3, col3, promoted)
    field[row2, col2] = 0


# weird syntax, but works fine almost like "with" in python
@njit()
def make_move_with_capture_reverted(field, row, col, row2, col2, row3, col3, promoted):
    captured_piece = field[row2, col2]
    piece = field[row, col]
    yield make_move_with_capture(field, row, col, row2, col2, row3, col3, promoted)
    field[row2, col2] = captured_piece
    field[row, col] = piece
    field[row3, col3] = 0


@njit()
def find_capture_for_piece_with_capture(field, side, row, col, pr_dir):
    for row2, col2, row3, col3, promoted, cur_dir in find_capture_for_piece(field, side, row, col, pr_dir):
        for _ in make_move_with_capture_reverted(field, row, col, row2, col2, row3, col3, promoted):
            yield row2, col2, row3, col3, promoted, cur_dir


@njit()
def find_capture_max_depth(field, side, row, col, pr_dir, depth):
    max_depth = depth
    for _, _, row3, col3, _, cur_dir in find_capture_for_piece_with_capture(field, side, row, col, pr_dir):
        max_depth = max(max_depth, find_capture_max_depth(field, side, row3, col3, cur_dir, depth + 1))

    return max_depth


@njit()
def find_field_capture_max_depth(field, side):
    max_capture = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            max_capture = max(max_capture, find_capture_max_depth(field, side, row, col, 0, 0))

    return max_capture


@njit()
def find_possible_capture(field, side, row, col, pr_dir, depth, max_depth, piece_idx, moves):
    if depth == max_depth:
        return 1

    piece_offset = piece_idx
    for row2, col2, row3, col3, promoted, cur_dir in find_capture_for_piece_with_capture(field, side, row, col, pr_dir):
        cnt = find_possible_capture(field, side, row3, col3, cur_dir, depth + 1, max_depth, piece_idx, moves)
        for i in range(cnt):
            moves[(piece_idx + i) * (max_depth + 1) + depth + 2] = row2, col2, row3, col3, promoted

        piece_idx += cnt

    return piece_idx - piece_offset


@njit()
def find_field_possible_capture(field, side, max_capture, moves):
    piece_idx = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            cnt = find_possible_capture(field, side, row, col, 0, 0, max_capture, piece_idx, moves)
            for i in range(cnt):
                moves[(piece_idx + i) * (max_capture + 1) + 1] = 0, 0, row, col, 0

            piece_idx += cnt
    return piece_idx


@njit()
def find_field_possible_moves(field, side, moves):
    piece_idx = 0
    for row in range(field.shape[0]):
        for col in range(field.shape[1]):
            for row2, col2, promoted in find_moves_for_piece(field, side, row, col):
                moves[piece_idx + 1] = row, col, row2, col2, promoted
                piece_idx += 1
    return piece_idx


@njit()
def get_possible_moves(field: np.ndarray, side: int):
    # moves array has three purposes: 1) save metadata 2) save non capture moves 3) save capture moves
    # structure for three cases:
    # 1) saving metadata in first index (reserved):
    # (index_end_of_array, max_capture, 0, 0, 0)
    # 2) saving move (from_row, from_col, to_row, to_col, promoted)
    # 3) saving sequences of captures
    # first element in every sequence:
    # (0, 0, row, col, 0)
    # other elements are elements of sequence itself size of capture_depth:
    # (captured_row, captured_col, new_row, new_col, promoted)

    moves = np.zeros((200, 5), dtype=np.uint8)
    moves[0] = 0, 0, 0, 0, 0

    max_capture = find_field_capture_max_depth(field, side)
    moves[0, 1] = max_capture
    if max_capture > 0:
        moves[0, 0] = find_field_possible_capture(field, side, max_capture, moves) * (max_capture + 1) + 1
    else:
        moves[0, 0] = find_field_possible_moves(field, side, moves) + 1

    return moves


@njit()
def make_move(move_idx, field, moves):
    max_capture = moves[0, 1]
    if max_capture:
        row, col = moves[move_idx, 2:4]
        row2, col2, row3, col3, promoted = moves[move_idx + 1]

        make_move_with_capture(field, row, col, row2, col2, row3, col3, promoted)
    else:
        row, col, row2, col2, promoted = moves[move_idx]
        make_move_without_capture(field, row, col, row2, col2, promoted)


def show_possible_moves(moves: np.ndarray, prev_sequences: list[int]):
    max_capture = moves[0, 1]
    possible: dict[tuple[int, int], dict[tuple[int, int], list[int]]] = {}

    if max_capture:
        if prev_sequences:
            for i in prev_sequences:
                row, col, row2, col2 = int(moves[i, 2]), int(moves[i, 3]), int(moves[i + 1, 2]), int(moves[i + 1, 3])
                if (row, col) not in possible:
                    possible[row, col] = {}
                if (row2, col2) not in possible[row, col]:
                    possible[row, col][row2, col2] = []

                possible[row, col][row2, col2].append(i)
        else:
            for i in range(1, moves[0, 0], max_capture + 1):
                row, col, row2, col2 = int(moves[i, 2]), int(moves[i, 3]), int(moves[i + 1, 2]), int(moves[i + 1, 3])
                if (row, col) not in possible:
                    possible[row, col] = {}
                if (row2, col2) not in possible[row, col]:
                    possible[row, col][row2, col2] = []

                possible[row, col][row2, col2].append(i)
    else:
        for i in range(1, moves[0, 0]):
            row, col, row2, col2 = int(moves[i, 0]), int(moves[i, 1]), int(moves[i, 2]), int(moves[i, 3])
            if (row, col) not in possible:
                possible[row, col] = {}
            if (row2, col2) not in possible[row, col]:
                possible[row, col][row2, col2] = []

            possible[row, col][row2, col2].append(i)

    return possible


def print_moves(moves):
    max_capture = moves[0, 1]
    print(moves[0], '\n')
    for i in range(1, moves[0, 0]):
        print(moves[i])
        if max_capture and (i - 1) % (max_capture + 1) == max_capture:
            print()


# compile
test_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
test_moves = get_possible_moves(test_field, 1)
make_move(1, test_field, test_moves)


def main():
    # start_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
    start_field = np.array([
        [0, 0, 0, 0, 0, -1, 0, 0],
        [-1, -1, -1, -1, -1, 0, -1, -1],
        [-1, -1, -1, -1, 0, -1, -1, -1],
        [0, 0, -1, 0, -1, 0, 0, 0],
        [-1, -1, 0, 0, 0, -1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ], dtype=np.int8)
    print(start_field)

    moves = get_possible_moves(start_field, 1)
    print_moves(moves)


if __name__ == '__main__':
    main()

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
