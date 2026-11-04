"""Generate the HealthRota bank shift extract.

Produces one row per bank shift worked. Unlike the ESR snapshot this is
an event fact. Includes deliberate problems: orphan employee numbers
(bank-only workers never on ESR), inconsistent shift type casing, and
missing actual-hours values.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from workforce_analytics.generators import config
from workforce_analytics.generators.employees import generate_employees

SHIFT_TYPES = ["Early", "Late", "Night", "Long Day", "OnCall"]

BOOKING_REASONS = [
    "Sickness cover",
    "Vacancy",
    "Additional activity",
    "Annual leave cover",
    "Escalation beds",
    "Maternity cover",
]

N_SHIFTS = 18000


def healthrota_department(department: str) -> str:
    """HealthRota stores the bare department name, no ESR prefix."""
    return department


def generate_bank_shifts(seed: int = config.RANDOM_SEED) -> list[dict]:
    """Build bank shift rows."""
    rng = random.Random(seed + 1)
    employees = generate_employees(seed)

    # Bank-only workers: employee numbers that will never appear in ESR
    n_orphans = int(config.N_EMPLOYEES * config.MESS["orphan_employee_rate"] * 10)
    orphan_numbers = [90000 + i for i in range(n_orphans)]

    day_span = (config.END_DATE - config.START_DATE).days
    rows = []

    for _ in range(N_SHIFTS):
        use_orphan = rng.random() < 0.15

        if use_orphan:
            employee_number = rng.choice(orphan_numbers)
            department = rng.choice(config.DEPARTMENTS)
            grade = f"Band {rng.choice(config.AFC_BANDS)}"
        else:
            emp = rng.choice(employees)
            employee_number = emp["employee_number"]
            department = emp["department"]
            grade = emp["grade"]

        shift_date = config.START_DATE + timedelta(days=rng.randint(0, day_span))
        shift_type = rng.choice(SHIFT_TYPES)

        booked_hours = {
            "Early": 7.5,
            "Late": 7.5,
            "Night": 10.0,
            "Long Day": 12.5,
            "OnCall": 12.0,
        }[shift_type]

        # Actual hours missing on some rows, forcing fallback logic downstream
        if rng.random() < 0.25:
            actual_hours = ""
        else:
            actual_hours = round(booked_hours + rng.choice([-1, -0.5, 0, 0, 0, 0.5, 1]), 2)

        # Inconsistent casing on shift type
        if rng.random() < 0.10:
            shift_type_out = shift_type.upper()
        elif rng.random() < 0.10:
            shift_type_out = shift_type.lower()
        else:
            shift_type_out = shift_type

        rows.append(
            {
                "Esr Person Number": employee_number,
                "Date Of Shift": shift_date.strftime("%d/%m/%Y"),
                "Shift Type": shift_type_out,
                "Booked Hours": booked_hours,
                "Total Hours Worked": actual_hours,
                "Booked Grade": grade,
                "Rota": healthrota_department(department),
                "Reason": rng.choice(BOOKING_REASONS),
            }
        )

    return rows


def write_bank_shifts(rows: list[dict], output_dir: str = config.OUTPUT_DIR) -> Path:
    """Write the rows to CSV and return the file path."""
    path = Path(output_dir) / "healthrota_bank_shifts.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return path


if __name__ == "__main__":
    shifts = generate_bank_shifts()
    out = write_bank_shifts(shifts)
    print(f"Wrote {len(shifts):,} rows to {out}")