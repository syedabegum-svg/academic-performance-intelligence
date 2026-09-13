"""Command-line entry point for the three academic-intelligence workflows."""

from __future__ import annotations

import argparse
from pathlib import Path

from academic_intelligence import (
    at_risk_student_detector,
    faculty_academic_report_generator,
    student_performance_analyzer,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze student marks CSV data.")
    parser.add_argument(
        "workflow", choices=["analyzer", "at-risk", "report", "all"],
        help="Workflow to run",
    )
    parser.add_argument(
        "--csv", default="data/student_marks.csv", help="Path to the marks CSV",
    )
    args = parser.parse_args()
    csv_path = Path(args.csv)

    if args.workflow in ("analyzer", "all"):
        analysis = student_performance_analyzer(csv_path)
        print("\nSTUDENT PERFORMANCE ANALYZER")
        print(analysis["student_performance"].to_string(index=False))
        print("\nSubject-wise averages")
        print(analysis["subject_averages"].to_string())
        print("\nKey insights")
        print("\n".join(f"- {insight}" for insight in analysis["insights"]))

    if args.workflow in ("at-risk", "all"):
        print("\nAT-RISK STUDENT DETECTOR")
        print(at_risk_student_detector(csv_path).to_string(index=False))

    if args.workflow in ("report", "all"):
        print("\n" + faculty_academic_report_generator(csv_path))


if __name__ == "__main__":
    main()
