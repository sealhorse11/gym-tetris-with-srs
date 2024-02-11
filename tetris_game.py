import pygame
import ctypes
import ctypes.util
import sys
import re

# lib = ctypes.CDLL('C:/Users/omyjj/OneDrive/2-winter/tetris-pvp-ai/libtetris.so', winmode=ctypes.RTLD_GLOBAL)
lib = ctypes.CDLL('./libtetris.so', winmode=ctypes.RTLD_GLOBAL)

# Colors
BACKGROUND = (0, 0, 0)
T_COLOR = (128, 0, 128)
S_COLOR = (0, 255, 0)
Z_COLOR = (255, 0, 0)
O_COLOR = (255, 255, 0)
I_COLOR = (0, 255, 255)
J_COLOR = (0, 0, 255)
L_COLOR = (255, 127, 0)
GHOST_COLOR = (50, 50, 50)
GARBAGE_COLOR = (127, 127, 127)
GRID_COLOR = (30, 30, 30)

COLORS = [T_COLOR, S_COLOR, Z_COLOR, O_COLOR, I_COLOR, J_COLOR, L_COLOR, GARBAGE_COLOR, GHOST_COLOR]

# Pieces' shapes
T_SHAPE = [
    [0, 1, 0],
    [1, 1, 1]
]
S_SHAPE = [
    [0, 1, 1],
    [1, 1, 0]
]
Z_SHAPE = [
    [1, 1, 0],
    [0, 1, 1]
]
O_SHAPE = [
    [1, 1],
    [1, 1]
]
I_SHAPE = [
    [1, 1, 1, 1]
]
J_SHAPE = [
    [1, 0, 0],
    [1, 1, 1]
]
L_SHAPE = [
    [0, 0, 1],
    [1, 1, 1]
]
SHAPES = [T_SHAPE, S_SHAPE, Z_SHAPE, O_SHAPE, I_SHAPE, J_SHAPE, L_SHAPE]

# Game class
class GameLogic(object):
    def __init__(self):
        lib.Game_new.argtypes = []
        lib.Game_new.restype = ctypes.c_void_p
        lib.Game_set_opponent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.Game_set_opponent.restype = None
        lib.Game_is_game_over.argtypes = [ctypes.c_void_p]
        lib.Game_is_game_over.restype = ctypes.c_bool

        lib.Game_move_left.argtypes = [ctypes.c_void_p]
        lib.Game_move_left.restype = None
        lib.Game_move_right.argtypes = [ctypes.c_void_p]
        lib.Game_move_right.restype = None
        lib.Game_soft_drop.argtypes = [ctypes.c_void_p]
        lib.Game_soft_drop.restype = None
        lib.Game_hard_drop.argtypes = [ctypes.c_void_p]
        lib.Game_hard_drop.restype = None

        lib.Game_rotate_counterclockwise.argtypes = [ctypes.c_void_p]
        lib.Game_rotate_counterclockwise.restype = None
        lib.Game_rotate_clockwise.argtypes = [ctypes.c_void_p]
        lib.Game_rotate_clockwise.restype = None

        lib.Game_hold.argtypes = [ctypes.c_void_p]
        lib.Game_hold.restype = None
        lib.Game_lock.argtypes = [ctypes.c_void_p]
        lib.Game_lock.restype = None

        lib.Game_is_on_ground.argtypes = [ctypes.c_void_p]
        lib.Game_is_on_ground.restype = ctypes.c_bool

        lib.Game_get_held_piece.argtypes = [ctypes.c_void_p]
        lib.Game_get_held_piece.restype = ctypes.c_int
        lib.Game_get_next_pieces_top_five.argtypes = [ctypes.c_void_p]
        lib.Game_get_next_pieces_top_five.restype = ctypes.POINTER(ctypes.c_int * 5)
        lib.Game_get_sum_of_gauge.argtypes = [ctypes.c_void_p]
        lib.Game_get_sum_of_gauge.restype = ctypes.c_int
        lib.Game_get_board.argtypes = [ctypes.c_void_p]
        lib.Game_get_board.restype = ctypes.POINTER(ctypes.c_int * 200)

        lib.Game_get_last_attack_type.argtypes = [ctypes.c_void_p]
        lib.Game_get_last_attack_type.restype = ctypes.c_char_p
        lib.Game_get_last_attack_lines.argtypes = [ctypes.c_void_p]
        lib.Game_get_last_attack_lines.restype = ctypes.c_int
        lib.Game_get_last_attack_combo.argtypes = [ctypes.c_void_p]
        lib.Game_get_last_attack_combo.restype = ctypes.c_int
        lib.Game_get_last_attack_back_to_back.argtypes = [ctypes.c_void_p]
        lib.Game_get_last_attack_back_to_back.restype = ctypes.c_bool

        lib.Game_get_sent_attack.argtypes = [ctypes.c_void_p]
        lib.Game_get_sent_attack.restype = ctypes.c_int

        lib.Game_delete.argtypes = [ctypes.c_void_p]
        lib.Game_delete.restype = None

        self.obj = lib.Game_new()
    
    def set_opponent(self, opponent):
        lib.Game_set_opponent(self.obj, opponent.obj)

    def is_game_over(self):
        return lib.Game_is_game_over(self.obj)
    
    def move_left(self):
        lib.Game_move_left(self.obj)
    
    def move_right(self):
        lib.Game_move_right(self.obj)
    
    def soft_drop(self):
        lib.Game_soft_drop(self.obj)
    
    def hard_drop(self):
        lib.Game_hard_drop(self.obj)
    
    def rotate_counterclockwise(self):
        lib.Game_rotate_counterclockwise(self.obj)
    
    def rotate_clockwise(self):
        lib.Game_rotate_clockwise(self.obj)
    
    def hold(self):
        lib.Game_hold(self.obj)
    
    def lock(self):
        lib.Game_lock(self.obj)
    
    def is_on_ground(self):
        return lib.Game_is_on_ground(self.obj)

    def get_held_piece(self):
        return lib.Game_get_held_piece(self.obj)
    
    def get_next_pieces_top_five(self) -> list:
        darrayptr = lib.Game_get_next_pieces_top_five(self.obj)
        darray = darrayptr.contents
        return list(darray)

    def get_sum_of_gauge(self):
        return lib.Game_get_sum_of_gauge(self.obj)
    
    def get_board(self) -> list:
        darrayptr = lib.Game_get_board(self.obj)
        darray = darrayptr.contents
        return list(darray)
    
    def get_last_attack_type(self):
        last_attack_type = str(lib.Game_get_last_attack_type(self.obj), 'utf-8')
        return last_attack_type.replace(" ", "\n")
    
    def get_last_attack_lines(self):
        return lib.Game_get_last_attack_lines(self.obj)
    
    def get_last_attack_combo(self):
        return lib.Game_get_last_attack_combo(self.obj)
    
    def get_last_attack_back_to_back(self):
        return lib.Game_get_last_attack_back_to_back(self.obj)
    
    def get_sent_attack(self):
        return lib.Game_get_sent_attack(self.obj)
    
    def __del__(self):
        lib.Game_delete(self.obj)


class Game():
    def __init__(self, n_agent=2, window_size=(1600, 600), block_size=30, drop_delay=1000, das=200, arr=50, fps=60):
        self.n_agent = n_agent
        self.window_size = window_size
        self.block_size = block_size
        self.play_width = block_size * 10
        self.play_height = block_size * 20
        self.drop_delay = drop_delay
        self.das = das
        self.arr = arr
        self.fps = fps

        self.top_left_x = [(window_size[0] // n_agent * i) + (window_size[0] // n_agent - self.play_width) // 2 for i in range(n_agent)]
        self.top_left_y = (window_size[1] - self.play_height) // 2

        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 50)
        self.mini_font = pygame.font.SysFont("Consolas", 20)

        self.DROP_BLOCK_EVENT = [pygame.USEREVENT + i for i in range(1, n_agent + 1)]

        for i in range(n_agent):
            pygame.time.set_timer(self.DROP_BLOCK_EVENT[i], drop_delay)
        
        self.start()

    def start(self):
        self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Tetris")

        self.player = [GameLogic() for _ in range(self.n_agent)]

        if self.n_agent == 2:
            self.player[0].set_opponent(self.player[1])
            self.player[1].set_opponent(self.player[0])
        
        self.game_over = False

        self.on_grounded = [False for _ in range(self.n_agent)]
        self.on_grounded_time = [0 for _ in range(self.n_agent)]
        self.struggled_time = [0 for _ in range(self.n_agent)]
        self.struggled = [False for _ in range(self.n_agent)]

        self.left_pressed_time = [-1 for _ in range(self.n_agent)]
        self.right_pressed_time = [-1 for _ in range(self.n_agent)]
        self.down_pressed = [False for _ in range(self.n_agent)]
        self.last_moved_time = [-1 for _ in range(self.n_agent)]

        self.start_time = pygame.time.get_ticks()

    def control_lock(self, is_on_ground, on_grounded, struggled, on_grounded_time, struggled_time) -> tuple[bool, bool, int, int, bool]:
        if is_on_ground and not on_grounded:
            struggled_time = pygame.time.get_ticks()
            on_grounded_time = pygame.time.get_ticks()
            on_grounded = True

        if on_grounded:
            if struggled or not is_on_ground:
                on_grounded_time = pygame.time.get_ticks()
                struggled = False
            
            if is_on_ground:
                if (not struggled and pygame.time.get_ticks() - on_grounded_time >= 1000) or (pygame.time.get_ticks() - struggled_time >= 6000):
                    on_grounded = False
                    return (on_grounded, struggled, on_grounded_time, struggled_time, True)
        
        return (on_grounded, struggled, on_grounded_time, struggled_time, False)
    
    def draw_board(self, window, player, top_left_x, top_left_y, block_size):    
        # Draw grid
        line_width = 2
        for i in range(0, 11):
            pygame.draw.line(window, GRID_COLOR, (top_left_x + i * block_size, top_left_y), (top_left_x + i * block_size, top_left_y + 20 * block_size), line_width)
        
        for i in range(0, 21):
            pygame.draw.line(window, GRID_COLOR, (top_left_x, top_left_y + i * block_size), (top_left_x + 10 * block_size, top_left_y + i * block_size), line_width)
        
        # Draw blocks
        board = player.get_board()
        for i in range(200):
            if board[i] != -1:
                pygame.draw.rect(window, COLORS[board[i]], (top_left_x + (i % 10) * block_size, top_left_y + (i // 10) * block_size, block_size, block_size))

        # Draw next pieces
        next_pieces = player.get_next_pieces_top_five()
        for i, target_piece in enumerate(next_pieces):
            for j in range(len(SHAPES[target_piece])):
                for k in range(len(SHAPES[target_piece][j])):
                    if SHAPES[target_piece][j][k] == 1:
                        pygame.draw.rect(window, COLORS[target_piece], (top_left_x + (k + 11) * block_size, top_left_y + (3 * i + j + 1) * block_size, block_size, block_size))
        
        # Draw held piece
        held_piece = player.get_held_piece()
        if held_piece != -1:
            for i in range(len(SHAPES[held_piece])):
                for j in range(len(SHAPES[held_piece][i])):
                    if SHAPES[held_piece][i][j] == 1:
                        pygame.draw.rect(window, COLORS[held_piece], (top_left_x + (j - 5) * block_size, top_left_y + (i + 3) * block_size, block_size, block_size))
        
        # Draw attack
        last_attack_type = player.get_last_attack_type()
        if "PERFECT\nCLEAR" in last_attack_type:
            last_attack_type = str(last_attack_type[len("PERFECT\nCLEAR"):])
            self.window.blit(self.font.render("PERFECT", True, (200, 200, 0)), (top_left_x + 15 * block_size // 8, top_left_y + 9 * block_size))
            self.window.blit(self.font.render("CLEAR", True, (200, 200, 0)), (top_left_x + 11 * block_size // 4, top_left_y + 21 * block_size // 2))

        if last_attack_type != "":
            last_attack_type = last_attack_type.split("\n")
            for i, word in enumerate(last_attack_type):
                if word == "T-SPIN":
                    self.window.blit(self.font.render(word, True, T_COLOR), (top_left_x - 27 * block_size // 4, top_left_y + (9 + 2 * i) * block_size))
                elif word == "TETRIS":
                    self.window.blit(self.font.render(word, True, (0, 255, 255)), (top_left_x - 27 * block_size // 4, top_left_y + (9 + 2 * i) * block_size))
                else:
                    self.window.blit(self.font.render(word, True, (255, 255, 255)), (top_left_x - 27 * block_size // 4, top_left_y + (9 + 2 * i) * block_size))
        
        # Draw back to back
        back_to_back = player.get_last_attack_back_to_back()
        if back_to_back:

            self.window.blit(self.mini_font.render("BACK-TO-BACK", True, (200, 200, 200)), (top_left_x - 25 * block_size // 4, top_left_y + 8 * block_size))

        # Draw combo
        combo = player.get_last_attack_combo()
        if combo > 0:
            self.window.blit(self.font.render(str(combo) + "COMBO", True, (255, 255, 255)), (top_left_x - (25 + len(str(combo)) * 2) * block_size // 4, top_left_y + 17 * block_size))
        
        # Draw gauge
        gauge = player.get_sum_of_gauge()
        if gauge > 0:
            pygame.draw.line(window, (255, 100, 100), (top_left_x + 10 * block_size, top_left_y + 20 * block_size), (top_left_x + 10 * block_size, top_left_y + 20 * block_size - gauge * block_size), 5)
        
        # Draw APM
        apm = (player.get_sent_attack() / (pygame.time.get_ticks() - self.start_time)) * 60000
        self.window.blit(self.mini_font.render("APM: " + str(round(apm, 3)), True, (255, 255, 255)), (top_left_x + 11 * block_size, top_left_y + 20 * block_size - 2 * block_size))



    def play(self, user=0):
        assert self.n_agent <= 2
        
        while not self.game_over:
            # Check game over
            for i in range(self.n_agent):
                if self.player[i].is_game_over():
                    self.game_over = True
                    break
            
            # Deal with events
            self.strgguled = [False, False]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

                if event.type == pygame.KEYDOWN:
                    if self.on_grounded[user]:
                        self.struggled[user] = True
                    
                    if event.key == pygame.K_LEFT:
                        self.left_pressed_time[user] = pygame.time.get_ticks()
                        self.player[user].move_left()
                    if event.key == pygame.K_RIGHT:
                        self.right_pressed_time[user] = pygame.time.get_ticks()
                        self.player[user].move_right()
                    if event.key == pygame.K_DOWN:
                        self.down_pressed[user] = True
                        self.player[user].soft_drop()
                    if event.key == pygame.K_SPACE:
                        self.player[user].hard_drop()
                    if event.key == pygame.K_UP or event.key == pygame.K_x:
                        self.player[user].rotate_clockwise()
                    if event.key == pygame.K_z:
                        self.player[user].rotate_counterclockwise()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_c:
                        self.player[user].hold()
                        self.on_grounded[user] = False
                        self.struggled[user] = False
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.left_pressed_time[user] = -1
                        self.last_moved_time[user] = -1
                    if event.key == pygame.K_RIGHT:
                        self.right_pressed_time[user] = -1
                        self.last_moved_time[user] = -1
                    if event.key == pygame.K_DOWN:
                        self.down_pressed[user] = False
                        self.last_moved_time[user] = -1
                
                for i in range(self.n_agent):
                    if event.type == self.DROP_BLOCK_EVENT[i]:
                        self.player[i].soft_drop()

            # Deal with auto shift
            if self.left_pressed_time[user] != -1 or self.right_pressed_time[user] != -1:
                if self.left_pressed_time[user] != -1 and (pygame.time.get_ticks() - self.left_pressed_time[user] < pygame.time.get_ticks() - self.right_pressed_time[user]) \
                    and pygame.time.get_ticks() - self.left_pressed_time[user] >= self.das:
                    if self.last_moved_time[user] == -1:
                        self.last_moved_time[user] = pygame.time.get_ticks()
                    
                    if self.last_moved_time[user] != -1 and pygame.time.get_ticks() - self.last_moved_time[user] >= self.arr:
                        self.player[user].move_left()
                        self.last_moved_time[user] = pygame.time.get_ticks()
                elif self.right_pressed_time[user] != -1 and (pygame.time.get_ticks() - self.right_pressed_time[user] < pygame.time.get_ticks() - self.left_pressed_time[user]) \
                    and pygame.time.get_ticks() - self.right_pressed_time[user] >= self.das:
                    if self.last_moved_time[user] == -1:
                        self.last_moved_time[user] = pygame.time.get_ticks()
                    
                    if self.last_moved_time[user] != -1 and pygame.time.get_ticks() - self.last_moved_time[user] >= self.arr:
                        self.player[user].move_right()
                        self.last_moved_time[user] = pygame.time.get_ticks()
            
            if self.down_pressed[user]:
                if self.last_moved_time[user] == -1:
                    self.last_moved_time[user] = pygame.time.get_ticks()
                
                if self.last_moved_time[user] != -1 and pygame.time.get_ticks() - self.last_moved_time[user] >= self.arr:
                    self.player[user].soft_drop()
                    self.last_moved_time[user] = pygame.time.get_ticks()
            
            # Deal with lock
            for i in range(self.n_agent):
                self.on_grounded[i], self.struggled[i], self.on_grounded_time[i], self.struggled_time[i], is_to_lock = \
                    self.control_lock(self.player[i].is_on_ground(), self.on_grounded[i], self.struggled[i], self.on_grounded_time[i], self.struggled_time[i])
                
                if is_to_lock:
                    self.player[i].lock()

            # Draw window
            self.window.fill(BACKGROUND)
            for i in range(self.n_agent):
                self.draw_board(self.window, self.player[i], self.top_left_x[i], self.top_left_y, self.block_size)
            pygame.display.flip()

            # Limit frame rate
            self.clock.tick(self.fps)

    def get_obs(self, target_player=0):
        return {
            "board": self.player[target_player].get_board(),
            "held_piece": self.player[target_player].get_held_piece(),
            "next_pieces": self.player[target_player].get_next_pieces_top_five(),
            "combo": self.player[target_player].get_last_attack_combo(),
            "back_to_back": self.player[target_player].get_last_attack_back_to_back(),
            "gauge": self.player[target_player].get_sum_of_gauge(),
            "opponent_board": self.player[1 - target_player].get_board()
        }
    
    def step(self, action, player=0):
        if action == 0:
            self.player[player].move_left()
        elif action == 1:
            self.player[player].move_right()
        elif action == 2:
            self.player[player].soft_drop()
        elif action == 3:
            self.player[player].hard_drop()
        elif action == 4:
            self.player[player].rotate_clockwise()
        elif action == 5:
            self.player[player].rotate_counterclockwise()
        elif action == 6:
            self.player[player].hold()
            self.on_grounded[player] = False
            self.struggled[player] = False
    
    def __del__(self):
        pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "solo":
        game = Game(n_agent=1, window_size=(800, 600), block_size=30, drop_delay=1000, das=200, arr=50, fps=60)
        game.play()
    elif sys.argv[1] == "multi":
        game = Game(n_agent=2, window_size=(1600, 600), block_size=30, drop_delay=1000, das=200, arr=50, fps=60)
        game.play()
    
