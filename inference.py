import os
import requests
try:
    from openai import OpenAI
    USE_OPENAI = True
except ImportError:
    USE_OPENAI = False 

if USE_OPENAI:
    client = OpenAI(
        base_url=os.environ.get("API_BASE_URL"),
        api_key=os.environ.get("API_KEY")
    )

# IMPORTANT: use injected env vars
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.environ.get("API_KEY", "dummy")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

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


from openai import OpenAI

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

def call_llm(obs):
    # TRY OpenAI client (if available)
    if USE_OPENAI:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Choose: investigate or resolve"},
                    {"role": "user", "content": str(obs)}
                ],
                max_tokens=5,
            )

            act = response.choices[0].message.content.strip().lower()

            if act in ["investigate", "resolve"]:
                return act

        except Exception:
            pass

    # 🔥 FALLBACK → DIRECT PROXY CALL (NO CRASH)
    try:
        import requests

        headers = {
            "Authorization": f"Bearer {os.environ.get('API_KEY')}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Choose: investigate or resolve"},
                {"role": "user", "content": str(obs)},
            ],
            "max_tokens": 5,
        }

        res = requests.post(
            f"{os.environ.get('API_BASE_URL')}/chat/completions",
            json=payload,
            headers=headers,
            timeout=5
        )

        data = res.json()
        text = data["choices"][0]["message"]["content"].strip().lower()

        if text in ["investigate", "resolve"]:
            return text

    except Exception:
        pass

    # FINAL fallback (never crash)
    return "investigate"


def main():
    rewards = []
    steps = 0
    success = False
    score = 0.0

    log_start()

    try:
        # RESET
        res = requests.post(f"{API_BASE_URL}/reset")
        obs = res.json().get("observation", {})

        # ACTION LOOP
        for i in range(1, 4):
            action = call_llm(obs)

            res = requests.post(f"{API_BASE_URL}/step", json={"action": action})
            data = res.json()

            reward = data.get("reward", 0.0)
            done = data.get("done", False)

            rewards.append(reward)
            steps = i

            log_step(i, action, reward, done)

            obs = data.get("observation", obs)

            if done:
                break

        # FINAL STATE
        state = requests.get(f"{API_BASE_URL}/state").json()

        if "evaluation" in state and len(state["evaluation"]) > 0:
            score = state["evaluation"][0].get("score", 0.0)

        success = score >= 1.0

    except Exception as e:
        log_step(steps, "error", 0.0, True, str(e))
        success = False

    finally:
        log_end(success, steps, score, rewards)


if __name__ == "__main__":
    main()
