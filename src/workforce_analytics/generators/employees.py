"""Generate the master employee list.

This is the source of truth for who exists. Every other generator draws
from this pool, so referential integrity starts here.
"""

import random

from faker import Faker

from workforce_analytics.generators import config


def generate_employees(seed: int = config.RANDOM_SEED) -> list[dict]:
    """Build a list of employee records.

    Args:
        seed: Random seed, so the same employees are produced every run.

    Returns:
        A list of dicts, one per employee.
    """
    random.seed(seed)
    fake = Faker("en_GB")
    Faker.seed(seed)

    employees = []

    for i in range(config.N_EMPLOYEES):
        staff_group = random.choice(list(config.STAFF_GROUPS.keys()))

        if staff_group == "Medical and Dental":
            grade = random.choice(config.MEDICAL_GRADES)
        else:
            grade = f"Band {random.choice(config.AFC_BANDS)}"

        employees.append(
            {
                "employee_number": 10000 + i,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "department": random.choice(config.DEPARTMENTS),
                "staff_group": staff_group,
                "grade": grade,
                "fte": random.choice([1.0, 1.0, 1.0, 0.8, 0.6, 0.5]),
            }
        )

    return employees


if __name__ == "__main__":
    staff = generate_employees()
    print(f"Generated {len(staff)} employees")
    print(staff[0])