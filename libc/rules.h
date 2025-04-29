// 
// 29.04.2025

#ifndef RULES_H
#define RULES_H

typedef enum { WHITE = 1, BLACK = -1 } Color;

typedef enum { MAN = 1, KING = 2 } Piece;

typedef struct CaptureMove {
    int row2;
    int col2;
    int row3;
    int col3;
    int promoted;
    int pr_dir;
} CaptureMove;

typedef struct NonCaptureMove {
    int row2;
    int col2;
    int promoted;
} NonCaptureMove;

void make_move_without_capture(int [8][8], int, int, int, int, int);

void make_move_with_capture(int [8][8], int, int, int, int, int, int, int);

void get_possible_moves(long moves[10000][5], int field[8][8], Color side);
#endif //RULES_H
