import gymnasium as gym
import cv2
from tetris_gymnasium.envs.tetris import Tetris

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env


def train(save_model = True):
    # Parallel environments
    training_env = make_vec_env("tetris_gymnasium/Tetris", n_envs=8, env_kwargs={"render_mode": None})

    model = PPO("MultiInputPolicy", training_env, verbose=1)
    model.learn(total_timesteps=50000)
    if save_model:
        model.save("ppo_tetris")

def test(load_model="ppo_tetris"):
    model = PPO.load(load_model)

    test_env = make_vec_env("tetris_gymnasium/Tetris", n_envs=1, env_kwargs={"render_mode": "human"})
    obs = test_env.reset()    

    terminated = False

    total_score = 0
    test_env.render()
    key = cv2.waitKey(500) #Wait at first to see window

    while not terminated:
        test_env.render()
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = test_env.step(action)

        terminated = dones[0] #If the game is over or not
        
        key = cv2.waitKey(100) # timeout to see the movement
        total_score += rewards[0]

    print("Game Over!")
    print(f"Final Score: {total_score}")  


#train()
test()