import gymnasium as gym
import numpy as np
import random
import gym_tetris_with_srs
import os
import datetime
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN

env = gym.make("tetris_with_srs-v0")
check_env(env)
print("Environment is OK")

model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1000000000, log_interval=4)
model.save("dqn_tetris_single")
print("model saved")

del model # remove to demonstrate saving and loading

model = DQN.load("dqn_tetris_single")

obs, info = env.reset()
while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()