import gymnasium as gym
import cv2
from tetris_gymnasium.envs.tetris import Tetris

from stable_baselines3 import PPO #We can try other models
from stable_baselines3.common.env_util import make_vec_env


def train(save_model = True):
    #Training in 8 parallel environments
    training_env = make_vec_env("tetris_gymnasium/Tetris", n_envs=8, env_kwargs={"render_mode": None})

    #training for 50000 steps, probably should be more if we keep this model
    #Used PPO since that's what I know, but probably need some sort of
    #CNN in there to capture the empty spaces in the grid
    #There is an example on the Tetris github but it is quite complex
    model = PPO("MultiInputPolicy", training_env, verbose=1)
    model.learn(total_timesteps=50000)
    if save_model:
        model.save("ppo_tetris")

def test(load_model="ppo_tetris"):
    model = PPO.load(load_model)

    test_env = make_vec_env("tetris_gymnasium/Tetris", n_envs=1, env_kwargs={"render_mode": "human"})
    obs = test_env.reset()   #initial observations (state) 

    terminated = False

    total_score = 0 #Score tracker
    test_env.render()
    key = cv2.waitKey(500) #Wait at first to see window

    while not terminated:
        test_env.render()
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = test_env.step(action)

        terminated = dones[0] #If the game is over or not
        #[0] since it is formatted as if there were multiple parallel environments
        
        key = cv2.waitKey(100) # timeout to see the movement
        total_score += rewards[0]

    print("Game Over!")
    print(f"Final Score: {total_score}")  


#train()
test()