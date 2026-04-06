from fastapi import FastAPI
from env import Env

app = FastAPI()
env = Env()

@app.get("/")
def root():
    return {"message": "Environment is running"}

@app.post("/reset")
def reset():
    state = env.reset()
    return {"state": state}

@app.post("/step")
def step(action: dict):
    result = env.step(action["action"])
    return result

from fastapi.responses import HTMLResponse

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
        <head>
            <title>Incident Env UI</title>
        </head>
        <body style="font-family: Arial; text-align:center; margin-top:50px;">
            <h1>🚨 Incident Environment</h1>

            <button onclick="reset()">Reset</button>
            <button onclick="step('investigate')">Investigate</button>
            <button onclick="step('resolve')">Resolve</button>

            <pre id="output"></pre>

            <script>
                async function reset() {
                    let res = await fetch('/reset', {method:'POST'});
                    let data = await res.json();
                    document.getElementById('output').innerText = JSON.stringify(data, null, 2);
                }

                async function step(action) {
                    let res = await fetch('/step', {
                        method:'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({action: action})
                    });
                    let data = await res.json();
                    document.getElementById('output').innerText = JSON.stringify(data, null, 2);
                }
            </script>
        </body>
    </html>
    """