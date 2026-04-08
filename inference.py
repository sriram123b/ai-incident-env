import requests
import os
import time

# ---------------- CONFIG ----------------

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-agent")

MAX_STEPS = 5

# ---------------- LOG HELPERS ----------------

def log_start():
    print(f"[START] env=incident-response model={MODEL_NAME}", flush=True)

def log_step(step, action, reward, done):
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done}",
        flush=True
    )

def log_end(success, steps, score):
    print(
        f"[END] success={success} steps={steps} score={score:.2f}",
        flush=True
    )

# ---------------- BASELINE POLICY ----------------

def choose_action(step):
    # simple deterministic policy
    if step == 1:
        return "investigate"
    return "resolve"

# ---------------- MAIN ----------------

def main():
    log_start()

    # RESET ENV
    requests.post(f"{BASE_URL}/reset")

    total_reward = 0.0
    steps_taken = 0
    success = False

    for step in range(1, MAX_STEPS + 1):

        action = choose_action(step)

        res = requests.post(
            f"{BASE_URL}/step",
            json={"action": action}
        )

        data = res.json()

        reward = data.get("reward", 0.0)
        done = data.get("done", False)

        total_reward += reward
        steps_taken = step

        log_step(step, action, reward, done)

        if done:
            success = True
            break

        time.sleep(0.2)  # slight delay (safe)

    # Normalize score to 0–1
    score = max(0.0, min(1.0, total_reward))

    log_end(success, steps_taken, score)


if __name__ == "__main__":
    main()