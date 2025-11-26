import streamlit as st
import google.generativeai as genai
import os.path
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- 1. ARCHITECTURE & CONFIGURATION ---
st.set_page_config(page_title="OnboardAI - Enterprise Agent System", layout="wide", page_icon="🚀")

# Initialize Session State (Memory)
if "logs" not in st.session_state:
    st.session_state["logs"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

def log_event(agent_name, action, details):
    """Observability: Logs agent actions for the user to see."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] **{agent_name}**: {action} -> {details}"
    st.session_state["logs"].append(entry)

# --- 2. TOOL AGENT (The Hands) ---
class WorkspaceToolsAgent:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.compose']
        self.creds = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    return None
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def create_calendar_event(self, emp_name):
        if not self.creds: return "❌ Auth Failed"
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            event = {
                'summary': f'Induction: {emp_name}',
                'description': 'Welcome session with HR.',
                'start': {'dateTime': f"{tomorrow}T10:00:00", 'timeZone': 'Asia/Kolkata'},
                'end': {'dateTime': f"{tomorrow}T11:00:00", 'timeZone': 'Asia/Kolkata'},
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            return f"✅ Meeting ID: {event.get('id')} (Created)"
        except Exception as e: return f"❌ Error: {str(e)}"

    def draft_email(self, emp_name):
        if not self.creds: return "❌ Auth Failed"
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            profile = service.users().getProfile(userId='me').execute()
            return f"✅ Draft created for {emp_name} (Sender: {profile['emailAddress']})"
        except Exception as e: return f"❌ Error: {str(e)}"

# --- 3. POLICY AGENT (The Brain) ---
class PolicyRAGAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = self._get_working_model()
        self.context = """
        SYSTEM CONTEXT: You are an Expert HR Policy Manager.
        RULES:
        1. Work Hours: 9:00 AM - 6:00 PM.
        2. Leaves: 1.5 Paid Leaves per month (18/year).
        3. WFH: Allowed 2 days/week with approval.
        4. Probation: 3 Months.
        5. Insurance: Starts from Day 1.
        """

    def _get_working_model(self):
        if not self.api_key: return None
        genai.configure(api_key=self.api_key)
        # Priority list for models (Free & Stable first)
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-001', 'gemini-pro']
        for m in models_to_try:
            try:
                test_model = genai.GenerativeModel(m)
                # Test Query
                test_model.generate_content("test")
                log_event("System", "Model Selected", m)
                return test_model
            except:
                continue
        return None

    def ask(self, query):
        if not self.model: return "⚠️ API Key Missing or Invalid."
        try:
            response = self.model.generate_content(f"{self.context}\nUSER QUESTION: {query}")
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# --- 4. ORCHESTRATOR (The Boss) ---
class Orchestrator:
    def __init__(self, api_key):
        self.tools_agent = WorkspaceToolsAgent()
        self.policy_agent = PolicyRAGAgent(api_key)

    def run_onboarding_sequence(self, name):
        log_event("Orchestrator", "Task Received", f"Onboard {name}")
        
        # Step 1: Calendar
        log_event("Orchestrator", "Delegating", "ToolAgent -> Calendar")
        cal_res = self.tools_agent.create_calendar_event(name)
        log_event("ToolAgent", "Output", cal_res)
        
        # Step 2: Email
        log_event("Orchestrator", "Delegating", "ToolAgent -> Gmail")
        mail_res = self.tools_agent.draft_email(name)
        log_event("ToolAgent", "Output", mail_res)
        
        return "Onboarding Sequence Completed Successfully."

    def answer_query(self, query):
        log_event("Orchestrator", "Delegating", "PolicyAgent -> Gemini")
        response = self.policy_agent.ask(query)
        log_event("PolicyAgent", "Output", "Response Generated")
        return response

# --- 5. USER INTERFACE (Streamlit) ---
st.title("🚀 OnboardAI: Enterprise Agent System")
st.caption("Architecture: Orchestrator -> [Tool Agent | Policy Agent] -> Google Workspace")

# Sidebar: Configuration & Observability
with st.sidebar:
    st.header("⚙️ System Config")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("🧠 Observability (Logs)")
    # Showing logs in real-time
    if st.session_state["logs"]:
        for log in reversed(st.session_state["logs"]):
            st.caption(log)
    else:
        st.info("Waiting for tasks...")

# Main Layout
if api_key:
    orchestrator = Orchestrator(api_key)
    
    col1, col2 = st.columns(2)
    
    # Section 1: Action Agent
    with col1:
        st.subheader("🛠️ Operational Agent")
        st.info("Handles Calendar & Gmail APIs")
        new_emp = st.text_input("New Employee Name")
        if st.button("Initiate Onboarding"):
            if new_emp:
                with st.spinner("Orchestrating Agents..."):
                    status = orchestrator.run_onboarding_sequence(new_emp)
                    st.success(status)
            else:
                st.warning("Enter a name.")

    # Section 2: Knowledge Agent
    with col2:
        st.subheader("🤖 Knowledge Agent")
        st.info("Handles HR Policy Queries (RAG)")
        
        # Chat Interface
        user_q = st.chat_input("Ask about HR Policies...")
        
        # Display History
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        if user_q:
            # Display User Message
            with st.chat_message("user"):
                st.write(user_q)
            st.session_state["chat_history"].append({"role": "user", "content": user_q})
            
            # Get & Display Answer
            with st.spinner("Thinking..."):
                ans = orchestrator.answer_query(user_q)
                with st.chat_message("assistant"):
                    st.write(ans)
                st.session_state["chat_history"].append({"role": "assistant", "content": ans})

else:
    st.warning("Please enter your Gemini API Key in the sidebar to initialize the Agent System.")