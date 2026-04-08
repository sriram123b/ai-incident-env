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
class EnvState(BaseModel):
    status: str
    logs: list
    score: int
    step_count: int

# Initial state
state = EnvState(
    status="idle",
    logs=[],
    score=0,
    step_count=0
)

# ---------------- CORE API (OPENENV STYLE) ----------------

@app.get("/")
def root():
    return {"message": "Incident Environment Running"}

# RESET
@app.post("/reset")
def reset():
    global state
    state = EnvState(
        status="reset",
        logs=["System reset triggered"],
        score=0,
        step_count=0
    )
    return state

# STEP (IMPORTANT FOR HACKATHON)
class Action(BaseModel):
    action: str

@app.post("/step")
def step(action: Action):
    global state

    state.step_count += 1

    # Simple logic
    if action.action == "investigate":
        state.status = "investigating"
        state.logs.append("Investigation started")
        state.score += 10

    elif action.action == "resolve":
        if state.status == "investigating":
            state.status = "resolved"
            state.logs.append("Incident resolved successfully")
            state.score += 20
        else:
            state.logs.append("Resolve failed: investigate first")
            state.score -= 5

    else:
        state.logs.append(f"Unknown action: {action.action}")
        state.score -= 1

    return state

# STATE
@app.get("/state")
def get_state():
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

            <pre id="output" style="
                background:white;
                padding:20px;
                display:inline-block;
                text-align:left;
                border-radius:10px;
                box-shadow:0 2px 10px rgba(0,0,0,0.1);
                min-width:350px;
            ">Click a button to start</pre>

            <script>
                async function sendAction(action) {

                    if(action === "reset"){
                        let res = await fetch('/reset', {method:'POST'});
                        let data = await res.json();
                        update(data);
                        return;
                    }

                    let res = await fetch('/step', {
                        method:'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({action: action})
                    });

                    let data = await res.json();
                    update(data);
                }

                function update(data){
                    document.getElementById('output').innerText =
                        JSON.stringify(data, null, 2);
                }
            </script>

        </body>
    </html>
    """