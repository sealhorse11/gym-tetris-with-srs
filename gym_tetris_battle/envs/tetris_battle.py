import gym
from gym import spaces
import pygame
import numpy as np
import ctypes
import ctypes.util
import sys
from ...tetris_game import *

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

        self.reset()

    def _get_obs(self, player=0):
        return self.game.get_obs(player)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.game = Game()

        observation = self._get_obs()

        if self.render_mode == "human":
            self._render_frame()
        
        return observation
        
    def step(self, action):
        self.game.step(action)

        observation = self._get_obs()

        if self.render_mode == "human":
            self._render_frame()

        return observation, self.game.get_reward(), self.game.done, {}

            
