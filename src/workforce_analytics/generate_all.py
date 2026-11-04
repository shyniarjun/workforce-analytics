"""Entry point: generate all synthetic source files.

Runs every generator in sequence and reports what was written. This is
the single command a new user runs after cloning the repo.
"""

import logging
import sys
import time

from workforce_analytics.generators import esr, gl, healthrota, staffdirect

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    """Set up console logging with timestamps and severity."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


def main() -> int:
    """Generate every source file. Returns a process exit code."""
    configure_logging()
    started = time.perf_counter()

    jobs = [
        ("ESR staff in post", esr.generate_esr_extract, esr.write_esr_extract),
        ("HealthRota bank shifts", healthrota.generate_bank_shifts, healthrota.write_bank_shifts),
        ("StaffDirect agency", staffdirect.generate_agency_weeks, staffdirect.write_agency_weeks),
        ("GL establishment", gl.generate_establishment, gl.write_establishment),
    ]

    total_rows = 0
    failures = 0

    for name, generate, write in jobs:
        try:
            logger.info("Generating %s ...", name)
            rows = generate()
            path = write(rows)
            total_rows += len(rows)
            logger.info("  wrote %s rows to %s", f"{len(rows):,}", path)
        except Exception:
            failures += 1
            logger.exception("  FAILED to generate %s", name)

    elapsed = time.perf_counter() - started

    if failures:
        logger.error("Finished with %d failure(s) in %.1fs", failures, elapsed)
        return 1

    logger.info("Generated %s rows across %d files in %.1fs", f"{total_rows:,}", len(jobs), elapsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())