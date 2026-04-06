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