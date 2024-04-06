import gymnasium as gym
import gym_tetris_with_srs

from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_util import make_atari_env

# Parallel environments
model_name = "ppo_tetris_single"

# env = gym.make("tetris_with_srs-v0")
# check_env(env)
# print("Environment is OK")

# env = gym.make("tetris_with_srs-v0")
env = make_atari_env("tetris_with_srs-v0", n_envs=4, seed=0)

model = PPO(
    policy="CnnPolicy",
    env=env,
    verbose=1,
    policy_kwargs={"normalize_images": False, "cnn_kwargs": {"kernel_size": 8}},  # Modify the kernel size here
)
timesteps_interval = 1000000
timesteps = 0

model.learn(total_timesteps=timesteps_interval)
model.save(model_name)
timesteps += timesteps_interval
print(f"Trained and saved for {timesteps} timesteps")

del model # remove to demonstrate saving and loading


model = PPO.load(model_name)

obs, info = env.reset()
while True:
    action, _states = model.predict(obs, deterministic=True)
    print(action)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()