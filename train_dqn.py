import gymnasium as gym
import numpy as np
import tensorflow as tf
import random
import gym_tetris_with_srs
import os
import datetime
from stable_baselines3.common.env_checker import check_env

env = gym.make("tetris_with_srs-v0")
check_env(env)