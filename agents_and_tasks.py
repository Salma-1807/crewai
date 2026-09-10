"""
agents_and_tasks.py
Defines the CrewAI agents, tasks, and crew with rate limiting and retry logic.
Includes Qwen LLM configuration, max_rpm settings, and tenacity retry wrappers.
"""

import os
import threading
import time
from typing import Any, Callable
from functools import wraps

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai.llms import cache as crewai_cache
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Import config for environment variables
from config import Config


def _normalize_groq_tool_schema() -> None:
    """Groq rejects OpenAI tool schemas that omit properties on empty-arg functions."""
    try:
        from crewai.utilities import agent_utils

        original = agent_utils.convert_tools_to_openai_schema

        def _patched(tools):
            openai_tools, available_functions, tool_name_mapping = original(tools)
            for schema in openai_tools:
                function = schema.get("function")
                if not isinstance(function, dict):
                    continue
                params = function.get("parameters")
                if not isinstance(params, dict):
                    params = {"type": "object", "properties": {}}
                    function["parameters"] = params
                    continue
                params.setdefault("type", "object")
                params.setdefault("properties", {})
                if "required" in params and not params["required"]:
                    params.pop("required", None)
            return openai_tools, available_functions, tool_name_mapping

        agent_utils.convert_tools_to_openai_schema = _patched
    except Exception:
        pass


_normalize_groq_tool_schema()

# Import all tools from mcp_tools
from mcp_tools import (
    get_account_balance,
    get_account_details,
    list_all_accounts,
    get_transaction_history,
    get_spending_analysis,
    get_account_statement,
    get_service_requests,
    create_service_request,
    get_service_request_status,
    search_transactions_by_merchant,
)


def _disable_groq_cache_breakpoints() -> None:
    """Groq rejects CrewAI's prompt-cache metadata. Strip that marker for Groq only."""
    model_name = str(Config.LLM_MODEL or "").lower()
    if "groq" not in model_name:
        return

    def _strip_cache_key(messages):
        if not isinstance(messages, list):
            return messages

        cleaned = []
        for msg in messages:
            if isinstance(msg, dict):
                copy = dict(msg)
                copy.pop("cache_breakpoint", None)
                cleaned.append(copy)
            else:
                cleaned.append(msg)
        return cleaned

    try:
        from crewai.llm import LLM as CrewAILLM

        original_prepare = CrewAILLM._prepare_completion_params

        def _safe_prepare(self, messages, tools=None, skip_file_processing=False):
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]
            messages = _strip_cache_key(messages)
            return original_prepare(self, messages, tools, skip_file_processing)

        CrewAILLM._prepare_completion_params = _safe_prepare

        original_call = CrewAILLM.call

        def _safe_call(
            self,
            messages,
            tools=None,
            callbacks=None,
            available_functions=None,
            from_task=None,
            from_agent=None,
            response_model=None,
        ):
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]
            messages = _strip_cache_key(messages)
            return original_call(
                self,
                messages,
                tools=tools,
                callbacks=callbacks,
                available_functions=available_functions,
                from_task=from_task,
                from_agent=from_agent,
                response_model=response_model,
            )

        CrewAILLM.call = _safe_call
    except Exception:
        pass

    try:
        crewai_cache.mark_cache_breakpoint = lambda message: dict(message)
    except Exception:
        pass

    print("✓ Disabled CrewAI cache_breakpoint markers for Groq requests")


_disable_groq_cache_breakpoints()


# ============================================================================
# RATE LIMIT & RETRY CONFIGURATION
# ============================================================================

# Constants for rate limiting
MAX_RPM = 900  # Conservative rate limit
MAX_TOKENS_PER_REQUEST = Config.LLM_MAX_TOKENS
MIN_REQUEST_INTERVAL = 0.1  # Minimum delay between requests (seconds)


def retry_with_exponential_backoff(max_attempts: int = 3):
    """
    Decorator that retries a function with exponential backoff on rate limit errors.
    Catches HTTP 429 errors and other transient failures.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )


@retry_with_exponential_backoff(max_attempts=3)
def initialize_llm_with_retry() -> Any:
    """
    Initialize the CrewAI LLM wrapper for Groq with retry logic.
    CrewAI 1.15 requires a CrewAI LLM object, not a raw LangChain ChatGroq instance.
    """
    try:
        if not Config.LLM_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not set in environment variables. "
                "Please set GROQ_API_KEY before running the application."
            )

        model_name = Config.LLM_MODEL.strip()
        if not model_name.startswith("groq/"):
            model_name = f"groq/{model_name}"

        llm = LLM(
            model=model_name,
            api_key=Config.LLM_API_KEY,
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=MAX_TOKENS_PER_REQUEST,
            timeout=Config.LLM_TIMEOUT,
            provider="groq",
        )
        print(f"✓ CrewAI LLM initialized successfully with model: {model_name}")
        return llm
    except Exception as e:
        print(f"⚠ Error initializing LLM: {e}")
        raise


def throttle_requests(func: Callable) -> Callable:
    """
    Decorator that enforces minimum interval between consecutive requests
    to avoid bursting the rate limit.
    """
    last_call_time = [0]  # Use list to allow modification in closure

    @wraps(func)
    def wrapper(*args, **kwargs):
        elapsed = time.time() - last_call_time[0]
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
        result = func(*args, **kwargs)
        last_call_time[0] = time.time()
        return result

    return wrapper


# ============================================================================
# LLM INITIALIZATION (with rate limiting)
# ============================================================================

print("Initializing ChatGroq LLM with rate limit handling...")
try:
    llm = initialize_llm_with_retry()
except Exception as e:
    print(f"✗ Failed to initialize LLM after retries: {e}")
    print("Please ensure GROQ_API_KEY and GROQ_MODEL are set in environment variables.")
    raise


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================


def create_coordinator_agent() -> Agent:
    """
    Creates the Coordinator Agent (Banking Operations Manager).
    Analyzes user requests and delegates to specialized sub-agents.
    """
    return Agent(
        role="Banking Operations Manager",
        goal="Analyze customer banking needs and coordinate with appropriate specialists to resolve inquiries and requests.",
        backstory="""You are an experienced banking operations manager with 10+ years in customer service.
        You excel at understanding customer needs and routing them to the right department.
        You maintain a professional, helpful demeanor and ensure every customer inquiry is addressed thoroughly.""",
        llm=llm,
        tools=[
            get_account_balance,
            get_account_details,
            get_transaction_history,
            get_spending_analysis,
            get_account_statement,
            get_service_requests,
            create_service_request,
            search_transactions_by_merchant,
        ],
        verbose=True,
        max_iter=5,
        max_rpm=MAX_RPM,
    )


def create_accounts_agent() -> Agent:
    """
    Creates the Accounts Agent (Account Details Specialist).
    Handles account information, balance inquiries, and customer profile details.
    """
    return Agent(
        role="Account Details Specialist",
        goal="Provide comprehensive account information, verify account status, and assist with account-related inquiries.",
        backstory="""You are a detail-oriented account specialist with expertise in customer account management.
        You can quickly access and interpret account information, explain account types and features,
        and help customers understand their account status and holdings.""",
        llm=llm,
        tools=[get_account_balance, get_account_details, list_all_accounts],
        verbose=True,
        max_iter=3,
        max_rpm=MAX_RPM,
    )


def create_transaction_agent() -> Agent:
    """
    Creates the Transaction Agent (Transaction & Statement Specialist).
    Handles transaction history, spending analysis, and statement generation.
    """
    return Agent(
        role="Transaction & Statement Specialist",
        goal="Analyze transaction history, provide spending insights, and generate comprehensive account statements.",
        backstory="""You are an analytical financial specialist with deep knowledge of transaction patterns and spending trends.
        You can drill down into transaction details, identify spending patterns by category and merchant,
        and provide clear explanations of account activity. You're detail-oriented and thorough in your analysis.""",
        llm=llm,
        tools=[
            get_transaction_history,
            get_spending_analysis,
            get_account_statement,
            search_transactions_by_merchant,
        ],
        verbose=True,
        max_iter=3,
        max_rpm=MAX_RPM,
    )


def create_service_agent() -> Agent:
    """
    Creates the Service Agent (Customer Service Specialist).
    Handles service requests, change of address, cheque book issuance, and KYC updates.
    """
    return Agent(
        role="Customer Service Specialist",
        goal="Manage customer service requests efficiently, including account modifications, document requests, and KYC updates.",
        backstory="""You are a customer service professional with extensive experience in handling various service requests.
        You specialize in Change of Address, Cheque Book issuance, KYC updates, and other customer service tasks.
        You're empathetic, efficient, and always ensure customers understand the status of their requests.""",
        llm=llm,
        tools=[
            get_service_requests,
            create_service_request,
            get_service_request_status,
        ],
        verbose=True,
        max_iter=3,
        max_rpm=MAX_RPM,
    )


# ============================================================================
# TASK DEFINITIONS
# ============================================================================


def create_coordination_task(coordinator_agent: Agent, user_query: str) -> Task:
    """Creates a task for the coordinator to analyze and route the user query."""
    return Task(
        description=f"""Analyze the following customer inquiry and determine which specialist(s) should handle it.
        
        Customer Inquiry: "{user_query}"
        
        Based on the inquiry, identify:
        1. The primary category (Account Info, Transactions, Service Request, etc.)
        2. Relevant details and account ID
        3. Which agent(s) should be involved
        4. Recommended next steps
        
        Provide a clear routing decision and explanation.""",
        agent=coordinator_agent,
        expected_output="A clear analysis of the customer need and recommended action plan.",
    )


def create_accounts_task(accounts_agent: Agent, account_id: str, query: str) -> Task:
    """Creates a task for the accounts agent to retrieve account information."""
    return Task(
        description=f"""Handle the following account inquiry for account ID: {account_id}
        
        Customer Request: "{query}"
        
        Use the available tools to:
        1. Fetch relevant account information
        2. Answer the customer's specific questions
        3. Provide clear, accurate details
        
        Respond with accurate account information and clear explanations.""",
        agent=accounts_agent,
        expected_output="Complete account information and answers to the customer's questions.",
    )


def create_transaction_task(
    transaction_agent: Agent, account_id: str, query: str
) -> Task:
    """Creates a task for the transaction agent to analyze transactions."""
    return Task(
        description=f"""Analyze transaction activity for account ID: {account_id}
        
        Customer Request: "{query}"
        
        Use the available tools to:
        1. Retrieve transaction history as needed
        2. Perform spending analysis if requested
        3. Generate account statements if required
        4. Answer specific transaction-related questions
        
        Provide detailed transaction insights and analysis.""",
        agent=transaction_agent,
        expected_output="Transaction details, spending analysis, or statement as appropriate for the request.",
    )


def create_service_task(
    service_agent: Agent, account_id: str, query: str
) -> Task:
    """Creates a task for the service agent to handle service requests."""
    return Task(
        description=f"""Handle the service request for account ID: {account_id}
        
        Customer Request: "{query}"
        
        Use the available tools to:
        1. Retrieve existing service requests if needed
        2. Create new service requests as appropriate
        3. Check status of pending requests
        4. Provide clear next steps
        
        Ensure the customer's service needs are properly addressed and tracked.""",
        agent=service_agent,
        expected_output="Service request confirmation, status updates, or next steps for the customer.",
    )


# ============================================================================
# CREW ASSEMBLY
# ============================================================================


class BankingAssistantCrew:
    """
    Main Banking Assistant Crew coordinator.
    Orchestrates all agents with proper error handling and rate limiting.
    """

    def __init__(self):
        """Initialize all agents and tasks."""
        self.coordinator = create_coordinator_agent()
        self.accounts_agent = create_accounts_agent()
        self.transaction_agent = create_transaction_agent()
        self.service_agent = create_service_agent()
        self._process_lock = threading.Lock()

    def process_query(self, user_query: str, account_id: str = "ACC001") -> str:
        """
        Process a user query through the appropriate agent(s).

        Args:
            user_query: The customer's inquiry or request
            account_id: The account ID to process (defaults to demo account)

        Returns:
            The response from the appropriate agent(s)
        """
        try:
            with self._process_lock:
                print(f"\n📋 Processing query: {user_query}")
                print(f"🔑 Account ID: {account_id}")

                # Create coordination task
                coordination_task = create_coordination_task(self.coordinator, user_query)

                # Create coordinator crew to analyze the query
                coordinator_crew = Crew(
                    agents=[self.coordinator],
                    tasks=[coordination_task],
                    verbose=True,
                    max_rpm=MAX_RPM,
                )

                # Get coordination analysis
                print("\n🤖 Coordinator analyzing query...")
                coordination_result = coordinator_crew.kickoff()
                print(f"✓ Coordination analysis complete")

                # Determine which agent to use based on query content
                query_lower = user_query.lower()

                if any(
                    word in query_lower
                    for word in ["transaction", "history", "statement", "spending", "merchant"]
                ):
                    print("\n🤖 Routing to Transaction Agent...")
                    task = create_transaction_task(
                        self.transaction_agent, account_id, user_query
                    )
                    crew = Crew(
                        agents=[self.transaction_agent],
                        tasks=[task],
                        verbose=True,
                        max_rpm=MAX_RPM,
                    )
                    result = crew.kickoff()

                elif any(
                    word in query_lower
                    for word in [
                        "service",
                        "request",
                        "address",
                        "cheque",
                        "kyc",
                        "document",
                    ]
                ):
                    print("\n🤖 Routing to Service Agent...")
                    task = create_service_task(self.service_agent, account_id, user_query)
                    crew = Crew(
                        agents=[self.service_agent],
                        tasks=[task],
                        verbose=True,
                        max_rpm=MAX_RPM,
                    )
                    result = crew.kickoff()

                else:
                    print("\n🤖 Routing to Accounts Agent...")
                    task = create_accounts_task(
                        self.accounts_agent, account_id, user_query
                    )
                    crew = Crew(
                        agents=[self.accounts_agent],
                        tasks=[task],
                        verbose=True,
                        max_rpm=MAX_RPM,
                    )
                    result = crew.kickoff()

                return str(result)

        except Exception as e:
            error_msg = f"""
            Error processing query: {str(e)}
            
            This may be due to:
            - Rate limit exceeded (HTTP 429) - Please try again in a few moments
            - LLM provider issue - Check your API key and connection
            - Database connection issue - Ensure database_setup.py has been run
            
            Please try again or contact support if the issue persists.
            """
            print(f"✗ {error_msg}")
            return error_msg


# ============================================================================
# INITIALIZATION & TESTING
# ============================================================================

if __name__ == "__main__":
    print("Initializing Banking Assistant Crew...\n")

    try:
        crew = BankingAssistantCrew()
        print("✓ Banking Assistant Crew initialized successfully\n")

        # Test with a sample query
        test_query = "What is my current account balance?"
        print(f"Test Query: {test_query}")
        response = crew.process_query(test_query)
        print(f"\nResponse:\n{response}")

    except Exception as e:
        print(f"✗ Error initializing crew: {e}")
        raise
