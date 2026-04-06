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



@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
        <head>
            <title>Incident Env UI</title>
        </head>
        <body style="font-family: Arial; text-align:center; margin-top:40px; background:#f5f7fa;">
            
            <h1 style="color:#333;">🚨 Incident Environment Dashboard</h1>

            <div style="margin:20px;">
                <button onclick="reset()" style="padding:10px 20px; margin:5px;">Reset</button>
                <button onclick="step('investigate')" style="padding:10px 20px; margin:5px;">Investigate</button>
                <button onclick="step('resolve')" style="padding:10px 20px; margin:5px;">Resolve</button>
            </div>

            <h3>System State</h3>
            <pre id="output" style="
                background:white;
                padding:20px;
                display:inline-block;
                text-align:left;
                border-radius:10px;
                box-shadow:0 2px 10px rgba(0,0,0,0.1);
            "></pre>

            <script>
                async function reset() {
                    let res = await fetch('/reset', {method:'POST'});
                    let data = await res.json();
                    update(data);
                }

                async function step(action) {
                    let res = await fetch('/step', {
                        method:'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({action: action})
                    });
                    let data = await res.json();
                    update(data);
                }

                function update(data){
                    document.getElementById('output').innerText = JSON.stringify(data, null, 2);
                }
            </script>
        </body>
    </html>
    """