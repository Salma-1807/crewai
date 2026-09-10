# Banking Assistant with CrewAI 🏦

A conversational multi-agent banking assistant built with **CrewAI**, **Streamlit**, and the **Qwen 3.6-27B** LLM. Features a Coordinator Agent that delegates tasks to specialized sub-agents for account management, transaction analysis, and service requests.

## Overview

This project implements a sophisticated banking assistant with:

- **Multi-Agent Architecture**: Coordinator + 3 specialized agents (Accounts, Transactions, Service)
- **CrewAI Integration**: Autonomous agents with role-based tasks
- **Streamlit UI**: Beautiful conversational chat interface
- **Mock MCP Servers**: Simulated MCP tool integrations via Python functions
- **Rate Limit Handling**: Automatic retry logic with exponential backoff for 1000 RPM limit
- **SQLite Database**: Mock banking data (accounts, transactions, service requests)
- **Session State Management**: Full chat history with Streamlit

## Tech Stack

- **Backend**: Python 3.10+, CrewAI 0.50+, LangChain
- **Frontend**: Streamlit 1.39+
- **LLM**: Qwen 3.6-27B (via OpenAI-compatible endpoint)
- **Database**: SQLite3
- **Concurrency**: Tenacity (retry logic with exponential backoff)

## Project Structure

```
crewai/
├── requirements.txt              # Python dependencies
├── database_setup.py             # SQLite database initialization
├── mcp_tools.py                  # Tool definitions (simulated MCP endpoints)
├── agents_and_tasks.py           # CrewAI agents, tasks, and crew
├── app.py                        # Streamlit application
├── bank_data.db                  # Generated SQLite database (created on first run)
└── README.md                     # This file
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database

```bash
python database_setup.py
```

You should see:
```
✓ Tables created successfully
✓ 10 accounts inserted
✓ 120 transactions inserted
✓ 10 service requests inserted
✓ Database successfully created at: .../bank_data.db
```

### 4. Configure LLM Provider (Important!)

This project is configured for Groq. The app reads values from a local `.env` file during development and from Streamlit secrets when deployed to Streamlit Community Cloud.

```bash
# Create a .env file in the project directory
copy .env.example .env
```

Then edit `.env` and set:
```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=groq/openai/gpt-oss-120b
```

For Streamlit Cloud, create a `.streamlit/secrets.toml` file with:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "groq/openai/gpt-oss-120b"
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Rate Limit Handling

The application implements comprehensive rate limit safeguards:

### 1. **max_rpm Configuration**
```python
max_rpm=900  # Crew and Agent settings (10% buffer below 1000 limit)
```

### 2. **Tenacity Retry Logic**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
```
Automatically retries on:
- HTTP 429 (Too Many Requests)
- Connection errors
- Timeout errors

### 3. **Request Throttling**
```python
MIN_REQUEST_INTERVAL = 0.1  # Minimum delay between requests
```

### 4. **Graceful UI Handling**
- Rate limit warnings displayed in the sidebar
- Informative error messages with recovery steps
- Automatic retry on subsequent messages

## Agent Architecture

### Coordinator Agent (Banking Operations Manager)
- Analyzes customer inquiries
- Determines appropriate specialist(s)
- Routes requests to sub-agents
- Available tools: All specialized tools

### Accounts Agent (Account Details Specialist)
- Account balance inquiries
- Account type and profile information
- KYC status checks
- Tools: `get_account_balance`, `get_account_details`, `list_all_accounts`

### Transaction Agent (Transaction & Statement Specialist)
- Transaction history retrieval
- Spending analysis by category
- Account statement generation
- Merchant search functionality
- Tools: `get_transaction_history`, `get_spending_analysis`, `get_account_statement`, `search_transactions_by_merchant`

### Service Agent (Customer Service Specialist)
- Service request creation and tracking
- Change of address processing
- Cheque book issuance requests
- KYC update management
- Tools: `get_service_requests`, `create_service_request`, `get_service_request_status`

## Mock Database

### Demo Accounts (ACC001-ACC010)
- John Doe, Jane Smith, Michael Johnson, etc.
- Various account types: Checking, Savings, Money Market, Business, Premium Savings
- Balance range: $1,500 - $250,000

### Generated Data
- **120 transactions**: Spread across 90 days with realistic categories
- **10 service requests**: Various statuses (PENDING, IN_PROGRESS, COMPLETED)
- **Merchant data**: Amazon, Walmart, Starbucks, Uber, etc.

### Accessing Other Accounts
Use the account selector in the sidebar to switch between the 10 demo accounts.

## Example Queries

Try these questions:

**Account Information:**
- "What's my current account balance?"
- "Show me my account details"
- "List all accounts"

**Transactions:**
- "Show me my transaction history"
- "What's my spending by category?"
- "Generate my account statement"
- "Find all transactions at Amazon"

**Service Requests:**
- "I need to change my address"
- "Request a new cheque book"
- "Update my KYC information"
- "Check status of my service request"

## Error Handling

The application handles:

| Error | Handling | Recovery |
|-------|----------|----------|
| HTTP 429 (Rate Limit) | Automatic retry with exponential backoff | Sidebar warning + auto-retry on next message |
| Database not initialized | Graceful error message | "Initialize Database" button in sidebar |
| LLM API errors | Clear error message with context | Check credentials in .env |
| Tool execution errors | Logged + friendly error to user | User can retry or rephrase |

## Streamlit Features

### Session State Management
- Persistent chat history across reruns
- Account selection state
- Rate limit warning state
- Database initialization tracking

### Custom UI
- Themed chat messages (user vs assistant)
- Information boxes with styling
- Sidebar configuration panel
- Expandable sections for instructions

### Performance
- Cached crew initialization (expensive operation)
- Efficient SQLite queries
- Minimal reruns with proper state management

## Troubleshooting

### Issue: "Database not found"
**Solution**: Click "Initialize Database" in the sidebar or run:
```bash
python database_setup.py
```

### Issue: "401 Unauthorized" or "API Key Error"
**Solution**: Check your .env file and ensure:
```bash
OPENAI_API_KEY=your_valid_key
OPENAI_API_BASE=https://api.provider.com/v1
```

### Issue: "Rate limit hit - HTTP 429"
**Solution**: This is normal. The system automatically retries with exponential backoff. Wait 30-60 seconds and send another message.

### Issue: "Qwen model not found"
**Solution**: Ensure your API provider supports `qwen/qwen3.6-27b`. Update the model name in `agents_and_tasks.py` if needed.

### Issue: Streamlit stuck/frozen
**Solution**: 
1. Stop the app (Ctrl+C)
2. Clear cache: `rm -rf .streamlit/cache*`
3. Restart: `streamlit run app.py`

## Configuration Reference

### agents_and_tasks.py
```python
MAX_RPM = 900                    # Rate limit (default: 900 for safety)
MAX_TOKENS_PER_REQUEST = 4000    # Token limit per request
MIN_REQUEST_INTERVAL = 0.1       # Minimum seconds between requests
```

### database_setup.py
```python
DB_PATH = "bank_data.db"         # Database location
# Tables: accounts, transactions, service_requests
```

### app.py
```python
DEMO_ACCOUNT_ID = "ACC001"       # Default account for demo
```

## Production Considerations

⚠️ **This is a proof-of-concept implementation. For production:**

1. **Authentication**: Implement proper OAuth2/JWT authentication (currently hardcoded)
2. **Authorization**: Add role-based access control
3. **Real Database**: Replace SQLite with PostgreSQL/MySQL
4. **Real MCP**: Integrate actual MCP servers instead of Python functions
5. **Security**: Use secure credential storage (e.g., AWS Secrets Manager)
6. **Monitoring**: Add comprehensive logging and error tracking
7. **Testing**: Implement unit tests, integration tests, and load testing
8. **Scaling**: Deploy on cloud infrastructure with proper load balancing

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the agent outputs in verbose mode (check terminal)
3. Ensure all prerequisites are installed: `pip list | grep -E "crewai|streamlit|langchain"`

## License

This project is provided as-is for demonstration purposes.

## Additional Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Documentation](https://python.langchain.com)
- [Tenacity Documentation](https://tenacity.readthedocs.io)

---

**Happy Banking! 🏦💰**
