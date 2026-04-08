from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

class Action(BaseModel):
    action: str

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

# ---------------- STATE ----------------

class EnvState:
    def __init__(self):
        self.status = "idle"
        self.logs = []
        self.step_count = 0
        self.incident_type = "none"

state = EnvState()

# ---------------- GRADER ----------------

def evaluate_tasks():
    return [
        {
            "task": "easy_resolution",
            "score": 1.0 if state.status == "resolved" else 0.0
        },
        {
            "task": "efficient_resolution",
            "score": 1.0 if state.step_count <= 3 else 0.5 if state.step_count <= 5 else 0.0
        },
        {
            "task": "correct_sequence",
            "score": 1.0 if (
                any("Investigating" in log for log in state.logs) and
                state.status == "resolved"
            ) else 0.0
        }
    ]

# ---------------- CORE API ----------------

@app.get("/")
def root():
    return {"message": "Incident Environment Running"}

# RESET
@app.post("/reset")
def reset():
    global state

    incident = random.choice([
        "server_down",
        "security_breach",
        "database_failure"
    ])

    state = EnvState()
    state.status = "reset"
    state.logs = [f"New incident: {incident}"]
    state.incident_type = incident

    return {
        "observation": Observation(
            status=state.status,
            logs=state.logs,
            step_count=state.step_count,
            incident_type=state.incident_type
        )
    }

# STEP
@app.post("/step", response_model=StepResult)
def step(action: Action):
    global state

    state.step_count += 1
    reward = 0.0
    done = False

    if action.action == "investigate":
        state.status = "investigating"
        state.logs.append(f"Investigating {state.incident_type}")
        reward = 0.3

    elif action.action == "resolve":
        if state.status != "investigating":
            state.logs.append("Resolve failed: investigate first")
            reward = -0.2
        else:
            state.status = "resolved"
            state.logs.append("Incident resolved successfully")
            reward = 0.7
            done = True

    else:
        state.logs.append(f"Unknown action: {action.action}")
        reward = -0.1

    return StepResult(
        observation=Observation(
            status=state.status,
            logs=state.logs,
            step_count=state.step_count,
            incident_type=state.incident_type
        ),
        reward=reward,
        done=done,
        info={"tasks": evaluate_tasks()}
    )

# STATE
@app.get("/state")
def get_state():
    return {
        "state": {
            "status": state.status,
            "logs": state.logs,
            "step_count": state.step_count,
            "incident_type": state.incident_type
        },
        "evaluation": evaluate_tasks()
    }


##----------UI------------------

from fastapi.responses import HTMLResponse

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
    <body style="font-family:Arial;text-align:center;margin-top:40px;">
        <h2>Incident Environment</h2>

        <button onclick="act('investigate')">Investigate</button>
        <button onclick="act('resolve')">Resolve</button>
        <button onclick="reset()">Reset</button>

        <pre id="out"></pre>

        <script>
        async function reset(){
            await fetch('/reset',{method:'POST'});
            update();
        }

        async function act(a){
            await fetch('/step',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({action:a})
            });
            update();
        }

        async function update(){
            let r = await fetch('/state');
            let d = await r.json();
            document.getElementById('out').innerText =
                JSON.stringify(d,null,2);
        }
        </script>
    </body>
    </html>
    """