# 🚀 OnboardAI: Enterprise HR Agent
### 🏆 Google AI Agents Intensive Capstone Project (Enterprise Track)

OnboardAI is an autonomous Multi-Agent System designed to automate the repetitive "First Day" onboarding process for HR teams. Unlike simple chatbots, this agent takes **real-world actions** using Google Workspace APIs to schedule meetings and draft emails instantly.

![Architecture](https://img.shields.io/badge/Architecture-Orchestrator-blue) ![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange)

## 🌟 Key Features
* **📅 Auto-Scheduler Agent:** Checks calendar availability and books induction meetings automatically.
* **📧 Communication Agent:** Drafts personalized welcome emails via Gmail API using the new employee's details.
* **🧠 Policy RAG Agent:** Powered by **Google Gemini 2.0 Flash**, it acts as an expert HR assistant, answering queries about company policies (leaves, WFH, timings) with context-aware accuracy.
* **👀 Observability:** Real-time logs in the sidebar show the agent's "thought process" and tool execution.

## 🛠️ Tech Stack
* **Core AI:** Google Gemini 2.0 Flash
* **Tools:** Google Calendar API, Gmail API
* **Framework:** Streamlit (Python)
* **Auth:** OAuth 2.0 Client

## 📸 Architecture
The system uses an **Orchestrator Pattern**:
1.  **User** inputs a request (e.g., "Onboard Ram").
2.  **Orchestrator** breaks this down into tasks.
3.  **Tool Agent** executes API calls (Calendar/Gmail).
4.  **Policy Agent** handles Q&A using LLM reasoning.

## ⚙️ How to Run Locally
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Bhaskar-AI-Dev/OnboardAI-HR-Agent.git
    cd OnboardAI-HR-Agent
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Credentials:**
    * Add your `credentials.json` (Google Workspace OAuth) to the root folder.
    * Get a Gemini API Key from Google AI Studio.
4.  **Run the Agent:**
    ```bash
    streamlit run app.py
    ```

---
*Built for the Google AI Agents Intensive 2025.*
