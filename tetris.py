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

    WALL_KICK_TEST_JLTSZ = [
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    ]

    WALL_KICK_EXCEPTION = [
        {"rotation": 0, "clockwise": 1, "test": 4},
        {"rotation": 1, "clockwise": 0, "test": 3},
        {"rotation": 2, "clockwise": 1, "test": 3},
        {"rotation": 3, "clockwise": 0, "test": 4},
    ]

    WALL_KICK_TEST_I = [
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    ]

    t_spinned = False
    mini_t_spinned = False

    curr_tetromino = 0
    curr_pos = START_POINT
    curr_rotation_state = 0

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
        self.curr_rotation_state = 0

        self.t_spinned = False
        self.mini_t_spinned = False

    def make_bag(self) -> list:
        basic_bag = range(1, 8)
        random.shuffle(basic_bag)
        return basic_bag

    def hard_drop_pos(self) -> (int, int):
        expected_dropped_pos = self.curr_pos
        diff_blocks_pos = self.TETROMINOS[self.curr_tetromino][self.curr_rotation_state]
        is_move_down_available = True

        while is_move_down_available:
            next_pos = expected_dropped_pos + (1, 0)
            for diff_pos in diff_blocks_pos:
                x, y = next_pos + diff_pos
                if (
                    y < 0
                    or y >= self.BOARD_WIDTH
                    or x >= self.BOARD_HEIGHT
                    or self.board[x][y] != 0
                ):
                    is_move_down_available = False
                    break

            if is_move_down_available:
                expected_dropped_pos = next_pos

        return expected_dropped_pos

    def is_available_move(self, move) -> bool:
        expected_pos = move()
        diff_blocks_pos = self.TETROMINOS[self.curr_tetromino][self.curr_rotation_state]
        for diff_pos in diff_blocks_pos:
            x, y = expected_pos + diff_pos
            if (
                y < 0
                or y >= self.BOARD_WIDTH
                or x >= self.BOARD_HEIGHT
                or self.board[x][y] != 0
            ):
                return False

        return True

    def is_in_board(self, pos: (int, int)) -> bool:
        return (
            pos[0] >= 0
            and pos[0] < self.BOARD_HEIGHT
            and pos[1] >= 0
            and pos[1] < self.BOARD_WIDTH
        )

    def rotate_test(self, is_clockwise: bool) -> (bool, (int, int)):
        rotation_state = self.curr_rotation_state
        next_rotation_state = (rotation_state + 90) % 360
        rotation_state_for_test = self.curr_rotation_state // 90
        if not is_clockwise:
            # set next rotation state for correct test
            next_rotation_state = (rotation_state + 270) % 360
            rotation_state_for_test = next_rotation_state // 90

        base_point = self.curr_pos
        changed_base_point = base_point
        is_rotatable = True

        if self.curr_tetromino == 5:  # I tetromino
            for test_num in range(5):
                if is_clockwise:
                    changed_base_point = (
                        base_point
                        + self.WALL_KICK_TEST_I[rotation_state_for_test][test_num]
                    )
                else:
                    changed_base_point = base_point + (
                        -self.WALL_KICK_TEST_I[rotation_state_for_test][test_num]
                    )
                for block_pos_diff in self.TETROMINOS[5][next_rotation_state]:
                    block_pos = base_point + block_pos_diff
                    if (
                        not self.is_in_board(block_pos)
                        or self.board[block_pos[0]][block_pos[1]] != 0
                    ):
                        is_rotatable = False
                        break

                if is_rotatable:
                    return (is_rotatable, changed_base_point)

                is_rotatable = True
            return (False, changed_base_point)

        elif self.curr_tetromino == 1:  # T tetromino
            for test_num in range(5):
                test_info = {
                    "rotation": rotation_state_for_test,
                    "clockwise": int(is_clockwise),
                    "test": test_num + 1,
                }
                if test_info in self.WALL_KICK_EXCEPTION:
                    continue

                if is_clockwise:
                    changed_base_point = (
                        base_point
                        + self.WALL_KICK_TEST_JLTSZ[rotation_state_for_test][test_num]
                    )
                else:
                    changed_base_point = base_point + (
                        -self.WALL_KICK_TEST_JLTSZ[rotation_state_for_test][test_num]
                    )
                for block_pos_diff in self.TETROMINOS[self.curr_tetromino][
                    next_rotation_state
                ]:
                    block_pos = base_point + block_pos_diff
                    if (
                        not self.is_in_board(block_pos)
                        or self.board[block_pos[0]][block_pos[1]] != 0
                    ):
                        is_rotatable = False
                        break

                if is_rotatable:
                    return (is_rotatable, changed_base_point)

                is_rotatable = True
            return (False, changed_base_point)
        elif self.curr_tetromino != 4:  # SZJL tetromino
            for test_num in range(5):
                if is_clockwise:
                    changed_base_point = (
                        base_point
                        + self.WALL_KICK_TEST_JLTSZ[rotation_state_for_test][test_num]
                    )
                else:
                    changed_base_point = base_point + (
                        -self.WALL_KICK_TEST_JLTSZ[rotation_state_for_test][test_num]
                    )
                for block_pos_diff in self.TETROMINOS[self.curr_tetromino][
                    next_rotation_state
                ]:
                    block_pos = base_point + block_pos_diff
                    if (
                        not self.is_in_board(block_pos)
                        or self.board[block_pos[0]][block_pos[1]] != 0
                    ):
                        is_rotatable = False
                        break

                if is_rotatable:
                    return (is_rotatable, changed_base_point)

                is_rotatable = True
            return (False, changed_base_point)
        else:  # O tetromino
            for block_pos_diff in self.TETROMINOS[4][0]:
                block_pos = base_point + block_pos_diff
                if self.board[block_pos[0]][block_pos[1]] != 0:
                    is_rotatable = False
                    break
            return (is_rotatable, base_point)

    def rotate_clockwise(self) -> bool:
        is_rotatable, new_pos = self.rotate_test(is_clockwise=True)
        if is_rotatable:
            self.curr_rotation_state = (self.curr_rotation_state + 90) % 360
            self.curr_pos = new_pos
            return True
        return False

    def rotate_counterclockwise(self) -> bool:
        is_rotatable, new_pos = self.rotate_test(is_clockwise=False)
        if is_rotatable:
            self.curr_rotation_state = (self.curr_rotation_state + 270) % 360
            self.curr_pos = new_pos
            return True
        return False

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

    def is_on_floor(self):
        if self.is_available_move(self, self.soft_drop_pos):
            return True
        return False

    def line_clear(self, other) -> bool:
        """
        return if line is cleared
        """

        target_lines = []

        for line_num, line in enumerate(self.board):
            if 0 not in line:
                target_lines.append(line_num)

        if not target_lines:
            self.back_to_back = False
            self.combo = 0
            return False

        total_damage = []

        if self.combo > 0:
            total_damage.append(("combo", self.COMBO_DAMAGE[self.combo]))
        self.combo = self.combo + 1

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

        self.t_spinned = False
        self.mini_t_spinned = False

        for target_line in target_lines:
            for line_num in range(target_line, 0, -1):
                self.board[line_num] = self.board[line_num - 1]
            self.board[0] = np.zeros(self.BOARD_WIDTH, dtype=int)

        is_all_clear = True
        for line in self.board:
            if np.sum(line) != 0:
                is_all_clear = False
                break

        if is_all_clear:
            if total_damage[-1][0] == "lines":
                del total_damage[-1]
            total_damage.append("perfect-clear", 10)

        # if user's gauge is not empty, clear gauge and send

        while self.gauge and total_damage:
            if self.gauge[0][1] < total_damage[0][1]:
                total_damage[0] = (
                    total_damage[0][0],
                    total_damage[0][1] - self.gauge[0][1],
                )
                del self.gauge[0]
            elif self.gauge[0][1] > total_damage[0][1]:
                self.gauge[0] = (
                    self.gauge[0][0],
                    self.gauge[0][1] - total_damage[0][1],
                )
                del total_damage[0]
            else:
                del self.gauge[0]
                del total_damage[0]

        if total_damage:
            other.gauge = other.gauge + total_damage

        return True

    def create_garbage_lines(self):
        for garbage in self.gauge:
            hole = random.randint(0, 9)
            garbage_line = [8 for _ in range(10)]
            garbage_line[hole] = 0
            lines = garbage[1]

            garbage_lines = np.repeat(np.array(garbage_line), lines, 0)

            self.board[: self.BOARD_HEIGHT - lines] = self.board[lines:]
            self.board[self.BOARD_HEIGHT - lines :] = garbage_lines

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

        self.curr_rotation_state = 0
        self.curr_pos = (0, self.START_POINT[1])

        diff_blocks_pos = self.TETROMINOS[self.curr_tetromino][self.curr_rotation_state]
        is_move_down_available = True

        while is_move_down_available:
            next_pos = self.curr_pos + (1, 0)
            for diff_pos in diff_blocks_pos:
                x, y = next_pos + diff_pos
                if (
                    y < 0
                    or y >= self.BOARD_WIDTH
                    or x >= self.VISIBLE_BOARD_HEIGHT
                    or self.board[x][y] != 0
                ):
                    is_move_down_available = False
                    break

            if is_move_down_available:
                self.curr_pos = next_pos

        if self.curr_pos[0] < self.VISIBLE_BOARD_HEIGHT - 1:
            self.is_game_over = True

        return
