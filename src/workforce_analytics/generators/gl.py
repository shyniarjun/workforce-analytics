"""Generate the General Ledger establishment extract.

Produces one row per budgeted position per cost centre per month.
This is the finance view: funded posts in FTE, with no people attached.
Division names follow the GL's own convention, which differs from both
ESR and StaffDirect.
"""

import csv
import random
from datetime import date
from pathlib import Path

from workforce_analytics.generators import config
from workforce_analytics.generators.esr import month_ends

N_COST_CENTRES = 90


def gl_division(department: str) -> str:
    """GL uses full names with 'Division' appended, but no numeric prefix."""
    return f"{department} Division"


def generate_establishment(seed: int = config.RANDOM_SEED) -> list[dict]:
    """Build budgeted establishment rows."""
    rng = random.Random(seed + 3)

    # Build a stable set of cost centres, each belonging to one department
    cost_centres = []
    for i in range(N_COST_CENTRES):
        cost_centres.append(
            {
                "code": f"{20000 + i * 7:07d}",
                "department": rng.choice(config.DEPARTMENTS),
                "name": f"Cost Centre {20000 + i * 7}",
            }
        )

    # Each cost centre funds a few positions at different grades
    positions = []
    for cc in cost_centres:
        for _ in range(rng.randint(2, 6)):
            staff_group = rng.choice(list(config.STAFF_GROUPS.keys()))
            if staff_group == "Medical and Dental":
                grade = rng.choice(config.MEDICAL_GRADES)
            else:
                grade = f"Band {rng.choice(config.AFC_BANDS)}"

            positions.append(
                {
                    "cost_centre": cc,
                    "staff_group": staff_group,
                    "grade": grade,
                    "budgeted_fte": round(rng.uniform(0.5, 12.0), 2),
                }
            )

    snapshots = month_ends(config.START_DATE, config.END_DATE)
    rows = []

    for snapshot_date in snapshots:
        for pos in positions:
            cc = pos["cost_centre"]

            # Budgets drift slightly month to month
            fte = pos["budgeted_fte"] + round(rng.uniform(-0.5, 0.5), 2)
            fte = max(0.0, round(fte, 2))

            # A small number of negative GL values — these need flagging, not summing
            if rng.random() < 0.015:
                fte = -abs(round(rng.uniform(0.5, 3.0), 2))

            rows.append(
                {
                    "Period": snapshot_date.strftime("%b-%y"),
                    "Division": gl_division(cc["department"]),
                    "Cost Centre Code": cc["code"],
                    "Cost Centre Name": cc["name"],
                    "Subjective Code": f"{rng.randint(100000, 199999)}",
                    "Staff Group": pos["staff_group"],
                    "Grade": pos["grade"],
                    "Budgeted FTE": fte,
                }
            )

    return rows


def write_establishment(rows: list[dict], output_dir: str = config.OUTPUT_DIR) -> Path:
    """Write the rows to CSV and return the file path."""
    path = Path(output_dir) / "gl_establishment.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return path


if __name__ == "__main__":
    establishment = generate_establishment()
    out = write_establishment(establishment)
    print(f"Wrote {len(establishment):,} rows to {out}")