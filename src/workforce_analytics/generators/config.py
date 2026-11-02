"""Configuration for synthetic workforce data generation.

All generation parameters live here so the shape of the dataset can be
changed without touching generator logic.
"""

from datetime import date

# Reproducibility — same seed gives identical output on every run
RANDOM_SEED = 42
# Output location
OUTPUT_DIR = "data/raw"

# Volume
N_EMPLOYEES = 2000
START_DATE = date(2025, 4, 1)
END_DATE = date(2026, 3, 31)

# Departments — the real-world list, before any source-system mangling
DEPARTMENTS = [
    "Medicine",
    "Surgery",
    "Women and Children",
    "Cancer and Specialist",
    "Infrastructure",
    "Corporate",
]

# Staff groups and their contracted weekly hours
STAFF_GROUPS = {
    "Nursing and Midwifery": 37.5,
    "Medical and Dental": 40.0,
    "Administrative and Clerical": 37.5,
    "Allied Health Professional": 37.5,
    "Estates and Ancillary": 37.5,
}

# Agenda for Change bands
AFC_BANDS = ["2", "3", "4", "5", "6", "7", "8a", "8b", "8c"]

# Medical grades
MEDICAL_GRADES = ["Consultant", "SAS", "ST3", "ST4", "FY1", "FY2", "SHO"]

# Deliberate data quality problems — proportion of rows affected
MESS = {
    "orphan_employee_rate": 0.03,
    "duplicate_row_rate": 0.01,
    "null_department_rate": 0.02,
    "trailing_space_rate": 0.05,
    "mixed_case_rate": 0.05,
}