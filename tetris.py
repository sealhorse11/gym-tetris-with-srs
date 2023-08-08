"""
Tetris Environment
"""


import numpy as np
import random


class Tetris:
    """
    Tetris game implementation
    """

    VISIBLE_BOARD_HEIGHT = 20
    BOARD_HEIGHT = VISIBLE_BOARD_HEIGHT * 2
    BOARD_WIDTH = 10

    board = np.zeros(shape=(BOARD_HEIGHT, BOARD_WIDTH), dtype=int)

    """
    TETROMINO (with spinned shapes)
    """

    TETROMINOS = {
        1: {  # T
            0: ((0, -1), (0, 0), (-1, 0), (0, 1)),
            90: ((1, 0), (0, 0), (-1, 0), (0, 1)),
            180: ((0, -1), (0, 0), (1, 0), (0, 1)),
            270: ((0, -1), (1, 0), (0, 0), (-1, 0)),
        },
        2: {  # S
            0: ((0, -1), (0, 0), (-1, 0), (-1, 1)),
            90: ((-1, 0), (0, 0), (1, 1), (0, 1)),
            180: ((1, -1), (1, 0), (0, 0), (0, 1)),
            270: ((-1, -1), (-1, 0), (1, 0), (0, 0)),
        },
        3: {  # Z
            0: ((-1, -1), (-1, 0), (0, 0), (0, 1)),
            90: ((1, 0), (0, 0), (0, 1), (-1, 1)),
            180: ((0, -1), (0, 0), (1, 0), (1, 1)),
            270: ((1, -1), (0, -1), (0, 0), (-1, 0)),
        },
        4: {  # O
            0: ((0, 0), (-1, 0), (-1, 1), (0, 1)),
            90: ((0, 0), (-1, 0), (-1, 1), (0, 1)),
            180: ((0, 0), (-1, 0), (-1, 1), (0, 1)),
            270: ((0, 0), (-1, 0), (-1, 1), (0, 1)),
        },
        5: {  # I
            0: ((0, -1), (0, 0), (0, 1), (0, 2)),
            90: ((-1, 0), (0, 0), (1, 0), (2, 0)),
            180: ((0, -2), (0, -1), (0, 0), (0, 1)),
            270: ((-2, 0), (-1, 0), (0, 0), (1, 0)),
        },
        6: {  # J
            0: ((-1, -1), (0, -1), (0, 0), (0, 1)),
            90: ((1, 0), (0, 0), (-1, 0), (-1, 1)),
            180: ((0, -1), (0, 0), (1, 1), (0, 1)),
            270: ((1, -1), (1, 0), (0, 0), (-1, 0)),
        },
        7: {  # L
            0: ((0, -1), (0, 0), (0, 1), (-1, 1)),
            90: ((1, 0), (0, 0), (-1, 0), (1, 1)),
            180: ((1, -1), (0, -1), (0, 0), (0, 1)),
            270: ((-1, -1), (-1, 0), (0, 0), (1, 0)),
        },
    }

    BLOCK_COLORS = {
        0: (0, 0, 0),  # background
        1: (120, 37, 111),  # T
        2: (83, 218, 63),  # S
        3: (253, 63, 89),  # Z
        4: (254, 251, 52),  # O
        5: (1, 237, 250),  # I
        6: (0, 119, 211),  # J
        7: (255, 200, 46),  # L
        8: (169, 169, 169),  # garbage block
    }

    GHOST_FILTER_CONST = 0.75
    START_POINT = (20, 4)

    is_map_empty = True
    is_game_over = False

    holded_tetromino = 0
    recently_holded = False
    next_bag = []
    score = 0
    combo = 0
    COMBO_DAMAGE = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4] + [5] * 30
    back_to_back = False
    gauge = []

    t_spinned = False
    mini_t_spinned = False

    curr_tetromino = 0
    curr_pos = START_POINT
    curr_rotation = 0

    def __init__(self):
        self.board = np.array()
        self.next_bag = list()

        self.reset()

    def reset(self):
        """
        Reset the game
        """
        self.is_game_over = False

        self.board = np.zeros(shape=(self.BOARD_HEIGHT, self.BOARD_WIDTH), dtype=int)
        self.is_map_empty = True

        self.next_bag = self.make_bag()
        self.holded_tetromino = 0
        self.recently_holded = False
        self.score = 0
        self.combo = 0
        self.back_to_back = False
        self.gauge = []

        self.curr_tetromino = 0
        self.curr_pos = self.START_POINT
        self.curr_rotation = 0

        self.t_spinned = False
        self.mini_t_spinned = False

    def make_bag(self) -> list:
        basic_bag = range(1, 8)
        random.shuffle(basic_bag)
        return basic_bag

    def game_over(self):
        # TODO: judge that the game is over
        pass

    def hard_drop_pos(self) -> (int, int):
        expected_dropped_pos = self.curr_pos
        diff_blocks_pos = self.TETROMINOS[self.curr_tetromino][self.curr_rotation]
        is_move_down_available = True

        while is_move_down_available:
            next_pos = expected_dropped_pos + (1, 0)
            for diff_pos in diff_blocks_pos:
                x, y = next_pos + diff_pos
                if y < 0 or y >= self.BOARD_WIDTH or x >= self.BOARD_HEIGHT or self.board[x][y] != 0:
                    is_move_down_available = False
                    break

            if is_move_down_available:
                expected_dropped_pos = next_pos

        return expected_dropped_pos

    def is_available_move(self, move) -> bool:
        expected_pos = move()
        diff_blocks_pos = self.TETROMINOS[self.curr_tetromino][self.curr_rotation]
        for diff_pos in diff_blocks_pos:
            x, y = expected_pos + diff_pos
            if y < 0 or y >= self.BOARD_WIDTH or x >= self.BOARD_HEIGHT or self.board[x][y] != 0:
                return False

        return True

    def rotate_clockwise(self) -> (int, int):
        # TODO: using is_available_pos and implement spin
        pass

    def rotate_counterclockwise(self) -> (int, int):
        # TODO: using is_available_pos and implement spin
        pass

    def move_left_pos(self) -> (int, int):
        x, y = self.curr_pos
        return (x, y - 1)

    def move_right_pos(self) -> (int, int):
        x, y = self.curr_pos
        return (x, y + 1)

    def soft_drop_pos(self) -> (int, int):
        x, y = self.curr_pos
        return (x + 1, y)

    def hard_drop(self):
        dropped_pos = self.hard_drop_pos()
        self.curr_pos = dropped_pos
        pass

    def soft_drop(self):
        if self.is_available_move(self, self.soft_drop_pos):
            self.curr_pos = self.soft_drop_pos()
        return

    def move_left(self):
        if self.is_available_move(self, self.move_left_pos):
            self.curr_pos = self.move_left_pos()
        return

    def move_right(self):
        if self.is_available_move(self, self.move_right_pos):
            self.curr_pos = self.move_right_pos()
        return

    def line_clear(self, other):
        # TODO: think my gauge....

        target_lines = []

        for line_num, line in enumerate(self.board):
            if 0 not in line:
                target_lines.append(line_num)

        if len(target_lines) == 0:
            self.back_to_back = False
            self.combo = 0
            return

        total_damage = []

        if len(target_lines) == 4:
            total_damage.append(("tetris", 4))

            if self.back_to_back:
                total_damage.append(("back-to-back", 1))
            else:
                self.back_to_back = True

        elif len(target_lines) <= 3:
            if self.t_spinned:
                total_damage.append(("t-spin", len(target_lines) * 2))

                if self.back_to_back:
                    total_damage.append(("back-to-back", 1))
                else:
                    self.back_to_back = True

            elif self.mini_t_spinned:
                if self.back_to_back:
                    total_damage.append(("back-to-back", 1))
                else:
                    self.back_to_back = True
            else:
                total_damage.append(("lines", len(target_lines) - 1))
                self.back_to_back = False

        if self.combo > 0:
            total_damage.append(("combo", self.COMBO_DAMAGE[self.combo]))
        self.combo = self.combo + 1

        self.t_spinned = False
        self.mini_t_spinned = False

        for target_line in target_lines:
            for line_num in range(target_line, 0, -1):
                self.board[line_num] = self.board[line_num - 1]
            self.board[0] = np.zeros(self.BOARD_WIDTH, dtype=int)

        # TODO: all clear

        is_all_clear = True
        for line in self.board:
            if np.sum(line) != 0:
                is_all_clear = False
                break

        if is_all_clear:
            if total_damage[-1][0] == "lines":
                del total_damage[-1]
            total_damage.append("all clear", 10)

        return

    def create_garbage_lines(self):
        # TODO: make garbage based on gauge ( gauge: list )
        for garbage in self.gauge:
            # TODO: create garbage lines for each enemy's attack
            self.board[0] = [
                0,
                1,
            ]
            pass
        return

    def hold(self):
        if not self.recently_holded:
            if self.holded_tetromino == 0:
                self.holded_tetromino = self.curr_tetromino
                self.pick_next_piece()
                self.recently_holded = True
            else:
                tmp = self.holded_tetromino
                self.holded_tetromino = self.curr_tetromino
                self.curr_tetromino = tmp
                self.recently_holded = True
        return

    def pick_next_piece(self):
        self.curr_tetromino = self.next_bag[0]
        del self.next_bag[0]
        if len(self.next_bag) <= 5:
            self.next_bag = self.next_bag + self.make_bag()
        return
