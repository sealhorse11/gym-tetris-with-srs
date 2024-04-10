import ctypes
import sys
import numpy as np

# Game class for logic
class GameLogic(object):
    def __init__(self, das=100, arr=50, sdf=50, time=0, lock_delay=500, drop_delay=1000):
        try:
            self.lib = ctypes.CDLL('./gym_tetris_with_srs/envs/tetris_battle/libtetris.so', winmode=ctypes.RTLD_GLOBAL)
        except OSError:
            self.lib = ctypes.CDLL('./libtetris.so', winmode=ctypes.RTLD_GLOBAL)

        # self.lib.Game_new.argtypes = []
        # self.lib.Game_new.restype = ctypes.c_void_p

        self.lib.Game_new_in_detail.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.Game_new_in_detail.restype = ctypes.c_void_p

        # self.lib.Game_set_opponent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        # self.lib.Game_set_opponent.restype = None
        self.lib.Game_is_game_over.argtypes = [ctypes.c_void_p]
        self.lib.Game_is_game_over.restype = ctypes.c_bool

        self.lib.Game_move_left.argtypes = [ctypes.c_void_p]
        self.lib.Game_move_left.restype = ctypes.c_bool
        self.lib.Game_move_right.argtypes = [ctypes.c_void_p]
        self.lib.Game_move_right.restype = ctypes.c_bool
        self.lib.Game_soft_drop.argtypes = [ctypes.c_void_p]
        self.lib.Game_soft_drop.restype = ctypes.c_bool

        self.lib.Game_off_left.argtypes = [ctypes.c_void_p]
        self.lib.Game_off_left.restype = None
        self.lib.Game_off_right.argtypes = [ctypes.c_void_p]
        self.lib.Game_off_right.restype = None
        self.lib.Game_off_soft_drop.argtypes = [ctypes.c_void_p]
        self.lib.Game_off_soft_drop.restype = None

        self.lib.Game_hard_drop.argtypes = [ctypes.c_void_p]
        self.lib.Game_hard_drop.restype = None

        self.lib.Game_rotate_counterclockwise.argtypes = [ctypes.c_void_p]
        self.lib.Game_rotate_counterclockwise.restype = None
        self.lib.Game_rotate_clockwise.argtypes = [ctypes.c_void_p]
        self.lib.Game_rotate_clockwise.restype = None

        self.lib.Game_hold.argtypes = [ctypes.c_void_p]
        self.lib.Game_hold.restype = ctypes.c_bool
        self.lib.Game_lock.argtypes = [ctypes.c_void_p]
        self.lib.Game_lock.restype = ctypes.c_bool

        self.lib.Game_is_on_ground.argtypes = [ctypes.c_void_p]
        self.lib.Game_is_on_ground.restype = ctypes.c_bool

        self.lib.Game_get_held_piece.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_held_piece.restype = ctypes.c_int
        self.lib.Game_get_next_pieces_top_five.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_next_pieces_top_five.restype = ctypes.POINTER(ctypes.c_int * 5)
        self.lib.Game_get_sum_of_gauge.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_sum_of_gauge.restype = ctypes.c_int
        
        c_int_p_10 = ctypes.POINTER(ctypes.c_int * 10)

        # restype is 2d pointer
        self.lib.Game_get_board_for_render.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_board_for_render.restype = ctypes.POINTER(ctypes.c_int * (20 * 10))

        self.lib.Game_get_obs.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_obs.restype = ctypes.POINTER(ctypes.c_int * (10 * 20 * 10))

        self.lib.Game_get_last_attack_type.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_last_attack_type.restype = ctypes.c_char_p
        self.lib.Game_get_last_attack_lines.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_last_attack_lines.restype = ctypes.c_int
        self.lib.Game_get_last_attack_combo.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_last_attack_combo.restype = ctypes.c_int
        self.lib.Game_get_last_attack_back_to_back.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_last_attack_back_to_back.restype = ctypes.c_bool

        self.lib.Game_get_sent_attack.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_sent_attack.restype = ctypes.c_int
        self.lib.Game_get_field_height.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_field_height.restype = ctypes.c_int
        self.lib.Game_get_piece_count.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_piece_count.restype = ctypes.c_int
        self.lib.Game_get_time.argtypes = [ctypes.c_void_p]
        self.lib.Game_get_time.restype = ctypes.c_int
        self.lib.Game_set_time.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.Game_set_time.restype = None

        self.lib.Game_delete.argtypes = [ctypes.c_void_p]
        self.lib.Game_delete.restype = None

        self.obj = self.lib.Game_new_in_detail(das, arr, sdf, time, lock_delay, drop_delay)
        self.arr = arr
        self.das = das
        self.sdf = sdf
    
    # def set_opponent(self, opponent):
    #     self.lib.Game_set_opponent(self.obj, opponent.obj)

    def is_game_over(self) -> bool:
        return self.lib.Game_is_game_over(self.obj)
    
    def move_left(self) -> bool:
        return self.lib.Game_move_left(self.obj)
    
    def move_right(self) -> bool:
        return self.lib.Game_move_right(self.obj)
    
    def soft_drop(self) -> bool:
        return self.lib.Game_soft_drop(self.obj)

    def off_left(self) -> None:
        self.lib.Game_off_left(self.obj)
    
    def off_right(self) -> None:
        self.lib.Game_off_right(self.obj)
    
    def off_soft_drop(self) -> None:
        self.lib.Game_off_soft_drop(self.obj)
    
    def hard_drop(self) -> None:
        self.lib.Game_hard_drop(self.obj)
    
    def rotate_counterclockwise(self):
        self.lib.Game_rotate_counterclockwise(self.obj)
    
    def rotate_clockwise(self):
        self.lib.Game_rotate_clockwise(self.obj)
    
    def hold(self) -> bool:
        return self.lib.Game_hold(self.obj)
    
    def lock(self) -> bool:
        return self.lib.Game_lock(self.obj)
    
    def is_on_ground(self) -> bool:
        return self.lib.Game_is_on_ground(self.obj)

    def get_held_piece(self) -> int:
        return self.lib.Game_get_held_piece(self.obj)
    
    def get_next_pieces_top_five(self) -> list:
        darrayptr = self.lib.Game_get_next_pieces_top_five(self.obj)
        darray = darrayptr.contents
        return list(darray)

    def get_sum_of_gauge(self):
        return self.lib.Game_get_sum_of_gauge(self.obj)
    
    def get_board_for_render(self) -> np.ndarray:
        darrayptr = self.lib.Game_get_board_for_render(self.obj)

        board_for_render = np.zeros((20, 10), dtype=np.int8)
        for i in range(20):
            for j in range(10):
                board_for_render[i, j] = darrayptr.contents[i * 10 + j]
        return board_for_render
    
    def get_obs(self) -> np.ndarray:
        darrayptr = self.lib.Game_get_obs(self.obj)
        obs = np.zeros((10, 20, 10), dtype=np.int8)
        for i in range(10):
            for j in range(20):
                for k in range(10):
                    obs[i, j, k] = darrayptr.contents[i * 200 + j * 10 + k]
        return obs
    

    def get_last_attack_type(self):
        last_attack_type = str(self.lib.Game_get_last_attack_type(self.obj), 'utf-8')
        return last_attack_type.replace(" ", "\n")
    
    def get_last_attack_lines(self):
        return self.lib.Game_get_last_attack_lines(self.obj)
    
    def get_last_attack_combo(self):
        return self.lib.Game_get_last_attack_combo(self.obj)
    
    def get_last_attack_back_to_back(self):
        return self.lib.Game_get_last_attack_back_to_back(self.obj)
    
    # for information at observation
    def get_sent_attack(self):
        return self.lib.Game_get_sent_attack(self.obj)

    def get_field_height(self):
        return self.lib.Game_get_field_height(self.obj)

    def get_piece_count(self):
        return self.lib.Game_get_piece_count(self.obj)
    
    def get_time(self):
        return self.lib.Game_get_time(self.obj)
    
    def set_time(self, time: int):
        self.lib.Game_set_time(self.obj, time)
    
    def __del__(self):
        try:
            self.lib.Game_delete(self.obj)
        except AttributeError:
            print("GameLogic object already deleted")