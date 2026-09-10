"""
app.py
Streamlit application for the Banking Assistant.
Provides a conversational chat interface with session state management.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional

# Add project directory to path
project_dir = Path(__file__).parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from database_setup import init_database
from agents_and_tasks import BankingAssistantCrew


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1f77b4;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #666;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "crew" not in st.session_state:
        st.session_state.crew = None

    if "account_id" not in st.session_state:
        st.session_state.account_id = "ACC001"

    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False

    if "rate_limit_warning" not in st.session_state:
        st.session_state.rate_limit_warning = False


# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================


@st.cache_resource
def initialize_crew():
    """
    Initialize the Banking Assistant Crew (cached to avoid recreating on rerun).
    This is expensive so we cache it.
    """
    try:
        with st.spinner("🔄 Initializing Banking Assistant Crew..."):
            crew = BankingAssistantCrew()
        st.success("✓ Banking Assistant Crew ready!")
        return crew
    except Exception as e:
        st.error(f"✗ Error initializing crew: {e}")
        st.stop()


def initialize_database():
    """Initialize the SQLite database with mock data."""
    try:
        db_path = project_dir / "bank_data.db"
        if not db_path.exists():
            with st.spinner("🔄 Initializing mock banking database..."):
                init_database()
            st.success("✓ Database initialized successfully!")
        return True
    except Exception as e:
        st.error(f"✗ Error initializing database: {e}")
        return False


# ============================================================================
# UI COMPONENTS
# ============================================================================


def display_header():
    """Display the application header."""
    st.markdown(
        """
        <h1 class="main-header">🏦 Banking Assistant</h1>
        <p style="text-align: center; color: #666;">
            Your AI-powered conversational banking assistant powered by CrewAI
        </p>
        """,
        unsafe_allow_html=True,
    )


def display_info_section():
    """Display information and instructions."""
    with st.expander("ℹ️ About This Assistant", expanded=False):
        st.markdown(
            """
            ### Features
            - **Account Information**: Check balances, account types, and customer details
            - **Transaction Analysis**: View transaction history, spending patterns, and statements
            - **Service Requests**: Create and manage service requests (change of address, cheque books, KYC updates)
            
            ### How It Works
            1. Enter your banking inquiry in the chat box below
            2. The Banking Operations Manager (Coordinator Agent) analyzes your request
            3. Your request is delegated to the appropriate specialist:
               - **Accounts Agent** → Account information
               - **Transaction Agent** → Transaction history & statements
               - **Service Agent** → Service requests
            4. Get detailed, personalized responses
            
            ### Demo Account
            - **Account ID**: ACC001 (John Doe)
            - **Balance**: $5,250.75
            - **Type**: Checking Account
            
            Try questions like:
            - "What's my account balance?"
            - "Show me my transaction history"
            - "I need to update my address"
            - "What's my spending by category?"
            """
        )


def display_sidebar():
    """Display the sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Settings")

        # Account selection
        st.subheader("Account Selection")
        account_options = {
            "ACC001": "John Doe - Checking",
            "ACC002": "Jane Smith - Savings",
            "ACC003": "Michael Johnson - Money Market",
            "ACC004": "Sarah Williams - Checking",
            "ACC005": "Robert Brown - Business",
            "ACC006": "Emily Davis - Savings",
            "ACC007": "David Martinez - Checking",
            "ACC008": "Lisa Anderson - Premium Savings",
            "ACC009": "James Taylor - Checking",
            "ACC010": "Patricia White - Savings",
        }

        selected_account = st.selectbox(
            "Select Account",
            options=list(account_options.keys()),
            format_func=lambda x: account_options[x],
            index=0,
        )

        st.session_state.account_id = selected_account

        # Database status
        st.subheader("Database Status")
        db_path = project_dir / "bank_data.db"
        if db_path.exists():
            st.success("✓ Database initialized")
        else:
            st.warning("⚠ Database not found")
            if st.button("🔄 Initialize Database"):
                if initialize_database():
                    st.session_state.db_initialized = True
                    st.rerun()

        # System information
        st.subheader("System Info")
        st.markdown(
            f"""
            - **Model**: Qwen 3.6-27B
            - **Rate Limit**: 900 RPM (1000 max)
            - **Backend**: CrewAI + LangChain
            - **Database**: SQLite
            """
        )

        # Clear chat history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        # Warning about rate limits
        if st.session_state.rate_limit_warning:
            st.warning(
                """
                ⚠️ **Rate Limit Warning**
                
                You've reached the API rate limit. Please wait a moment before sending another message.
                The system implements exponential backoff retry logic automatically.
                """
            )


def display_chat_history():
    """Display the chat conversation history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])


def display_input_area():
    """Display the chat input area."""
    user_input = st.chat_input(
        placeholder="Ask me about your account, transactions, or services...",
        key="user_input",
    )

    return user_input


# ============================================================================
# MAIN APPLICATION LOGIC
# ============================================================================


def process_user_query(query: str) -> str:
    """
    Process the user query through the Banking Assistant Crew.

    Args:
        query: The user's input question/request

    Returns:
        The response from the crew
    """
    try:
        with st.spinner("🤔 Analyzing your request..."):
            response = st.session_state.crew.process_query(
                query, account_id=st.session_state.account_id
            )
        return response

    except Exception as e:
        error_str = str(e)

        if "429" in error_str or "rate_limit" in error_str.lower():
            st.session_state.rate_limit_warning = True
            return """
            ⚠️ **Rate Limit Reached**
            
            The API has temporarily limited requests. This is normal - the system has retry logic
            with exponential backoff enabled.
            
            Please wait 30-60 seconds and try again. The next request will automatically be retried.
            
            Error details: HTTP 429 Too Many Requests
            """
        else:
            return f"""
            ✗ **Error Processing Request**
            
            {error_str}
            
            Possible issues:
            - Database not initialized (run database_setup.py first)
            - LLM API credentials missing
            - Network connectivity issue
            
            Please check the system logs or try again.
            """


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Display header
    display_header()

    # Display info section
    display_info_section()

    # Display sidebar
    display_sidebar()

    # Initialize database if needed
    if not st.session_state.db_initialized:
        if initialize_database():
            st.session_state.db_initialized = True

    # Initialize crew if needed
    if st.session_state.crew is None:
        st.session_state.crew = initialize_crew()

    # Display chat history
    st.subheader("💬 Conversation")
    display_chat_history()

    # Handle user input
    user_input = display_input_area()

    if user_input:
        # Add user message to history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
                "avatar": "🧑‍💼",
            }
        )

        # Display user message
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(user_input)

        # Process query and get response
        response = process_user_query(user_input)

        # Add assistant response to history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "avatar": "🤖",
            }
        )

        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)

        # Reset rate limit warning after successful message
        st.session_state.rate_limit_warning = False


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
