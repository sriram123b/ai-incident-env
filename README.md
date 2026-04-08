---
title: Incident Env
emoji: ⚡
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
short_description: OpenEnv incident response simulation with FastAPI endpoints.
---

# 🚨 Incident Response OpenEnv Environment

## 📌 Overview

This project simulates a **real-world incident response system** used in DevOps/SRE workflows.

Agents interact with the environment to investigate and resolve incidents such as:

- Server failures  
- Security breaches  
- Database outages  

---

## 🎯 Objective

The agent must:
1. Investigate the incident  
2. Take correct actions  
3. Resolve the issue efficiently  

---

## ⚙️ Action Space

| Action | Description |
|--------|------------|
| investigate | Analyze the incident |
| resolve | Attempt to resolve the issue |

---

## 📊 Observation Space

Each step returns:

- `status` → current system state  
- `logs` → history of actions  
- `step_count` → number of steps taken  
- `incident_type` → type of incident  

---

## 🧠 Reward Function

| Action | Reward |
|--------|--------|
| Investigate | +0.3 |
| Resolve correctly | +0.7 |
| Resolve without investigate | -0.2 |
| Invalid action | -0.1 |

---

## 🧪 Tasks & Graders

### 1. Easy — Resolution
✔ Resolve the incident successfully  
Score: 1.0 or 0.0  

### 2. Medium — Efficiency
✔ Solve in fewer steps  
- ≤3 steps → 1.0  
- ≤5 steps → 0.5  
- >5 steps → 0.0  

### 3. Hard — Correct Sequence
✔ Investigate before resolving  

---

## 🔄 API Endpoints

| Endpoint | Method |
|----------|--------|
| `/reset` | POST |
| `/step` | POST |
| `/state` | GET |

---

## 🚀 Setup

```bash
pip install fastapi uvicorn requests
uvicorn app:app --reload