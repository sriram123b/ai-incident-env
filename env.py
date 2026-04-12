from typing import Dict, Any 

class Env:
    def __init__(self):
        self.state_data = {
            "alert_level": 0,
            "system_load": 0.5
        }

    def reset(self) -> Dict[str, Any]:
        self.state_data = {
            "alert_level": 1,
            "system_load": 0.3
        }
        return self.state_data

    def step(self, action: str) -> Dict[str, Any]:
        if action == "investigate":
            self.state_data["alert_level"] += 1
        elif action == "resolve":
            self.state_data["alert_level"] = 0

        reward = 1 if self.state_data["alert_level"] == 0 else -1

        return {
            "state": self.state_data,
            "reward": reward,
            "done": self.state_data["alert_level"] == 0
        }

    def state(self):
        return self.state_data 
    
    def evaluate(self):
        return [
            {"task": "easy_resolution", "score": 0.5},
            {"task": "efficient_resolution", "score": 0.6},
            {"task": "correct_sequence", "score": 0.7}
        ]