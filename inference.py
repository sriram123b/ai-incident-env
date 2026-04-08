import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-agent")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy")

client = OpenAI(
    base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=HF_TOKEN
)

TASK_NAME = "incident_response"
BENCHMARK = "incident_env"

def log_start():
    print(f"[START] task={TASK_NAME} env={BENCHMARK} model={MODEL_NAME}", flush=True)

def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True
    )

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True
    )

def main():
    rewards = []
    steps = 0
    success = False
    score = 0.0

    log_start()

    try:
        # RESET
        res = requests.post(f"{API_BASE_URL}/reset")
        obs = res.json()["observation"]

        actions = []

        # Generate actions using OpenAI
        for _ in range(2):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are an incident response agent. Choose either investigate or resolve."},
                        {"role": "user", "content": str(obs)}
                    ],
                    max_tokens=10,
                    temperature=0
                )

                act = response.choices[0].message.content.strip().lower()

                if act not in ["investigate", "resolve"]:
                    act = "investigate"

            except Exception:
                act = "investigate"

            actions.append(act)

        # EXECUTE ACTIONS
        for i, action in enumerate(actions, start=1):
            res = requests.post(f"{API_BASE_URL}/step", json={"action": action})
            data = res.json()

            reward = data.get("reward", 0.0)
            done = data.get("done", False)

            rewards.append(reward)
            steps = i

            log_step(i, action, reward, done)

            # update observation
            obs = data.get("observation", obs)

            if done:
                break

        # FINAL STATE
        state = requests.get(f"{API_BASE_URL}/state").json()
        score = state["evaluation"][0]["score"]

        success = score >= 1.0

    except Exception as e:
        log_step(steps, "error", 0.0, True, str(e))
        success = False

    finally:
        log_end(success, steps, score, rewards)

if __name__ == "__main__":
    main()