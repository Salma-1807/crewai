# Quick Start Guide 🚀

Get your Banking Assistant running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure API Credentials (1 minute)

Copy `.env.example` to `.env` and add your credentials:

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and OPENAI_API_BASE
```

**What you need:**
- ✅ API key for Qwen 3.6-27B model provider
- ✅ API endpoint URL (OpenAI-compatible)

Example for common providers:
```bash
# Together AI
OPENAI_API_KEY=xxx-xxxxxxxx
OPENAI_API_BASE=https://api.together.xyz/v1

# Azure OpenAI (if using)
OPENAI_API_KEY=your-key
OPENAI_API_BASE=https://your-resource.openai.azure.com/

# Other providers
OPENAI_API_KEY=your-key
OPENAI_API_BASE=https://your-provider.com/v1
```

## Step 3: Initialize Database (1 minute)

```bash
python database_setup.py
```

Expected output:
```
✓ Tables created successfully
✓ 10 accounts inserted
✓ 120 transactions inserted
✓ 10 service requests inserted
✓ Database successfully created at: .../bank_data.db
```

## Step 4: Start the Application (1 minute)

```bash
streamlit run app.py
```

The browser will automatically open to `http://localhost:8501`

## Step 5: Test It! (1 minute)

Try these queries:
- "What's my account balance?"
- "Show me my recent transactions"
- "I need to change my address"

---

## Using the Startup Scripts

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

These scripts will automatically handle steps 1-3 for you!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Verify virtual environment is activated: `python -m pip list` should show installed packages |
| "API Key invalid" | Check your .env file: `cat .env` (or `type .env` on Windows) |
| "Database not found" | Run: `python database_setup.py` |
| Port 8501 already in use | Run: `streamlit run app.py --server.port 8502` |

---

## Architecture Overview

```
Your Question
    ↓
[Streamlit UI]
    ↓
[Coordinator Agent] analyzes request
    ↓
Routes to appropriate specialist:
├── [Accounts Agent] → Account info
├── [Transaction Agent] → Spending/history
└── [Service Agent] → Service requests
    ↓
[SQLite Database] (mock banking data)
    ↓
Response → Streamlit UI
```

---

## Key Features Enabled

✅ Rate limiting (900 RPM)
✅ Automatic retry logic (exponential backoff)
✅ Session state (chat history)
✅ 10 demo accounts with realistic data
✅ 3 specialized agents + coordinator
✅ Multi-turn conversation support

---

## Next Steps

1. Explore different queries for each agent type
2. Review `README.md` for full documentation
3. Check `agents_and_tasks.py` to understand the rate limiting implementation
4. Modify demo accounts in `database_setup.py` for custom testing

---

**Questions?** Check the README.md or review the code comments in each file.

**Ready to chat with your banking assistant!** 🏦💬
