# from numba import config

# config.DISABLE_JIT = True

import numpy as np
from time import time
from numba import njit
from lib.tama.rules import get_possible_moves, make_move_with_capture, make_move_without_capture
from lib.fen import fen_to_field, field_to_fen


@njit()
def evaluate_node(field):
    return np.sum(field)


@njit()
def find_best_moves(field_copy, side, depth):
    print(1)
    field = field_copy.copy()
    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    best_move_idx = 0
    alpha = -999999
    beta = -alpha
    stats = np.array([0, 0], dtype=np.int64)
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            evaluated = -negamax(stats, field, depth - 1, -beta, -alpha, -side)
            print(evaluated, stats)
            if evaluated > alpha:
                alpha = evaluated
                best_move_idx = i

            field = field_copy.copy()
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            evaluated = -negamax(stats, field, depth - 1, -beta, -alpha, -side)
            print(evaluated, stats)
            if evaluated > alpha:
                alpha = evaluated
                best_move_idx = i

            field = field_copy.copy()

    return best_move_idx, stats


@njit()
def negamax(stats, field_copy, depth, alpha, beta, side):
    if depth == 0:
        stats[0] += 1
        return evaluate_node(field_copy) * side

    field = field_copy.copy()
    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]
    stats[1] = max(stats[1], moves_idx)

    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            alpha = max(alpha, -negamax(stats, field, depth - 1, -beta, -alpha, -side))
            if alpha >= beta:
                return alpha

            field = field_copy.copy()
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            alpha = max(alpha, -negamax(stats, field, depth - 1, -beta, -alpha, -side))
            if alpha >= beta:
                return alpha

            field = field_copy.copy()

    return alpha


# compile
test_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
find_best_moves(test_field, 1, 2)


def main():
    field = fen_to_field('8/wwwwwwww/wwwww2w/7w/2b3b1/bb1bbbbb/2bWb3/8/ w')
    possible = get_possible_moves(field, 1)
    print(possible[0])

    field = fen_to_field('8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w')
    print('start')
    print(evaluate_node(field))
    t = time()
    print(*find_best_moves(field, 1, 10))
    print(f"time: {time() - t:.2f}")


'''
'8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w'
moves = np.zeros((1500, 5), dtype=np.uint32)
1 [20925520     1081]
time: 36.09
1 [20925520     1081]
time: 35.61
1 [20925520     1081]
time: 35.12

moves = np.zeros((1500, 5), dtype=np.uint16)
1 [20925520     1081]
time: 33.53
1 [20925520     1081]
time: 35.94
1 [20925520     1081]
time: 33.06

moves = np.zeros((1100, 5), dtype=np.uint16)
1 [20925520     1081]
time: 33.14
1 [20925520     1081]
time: 34.30
1 [20925520     1081]
time: 34.53

moves = np.empty((1100, 5), dtype=np.uint16)
1 [20925520     1081]
time: 35.33
1 [20925520     1081]
time: 36.27
1 [20925520     1081]
time: 33.91

'8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w'
moves = np.empty((1100, 5), dtype=np.uint16)
1 [19344153       56]
time: 96.65
1 [19344153       56]
time: 93.64
1 [19344153       56]
time: 94.59
1 [19344153       56]
time: 97.76

moves = np.empty((1100, 5), dtype=np.uint8) 17,3 GB
1 [19344153       56]
time: 94.45

moves = np.empty((1100, 5), dtype=np.uint32)
1 [19344153       56]
time: 100.40
1 [19344153       56]
time: 98.53
1 [19344153       56]
time: 101.09

moves = np.empty((1100, 5), dtype=np.int32)
1 [19344153       56]
time: 95.93
1 [19344153       56]
time: 105.52

moves = np.empty((1100, 5), dtype=np.int64) 17,3 GB
1 [19344153       56]
time: 104.71
1 [19344153       56]
time: 104.52

moves = np.empty((60, 5), dtype=np.int64)
1 [19344153       56]
time: 95.33

moves = np.empty((60, 5), dtype=np.uint8)
1 [19344153       56]
time: 96.86

'8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w'
moves = np.empty((1500, 5), dtype=np.uint32
1 [20925520     1081]
time: 34.17

moves = np.empty((1500, 5), dtype=np.int32) 15,5 GB
1 [20925520     1081]
time: 33.70
1 [20925520     1081]
time: 36.66

WITH MOVE GENERATOR 14,8GB - 36,6GB = -21,8 GB
1 [29832695        0]
time: 36.87
1 [29832695        0]
time: 39.16


'''

if __name__ == '__main__':
    main()
