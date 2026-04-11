from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class Observation(BaseModel):
    status: str
    logs: list
    step_count: int
    incident_type: str

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

class Action(BaseModel):
    action: str

# ---------------- INCIDENTS ----------------

INCIDENTS = [
    "User says login not working since morning",
    "Authentication failed multiple times",
    "Server CPU 100% suddenly",
    "uhh system not working pls help",
    "Database connection timeout error",
    "Server down!!! urgent",
]

# ---------------- STATE ----------------

state = {
    "status": "idle",
    "logs": [],
    "step_count": 0,
    "incident_type": "none",
    "history": [],
    "resolved": False
}

# ---------------- ROOT ----------------

@app.get("/")
def root():
    return {"message": "Incident Environment Running"}

# ---------------- RESET ----------------

@app.post("/reset")
def reset():
    global state

    incident = random.choice(INCIDENTS)

    state = {
        "status": "reset",
        "logs": [f"New incident: {incident}"],
        "step_count": 0,
        "incident_type": incident,
        "history": [],
        "resolved": False
    }

    return {"observation": state}

# ---------------- STEP ----------------

@app.post("/step")
def step(action: Action):
    global state

    state["step_count"] += 1
    reward = 0

    # Ensure keys exist
    if "history" not in state:
        state["history"] = []
    if "resolved" not in state:
        state["resolved"] = False

    state["history"].append(action.action)

    if action.action == "investigate":
        state["status"] = "investigating"
        state["logs"].append(f"Investigating {state['incident_type']}")
        reward += 0.2

    elif action.action == "resolve":
        if "investigate" not in state["history"]:
            state["logs"].append("Resolve failed: investigate first")
            reward -= 0.3
        else:
            state["status"] = "resolved"
            state["logs"].append("Resolved successfully")
            state["resolved"] = True
            reward += 0.6

    else:
        state["logs"].append(f"Unknown action: {action.action}")
        reward -= 0.2

    # Penalties
    if len(state["history"]) >= 2 and state["history"][-1] == state["history"][-2]:
        reward -= 0.2

    if state["step_count"] > 5:
        reward -= 0.3

    done = state["status"] == "resolved"

    return {
        "observation": state,
        "reward": reward,
        "done": done,
        "info": {}
    }

# ---------------- GRADER ----------------

def evaluate_tasks(state):
    results = []

    results.append({
        "task": "easy_resolution",
        "score": 1.0 if state.get("resolved") else 0.0
    })

    if state.get("resolved"):
        if state["step_count"] <= 3:
            score = 1.0
        elif state["step_count"] <= 5:
            score = 0.5
        else:
            score = 0.2
    else:
        score = 0.0

    results.append({
        "task": "efficient_resolution",
        "score": score
    })

    results.append({
        "task": "correct_sequence",
        "score": 1.0 if (
            "investigate" in state.get("history", []) and
            state.get("resolved")
        ) else 0.0
    })

    return results

# ---------------- STATE ----------------

@app.get("/state")
def get_state():
    return {
        "observation": state,
        "evaluation": evaluate_tasks(state)
    }
# ---------------- AUTOPLAY ----------------

@app.post("/autoplay")
def autoplay():
    global state

    reset()

    trajectory = []
    rewards = []

    actions = ["investigate", "resolve"]

    for step_id, action in enumerate(actions, start=1):
        result = step(Action(action=action))

        trajectory.append({
            "step": step_id,
            "action": action,
            "reward": result["reward"],
            "done": result["done"]
        })

        rewards.append(result["reward"])

        if result["done"]:
            break

    return {
        "trajectory": trajectory,
        "final_state": state,
        "evaluation": evaluate_tasks(state),
        "total_reward": sum(rewards)
    }

# ---------------- UI ----------------

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
    <head>
        <title>Incident Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #1f2937, #111827);
                color: white;
                text-align: center;
                padding: 30px;
            }

            h1 {
                margin-bottom: 10px;
            }

            .card {
                background: #1f2937;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                display: inline-block;
                min-width: 400px;
            }

            button {
                padding: 12px 18px;
                margin: 10px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
                font-size: 15px;
                transition: 0.2s;
            }

            button:hover {
                transform: scale(1.05);
            }

            .reset { background: #f59e0b; color: black; }
            .investigate { background: #3b82f6; }
            .resolve { background: #10b981; }

            .status {
                margin-top: 15px;
                font-size: 18px;
            }

            pre {
                text-align: left;
                background: #111827;
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
                max-height: 300px;
                overflow-y: auto;
            }

            .logs {
                text-align: left;
                margin-top: 15px;
            }

        </style>
    </head>

    <body>

        <h1>🚨 AI Incident Response Dashboard</h1>
        <p>Simulate investigation & resolution workflow</p>

        <div class="card">

            <div>
                <button class="reset" onclick="resetEnv()">Reset</button>
                <button class="investigate" onclick="sendAction('investigate')">Investigate</button>
                <button class="resolve" onclick="sendAction('resolve')">Resolve</button>
            </div>

            <div class="status" id="status">Status: idle</div>
            <div id="incident">Incident: none</div>
            <div id="steps">Steps: 0</div>

            <div class="logs">
                <h3>Logs</h3>
                <pre id="logs">No logs yet</pre>
            </div>

        </div>

        <script>
            async function resetEnv() {
                let res = await fetch('/reset', {method:'POST'});
                let data = await res.json();
                update(data.observation);
            }

            async function sendAction(action) {
                let res = await fetch('/step', {
                    method:'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({action: action})
                });
                let data = await res.json();
                update(data.observation);
            }

            function update(data){
                document.getElementById('status').innerText = "Status: " + data.status;
                document.getElementById('incident').innerText = "Incident: " + data.incident_type;
                document.getElementById('steps').innerText = "Steps: " + data.step_count;
                document.getElementById('logs').innerText = data.logs.join("\\n");
            }
        </script>

    </body>
    </html>
    """
