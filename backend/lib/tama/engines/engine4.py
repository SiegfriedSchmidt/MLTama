from numba import config

config.DISABLE_JIT = True

import numpy as np
from time import time
from numba import njit
from lib.tama.rules_libc import get_possible_moves, make_move_with_capture, make_move_without_capture
from lib.fen import fen_to_field
from lib.tama.helpers import field_to_fen_numba

pieces_eval_arrays = np.zeros((5, 8, 8), dtype=np.int32)

for i in range(8):
    for j in range(8):
        if i == 0 or i == 7:
            continue
        pieces_eval_arrays[1, i, j] = max(10, 10 + (6 - i) * 2)
        pieces_eval_arrays[-1, i, j] = min(-10, -10 - (i - 1) * 2)
        pieces_eval_arrays[2] = 100
        pieces_eval_arrays[-2] = -100


@njit()
def evaluate_node(field):
    value = 0
    white_count = 0
    black_count = 0
    for i in range(8):
        for j in range(8):
            if field[i, j] > 0:
                white_count += 1
            elif field[i, j] < 0:
                black_count += 1
            value += pieces_eval_arrays[field[i, j], i, j]

    if white_count == 0:
        return -10000
    elif black_count == 0:
        return 10000
    return value


@njit()
def evaluate_node_at_depth(stats, field_copy, side, depth):
    field = field_copy.copy()
    moves = get_possible_moves(field_copy, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    alpha = -999999
    beta = 999999
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            value = -negamax(stats, field, depth - 1, -beta, -alpha, -side)
            alpha = max(alpha, value)
            field = field_copy.copy()

            yield i, value, i == moves_idx - max_capture - 1
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            value = -negamax(stats, field, depth - 1, -beta, -alpha, -side)
            alpha = max(alpha, value)
            field = field_copy.copy()

            yield i, value, i == moves_idx - 1


@njit()
def negamax(stats, field_copy, depth, alpha, beta, side):
    if depth == 0:
        stats[0] += 1
        return evaluate_node(field_copy) * side

    moves = get_possible_moves(field_copy, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    # is terminal node
    if moves_idx == 1:
        stats[0] += 1
        return -10000

    field = field_copy.copy()
    stats[1] = max(stats[1], moves_idx)

    value = -999999
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            next_depth = depth - 1 if depth > 1 else depth
            value = max(value, -negamax(stats, field, next_depth, -beta, -alpha, -side))
            alpha = max(alpha, value)
            if alpha >= beta:
                break

            field = field_copy.copy()
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            value = max(value, -negamax(stats, field, depth - 1, -beta, -alpha, -side))
            alpha = max(alpha, value)
            if alpha >= beta:
                break

            field = field_copy.copy()

    return value


# compile
test_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
test_stats = np.array([0, 0], dtype=np.int64)
evaluate_node_at_depth(test_stats, test_field, 1, 2)


def main():
    from lib.tama.iterative_descent import iterative_descent
    field = fen_to_field('b4B2/2W5/8/3w1w2/8/8/w2w1w1w/1W2w1w1/ b')
    possible = get_possible_moves(field, -1)
    print(possible[0])

    field = fen_to_field('w1w1w1w1/1w1w1w1w/8/3b1b2/2w1w1w1/1b1b1b1b/b1b1b1b1/1b1b1b1b b')
    print(field)
    print('start')
    print(evaluate_node(field))
    t = time()
    iterative_descent(evaluate_node_at_depth, field, 1, 10, lambda a: a)
    print(f"time: {time() - t:.2f}")


if __name__ == '__main__':
    main()
