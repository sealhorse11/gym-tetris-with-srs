import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pygame
import numpy as np
import ctypes
import ctypes.util

import gym_tetris_with_srs.envs.tetris_battle.tetris_game as TetrisGame

class TetrisBattleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, render_mode=None):
        super().__init__()

        self.observation_space = spaces.Dict(
            {
                "board": spaces.Box(low=-1, high=8, shape=(20, 10), dtype=np.int8),
                "held_piece": spaces.Box(low=-1, high=6, shape=(), dtype=np.int8),
                "next_pieces": spaces.Box(low=0, high=7, shape=(5,), dtype=np.int8),
                "combo": spaces.Box(low=0, high=100, shape=(), dtype=np.int8),
                "back_to_back": spaces.Box(low=0, high=1, shape=(), dtype=np.int8),
                "gauge": spaces.Box(low=0, high=100, shape=(), dtype=np.int8),
                "opponent_board": spaces.Box(low=-1, high=7, shape=(20, 10), dtype=np.int8),
            }
        )

        self.action_space = spaces.Discrete(7)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.game = TetrisGame.Game()
        self.reset()

    def _get_obs(self, player=0):
        return self.game.get_obs(player)
    
    def _get_info(self):
        return self.game.player[0].get
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.game.start()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()
        
        return observation, info
        
    def step(self, action):
        sent_attack = self._get_info()["sent_attack"]

        self.game.step(action)

        observation = self._get_obs()
        info = self._get_info()
        reward = info - sent_attack

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, self.game.game_over, False, info
    
    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        self.game.window.fill(TetrisGame.BACKGROUND)
        self.game.draw_board()
        pygame.display.flip()
    
    def close(self):
        if self.game.window is not None:
            pygame.display.quit()
            pygame.quit()
    