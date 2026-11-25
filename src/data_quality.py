import json
from datetime import datetime

import pandas as pd


DATA_PATH = "data/tickets.csv"
REPORT_PATH = "data/processed/data_quality_report.json"


def load_data():
    """Load the PulseOps ticket dataset."""
    return pd.read_csv(DATA_PATH)


def check_missing_values(df):
    """Check missing values in the dataset."""
    return df.isnull().sum()


def check_duplicate_ids(df):
    """Check duplicate ticket IDs."""
    return int(df["ticket_id"].duplicated().sum())


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

        "In Progress without response": (
            (df["status"] == "In Progress")
            & df["first_response_at"].isna()
        ).sum(),

        "Pending without response": (
            (df["status"] == "Pending")
            & df["first_response_at"].isna()
        ).sum(),
    }

    return checks


def check_reopen_logic(df):
    """Validate reopened ticket flags."""

    mismatch = (
        df["is_reopened"] != (df["reopen_count"] > 0)
    ).sum()

    return int(mismatch)


def check_numeric_values(df):
    """Check numeric columns for invalid negative values."""

    numeric_columns = [
        "first_response_minutes",
        "resolution_minutes",
        "reopen_count",
    ]

    checks = {}

    for column in numeric_columns:
        checks[f"Negative values in {column}"] = int(
            (df[column] < 0).sum()
        )

    return checks


def check_sla_consistency(df):
    """Validate SLA flags against timestamps and deadlines."""

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
        "Response SLA flag mismatches": int(response_mismatch),
        "Resolution SLA flag mismatches": int(resolution_mismatch),
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

        results[f"Invalid values in {column}"] = int(invalid_count)

    return results


def build_validation_results(df):
    """Collect all validation checks into a structured dictionary."""

    results = {}

    # Duplicate ID validation
    results["Duplicate ticket IDs"] = check_duplicate_ids(df)

    # Timestamp validation
    results.update(check_timestamp_integrity(df))

    # Status validation
    results.update(check_status_logic(df))

    # Reopen validation
    results["Reopen flag mismatches"] = check_reopen_logic(df)

    # Numeric validation
    results.update(check_numeric_values(df))

    # Categorical validation
    results.update(check_categorical_values(df))

    # SLA validation
    results.update(check_sla_consistency(df))

    return results


def calculate_quality_score(validation_results):
    """Calculate overall dataset quality score."""

    total_checks = len(validation_results)

    passed_checks = sum(
        1 for violations in validation_results.values()
        if violations == 0
    )

    failed_checks = total_checks - passed_checks

    score = (
        (passed_checks / total_checks) * 100
        if total_checks > 0
        else 0
    )

    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "quality_score": round(score, 2),
    }


def build_report(df, validation_results, score_data):
    """Build a structured data quality report."""

    check_details = []

    for check_name, violations in validation_results.items():
        check_details.append({
            "check_name": check_name,
            "violations": int(violations),
            "status": "PASS" if violations == 0 else "FAIL",
        })

    missing_values = {
        column: int(count)
        for column, count in check_missing_values(df).items()
        if count > 0
    }

    report = {
        "report_generated_at": datetime.now().isoformat(),
        "dataset": {
            "file": DATA_PATH,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
        },
        "quality_summary": score_data,
        "missing_values": missing_values,
        "validation_checks": check_details,
    }

    return report


def export_report(report):
    """Export the data quality report as JSON."""

    import os

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"\nReport exported to: {REPORT_PATH}")


def print_report(report):
    """Display the data quality report."""

    summary = report["quality_summary"]

    print("=" * 70)
    print("PULSEOPS DATA QUALITY REPORT")
    print("=" * 70)

    print("\nDATASET INFORMATION")
    print(f"Rows: {report['dataset']['rows']}")
    print(f"Columns: {report['dataset']['columns']}")

    print("\nQUALITY SCORE")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed Checks: {summary['passed_checks']}")
    print(f"Failed Checks: {summary['failed_checks']}")
    print(f"Quality Score: {summary['quality_score']}%")

    print("\nVALIDATION RESULTS")

    for check in report["validation_checks"]:
        status = check["status"]
        name = check["check_name"]
        violations = check["violations"]

        print(f"[{status}] {name}: {violations}")

    print("\nMISSING VALUES (INFORMATIONAL)")

    if report["missing_values"]:
        for column, count in report["missing_values"].items():
            print(f"{column}: {count}")
    else:
        print("No missing values detected.")

    print("\n" + "=" * 70)
    print("DATA QUALITY REPORT COMPLETED")
    print("=" * 70)


def run_quality_checks():
    """Run all data quality checks and generate a report."""

    df = load_data()

    validation_results = build_validation_results(df)

    score_data = calculate_quality_score(validation_results)

    report = build_report(
        df,
        validation_results,
        score_data,
    )

    print_report(report)

    export_report(report)


if __name__ == "__main__":
    run_quality_checks()