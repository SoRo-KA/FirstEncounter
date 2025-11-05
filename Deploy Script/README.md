# 🧠 Mirokai Use Case Deployment Script

## 📖 Overview

This tool automates the deployment of **Prompts** and **Custom Skills** onto a **Mirokai robot**. 

It allows you to:

- 🧹 Remove all existing skills from the robot  
- 📦 Upload and enable new **Custom Skills** from a specific Use Case  
- 💬 Update the robot’s **Prompt** (LLM system prompt) using the official API  
- 🧪 Run in **simulation mode** for dry-runs (no robot required)  

It’s designed for developers or integrators working on **custom conversational behaviors** for Mirokai.

---

## ⚙️ Project Structure

The project expects the following folder structure:

```
root/
│
├── Use cases/
│   ├── [Use Case Name]/
│   │   ├── Prompt/
│   │   │   ├── [PromptName].txt
│   │   │   └── ...
│   │   ├── Skills/
│   │   │   ├── [SkillName].py
│   │   │   └── ...
│   │   └── Other/
│
└── Deploy Script/
    └── deploy_use_case.py   ← This script
```

Each **Use Case** contains:
- `Prompt/` → one or more `.txt` files containing LLM system prompts  
- `Skills/` → one or more `.py` files defining Custom Skills using `@skill()` decorators  

---

## 🚀 Features

| Feature | Description |
|----------|-------------|
| 🧹 **Skill cleanup** | Automatically removes all existing skills from the robot before deploying new ones |
| ⚡ **Skill upload** | Uploads and enables all `.py` skill files from the selected Use Case |
| 💬 **Prompt update** | Updates the robot’s system prompt using `robot.update_prompt()` |
| 🧪 **Simulation mode** | Allows testing the full process without connecting to a real robot |
| 🔐 **Safe REST interactions** | Uses official `pymirokai` API methods instead of direct REST endpoints |
| 📋 **Detailed logging** | Clean, color-coded console output with clear warnings and errors |

---

## 🖥️ Requirements

### Dependencies
- Python **3.10+**
- Installed in the robot’s environment or a virtualenv 

### Permissions
You need an **Admin API key** on the robot for prompt updates:
```bash
--api-key admin
```

---

## 💡 Usage

### 🧑‍💻 Basic Example
Deploy a Use Case called **"Base Demo"** to a robot running locally:

```bash
python "Deploy Script/deploy_use_case.py" --ip localhost --api-key admin --use-case "Base Demo"
```

### 🧪 Simulation Mode
Run a **dry test** without any real robot connection:
```bash
python "Deploy Script/deploy_use_case.py" --simulate --use-case "Base Demo"
```

### 🧱 Parameters

| Argument | Description | Example |
|-----------|-------------|----------|
| `--ip` | IP address of the target robot | `192.168.1.42` |
| `--api-key` | Robot API key (must be valid) | `admin` |
| `--use-case` | Name of the use case folder in `/Use cases/` | `"Base Demo"` |
| `--simulate` | Run in offline mode with fake API | (flag only) |

---

## 🧩 How It Works

### 1. **Connection**
The script connects to the robot using:
```python
async with connect(api_key, ip) as robot:
```
and establishes a valid WebSocket and REST session.

---

### 2. **Skill Cleanup**
Lists all currently registered skills and removes them:
```python
skills = await robot.rest_api.list_skill_files()
await robot.rest_api.remove_skill_file(skill_name)
```

---

### 3. **Skill Deployment**
Uploads all `.py` files found in the Use Case’s `Skills/` folder and enables them:
```python
await robot.rest_api.upload_skill_file("Skills/greet_user.py")
await robot.rest_api.enable_skill_file("greet_user", True)
```

---

### 4. **Prompt Update**
Reads the `.txt` prompt file and updates the robot’s current system prompt:
```python
mission = robot.update_prompt(prompt_text)
await mission.completed()
```

---

### 5. **Completion**
Logs a clear success message:
```
🎉 Deployment of 'Base Demo' completed successfully!
```

---

## 📋 Example Output

```
[10:05:31] [INFO] (MainThread) === 🚀 Deploying Use Case: Base Demo ===
[10:05:32] [INFO] (MainThread) Connected to robot ✅
[10:05:33] [INFO] (MainThread) Found 2 skill(s) to remove.
[10:05:34] [INFO] (MainThread) ✓ general_greeting.py: Skill uploaded successfully.
[10:05:34] [INFO] (MainThread) ✓ greeting_and_serve_visitors.py: Skill uploaded successfully.
[10:05:35] [INFO] (MainThread) ✓ Updated robot prompt with General_uscase_Prompt.txt
[10:05:35] [INFO] (MainThread) 🎉 Deployment of 'Base Demo' completed successfully!
```

---

## 🧪 Development Tips

- Run with `--simulate` to test the logic safely.
- Always ensure your **prompt file encoding** is UTF-8.
- Each skill should have the proper `@skill()` decorator and import from `pymirokai.decorators.skill`.
- Use `await mission.completed()` for every robot action to ensure sequential behavior.

---


## 📚 Credits

- **Author:** Gauthier GENDREAU (SANANGA TECHNOLOGY)    
- **Framework:** [`pymirokai`](https://docs.developers.enchanted.tools/legend-of-mirokai-v0.6.0/pymirokai/)  
- **Version tested:** `0.6.0`

---

