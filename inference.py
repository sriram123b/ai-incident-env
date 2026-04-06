import os
from env import Env

API_BASE_URL = os.getenv("API_BASE_URL", "local")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline")

def run_task(task_name):
    env = Env()
    obs = env.reset()

    print(f"[START] task={task_name} env=incident_env model={MODEL_NAME}")

    rewards = []
    steps = 0
    done = False

    try:
        while not done and steps < 5:
            steps += 1

            if obs["alert_level"] > 0:
                action = "resolve"
            else:
                action = "investigate"

            result = env.step(action)

            obs = result["state"]
            reward = result["reward"]
            done = result["done"]

            rewards.append(reward)

            print(
                f"[STEP] step={steps} action={action} "
                f"reward={reward:.2f} done={str(done).lower()} error=null"
            )

        score = 1.0 if done else 0.0
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])

        print(
            f"[END] success={str(done).lower()} steps={steps} "
            f"score={score:.2f} rewards={rewards_str}"
        )

    except Exception as e:
        print(
            f"[END] success=false steps={steps} score=0.00 rewards={','.join([f'{r:.2f}' for r in rewards])}"
        )

if __name__ == "__main__":
    for task in ["easy", "medium", "hard"]:
        run_task(task)