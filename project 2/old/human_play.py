import sys
import cv2
import gymnasium as gym
from tetris_gymnasium.envs import Tetris


"""
Scoring function = (rows_cleared**2) * self.width
This also serves as the reward function
"""



if __name__ == "__main__":
    env = gym.make("tetris_gymnasium/Tetris", render_mode="human")
    env.reset(seed=42)


    total_score = 0
    terminated = False

    while not terminated:
        env.render()

        action = None
        while action is None:
            key = cv2.waitKey(1)

            if key == ord("a"):
                action = env.unwrapped.actions.move_left
            elif key == ord("d"):
                action = env.unwrapped.actions.move_right
            elif key == ord("s"):
                action = env.unwrapped.actions.move_down
            elif key == ord("w"):
                action = env.unwrapped.actions.rotate_counterclockwise
            elif key == ord("e"):
                action = env.unwrapped.actions.rotate_clockwise
            elif key == ord(" "):
                action = env.unwrapped.actions.hard_drop
            elif key == ord("q"):
                action = env.unwrapped.actions.swap
            elif key == ord("r"):
                env.reset(seed=42)
                total_score = 0 # Reset score on manual restart
                break

            if cv2.getWindowProperty(env.unwrapped.window_name, cv2.WND_PROP_VISIBLE) == 0:
                sys.exit()

        # Perform the action
        observation, reward, terminated, truncated, info = env.step(action)
        
        # 2. Accumulate the reward into your score variable
        total_score += reward

    # 3. Print the final result
    print("Game Over!")
    print(f"Final Score: {int(total_score)}")  