import cv2
import gymnasium as gym
from tetris_gymnasium.envs.tetris import Tetris

"""
Scoring function = (rows_cleared**2) * self.width
This also serves as the reward function
"""


if __name__ == "__main__":
    total_score = 0
    env = gym.make("tetris_gymnasium/Tetris", render_mode="human")
    env.reset(seed=42)

    terminated = False
    while not terminated:
        env.render()
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        key = cv2.waitKey(100) # timeout to see the movement
        total_score += reward

    print("Game Over!")
    print(f"Final Score: {int(total_score)}")  