import pygame
import ctypes
import sys
import numpy as np
from tetris_constants_for_render import *
from tetris_logic_wrapping import GameLogic

class TetrisGame():
    def __init__(self, n_agent=1, window_size=(800, 600), block_size=30, arr=50, das=100, sdf=50, lock_delay=500, drop_delay=1000, fps=60):
        self.n_agent = n_agent
        self.window_size = window_size
        self.block_size = block_size
        self.play_width = block_size * 10
        self.play_height = block_size * 20
        self.drop_delay = drop_delay
        self.lock_delay = lock_delay
        self.das = das
        self.arr = arr
        self.sdf = sdf
        self.fps = fps

        self.top_left_x = [(window_size[0] // n_agent * i) + (window_size[0] // n_agent - self.play_width) // 2 for i in range(n_agent)]
        self.top_left_y = (window_size[1] - self.play_height) // 2

        pygame.init()
        self.font = pygame.font.SysFont("Consolas", 50)
        self.mini_font = pygame.font.SysFont("Consolas", 20)
        self.clock = pygame.time.Clock()
        
        self.start()
    
    def start(self):
        self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Tetris")

        print(pygame.time.get_ticks())
        self.player = [GameLogic(self.das, self.arr, self.sdf, pygame.time.get_ticks(), self.lock_delay, self.drop_delay) for _ in range(self.n_agent)]

        if self.n_agent == 2:
            self.player[0].set_opponent(self.player[1])
            self.player[1].set_opponent(self.player[0])
        
        self.game_over = False
    
    def draw_board_single(self):
        self.draw_board(self.window, self.player[0], self.top_left_x[0], self.top_left_y, self.block_size)
    
    def draw_board(self, window, player: GameLogic, top_left_x, top_left_y, block_size):    
        if window is None:
            window = self.window


        # Draw grid
        line_width = 2
        for i in range(0, 11):
            pygame.draw.line(window, GRID_COLOR, (top_left_x + i * block_size, top_left_y), (top_left_x + i * block_size, top_left_y + 20 * block_size), line_width)
        
        for i in range(0, 21):
            pygame.draw.line(window, GRID_COLOR, (top_left_x, top_left_y + i * block_size), (top_left_x + 10 * block_size, top_left_y + i * block_size), line_width)
        
        # Draw blocks
        board = player.get_board_for_render()
        print(board)
        for i in range(20):
            for j in range(10):
                if board[i, j] != -1:
                    pygame.draw.rect(window, COLORS[board[i, j]], (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size))

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
        try:
            apm = (player.get_sent_attack() / player.get_time()) * 60000
        except ZeroDivisionError:
            apm = 0
        self.window.blit(self.mini_font.render("APM: " + str(round(apm, 3)), True, (255, 255, 255)), (top_left_x + 11 * block_size, top_left_y + 20 * block_size - 2 * block_size))

    def play(self, user=0):
        # not implemented when number of agent != 1
        assert self.n_agent == 1

        # check if key is pressed
        key_pressed = [False for _ in range(3)]
        
        while not self.game_over:
            # Check game over
            for i in range(self.n_agent):
                if self.player[i].is_game_over():
                    self.game_over = True
                    break
            
            # Deal with events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player[user].move_left()
                        key_pressed[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.player[user].move_right()
                        key_pressed[1] = True
                    if event.key == pygame.K_DOWN:
                        self.player[user].soft_drop()
                        key_pressed[2] = True
                    if event.key == pygame.K_SPACE:
                        self.player[user].hard_drop()
                    if event.key == pygame.K_UP or event.key == pygame.K_x:
                        self.player[user].rotate_clockwise()
                    if event.key == pygame.K_z:
                        self.player[user].rotate_counterclockwise()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_c:
                        self.player[user].hold()
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        key_pressed[0] = False
                        self.player[user].off_left()
                    if event.key == pygame.K_RIGHT:
                        key_pressed[1] = False
                        self.player[user].off_right()
                    if event.key == pygame.K_DOWN:
                        key_pressed[2] = False
                        self.player[user].off_soft_drop()
            
            # Deal with moving
            if key_pressed[0]:
                self.player[user].move_left()
            if key_pressed[1]:
                self.player[user].move_right()
            if key_pressed[2]:
                self.player[user].soft_drop()
            
            # Lock
            self.player[user].lock()

            # Draw window
            self.window.fill(BACKGROUND)
            for i in range(self.n_agent):
                self.draw_board(self.window, self.player[i], self.top_left_x[i], self.top_left_y, self.block_size)
            pygame.display.flip()

            # Update time
            self.clock.tick(60)
            curr_ticks = pygame.time.get_ticks()
            for i in range(self.n_agent):
                self.player[i].set_time(curr_ticks)


if __name__ == "__main__":
    if sys.argv[1] == "new":
        game = TetrisGame(n_agent=1, window_size=(800, 600), block_size=30, drop_delay=1000, das=200, arr=50, sdf=200, fps=30)
        game.play()
    elif sys.argv[1] == "multi":
        # game = Game(n_agent=2, window_size=(1600, 600), block_size=30, drop_delay=1000, das=200, arr=50, fps=60)
        # game.play()
        pass
    else:
        # game = Game(n_agent=1, window_size=(800, 600), block_size=30, drop_delay=1000, das=200, arr=50, fps=60)
        # game.play()
        pass
    
