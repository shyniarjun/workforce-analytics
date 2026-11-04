"""Generate the StaffDirect agency extract.

Produces one row per agency worker per week, with seven day-total
columns. This wide format must be unpivoted downstream. Agency workers
have no ESR employee number, so this fact cannot link to dim_employee.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from workforce_analytics.generators import config

AGENCIES = [
    "Medacs Healthcare",
    "Pulse Nursing",
    "Thornbury Nursing",
    "ID Medical",
    "Holt Doctors",
    "Athona",
]

LABOUR_GRADES = [
    "Consultant",
    "Specialty Locum",
    "SPR",
    "Registered Nurse",
    "Healthcare Assistant",
    "Radiographer",
]

DAY_COLUMNS = [
    "Monday Total",
    "Tuesday Total",
    "Wednesday Total",
    "Thursday Total",
    "Friday Total",
    "Saturday Total",
    "Sunday Total",
]

N_PLACEMENT_WEEKS = 4500


def staffdirect_division(department: str) -> str:
    """StaffDirect uses abbreviated uppercase division codes."""
    return department.upper()[:12]


def week_endings(start: date, end: date) -> list[date]:
    """Return every Sunday in the range."""
    days_to_sunday = (6 - start.weekday()) % 7
    first_sunday = start + timedelta(days=days_to_sunday)

    sundays = []
    current = first_sunday
    while current <= end:
        sundays.append(current)
        current += timedelta(days=7)

    return sundays


def generate_agency_weeks(seed: int = config.RANDOM_SEED) -> list[dict]:
    """Build agency placement rows, one per worker per week."""
    rng = random.Random(seed + 2)
    fake = Faker("en_GB")
    Faker.seed(seed + 2)

    # A stable pool of agency workers who recur across weeks
    workers = [
        {
            "name": fake.name(),
            "agency": rng.choice(AGENCIES),
            "labour_grade": rng.choice(LABOUR_GRADES),
            "department": rng.choice(config.DEPARTMENTS),
        }
        for _ in range(400)
    ]

    sundays = week_endings(config.START_DATE, config.END_DATE)
    rows = []

    for _ in range(N_PLACEMENT_WEEKS):
        worker = rng.choice(workers)
        week_ending = rng.choice(sundays)

        # Most placements are a few days, not a full week
        days_worked = rng.choices([1, 2, 3, 4, 5, 6, 7], weights=[5, 10, 20, 25, 25, 10, 5])[0]
        worked_indices = rng.sample(range(7), days_worked)

        row = {
            "Candidate Name": worker["name"],
            "Agency Name": worker["agency"],
            "Actual Week Worked": week_ending.strftime("%Y-%m-%d"),
            "Labour Grade": worker["labour_grade"],
            "Division Name": staffdirect_division(worker["department"]),
        }

        for i, col in enumerate(DAY_COLUMNS):
            if i in worked_indices:
                row[col] = rng.choice([7.5, 7.5, 10.0, 12.0, 12.5])
            else:
                row[col] = 0

        # Credit notes: cancelled and rebooked timesheets produce negatives
        if rng.random() < 0.02:
            for col in DAY_COLUMNS:
                row[col] = -row[col]

        row["Standard Rate"] = f"£{rng.randint(25, 120)}.00"

        rows.append(row)

    return rows


def write_agency_weeks(rows: list[dict], output_dir: str = config.OUTPUT_DIR) -> Path:
    """Write the rows to CSV and return the file path."""
    path = Path(output_dir) / "staffdirect_agency.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return path


if __name__ == "__main__":
    weeks = generate_agency_weeks()
    out = write_agency_weeks(weeks)
    print(f"Wrote {len(weeks):,} rows to {out}")