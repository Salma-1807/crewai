"""
database_setup.py
Generates a mock SQLite banking database with realistic dummy data.
Run this script once to initialize the bank_data.db file.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "bank_data.db"


def create_database():
    """Create SQLite database with banking tables."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create Accounts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'ACTIVE',
            phone TEXT,
            email TEXT,
            created_date TEXT,
            kyc_status TEXT DEFAULT 'VERIFIED'
        )
    """
    )

    # Create Transactions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            balance_after REAL NOT NULL,
            merchant TEXT,
            category TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    """
    )

    # Create Service Requests table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS service_requests (
            request_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            request_type TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            description TEXT,
            created_date TEXT,
            updated_date TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    """
    )

    conn.commit()
    print("✓ Tables created successfully")
    return conn, cursor


def populate_accounts(cursor, conn):
    """Populate accounts table with mock data."""
    accounts = [
        (
            "ACC001",
            "John Doe",
            "Checking",
            5250.75,
            "USD",
            "ACTIVE",
            "+1-555-0101",
            "john.doe@email.com",
            "2022-01-15",
            "VERIFIED",
        ),
        (
            "ACC002",
            "Jane Smith",
            "Savings",
            12500.00,
            "USD",
            "ACTIVE",
            "+1-555-0102",
            "jane.smith@email.com",
            "2021-06-20",
            "VERIFIED",
        ),
        (
            "ACC003",
            "Michael Johnson",
            "Money Market",
            75000.50,
            "USD",
            "ACTIVE",
            "+1-555-0103",
            "michael.j@email.com",
            "2020-03-10",
            "VERIFIED",
        ),
        (
            "ACC004",
            "Sarah Williams",
            "Checking",
            3200.25,
            "USD",
            "ACTIVE",
            "+1-555-0104",
            "sarah.w@email.com",
            "2023-02-14",
            "VERIFIED",
        ),
        (
            "ACC005",
            "Robert Brown",
            "Business",
            150000.00,
            "USD",
            "ACTIVE",
            "+1-555-0105",
            "robert.b@email.com",
            "2019-11-01",
            "VERIFIED",
        ),
        (
            "ACC006",
            "Emily Davis",
            "Savings",
            45000.75,
            "USD",
            "ACTIVE",
            "+1-555-0106",
            "emily.d@email.com",
            "2022-05-22",
            "VERIFIED",
        ),
        (
            "ACC007",
            "David Martinez",
            "Checking",
            8900.99,
            "USD",
            "ACTIVE",
            "+1-555-0107",
            "david.m@email.com",
            "2021-09-11",
            "VERIFIED",
        ),
        (
            "ACC008",
            "Lisa Anderson",
            "Premium Savings",
            250000.00,
            "USD",
            "ACTIVE",
            "+1-555-0108",
            "lisa.a@email.com",
            "2018-04-05",
            "VERIFIED",
        ),
        (
            "ACC009",
            "James Taylor",
            "Checking",
            1500.50,
            "USD",
            "ACTIVE",
            "+1-555-0109",
            "james.t@email.com",
            "2023-08-18",
            "PENDING",
        ),
        (
            "ACC010",
            "Patricia White",
            "Savings",
            67500.00,
            "USD",
            "INACTIVE",
            "+1-555-0110",
            "patricia.w@email.com",
            "2020-12-30",
            "VERIFIED",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO accounts 
        (account_id, customer_name, account_type, balance, currency, status, 
         phone, email, created_date, kyc_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        accounts,
    )

    conn.commit()
    print(f"✓ {len(accounts)} accounts inserted")


def populate_transactions(cursor, conn):
    """Populate transactions table with mock data."""
    transactions = []
    transaction_id_counter = 1000

    account_ids = [f"ACC{i:03d}" for i in range(1, 11)]
    merchants = [
        "Amazon",
        "Whole Foods",
        "Shell Gas Station",
        "Starbucks",
        "Netflix",
        "Apple Store",
        "Walmart",
        "Target",
        "Uber",
        "DoorDash",
    ]
    categories = [
        "Shopping",
        "Groceries",
        "Gas",
        "Food & Dining",
        "Entertainment",
        "Electronics",
        "Retail",
        "Retail",
        "Transportation",
        "Food Delivery",
    ]

    base_date = datetime.now() - timedelta(days=90)

    for account_id in account_ids:
        current_balance = random.uniform(1000, 80000)
        for _ in range(12):  # 12 transactions per account
            days_ago = random.randint(0, 90)
            trans_date = base_date + timedelta(days=days_ago)
            transaction_id = f"TXN{transaction_id_counter:07d}"
            transaction_id_counter += 1

            amount = round(random.uniform(10, 500), 2)
            trans_type = random.choice(["DEBIT", "CREDIT"])
            if trans_type == "DEBIT":
                current_balance -= amount
            else:
                current_balance += amount

            merchant = random.choice(merchants)
            category_idx = merchants.index(merchant)

            transactions.append(
                (
                    transaction_id,
                    account_id,
                    trans_type,
                    amount,
                    f"{trans_type} transaction at {merchant}",
                    trans_date.strftime("%Y-%m-%d %H:%M:%S"),
                    round(current_balance, 2),
                    merchant,
                    categories[category_idx],
                )
            )

    cursor.executemany(
        """
        INSERT INTO transactions 
        (transaction_id, account_id, transaction_type, amount, description, 
         date, balance_after, merchant, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        transactions,
    )

    conn.commit()
    print(f"✓ {len(transactions)} transactions inserted")


def populate_service_requests(cursor, conn):
    """Populate service_requests table with mock data."""
    service_requests = [
        (
            "SR001",
            "ACC001",
            "Change of Address",
            "COMPLETED",
            "Address change request to 123 New St",
            "2024-01-10",
            "2024-01-15",
            "Address updated successfully",
        ),
        (
            "SR002",
            "ACC002",
            "Cheque Book Issuance",
            "COMPLETED",
            "Request for new cheque book",
            "2024-01-12",
            "2024-01-18",
            "Cheque book dispatched",
        ),
        (
            "SR003",
            "ACC003",
            "KYC Update",
            "COMPLETED",
            "Update KYC information",
            "2024-01-08",
            "2024-01-10",
            "KYC details updated and verified",
        ),
        (
            "SR004",
            "ACC004",
            "Card Replacement",
            "PENDING",
            "Lost credit card - need replacement",
            "2024-01-20",
            "2024-01-20",
            "In process",
        ),
        (
            "SR005",
            "ACC005",
            "Loan Application",
            "IN_PROGRESS",
            "Personal loan inquiry",
            "2024-01-15",
            "2024-01-19",
            "Documents received, under review",
        ),
        (
            "SR006",
            "ACC006",
            "Change of Address",
            "PENDING",
            "Address change to 456 Oak Ave",
            "2024-01-18",
            "2024-01-18",
            "Awaiting verification",
        ),
        (
            "SR007",
            "ACC007",
            "Cheque Book Issuance",
            "PENDING",
            "Request for cheque book",
            "2024-01-19",
            "2024-01-19",
            "Queued for dispatch",
        ),
        (
            "SR008",
            "ACC008",
            "Investment Inquiry",
            "IN_PROGRESS",
            "Information on investment products",
            "2024-01-14",
            "2024-01-18",
            "Portfolio options provided",
        ),
        (
            "SR009",
            "ACC009",
            "KYC Update",
            "PENDING",
            "Complete KYC verification",
            "2024-01-19",
            "2024-01-19",
            "Pending document submission",
        ),
        (
            "SR010",
            "ACC002",
            "Account Closure",
            "IN_PROGRESS",
            "Request to close account",
            "2024-01-16",
            "2024-01-19",
            "Final balance verification in progress",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO service_requests 
        (request_id, account_id, request_type, status, description, 
         created_date, updated_date, resolution_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        service_requests,
    )

    conn.commit()
    print(f"✓ {len(service_requests)} service requests inserted")


def init_database():
    """Initialize the complete database with all tables and data."""
    # Remove existing database if present (for fresh start)
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("✓ Removed existing database")

    conn, cursor = create_database()
    populate_accounts(cursor, conn)
    populate_transactions(cursor, conn)
    populate_service_requests(cursor, conn)

    cursor.close()
    conn.close()
    print(f"\n✓ Database successfully created at: {DB_PATH}")


if __name__ == "__main__":
    init_database()
