# from numba import config

# config.DISABLE_JIT = True

import numpy as np
import time
from numba import njit
from lib.tama.rules import get_possible_moves, make_move_with_capture, make_move_without_capture
from lib.tama.fen import fen_to_field


@njit()
def evaluate_node(field):
    return np.sum(field)


@njit()
def find_best_moves(field, side, depth):
    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    best_move_idx = 0
    alpha = -999999
    beta = -alpha
    stats = np.array([0], dtype=np.int64)
    field_copy = field.copy()
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture + 1):
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
def negamax(stats, field, depth, alpha, beta, side):
    if depth == 0:
        stats[0] += 1
        return evaluate_node(field) * side

    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    field_copy = field.copy()
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture + 1):
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
    field = fen_to_field('8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w')
    print('start')
    print(*find_best_moves(field, 1, 10))


'''
print(*find_best_moves(field, 1, 10))
5 [1673526]
4 [3183947]
1 [3183947]

5 [657450]
5 [1119505]
1 [1119505]
'''

if __name__ == '__main__':
    main()
