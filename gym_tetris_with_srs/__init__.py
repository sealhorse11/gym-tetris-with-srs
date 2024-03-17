from gym.envs.registration import register

register(
    id='tetris_with_srs-v0',
    entry_point='gym_tetris_with_srs.envs:TetrisWithSrsEnv',
)