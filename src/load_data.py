import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "tickets.csv"
DB_PATH = BASE_DIR / "data" / "pulseops.db"


def load_tickets():
    """Replace the tickets table contents with the current CSV snapshot.

    The refresh is transactional: if the insertion fails, the prior contents
    remain available. The database must first be initialized with init_db.py.
    """

    df = pd.read_csv(CSV_PATH)
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("BEGIN")
        connection.execute("DELETE FROM tickets")
        df.to_sql("tickets", connection, if_exists="append", index=False)
        connection.commit()

        print("Ticket data loaded successfully!")
        print(f"Records loaded: {len(df)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_tickets()
