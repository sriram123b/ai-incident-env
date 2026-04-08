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

# ---------------- STATE MODEL ----------------
#ENV STATE
class EnvState(BaseModel):
    status: str
    logs: list
    score: int
    step_count: int
    incident_type: str

# Initial state
state = EnvState(
    status="idle",
    logs=[],
    score=0,
    step_count=0,
    incident_type="none"
)

@app.get("/state")
def get_state():
    return {
        "state": state,
        "evaluation": evaluate_tasks(state)
    }

#-----------------GRADER FUNCTION-------------------
def evaluate_tasks(state):
    results = []

    # Task 1: Basic Investigation
    results.append({
        "task": "basic_investigation",
        "passed": state.status == "resolved" and state.score >= 20
    })

    # Task 2: Efficient Resolution
    results.append({
        "task": "efficient_resolution",
        "passed": state.status == "resolved" and state.step_count <= 3
    })

    # Task 3: Correct Sequence
    results.append({
        "task": "correct_sequence",
        "passed": (
            "Investigation started" in state.logs and
            "Incident resolved successfully" in state.logs
        )
    })

    return results
# ---------------- CORE API (OPENENV STYLE) ----------------

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

    state = EnvState(
        status="reset",
        logs=[f"New incident: {incident}"],
        score=0,
        step_count=0,
        incident_type=incident
    )

    return state

# STEP (IMPORTANT FOR HACKATHON)
@app.post("/step")
def step(action: Action):
    global state
    state.step_count += 1

    # INVESTIGATE
    if action.action == "investigate":
        state.status = "investigating"
        state.logs.append(f"Investigating {state.incident_type}")
        state.score += 10

    # RESOLVE (depends on incident)
    elif action.action == "resolve":

        if state.status != "investigating":
            state.logs.append("Resolve failed: investigate first")
            state.score -= 5

        else:
            if state.incident_type == "server_down":
                state.logs.append("Restarted server successfully")
                state.status = "resolved"
                state.score += 20

            elif state.incident_type == "security_breach":
                state.logs.append("Applied security patch")
                state.status = "resolved"
                state.score += 25

            elif state.incident_type == "database_failure":
                state.logs.append("Recovered database")
                state.status = "resolved"
                state.score += 20

    else:
        state.logs.append(f"Unknown action: {action.action}")
        state.score -= 1

    return state




# ---------------- FRONTEND UI ----------------

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
        <head>
            <title>Incident Environment</title>
        </head>

        <body style="font-family: Arial; text-align:center; margin-top:40px; background:#f5f7fa;">

            <h1 style="color:#333;">🚨 Incident Environment Dashboard</h1>

            <div style="margin:20px;">
                <button onclick="sendAction('reset')" style="padding:10px 20px; margin:5px;">Reset</button>
                <button onclick="sendAction('investigate')" style="padding:10px 20px; margin:5px;">Investigate</button>
                <button onclick="sendAction('resolve')" style="padding:10px 20px; margin:5px;">Resolve</button>
            </div>

            <h3>System State</h3>

            <div id="output" style="
    background:white;
    padding:20px;
    display:inline-block;
    text-align:left;
    border-radius:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.1);
    min-width:350px;
    font-size:14px;
"></div>

            <script>
    async function sendAction(action) {

        if(action === "reset"){
            await fetch('/reset', {method:'POST'});
            update();
            return;
        }

        await fetch('/step', {
            method:'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({action: action})
        });

        update();
    }
 
   async function update(){
    let res = await fetch('/state');
    let data = await res.json();

    let state = data.state;
    let evals = data.evaluation;

    let html = `
    <b>Incident:</b> ${state.incident_type} <br>
    <b>Status:</b> ${state.status} <br>
    <b>Score:</b> ${state.score} <br>
    <b>Steps:</b> ${state.step_count} <br><br>

        <b>Logs:</b><br>
        ${state.logs.map(l => "• " + l).join("<br>")}<br><br>

        <b>Evaluation:</b><br>
        ${evals.map(e => 
            (e.passed ? "✅" : "❌") + " " + e.task
        ).join("<br>")}
    `;

    document.getElementById('output').innerHTML = html;
}
</script>

        </body>
    </html>
    """


