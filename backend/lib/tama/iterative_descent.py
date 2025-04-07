from time import time
from typing import Iterator, Callable
import numpy as np

from lib.sio_server.types import InfoData
from lib.tama.rules import get_possible_moves


def is_one_move_possible(field, side):
    moves = get_possible_moves(field, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]
    return moves_idx == 2 + max_capture


def is_near_victory(depth_best_value, depth, side, callback):
    if depth_best_value > 9000:
        print(f'GUARANTIED VICTORY {"WHITE" if side == 1 else "BLACK"} IN {depth}')
        callback(
            {'side': side, 'depth': depth, 'value': depth_best_value, 'victoryIn': depth}
        )
        return True
    return False


def iterative_descent(
        evaluate_node_at_depth: Callable[[np.ndarray, np.ndarray, int, int], Iterator[tuple[int, int, bool]]],
        field: np.ndarray, side: int, think_time: int, callback: Callable[[InfoData], None]
):
    print('Start iterative descent')
    one_move = is_one_move_possible(field, side)
    if one_move:
        print('Only one move possible, skip')
        return 1

    t = time()
    stats = np.array([0, 0], dtype=np.int64)  # count of leaves, max sequence
    best_idx = 1
    for depth in range(1, 100):
        if time() - t > think_time / 2:
            return best_idx

        depth_best_value = -999999
        depth_best_idx = 0
        for move_idx, evaluated, last in evaluate_node_at_depth(stats, field, side, depth):
            # critical: > not >=
            if evaluated > depth_best_value:
                depth_best_value = evaluated
                depth_best_idx = move_idx

            print('.', end='')
            if last:
                continue

            if time() - t > think_time:
                print()
                if is_near_victory(depth_best_value, depth, side, callback):
                    return depth_best_idx
                return best_idx

        if is_near_victory(depth_best_value, depth, side, callback):
            return depth_best_idx

        best_idx = depth_best_idx
        callback({'side': side, 'depth': depth, 'value': depth_best_value, 'victoryIn': 0})
        print(
            f'\n{depth=}, best_val: {depth_best_value}, best_idx: {best_idx}, leaves: {stats[0]}, max seq: {stats[1]}'
        )
    return best_idx


# def arrange_moves(unsorted_moves, moves_indexes: np.ndarray):
#     # exploring better moves first
#     max_capture = unsorted_moves[0, 1]
#     moves = np.empty_like(unsorted_moves)
#     moves[0] = unsorted_moves[0]
#
#     new_move_idx = 1
#     for move_idx in moves_indexes:
#         if max_capture:
#             moves[new_move_idx:new_move_idx + max_capture + 1] = unsorted_moves[move_idx:move_idx + max_capture + 1]
#             new_move_idx += max_capture + 1
#         else:
#             moves[new_move_idx] = unsorted_moves[move_idx]
#             new_move_idx += 1
#
#     return moves
#
#
# def get_indexes(moves):
#     moves_idx, max_capture = moves[0, 0], moves[0, 1]
#     if max_capture:
#         return np.array([i for i in range(1, moves_idx, max_capture + 1)])
#     else:
#         return np.array([i for i in range(1, moves_idx)])

# def iterative_descent(
#         evaluate_node_at_depth: Callable[[np.ndarray, np.ndarray, np.ndarray, int, int], Iterator[int]],
#         field: np.ndarray, side: int, think_time: int
# ):
#     t = time()
#     stats = np.array([0, 0], dtype=np.int64)
#     moves = get_possible_moves(field, side)
#
#     moves_indexes = get_indexes(moves)
#     moves_values = np.zeros_like(moves_indexes)
#     for depth in range(5, think_time):
#         print('Depth: ', depth)
#         moves = get_possible_moves(field, side)
#         for j in range(2):
#             for i, evaluated in enumerate(evaluate_node_at_depth(stats, moves, field, side, depth)):
#                 print('.', end='')
#                 moves_values[i] = evaluated
#
#             sorted_indexes = np.argsort(-moves_values)
#             moves = arrange_moves(moves, get_indexes(moves)[sorted_indexes])
#
#             moves_indexes = get_indexes(moves)[sorted_indexes]
#             moves_values = moves_values[sorted_indexes]
#             print()
#             print(moves_indexes)
#             print(moves_values)
#             print(depth, stats, time() - t, moves_indexes[0], moves_values[0])
#
#     # print(moves_indexes)
#     # print(moves_values)
#     return moves_indexes[moves_values == np.max(moves_values)][0]


'''
Depth:  5
......................................
[13 16 14 15 11 12 10 25 24 23 22 21 20 19 18 17 29 26 27 28 31 30 32 33
 36 35 38 37 34  2  9  1  5  8  3  4  7  6]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -9 -9 -9 -9]
5 [182968   1863] 0.7015643119812012 13 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -9 -9 -9 -9]
5 [365936   1863] 1.4061219692230225 1 -3
Depth:  6
......................................
[34 13 14 16 11 12 10 15 25 26 23 24 21 20 19 29 31 30 27 28 32 35 33 18
 36 37 38  2  9  1  8  5 17 22  3  4  7  6]
[-3 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4
 -4 -4 -4 -5 -5 -5 -5 -5 -5 -5 -9 -9 -9 -9]
6 [3339404    1863] 5.167492151260376 34 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4
 -4 -4 -4 -5 -5 -5 -5 -5 -5 -5 -9 -9 -9 -9]
6 [6312872    1863] 8.932178735733032 1 -3
Depth:  7
......................................
[13 16 14 15 11 12 10 29 25 26 23 24 21 20 19 18 31 30 27 28 32 35 34 33
 36 37 38  2  9  1  8  5 17 22  7  6  3  4]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -5 -5 -9 -9]
7 [18077386     6189] 45.47552156448364 13 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -5 -5 -9 -9]
7 [29841900     6189] 82.10079264640808 1 -3
time: 82.10

Depth:  5
......................................
[13 16 14 15 11 12 10 25 24 23 22 21 20 19 18 17 29 26 27 28 31 30 32 33
 36 35 38 37 34  2  9  1  5  8  3  4  7  6]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -9 -9 -9 -9]
5 [79263  1863] 0.17211174964904785 13 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 38 35 36 37 32 30 31 33 34]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4]
5 [156847   1863] 0.33380126953125 1 -3
Depth:  6
......................................
[37 36 35 38 34 13 14 16 24 23 22 15 11 12 10 25 29 26 27 28 31 30 32 17
 20 19 33 21 18  2  9  1  5  8  3  4  7  6]
[-3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4
 -4 -4 -4 -4 -4 -5 -5 -5 -5 -5 -9 -9 -9 -9]
6 [1981188    1863] 2.7745091915130615 37 -3
......................................
[ 8  7  6  5 12 11 10  9 13 14 15 16 20 19 18 17 25 26 27 28 21 22 23 24
 29 31 35 36 37 38  2  1 32 30  3  4 33 34]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -4]
6 [3234867    1863] 4.706758975982666 8 -3
Depth:  7
......................................
[13 16 14 15 11 12 10 25 24 23 22 21 20 19 18 17 29 26 27 28 31 30 32 33
 36 35 38 37 34  8  7  1  2  9  5  6  3  4]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -8 -8]
7 [7333395    2339] 12.910046815872192 13 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3]
7 [10991405     3431] 19.461851835250854 1 -3
time: 19.46

Depth:  5
......................................
[13 16 14 15 11 12 10 25 24 23 22 21 20 19 18 17 29 26 27 28 31 30 32 33
 36 35 38 37 34  2  9  1  5  8  3  4  7  6]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -9 -9 -9 -9]
5 [182257   1863] 0.6621873378753662 13 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -9 -9 -9 -9]
5 [364299   1863] 1.3251402378082275 1 -3
Depth:  6
......................................
[34 13 14 16 11 12 10 15 25 26 23 24 21 20 19 29 31 30 27 28 32 35 33 18
 36 37 38  2  9  1  8  5 17 22  3  4  7  6]
[-3 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4
 -4 -4 -4 -5 -5 -5 -5 -5 -5 -5 -9 -9 -9 -9]
6 [3246169    1863] 5.04796028137207 34 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4
 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -9 -9 -9 -9]
6 [5773445    1863] 8.420280694961548 1 -3
Depth:  7
......................................
[13 16 14 15 11 12 10 29 25 26 23 24 21 20 19 18 31 30 27 28 32 35 34 33
 36 37 38  2  9  1  8  5 17 22  7  6  3  4]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -5 -5 -8 -8]
7 [17480938     6189] 45.1854088306427 13 -3
......................................
[ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
 25 26 27 28 29 30 31 32 33 34 35 36 37 38]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -4 -4 -8 -8]
7 [29140653     6189] 81.60589265823364 1 -3
time: 81.61
'''
