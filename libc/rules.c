// 
// 29.04.2025

#include "rules.h"

// CONST ARRAYS
#define MCD_SIZE 3
// men directions with capture
static const int MCD[3][MCD_SIZE][2] = {
    {{0, -1}, {1, 0}, {0, 1}}, // for black
    {{0, 0}, {0, 0}, {0, 0}}, // stub
    {{0, -1}, {-1, 0}, {0, 1}}, // for white
};

#define MD_SIZE 5
// men directions without capture
static const int MD[3][MD_SIZE][2] = {
    {{0, -1}, {1, -1}, {1, 0}, {1, 1}, {0, 1}}, // for black
    {{0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}}, // stub
    {{0, -1}, {-1, -1}, {-1, 0}, {-1, 1}, {0, 1}}, // for white
};

// men restricted backward dirs (king dirs indexes) while capturing
static const int M_RESTRICTED_DIR[3][3] = {
    {2, 1, 0}, // for black
    {0, 0, 0}, // stub
    {2, 3, 0}, // for white
};

#define KCD_SIZE 4
// king directions with capture
static const int KCD[KCD_SIZE][2] = {{0, -1}, {-1, 0}, {0, 1}, {1, 0}};

#define KD_SIZE 8
// king directions without capture
static const int KD[KD_SIZE][2] = {{0, -1}, {-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}};

// king restricted backward dirs (king dirs indexes) while capturing
static const int K_RESTRICTED_DIR[4] = {2, 3, 0, 1};

// BUFFER ARRAYS
int BUFFER_INDEX = 0;
CaptureMove BUFFER_CAPTURE_MOVES[10000];
NonCaptureMove BUFFER_NON_CAPTURE_MOVES[100];

static int maxi(int a, int b) {
    return a > b ? a : b;
}

static int on_board(const int row, const int col) {
    return 0 <= row && row < 8 && 0 <= col && col < 8;
}

static int is_promoted(Color side, int row) {
    return (side == WHITE && row == 0) || (side == BLACK && row == 7);
}

static void fill_buffer_capture_move(int index, int row2, int col2, int row3, int col3, int promoted, int pr_dir) {
    BUFFER_CAPTURE_MOVES[index].row2 = row2;
    BUFFER_CAPTURE_MOVES[index].col2 = col2;
    BUFFER_CAPTURE_MOVES[index].row3 = row3;
    BUFFER_CAPTURE_MOVES[index].col3 = col3;
    BUFFER_CAPTURE_MOVES[index].promoted = promoted;
    BUFFER_CAPTURE_MOVES[index].pr_dir = pr_dir;
}

static void fill_buffer_non_capture_move(int index, int row2, int col2, int promoted) {
    BUFFER_NON_CAPTURE_MOVES[index].row2 = row2;
    BUFFER_NON_CAPTURE_MOVES[index].col2 = col2;
    BUFFER_NON_CAPTURE_MOVES[index].promoted = promoted;
}

static void fill_moves_move(MOVES_TYPE moves[][5], int index, int row2, int col2, int row3, int col3, int promoted) {
    moves[index][0] = row2;
    moves[index][1] = col2;
    moves[index][2] = row3;
    moves[index][3] = col3;
    moves[index][4] = promoted;
}

static int find_capture_moves_for_piece(int field[8][8], Color side, int row, int col, int pr_dir) {
    int index = BUFFER_INDEX;
    if (field[row][col] * side == MAN) {
        for (int i = 0; i < MCD_SIZE; ++i) {
            int row2 = row + MCD[side + 1][i][0];
            int col2 = col + MCD[side + 1][i][1];
            if (on_board(row2, col2) && field[row2][col2] * side < 0) {
                int row3 = row2 + MCD[side + 1][i][0];
                int col3 = col2 + MCD[side + 1][i][1];
                if (on_board(row3, col3) && field[row3][col3] == 0) {
                    fill_buffer_capture_move(index++, row2, col2, row3, col3, is_promoted(side, row3),
                                             M_RESTRICTED_DIR[side + 1][i]);
                }
            }
        }
    } else if (field[row][col] * side == KING) {
        for (int i = 0; i < KCD_SIZE; ++i) {
            if (i == pr_dir) continue;

            int row2 = row;
            int col2 = col;
            while (1) {
                row2 += KCD[i][0];
                col2 += KCD[i][1];
                if (!on_board(row2, col2) || field[row2][col2] * side > 0) {
                    break;
                }

                if (field[row2][col2] * side < 0) {
                    int row3 = row2;
                    int col3 = col2;
                    while (1) {
                        row3 += KCD[i][0];
                        col3 += KCD[i][1];
                        if (!on_board(row3, col3) || field[row3][col3] * side != 0) {
                            break;
                        }

                        fill_buffer_capture_move(index++, row2, col2, row3, col3, 0, K_RESTRICTED_DIR[i]);
                    }
                    break;
                }
            }
        }
    }
    return index;
}

static int find_moves_for_piece(int field[8][8], Color side, int row, int col) {
    int index = 0;
    if (field[row][col] * side == MAN) {
        for (int i = 0; i < MD_SIZE; ++i) {
            int row2 = row + MD[side + 1][i][0];
            int col2 = col + MD[side + 1][i][1];
            if (on_board(row2, col2) && field[row2][col2] == 0) {
                fill_buffer_non_capture_move(index++, row2, col2, is_promoted(side, row2));
            }
        }
    } else if (field[row][col] * side == KING) {
        for (int i = 0; i < KD_SIZE; ++i) {
            int row2 = row;
            int col2 = col;
            while (1) {
                row2 += KD[i][0];
                col2 += KD[i][1];
                if (!on_board(row2, col2) || field[row2][col2] != 0) {
                    break;
                }
                fill_buffer_non_capture_move(index++, row2, col2, 0);
            }
        }
    }
    return index;
}

static int find_capture_max_depth(int field[8][8], Color side, int row, int col, int pr_dir, int depth) {
    int max_depth = depth;
    int index = find_capture_moves_for_piece(field, side, row, col, pr_dir);
    for (int i = BUFFER_INDEX; i < index; ++i) {
        const CaptureMove *move = &BUFFER_CAPTURE_MOVES[i];

        int captured_piece = field[move->row2][move->col2];
        int piece = field[row][col];
        make_move_with_capture(field, row, col, move->row2, move->col2, move->row3, move->col3, move->promoted);

        BUFFER_INDEX = index;
        max_depth = maxi(
            max_depth, find_capture_max_depth(field, side, move->row3, move->col3, move->pr_dir, depth + 1)
        );

        field[move->row2][move->col2] = captured_piece;
        field[row][col] = piece;
        field[move->row3][move->col3] = 0;
    }

    return max_depth;
}

static int find_field_capture_max_depth(int field[8][8], Color side) {
    int max_capture = 0;
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            BUFFER_INDEX = 0;
            max_capture = maxi(max_capture, find_capture_max_depth(field, side, row, col, -1, 0));
        }
    }

    return max_capture;
}

static int find_possible_capture(int field[8][8], Color side, int row, int col, int pr_dir, int depth, int max_depth,
                                 int piece_idx, MOVES_TYPE moves[][5]) {
    if (depth == max_depth) {
        return 1;
    }

    int piece_offset = piece_idx;
    int index = find_capture_moves_for_piece(field, side, row, col, pr_dir);
    for (int i = BUFFER_INDEX; i < index; ++i) {
        const CaptureMove *move = &BUFFER_CAPTURE_MOVES[i];

        int captured_piece = field[move->row2][move->col2];
        int piece = field[row][col];
        make_move_with_capture(field, row, col, move->row2, move->col2, move->row3, move->col3, move->promoted);

        BUFFER_INDEX = index;
        int cnt = find_possible_capture(field, side, move->row3, move->col3, move->pr_dir, depth + 1, max_depth,
                                        piece_idx, moves);

        for (int j = 0; j < cnt; ++j) {
            fill_moves_move(moves, (piece_idx + j) * (max_depth + 1) + depth + 2, move->row2, move->col2, move->row3,
                            move->col3, move->promoted);
        }
        piece_idx += cnt;

        field[move->row2][move->col2] = captured_piece;
        field[row][col] = piece;
        field[move->row3][move->col3] = 0;
    }

    return piece_idx - piece_offset;
}

static int find_field_possible_capture(int field[8][8], Color side, int max_capture, MOVES_TYPE moves[][5]) {
    int piece_idx = 0;
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            BUFFER_INDEX = 0;
            int cnt = find_possible_capture(field, side, row, col, -1, 0, max_capture, piece_idx, moves);
            for (int i = 0; i < cnt; ++i) {
                fill_moves_move(moves, (piece_idx + i) * (max_capture + 1) + 1, 0, 0, row, col, 0);
            }

            piece_idx += cnt;
        }
    }

    return piece_idx;
}

static int find_field_possible_moves(int field[8][8], Color side, MOVES_TYPE moves[][5]) {
    int piece_idx = 0;
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            int index = find_moves_for_piece(field, side, row, col);
            for (int i = 0; i < index; ++i) {
                const NonCaptureMove *move = &BUFFER_NON_CAPTURE_MOVES[index];
                fill_moves_move(moves, piece_idx + 1, row, col, move->row2, move->col2, move->promoted);
                piece_idx += 1;
            }
        }
    }
    return piece_idx;
}

void get_possible_moves(MOVES_TYPE moves[][5], int field[8][8], Color side) {
    fill_moves_move(moves, 0, 0, 0, 0, 0, 0);
    int max_capture = find_field_capture_max_depth(field, side);
    moves[0][1] = max_capture;
    if (max_capture > 0) {
        moves[0][0] = find_field_possible_capture(field, side, max_capture, moves) * (max_capture + 1) + 1;
    } else {
        moves[0][0] = find_field_possible_moves(field, side, moves) + 1;
    }
}

void make_move_without_capture(int field[8][8], int row, int col, int row2, int col2, int promoted) {
    field[row2][col2] = field[row][col] * (promoted ? KING : MAN);
    field[row][col] = 0;
}

void make_move_with_capture(int field[8][8], int row, int col, int row2, int col2, int row3, int col3, int promoted) {
    make_move_without_capture(field, row, col, row3, col3, promoted);
    field[row2][col2] = 0;
}
