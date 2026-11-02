"""Generate the ESR staff-in-post extract.

Produces one row per employee per month-end, mimicking a monthly ESR
export. Includes deliberate data quality problems: inconsistent date
formats, division prefixes, trailing whitespace, missing departments
and duplicate rows.
"""

import csv
import random
from datetime import date
from pathlib import Path

from workforce_analytics.generators import config
from workforce_analytics.generators.employees import generate_employees


def month_ends(start: date, end: date) -> list[date]:
    """Return the last calendar day of each month in the range."""
    ends = []
    year, month = start.year, start.month

    while date(year, month, 1) <= end:
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        last_day = date.fromordinal(next_month.toordinal() - 1)
        ends.append(last_day)

        year, month = next_month.year, next_month.month

    return ends


def esr_division(department: str) -> str:
    """Apply ESR's division naming convention."""
    return f"279 {department} Division"


def messy_date(d: date, rng: random.Random) -> str:
    """Return a date string in one of three inconsistent formats."""
    fmt = rng.choice(["%d/%m/%Y", "%Y-%m-%d", "%d-%b-%y"])
    return d.strftime(fmt)


def generate_esr_extract(seed: int = config.RANDOM_SEED) -> list[dict]:
    """Build the staff-in-post snapshot rows."""
    rng = random.Random(seed)
    employees = generate_employees(seed)
    snapshots = month_ends(config.START_DATE, config.END_DATE)

    # Give each employee a start and (sometimes) an end month
    tenure = {}
    for emp in employees:
        first = rng.choices(
            range(len(snapshots)),
            weights=[10] + [1] * (len(snapshots) - 1),
        )[0]
        leaves = rng.random() < 0.12
        last = rng.randint(first, len(snapshots) - 1) if leaves else len(snapshots) - 1
        tenure[emp["employee_number"]] = (first, last)

    rows = []

    for idx, snapshot_date in enumerate(snapshots):
        for emp in employees:
            first, last = tenure[emp["employee_number"]]
            if not (first <= idx <= last):
                continue

            name = emp["last_name"]
            if rng.random() < config.MESS["trailing_space_rate"]:
                name = name + "  "
            if rng.random() < config.MESS["mixed_case_rate"]:
                name = name.upper()

            department = emp["department"]
            if rng.random() < config.MESS["null_department_rate"]:
                division = ""
            else:
                division = esr_division(department)

            row = {
                "Employee Number": emp["employee_number"],
                "First Name": emp["first_name"],
                "Last Name": name,
                "Division": division,
                "Staff Group": emp["staff_group"],
                "Grade": emp["grade"],
                "FTE": emp["fte"],
                "Effective Date": messy_date(snapshot_date, rng),
            }
            rows.append(row)

            if rng.random() < config.MESS["duplicate_row_rate"]:
                rows.append(dict(row))

    return rows


def write_esr_extract(rows: list[dict], output_dir: str = config.OUTPUT_DIR) -> Path:
    """Write the rows to CSV and return the file path."""
    path = Path(output_dir) / "esr_staff_in_post.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return path


if __name__ == "__main__":
    extract = generate_esr_extract()
    out = write_esr_extract(extract)
    print(f"Wrote {len(extract):,} rows to {out}")