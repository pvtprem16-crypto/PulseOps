
import pandas as pd


DATA_PATH = "data/tickets.csv"


def load_data():
    """Load the PulseOps ticket dataset."""
    return pd.read_csv(DATA_PATH)


def check_missing_values(df):
    """Check missing values in the dataset."""
    return df.isnull().sum()


def check_duplicate_ids(df):
    """Check duplicate ticket IDs."""
    return df["ticket_id"].duplicated().sum()


def check_timestamp_integrity(df):
    """Validate ticket lifecycle timestamps."""

    df = df.copy()

    timestamp_columns = [
        "created_at",
        "first_response_at",
        "resolved_at",
        "closed_at",
    ]

    for column in timestamp_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    checks = {
        "Responses before creation": (
            df["first_response_at"] < df["created_at"]
        ).sum(),

        "Responses after resolution": (
            (df["first_response_at"] > df["resolved_at"])
            & df["resolved_at"].notna()
        ).sum(),

        "Resolutions before creation": (
            df["resolved_at"] < df["created_at"]
        ).sum(),

        "Closures before resolution": (
            (df["closed_at"] < df["resolved_at"])
            & df["closed_at"].notna()
        ).sum(),

        "Closures before creation": (
            df["closed_at"] < df["created_at"]
        ).sum(),
    }

    return checks


def check_status_logic(df):
    """Validate status and timestamp consistency."""

    checks = {
        "Closed without resolution": (
            (df["status"] == "Closed")
            & df["resolved_at"].isna()
        ).sum(),

        "Closed without closure": (
            (df["status"] == "Closed")
            & df["closed_at"].isna()
        ).sum(),

        "Resolved without resolution": (
            (df["status"] == "Resolved")
            & df["resolved_at"].isna()
        ).sum(),

        "Resolved with closure": (
            (df["status"] == "Resolved")
            & df["closed_at"].notna()
        ).sum(),

        "Open tickets with response": (
            (df["status"] == "Open")
            & df["first_response_at"].notna()
        ).sum(),

        "Unresolved statuses with resolution": (
            (~df["status"].isin(["Resolved", "Closed"]))
            & df["resolved_at"].notna()
        ).sum(),
    }

    return checks


def check_reopen_logic(df):
    """Validate reopened ticket flags."""

    mismatch = (
        df["is_reopened"] != (df["reopen_count"] > 0)
    ).sum()

    return mismatch


def check_numeric_values(df):
    """Check numeric columns for invalid negative values."""

    numeric_columns = [
        "first_response_minutes",
        "resolution_minutes",
        "reopen_count",
    ]

    checks = {}

    for column in numeric_columns:
        checks[f"Negative values in {column}"] = (
            (df[column] < 0).sum()
        )

    return checks


def check_sla_consistency(df):
    """Validate SLA flags against actual timestamps and deadlines."""

    df = df.copy()

    timestamp_columns = [
        "first_response_at",
        "resolved_at",
        "response_deadline",
        "resolution_deadline",
    ]

    for column in timestamp_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    response_expected = (
        df["first_response_at"] <= df["response_deadline"]
    )

    resolution_expected = (
        df["resolved_at"] <= df["resolution_deadline"]
    )

    response_mismatch = (
        df["first_response_at"].notna()
        & (df["response_sla_met"] != response_expected)
    ).sum()

    resolution_mismatch = (
        df["resolved_at"].notna()
        & (df["resolution_sla_met"] != resolution_expected)
    ).sum()

    return {
        "Response SLA flag mismatches": response_mismatch,
        "Resolution SLA flag mismatches": resolution_mismatch,
    }


def check_categorical_values(df):
    """Validate categorical values against expected categories."""

    valid_categories = {
        "priority": ["Low", "Medium", "High", "Critical"],
        "status": ["Open", "In Progress", "Pending", "Resolved", "Closed"],
        "channel": ["Email", "Portal", "Phone", "Monitoring"],
    }

    results = {}

    for column, valid_values in valid_categories.items():
        invalid_count = (~df[column].isin(valid_values)).sum()

        results[f"Invalid values in {column}"] = invalid_count

    return results


def run_quality_checks():
    """Run all data quality checks and display a report."""

    df = load_data()

    print("=" * 60)
    print("PULSEOPS DATA QUALITY REPORT")
    print("=" * 60)

    print("\n1. MISSING VALUES")
    print(check_missing_values(df))

    print("\n2. DUPLICATE TICKET IDs")
    print(check_duplicate_ids(df))

    print("\n3. TIMESTAMP INTEGRITY")
    for check, result in check_timestamp_integrity(df).items():
        print(f"{check}: {result}")

    print("\n4. STATUS LOGIC")
    for check, result in check_status_logic(df).items():
        print(f"{check}: {result}")

    print("\n5. REOPEN LOGIC")
    print("Reopen flag mismatches:", check_reopen_logic(df))

    print("\n6. NUMERIC VALIDATION")
    for check, result in check_numeric_values(df).items():
        print(f"{check}: {result}")

    print("\n7. CATEGORICAL VALIDATION")
    for check, result in check_categorical_values(df).items():
        print(f"{check}: {result}")

    print("\n8. SLA CONSISTENCY")
    for check, result in check_sla_consistency(df).items():
        print(f"{check}: {result}")

    print("\n" + "=" * 60)
    print("DATA QUALITY REPORT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_quality_checks()
