import pygame
import ctypes
import ctypes.util
import sys

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
class Game(object):
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
    
    def __del__(self):
        lib.Game_delete(self.obj)


def control_lock(is_on_ground, on_grounded, struggled, on_grounded_time, struggled_time) -> (bool, bool, int, int, bool):
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
    


def draw_window(window, game, top_left_x, top_left_y, block_size):    
    # Draw grid
    line_width = 2
    for i in range(0, 11):
        pygame.draw.line(window, GRID_COLOR, (top_left_x + i * block_size, top_left_y), (top_left_x + i * block_size, top_left_y + 20 * block_size), line_width)
    
    for i in range(0, 21):
        pygame.draw.line(window, GRID_COLOR, (top_left_x, top_left_y + i * block_size), (top_left_x + 10 * block_size, top_left_y + i * block_size), line_width)
    
    # Draw blocks
    board = game.get_board()
    for i in range(200):
        if board[i] != -1:
            pygame.draw.rect(window, COLORS[board[i]], (top_left_x + (i % 10) * block_size, top_left_y + (i // 10) * block_size, block_size, block_size))

    # Draw next pieces
    next_pieces = game.get_next_pieces_top_five()
    for i, target_piece in enumerate(next_pieces):
        for j in range(len(SHAPES[target_piece])):
            for k in range(len(SHAPES[target_piece][j])):
                if SHAPES[target_piece][j][k] == 1:
                    pygame.draw.rect(window, COLORS[target_piece], (top_left_x + (k + 11) * block_size, top_left_y + (3 * i + j + 1) * block_size, block_size, block_size))
    
    # Draw held piece
    held_piece = game.get_held_piece()
    if held_piece != -1:
        for i in range(len(SHAPES[held_piece])):
            for j in range(len(SHAPES[held_piece][i])):
                if SHAPES[held_piece][i][j] == 1:
                    pygame.draw.rect(window, COLORS[held_piece], (top_left_x + (j - 5) * block_size, top_left_y + (i + 3) * block_size, block_size, block_size))
    
    # Draw gauge
    gauge = game.get_sum_of_gauge()
    if gauge > 0:
        pygame.draw.line(window, (255, 100, 100), (top_left_x + 10 * block_size, top_left_y + 20 * block_size), (top_left_x + 10 * block_size, top_left_y + 20 * block_size - gauge * block_size), 5)

def solo_mode():
    window_width = 800
    window_height = 600
    block_size = 30
    play_width = block_size * 10
    play_height = block_size * 20

    window = pygame.display.set_mode((window_width, window_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Tetris")

    top_left_x = (window_width - play_width) // 2
    top_left_y = (window_height - play_height) // 2

    clock = pygame.time.Clock()
    game = Game()
    running = True

    DROP_BLOCK_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(DROP_BLOCK_EVENT, 1000)

    on_grounded = False
    on_grounded_time = 0
    struggled_time = 0
    struggled = False

    delayed_auto_shift = 200
    move_delay = 50
    fps = 30
    left_pressed_time = -1
    right_pressed_time = -1
    down_pressed = False
    last_moved_time = -1

    while running:
        if(game.is_game_over()):
            running = False
            continue
        strgguled = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if on_grounded:
                    struggled = True
                
                if event.key == pygame.K_LEFT:
                    left_pressed_time = pygame.time.get_ticks()
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    right_pressed_time = pygame.time.get_ticks()
                    game.move_right()
                if event.key == pygame.K_DOWN:
                    down_pressed = True
                    game.soft_drop()
                if event.key == pygame.K_SPACE:
                    game.hard_drop()
                if event.key == pygame.K_UP or event.key == pygame.K_x:
                    game.rotate_clockwise()
                if event.key == pygame.K_z:
                    game.rotate_counterclockwise()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_c:
                    game.hold()
                    on_grounded = False
                    struggled = False
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left_pressed_time = -1
                    last_moved_time = -1
                if event.key == pygame.K_RIGHT:
                    right_pressed_time = -1
                    last_moved_time = -1
                if event.key == pygame.K_DOWN:
                    down_pressed = False
                    last_moved_time = -1
            
            if event.type == DROP_BLOCK_EVENT:
                game.soft_drop()

        if left_pressed_time != -1 and pygame.time.get_ticks() - left_pressed_time >= delayed_auto_shift:
            if last_moved_time == -1:
                last_moved_time = pygame.time.get_ticks()
            
            if last_moved_time != -1 and pygame.time.get_ticks() - last_moved_time >= move_delay:
                game.move_left()
                last_moved_time = pygame.time.get_ticks()
        
        if right_pressed_time != -1 and pygame.time.get_ticks() - right_pressed_time >= delayed_auto_shift:
            if last_moved_time == -1:
                last_moved_time = pygame.time.get_ticks()
            
            if last_moved_time != -1 and pygame.time.get_ticks() - last_moved_time >= move_delay:
                game.move_right()
                last_moved_time = pygame.time.get_ticks()
        
        if down_pressed:
            if last_moved_time == -1:
                last_moved_time = pygame.time.get_ticks()
            
            if last_moved_time != -1 and pygame.time.get_ticks() - last_moved_time >= move_delay:
                game.soft_drop()
                last_moved_time = pygame.time.get_ticks()

        on_grounded, struggled, on_grounded_time, struggled_time, is_to_lock = \
            control_lock(game.is_on_ground(), on_grounded, struggled, on_grounded_time, struggled_time)

        if is_to_lock:
            game.lock()
        
        # Draw game
        window.fill(BACKGROUND)
        draw_window(window, game, top_left_x, top_left_y, block_size)
        pygame.display.flip()
        
        # Limit frame rate
        clock.tick(fps)


def multi_mode_debug():
    window_width = 1600
    window_height = 600
    block_size = 30
    play_width = block_size * 10
    play_height = block_size * 20

    window = pygame.display.set_mode((window_width, window_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Tetris")

    top_left_x = ((window_width // 2 - play_width) // 2, window_width // 2 + (window_width // 2 - play_width) // 2)
    top_left_y = (window_height - play_height) // 2

    clock = pygame.time.Clock()
    game = [Game(), Game()]

    game[0].set_opponent(game[1])
    game[1].set_opponent(game[0])

    running = True

    DROP_BLOCK_EVENT = (pygame.USEREVENT + 1, pygame.USEREVENT + 2)

    pygame.time.set_timer(DROP_BLOCK_EVENT[0], 1000)
    pygame.time.set_timer(DROP_BLOCK_EVENT[1], 1000)

    on_grounded = [False, False]
    on_grounded_time = [0, 0]
    struggled_time = [0, 0]
    struggled = [False, False]

    delayed_auto_shift = 200
    move_delay = 50
    fps = 60
    left_pressed_time = -1
    right_pressed_time = -1
    down_pressed = False
    last_moved_time = -1

    while running:
        if game[0].is_game_over() or game[1].is_game_over():
            running = False
            continue
        strgguled = [False, False]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if on_grounded:
                    struggled[0] = True
                
                if event.key == pygame.K_LEFT:
                    left_pressed_time = pygame.time.get_ticks()
                    game[0].move_left()
                if event.key == pygame.K_RIGHT:
                    right_pressed_time = pygame.time.get_ticks()
                    game[0].move_right()
                if event.key == pygame.K_DOWN:
                    down_pressed = True
                    game[0].soft_drop()
                if event.key == pygame.K_SPACE:
                    game[0].hard_drop()
                if event.key == pygame.K_UP or event.key == pygame.K_x:
                    game[0].rotate_clockwise()
                if event.key == pygame.K_z:
                    game[0].rotate_counterclockwise()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_c:
                    game[0].hold()
                    on_grounded[0] = False
                    struggled[0] = False
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left_pressed_time = -1
                    last_moved_time = -1
                if event.key == pygame.K_RIGHT:
                    right_pressed_time = -1
                    last_moved_time = -1
                if event.key == pygame.K_DOWN:
                    down_pressed = False
                    last_moved_time = -1
            
            if event.type == DROP_BLOCK_EVENT[0]:
                game[0].soft_drop()
            if event.type == DROP_BLOCK_EVENT[1]:
                game[1].soft_drop()
        

        # Deal with auto shift
        if left_pressed_time != -1 and pygame.time.get_ticks() - left_pressed_time >= delayed_auto_shift:
            if last_moved_time == -1:
                last_moved_time = pygame.time.get_ticks()
            
            if last_moved_time != -1 and pygame.time.get_ticks() - last_moved_time >= move_delay:
                game[0].move_left()
                last_moved_time = pygame.time.get_ticks()
        
        if right_pressed_time != -1 and pygame.time.get_ticks() - right_pressed_time >= delayed_auto_shift:
            if last_moved_time == -1:
                last_moved_time = pygame.time.get_ticks()
            
            if last_moved_time != -1 and pygame.time.get_ticks() - last_moved_time >= move_delay:
                game[0].move_right()
                last_moved_time = pygame.time.get_ticks()
        
        if down_pressed:
            if last_moved_time == -1:
                last_moved_time = pygame.time.get_ticks()
            
            if last_moved_time != -1 and pygame.time.get_ticks() - last_moved_time >= move_delay:
                game[0].soft_drop()
                last_moved_time = pygame.time.get_ticks()


        # Deal with lock
        on_grounded[0], struggled[0], on_grounded_time[0], struggled_time[0], is_to_lock = \
            control_lock(game[0].is_on_ground(), on_grounded[0], struggled[0], on_grounded_time[0], struggled_time[0])
        
        if is_to_lock:
            game[0].lock()

        on_grounded[1], struggled[1], on_grounded_time[1], struggled_time[1], is_to_lock = \
            control_lock(game[1].is_on_ground(), on_grounded[1], struggled[1], on_grounded_time[1], struggled_time[1])
        
        if is_to_lock:
            game[1].lock()
        

        # Draw window
        window.fill(BACKGROUND)
        draw_window(window, game[0], top_left_x[0], top_left_y, block_size)
        draw_window(window, game[1], top_left_x[1], top_left_y, block_size)
        pygame.display.flip()
        

        # Limit frame rate
        clock.tick(fps)


if __name__ == "__main__":
    # Initialize game
    pygame.init()

    if len(sys.argv) == 1 or sys.argv[1] == "solo":
        solo_mode()
    elif sys.argv[1] == "multi_debug":
        multi_mode_debug()
    
    pygame.quit()

    
