import gymnasium as gym 
from gymnasium import error, spaces, utils
from gymnasium.utils import seeding
import pygame
import numpy as np
import ctypes
import ctypes.util

import gym_tetris_with_srs.envs.tetris_battle.tetris_game as TetrisGame

class TetrisBattleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, render_mode="human"):
        super().__init__()

        self.observation_space = spaces.Box(low=0, high=1, shape=(1, 20, 20), dtype=np.uint8)

        self.action_space = spaces.MultiDiscrete(np.array([2, 4, 10, 2, 6]))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.game = TetrisGame.Game(n_agent=1, window_size=(800, 600), block_size=30)
        self.reset()

    def _get_obs(self, player=0):
        return self.game.get_obs(player)
    
    def _get_info(self):
        return self.game.get_info()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.game.start()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()
        
        return observation, info
        
    def step(self, action):
        sent_attack_before = self._get_info()["sent_attack"]
        height_before = self._get_info()["height"]
        next_piece_before = self._get_info()["next_piece"]

        self.game.step(action)

        observation = self._get_obs()
        info = self._get_info()
        sent_attack_after = info["sent_attack"]
        height_after = info["height"]
        next_piece_after = info["next_piece"]

        pps = info["piece_count"] / (info["time"] + 1) * 1000
        pps_penalty = 0 if pps >= 2 else -1000

        reward = (sent_attack_after - sent_attack_before) * 10000 + pps_penalty

        if next_piece_after != next_piece_before:
            if height_after - height_before <= 1:
                reward += 100
            elif height_after - height_before == 3:
                reward -= 100
            elif height_after - height_before == 4:
                reward -= 500

        is_game_over = self.game.get_game_over()

        if is_game_over:
            reward = -99999999

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, is_game_over, False, info
    
    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        self.game.window.fill(TetrisGame.BACKGROUND)
        self.game.draw_board_single()
        pygame.display.flip()
    
    def close(self):
        if self.game.window is not None:
            pygame.display.quit()
            pygame.quit()
    