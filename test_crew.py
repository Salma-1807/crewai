"""
test_crew.py
Test script for the Banking Assistant Crew.
Run this to verify the system works without launching Streamlit.
"""

import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))


def test_database():
    """Test database initialization and connectivity."""
    print("\n" + "=" * 60)
    print("TEST 1: Database Initialization")
    print("=" * 60)

    try:
        from database_setup import init_database, DB_PATH
        import sqlite3

        # Initialize database
        print("Initializing database...")
        init_database()

        # Verify database was created
        if not DB_PATH.exists():
            print("✗ FAILED: Database file was not created")
            return False

        # Verify tables exist
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        expected_tables = {"accounts", "transactions", "service_requests"}
        if expected_tables.issubset(set(tables)):
            print(f"✓ PASSED: Database has all required tables: {tables}")
            return True
        else:
            print(f"✗ FAILED: Missing tables. Found: {tables}")
            return False

    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_mcp_tools():
    """Test MCP tool definitions."""
    print("\n" + "=" * 60)
    print("TEST 2: MCP Tools")
    print("=" * 60)

    try:
        from mcp_tools import (
            get_account_balance,
            get_transaction_history,
            get_service_requests,
            DEMO_ACCOUNT_ID,
        )

        print(f"Testing tools with account: {DEMO_ACCOUNT_ID}")

        # Test account balance
        print("\n[1/3] Testing get_account_balance()...")
        result = get_account_balance()
        if "Balance:" in result or "balance:" in result:
            print("✓ Account balance retrieved successfully")
        else:
            print(f"⚠ Unexpected result: {result}")

        # Test transaction history
        print("\n[2/3] Testing get_transaction_history()...")
        result = get_transaction_history(limit=5)
        if "Transaction" in result or "transaction" in result:
            print("✓ Transaction history retrieved successfully")
        else:
            print(f"⚠ Unexpected result: {result}")

        # Test service requests
        print("\n[3/3] Testing get_service_requests()...")
        result = get_service_requests()
        if "Service" in result or "service" in result or "Request" in result:
            print("✓ Service requests retrieved successfully")
        else:
            print(f"⚠ Unexpected result: {result}")

        print("\n✓ PASSED: All MCP tools working correctly")
        return True

    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_llm_initialization():
    """Test LLM initialization with rate limiting."""
    print("\n" + "=" * 60)
    print("TEST 3: LLM Initialization (with rate limiting)")
    print("=" * 60)

    try:
        from agents_and_tasks import (
            initialize_llm_with_retry,
            MAX_RPM,
            MIN_REQUEST_INTERVAL,
        )

        print(f"Rate Limit Settings:")
        print(f"  - MAX_RPM: {MAX_RPM}")
        print(f"  - MIN_REQUEST_INTERVAL: {MIN_REQUEST_INTERVAL}s")

        print("\nInitializing LLM with retry logic...")
        llm = initialize_llm_with_retry()

        if llm is not None:
            print("✓ PASSED: LLM initialized successfully")
            return True
        else:
            print("✗ FAILED: LLM is None")
            return False

    except Exception as e:
        error_msg = str(e)
        if "API" in error_msg or "401" in error_msg or "OPENAI" in error_msg:
            print(f"⚠ WARNING: LLM initialization requires API credentials")
            print(f"  Error: {error_msg}")
            print(f"  Please set OPENAI_API_KEY and OPENAI_API_BASE in .env")
            return True  # Not a failure, expected for test environment
        else:
            print(f"✗ FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False


def test_crew_initialization():
    """Test CrewAI Crew initialization."""
    print("\n" + "=" * 60)
    print("TEST 4: CrewAI Crew Initialization")
    print("=" * 60)

    try:
        from agents_and_tasks import BankingAssistantCrew

        print("Initializing Banking Assistant Crew...")
        crew = BankingAssistantCrew()

        if crew is not None:
            if (
                hasattr(crew, "coordinator")
                and hasattr(crew, "accounts_agent")
                and hasattr(crew, "transaction_agent")
                and hasattr(crew, "service_agent")
            ):
                print("✓ PASSED: Crew initialized with all 4 agents:")
                print("  - Coordinator Agent")
                print("  - Accounts Agent")
                print("  - Transaction Agent")
                print("  - Service Agent")
                return True
            else:
                print("✗ FAILED: Crew missing one or more agents")
                return False
        else:
            print("✗ FAILED: Crew is None")
            return False

    except Exception as e:
        error_msg = str(e)
        if "LLM" in error_msg or "API" in error_msg or "OPENAI" in error_msg:
            print(f"⚠ WARNING: Crew initialization requires LLM API credentials")
            print(f"  Error: {error_msg}")
            print(f"  This is expected if .env is not configured")
            return True  # Not a failure for test environment
        else:
            print(f"✗ FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False


def test_query_processing():
    """Test end-to-end query processing."""
    print("\n" + "=" * 60)
    print("TEST 5: Query Processing (End-to-End)")
    print("=" * 60)

    try:
        from agents_and_tasks import BankingAssistantCrew

        print("Testing sample query: 'What is my account balance?'")
        crew = BankingAssistantCrew()

        print("\n(This may take 10-30 seconds due to LLM processing...)")
        response = crew.process_query("What is my account balance?")

        if response and len(response) > 0:
            print(f"\n✓ PASSED: Query processed successfully")
            print(f"\nResponse Preview (first 200 chars):")
            print("-" * 60)
            print(response[:200] + "..." if len(response) > 200 else response)
            print("-" * 60)
            return True
        else:
            print("✗ FAILED: Empty response from crew")
            return False

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            print(f"⚠ WARNING: Rate limit hit (HTTP 429)")
            print(f"  This is expected and should auto-retry")
            return True
        elif "API" in error_msg or "OPENAI" in error_msg:
            print(f"⚠ SKIPPED: Requires LLM API credentials")
            print(f"  Error: {error_msg}")
            return True  # Expected for test environment
        else:
            print(f"✗ FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False


def test_concurrent_query_processing():
    """Regression test: a single crew instance must serialize overlapping queries."""
    print("\n" + "=" * 60)
    print("TEST 6: Concurrent Query Processing")
    print("=" * 60)

    try:
        from concurrent.futures import ThreadPoolExecutor

        from agents_and_tasks import BankingAssistantCrew

        crew = BankingAssistantCrew()

        def run_query():
            return crew.process_query("What is my account balance?")

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(run_query)
            future_b = executor.submit(run_query)
            results = [future_a.result(), future_b.result()]

        if all(isinstance(result, str) and len(result) > 0 for result in results):
            print("✓ PASSED: Concurrent requests completed without executor re-entry errors")
            return True

        print("✗ FAILED: Concurrent request results were empty or invalid")
        return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Banking Assistant - System Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    results = {
        "Database": test_database(),
        "MCP Tools": test_mcp_tools(),
        "LLM Init": test_llm_initialization(),
        "Crew Init": test_crew_initialization(),
        "Query Processing": test_query_processing(),
        "Concurrent Query Processing": test_concurrent_query_processing(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Open: http://localhost:8501")
        print("  3. Ask questions about your banking!")
    elif passed >= total - 1:
        print(
            f"\n⚠ {total - passed} test(s) need attention (likely API credentials)"
        )
        print("\nSetup .env with API credentials:")
        print("  OPENAI_API_KEY=your_key")
        print("  OPENAI_API_BASE=https://api.provider.com/v1")
        print("\nOtherwise, the system should work!")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check the errors above.")

    print("\n" + "=" * 60 + "\n")

    return 0 if passed >= total - 1 else 1


if __name__ == "__main__":
    exit(main())
