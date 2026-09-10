"""
mcp_tools.py
Defines CrewAI/LangChain tools that simulate MCP endpoints for Accounts, 
Transactions, and Service requests. These tools query the SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from crewai.tools import tool


# Database path
DB_PATH = Path(__file__).parent / "bank_data.db"

# Hardcoded user_id for demo (no authentication)
DEMO_ACCOUNT_ID = "ACC001"


def get_db_connection():
    """Get a connection to the banking database."""
    if not DB_PATH.exists():
        raise RuntimeError(
            f"Database not found at {DB_PATH}. Run database_setup.py first."
        )
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# ACCOUNTS AGENT TOOLS (MCP: Accounts Server)
# ============================================================================


@tool("Get Account Balance")
def get_account_balance(account_id: str = DEMO_ACCOUNT_ID) -> str:
    """
    Retrieves the current account balance for a given account ID.
    Simulates querying the Accounts MCP Server.

    Args:
        account_id: The account identifier (defaults to demo account)

    Returns:
        A formatted string with account balance information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT account_id, customer_name, balance, currency, status FROM accounts WHERE account_id = ?",
            (account_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return f"Account {account_id} not found."

        return f"""
        Account Balance Information:
        - Account ID: {row['account_id']}
        - Customer: {row['customer_name']}
        - Balance: {row['currency']} {row['balance']:.2f}
        - Status: {row['status']}
        """
    except Exception as e:
        return f"Error retrieving balance: {str(e)}"


@tool("Get Account Details")
def get_account_details(account_id: str = DEMO_ACCOUNT_ID) -> str:
    """
    Retrieves comprehensive account details including contact info and KYC status.
    Simulates querying the Accounts MCP Server.

    Args:
        account_id: The account identifier (defaults to demo account)

    Returns:
        A formatted string with account details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT account_id, customer_name, account_type, balance, currency,
                   status, phone, email, created_date, kyc_status
            FROM accounts WHERE account_id = ?
        """,
            (account_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return f"Account {account_id} not found."

        return f"""
        Complete Account Details:
        - Account ID: {row['account_id']}
        - Customer Name: {row['customer_name']}
        - Account Type: {row['account_type']}
        - Balance: {row['currency']} {row['balance']:.2f}
        - Account Status: {row['status']}
        - Phone: {row['phone']}
        - Email: {row['email']}
        - Account Created: {row['created_date']}
        - KYC Status: {row['kyc_status']}
        """
    except Exception as e:
        return f"Error retrieving account details: {str(e)}"


@tool("List All Accounts")
def list_all_accounts() -> str:
    """
    Lists all active accounts in the system.
    Simulates querying the Accounts MCP Server.

    Returns:
        A formatted string with all account summaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT account_id, customer_name, account_type, balance, status 
            FROM accounts ORDER BY account_id
        """
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No accounts found."

        result = "All Accounts in System:\n"
        for row in rows:
            result += f"\n- {row['account_id']}: {row['customer_name']} ({row['account_type']}) - Balance: ${row['balance']:.2f} - Status: {row['status']}"

        return result
    except Exception as e:
        return f"Error listing accounts: {str(e)}"


# ============================================================================
# TRANSACTION AGENT TOOLS (MCP: Transactions Server)
# ============================================================================


@tool("Get Transaction History")
def get_transaction_history(
    account_id: str = DEMO_ACCOUNT_ID, limit: int = 10
) -> str:
    """
    Retrieves recent transaction history for an account.
    Simulates querying the Transactions MCP Server.

    Args:
        account_id: The account identifier (defaults to demo account)
        limit: Maximum number of transactions to return (default 10)

    Returns:
        A formatted string with transaction history
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT transaction_id, transaction_type, amount, description, 
                   date, balance_after, merchant, category
            FROM transactions 
            WHERE account_id = ?
            ORDER BY date DESC
            LIMIT ?
        """,
            (account_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No transactions found for account {account_id}."

        result = f"Recent Transaction History for {account_id}:\n"
        for row in rows:
            result += f"\n- {row['date']}: [{row['transaction_type']}] {row['description']}"
            result += f"\n  Amount: {row['amount']:.2f} | Merchant: {row['merchant']} | Category: {row['category']}"
            result += f"\n  Balance After: ${row['balance_after']:.2f}\n"

        return result
    except Exception as e:
        return f"Error retrieving transaction history: {str(e)}"


@tool("Get Spending Analysis")
def get_spending_analysis(account_id: str = DEMO_ACCOUNT_ID) -> str:
    """
    Provides a spending analysis by category for the past 90 days.
    Simulates querying the Transactions MCP Server.

    Args:
        account_id: The account identifier (defaults to demo account)

    Returns:
        A formatted string with spending analysis
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT category, COUNT(*) as transaction_count, SUM(amount) as total_spending
            FROM transactions
            WHERE account_id = ? AND transaction_type = 'DEBIT'
            GROUP BY category
            ORDER BY total_spending DESC
        """,
            (account_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No debit transactions found for account {account_id}."

        result = f"Spending Analysis for Account {account_id}:\n"
        total_debit = 0
        for row in rows:
            result += f"\n- {row['category']}: {row['transaction_count']} transactions, Total: ${row['total_spending']:.2f}"
            total_debit += row["total_spending"]

        result += f"\n\nTotal Spending (90 days): ${total_debit:.2f}"
        return result
    except Exception as e:
        return f"Error analyzing spending: {str(e)}"


@tool("Get Account Statement")
def get_account_statement(account_id: str = DEMO_ACCOUNT_ID) -> str:
    """
    Generates a summary account statement for the current period.
    Simulates querying the Transactions MCP Server.

    Args:
        account_id: The account identifier (defaults to demo account)

    Returns:
        A formatted account statement
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get account info
        cursor.execute(
            "SELECT customer_name, balance, currency FROM accounts WHERE account_id = ?",
            (account_id,),
        )
        account = cursor.fetchone()

        if not account:
            return f"Account {account_id} not found."

        # Get transaction summary
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN transaction_type = 'DEBIT' THEN amount ELSE 0 END) as total_debits,
                SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE 0 END) as total_credits,
                COUNT(*) as transaction_count
            FROM transactions
            WHERE account_id = ?
        """,
            (account_id,),
        )
        summary = cursor.fetchone()
        conn.close()

        total_debits = summary["total_debits"] or 0
        total_credits = summary["total_credits"] or 0

        statement = f"""
        Account Statement - {account_id}
        Customer: {account['customer_name']}
        Current Balance: {account['currency']} {account['balance']:.2f}
        
        Transaction Summary (Last 90 Days):
        - Total Credits: ${total_credits:.2f}
        - Total Debits: ${total_debits:.2f}
        - Net Change: ${total_credits - total_debits:.2f}
        - Transaction Count: {summary['transaction_count']}
        """
        return statement
    except Exception as e:
        return f"Error generating statement: {str(e)}"


# ============================================================================
# SERVICE AGENT TOOLS (MCP: Service/Ticketing Server)
# ============================================================================


@tool("Get Service Requests")
def get_service_requests(account_id: str = DEMO_ACCOUNT_ID) -> str:
    """
    Retrieves all service requests (tickets) for an account.
    Simulates querying the Service MCP Server.

    Args:
        account_id: The account identifier (defaults to demo account)

    Returns:
        A formatted string with service requests
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT request_id, request_type, status, description, 
                   created_date, updated_date, resolution_notes
            FROM service_requests
            WHERE account_id = ?
            ORDER BY updated_date DESC
        """,
            (account_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No service requests found for account {account_id}."

        result = f"Service Requests for {account_id}:\n"
        for row in rows:
            result += f"\n- Request ID: {row['request_id']}"
            result += f"\n  Type: {row['request_type']}"
            result += f"\n  Status: {row['status']}"
            result += f"\n  Description: {row['description']}"
            result += f"\n  Created: {row['created_date']} | Updated: {row['updated_date']}"
            if row["resolution_notes"]:
                result += f"\n  Notes: {row['resolution_notes']}"
            result += "\n"

        return result
    except Exception as e:
        return f"Error retrieving service requests: {str(e)}"


@tool("Create Service Request")
def create_service_request(
    account_id: str,
    request_type: str,
    description: str,
    request_id: Optional[str] = None,
) -> str:
    """
    Creates a new service request (ticket) for an account.
    Simulates querying the Service MCP Server.

    Args:
        account_id: The account identifier
        request_type: Type of request (e.g., "Change of Address", "Cheque Book Issuance", "KYC Update")
        description: Description of the request
        request_id: Optional custom request ID (auto-generated if not provided)

    Returns:
        Confirmation message with request details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = ?", (account_id,))
        if not cursor.fetchone():
            return f"Account {account_id} not found."

        # Generate request ID if not provided
        if not request_id:
            cursor.execute("SELECT MAX(CAST(SUBSTR(request_id, 3) AS INTEGER)) FROM service_requests")
            max_id = cursor.fetchone()[0] or 0
            request_id = f"SR{max_id + 1:03d}"

        from datetime import datetime

        now = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            INSERT INTO service_requests 
            (request_id, account_id, request_type, status, description, 
             created_date, updated_date)
            VALUES (?, ?, ?, 'PENDING', ?, ?, ?)
        """,
            (request_id, account_id, request_type, description, now, now),
        )
        conn.commit()
        conn.close()

        return f"""
        Service Request Created Successfully:
        - Request ID: {request_id}
        - Account: {account_id}
        - Type: {request_type}
        - Status: PENDING
        - Description: {description}
        - Created: {now}
        
        Your request has been submitted and is being processed.
        """
    except Exception as e:
        return f"Error creating service request: {str(e)}"


@tool("Get Service Request Status")
def get_service_request_status(request_id: str) -> str:
    """
    Retrieves the status of a specific service request.
    Simulates querying the Service MCP Server.

    Args:
        request_id: The service request identifier

    Returns:
        A formatted string with request status details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT request_id, account_id, request_type, status, description,
                   created_date, updated_date, resolution_notes
            FROM service_requests
            WHERE request_id = ?
        """,
            (request_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return f"Service request {request_id} not found."

        status_info = f"""
        Service Request Status:
        - Request ID: {row['request_id']}
        - Account: {row['account_id']}
        - Type: {row['request_type']}
        - Status: {row['status']}
        - Description: {row['description']}
        - Created: {row['created_date']}
        - Last Updated: {row['updated_date']}
        """

        if row["resolution_notes"]:
            status_info += f"\n- Resolution Notes: {row['resolution_notes']}"

        return status_info
    except Exception as e:
        return f"Error retrieving request status: {str(e)}"


# ============================================================================
# UTILITY TOOLS
# ============================================================================


@tool("Search Transactions by Merchant")
def search_transactions_by_merchant(
    account_id: str = DEMO_ACCOUNT_ID, merchant: str = "Amazon"
) -> str:
    """
    Searches for transactions from a specific merchant.

    Args:
        account_id: The account identifier (defaults to demo account)
        merchant: The merchant name to search for

    Returns:
        A formatted string with matching transactions
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT transaction_id, date, amount, description, balance_after
            FROM transactions
            WHERE account_id = ? AND merchant = ?
            ORDER BY date DESC
        """,
            (account_id, merchant),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No transactions found from {merchant} for account {account_id}."

        result = f"Transactions from {merchant} for {account_id}:\n"
        total = 0
        for row in rows:
            result += f"\n- {row['date']}: ${row['amount']:.2f} - {row['description']}"
            total += row["amount"]

        result += f"\n\nTotal: ${total:.2f} ({len(rows)} transactions)"
        return result
    except Exception as e:
        return f"Error searching transactions: {str(e)}"
