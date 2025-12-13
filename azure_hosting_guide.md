# Azure Hosting Guide: From Scratch

This guide assumes you have a fresh **Ubuntu** (or Debian-based) server on Azure and you have just logged in via SSH.

## 0. The Golden Rule of Ports
To ensure this app is "compatible with other projects" running on the same server, **we must pick a unique port**.

1.  **Check used ports**: Run this to see what is already taken.
    ```bash
    sudo ss -tulpn | grep LISTEN
    ```
2.  **Pick your port**: The default is `5050`. If `5050` is in the list above, pick another (e.g., `5051`, `8000`, `3000`).
3.  **Open Firewall**: You must allow this port in your **Azure Network Security Group (NSG)** for the VM.
    *   Go to Azure Portal -> Compute -> Networking -> Add Inbound Rule -> Destination Port Ranges: `5050` (or your validated choice).

---

## 1. System Preparation
Update the system and install necessary tools (Python, Git, Virtualenv).

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install Python 3, pip, venv, and git
sudo apt install -y python3 python3-pip python3-venv git
```

## 2. Clone & Setup
We will install the app in the `/opt` directory (standard for optional software).

```bash
# 1. Navigate to /opt
cd /opt

# 2. Clone the repo (replace with your URL)
# If private, you'll need a Personal Access Token (PAT)
sudo git clone https://github.com/AbdullrahmanEsmael2007/LLMviaCall.git llm-voice

# 3. Fix permissions (give your user ownership)
# Replace 'azureuser' with your actual username (run `whoami` to check)
sudo chown -R azureuser:azureuser llm-voice

# 4. Enter directory
cd llm-voice
```

## 3. Environment Setup (The Virtual Environment)
Always use a virtual environment to avoid conflicts with system python packages.

```bash
# 1. Create venv
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 4. Configuration (.env) and Ports
This is where you define the port compatibility.

```bash
# Create .env file
nano .env
```

**Paste the following (Edit the PORT if needed):**
```ini
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
# CRITICAL: Set this to the unused port you found in Step 0
PORT=5050 
```
*(Save: Ctrl+X, Y, Enter)*

## 5. Run as a Background Service
We use `systemd` to keep it running 24/7.

1.  **Create Service File**:
    ```bash
    sudo nano /etc/systemd/system/llm-voice.service
    ```

2.  **Paste Content** (Ensure `User` and `WorkingDirectory` are correct):
    ```ini
    [Unit]
    Description=LLM Voice Assistant
    After=network.target

    [Service]
    User=azureuser
    Group=azureuser
    WorkingDirectory=/opt/llm-voice
    EnvironmentFile=/opt/llm-voice/.env
    Environment="PATH=/opt/llm-voice/venv/bin"
    # The port is loaded from your .env file automatically
    ExecStart=/opt/llm-voice/venv/bin/uvicorn main:app --host 0.0.0.0

    Restart=always
    RestartSec=3

    [Install]
    WantedBy=multi-user.target
    ```

3.  **Start It**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable llm-voice
    sudo systemctl start llm-voice
    ```

4.  **Check It**:
    ```bash
    sudo systemctl status llm-voice
    ```

## 6. Exposing to the World
Now your app is running on `http://YOUR_SERVER_IP:5050`.

*   **Option A: Direct Access** (Easiest)
    *   Update Twilio Webhook to: `http://YOUR_SERVER_IP:5050/twiml`
    *   (Requires Port 5050 open in Azure NSG).

*   **Option B: Ngrok** (If you don't want to open ports/mess with static IPs)
    *   Use the `deployment_guide.md` to set up the Ngrok service.

*   **Option C: Nginx Reverse Proxy** (Professional)
    *   If you have many apps on one server, install Nginx.
    *   Route `domain.com/voice` -> `localhost:5050`.
    *   Route `domain.com/other-app` -> `localhost:3000`.
