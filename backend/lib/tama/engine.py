# from numba import config

# config.DISABLE_JIT = True

import numpy as np
from numba import njit
from lib.tama.rules import get_possible_moves, make_move_with_capture, make_move_without_capture
from lib.tama.fen import fen_to_field


@njit()
def evaluate_field(field, side):
    return np.sum(field * side)


@njit()
def find_best_moves(field, side, max_depth):
    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    best_move_idx = 0
    alpha = -999999
    stats = np.array([0], dtype=np.int64)
    field_copy = field.copy()
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture + 1):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            evaluated = -evaluate_move(field, max_depth, stats, -side, -alpha, 1)
            print(evaluated, stats)
            if evaluated > alpha:
                alpha = evaluated
                best_move_idx = i

            field = field_copy.copy()
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            evaluated = -evaluate_move(field, max_depth, stats, -side, -alpha, 1)
            print(evaluated, stats)
            if evaluated > alpha:
                alpha = evaluated
                best_move_idx = i
            field = field_copy.copy()

    return best_move_idx, stats


@njit()
def evaluate_move(field, max_depth, stats, side, beta, depth):
    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    if depth == max_depth:
        stats[0] += 1
        return evaluate_field(field, side)

    alpha = -999999
    field_copy = field.copy()
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture + 1):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            alpha = max(alpha, -evaluate_move(field, max_depth, stats, -side, -alpha, depth + 1))
            if alpha >= beta:
                return alpha

            field = field_copy.copy()
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            alpha = max(alpha, -evaluate_move(field, max_depth, stats, -side, -alpha, depth + 1))
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
    print(*find_best_moves(field, 1, 9))


if __name__ == '__main__':
    main()
