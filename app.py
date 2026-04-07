from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STATE ----------------
state = {
    "status": "idle",
    "logs": []
}

# ---------------- BACKEND API ----------------

@app.get("/")
def root():
    return {"message": "Incident Environment Running"}

@app.post("/reset")
def reset():
    state["status"] = "reset"
    state["logs"].append("System reset triggered")
    return state

@app.post("/investigate")
def investigate():
    state["status"] = "investigating"
    state["logs"].append("Investigation started")
    return state

@app.post("/resolve")
def resolve():
    state["status"] = "resolved"
    state["logs"].append("Incident resolved")
    return state

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
                <button onclick="resetEnv()" style="padding:10px 20px; margin:5px;">Reset</button>
                <button onclick="investigate()" style="padding:10px 20px; margin:5px;">Investigate</button>
                <button onclick="resolve()" style="padding:10px 20px; margin:5px;">Resolve</button>
            </div>

            <h3>System State</h3>

            <pre id="output" style="
                background:white;
                padding:20px;
                display:inline-block;
                text-align:left;
                border-radius:10px;
                box-shadow:0 2px 10px rgba(0,0,0,0.1);
                min-width:300px;
            ">Click a button to see output</pre>

            <script>
                async function resetEnv() {
                    let res = await fetch('/reset', {method:'POST'});
                    let data = await res.json();
                    update(data);
                }

                async function investigate() {
                    let res = await fetch('/investigate', {method:'POST'});
                    let data = await res.json();
                    update(data);
                }

                async function resolve() {
                    let res = await fetch('/resolve', {method:'POST'});
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