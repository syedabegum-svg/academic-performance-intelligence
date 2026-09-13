"""Reusable functions for student-mark analysis and academic reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

IDENTITY_COLUMNS = ("student_id", "name")


def load_marks(csv_path: str | Path) -> tuple[pd.DataFrame, list[str]]:
    """Load and validate a marks CSV, returning data and subject column names."""
    marks = pd.read_csv(csv_path)
    missing = [column for column in IDENTITY_COLUMNS if column not in marks.columns]
    if missing:
        raise ValueError(f"CSV is missing required column(s): {', '.join(missing)}")

    subjects = [column for column in marks.columns if column not in IDENTITY_COLUMNS]
    if not subjects:
        raise ValueError("CSV must contain at least one subject column.")
    marks[subjects] = marks[subjects].apply(pd.to_numeric, errors="raise")
    if marks[subjects].isna().any().any():
        raise ValueError("Marks cannot be blank.")
    if ((marks[subjects] < 0) | (marks[subjects] > 100)).any().any():
        raise ValueError("Marks must be between 0 and 100.")
    return marks, subjects


def add_performance_metrics(marks: pd.DataFrame, subjects: Iterable[str]) -> pd.DataFrame:
    """Add total marks and overall percentage to a copy of the marks table."""
    result = marks.copy()
    subject_list = list(subjects)
    result["total_marks"] = result[subject_list].sum(axis=1)
    result["overall_percentage"] = result[subject_list].mean(axis=1).round(2)
    return result


def weak_subjects_by_student(
    marks: pd.DataFrame, subjects: Iterable[str], threshold: float = 60
) -> pd.Series:
    """Return a comma-separated weak-subject list for every student."""
    subject_list = list(subjects)
    return marks[subject_list].apply(
        lambda row: ", ".join(column for column in subject_list if row[column] < threshold)
        or "None",
        axis=1,
    )


def student_performance_analyzer(
    csv_path: str | Path, weak_threshold: float = 60
) -> dict[str, object]:
    """Workflow 1: calculate overall and subject-wise performance and insights."""
    marks, subjects = load_marks(csv_path)
    performance = add_performance_metrics(marks, subjects)
    performance["weak_subjects"] = weak_subjects_by_student(
        marks, subjects, weak_threshold
    )
    subject_averages = marks[subjects].mean().sort_values().round(2)
    weakest_subject = subject_averages.index[0]
    strongest_subject = subject_averages.index[-1]
    insights = [
        f"Class average: {performance['overall_percentage'].mean():.2f}%.",
        f"Strongest subject: {strongest_subject} ({subject_averages[strongest_subject]:.2f}%).",
        f"Priority subject: {weakest_subject} ({subject_averages[weakest_subject]:.2f}%).",
        f"Students below {weak_threshold:.0f}% overall: "
        f"{(performance['overall_percentage'] < weak_threshold).sum()}.",
    ]
    return {
        "student_performance": performance,
        "subject_averages": subject_averages,
        "insights": insights,
    }


def _risk_level(overall_percentage: float, weak_subject_count: int) -> str:
    if overall_percentage < 50 or weak_subject_count >= 3:
        return "High"
    if overall_percentage < 60 or weak_subject_count >= 2:
        return "Medium"
    if overall_percentage < 70 or weak_subject_count == 1:
        return "Low"
    return "On Track"


def _intervention_suggestion(risk_level: str) -> str:
    suggestions = {
        "High": "Create an individual improvement plan; arrange weekly tutoring and guardian follow-up.",
        "Medium": "Provide targeted practice, a mentor check-in, and review progress in two weeks.",
        "Low": "Offer subject-specific revision material and monitor the next assessment.",
        "On Track": "Continue enrichment and regular progress monitoring.",
    }
    return suggestions[risk_level]


def at_risk_student_detector(
    csv_path: str | Path, weak_threshold: float = 60
) -> pd.DataFrame:
    """Workflow 2: classify students and suggest appropriate interventions."""
    marks, subjects = load_marks(csv_path)
    result = add_performance_metrics(marks, subjects)
    result["weak_subjects"] = weak_subjects_by_student(marks, subjects, weak_threshold)
    result["weak_subject_count"] = (marks[subjects] < weak_threshold).sum(axis=1)
    result["risk_level"] = result.apply(
        lambda row: _risk_level(row["overall_percentage"], row["weak_subject_count"]), axis=1
    )
    result["intervention_suggestion"] = result["risk_level"].map(_intervention_suggestion)
    columns = [
        "student_id", "name", "overall_percentage", "weak_subjects",
        "weak_subject_count", "risk_level", "intervention_suggestion",
    ]
    order = {"High": 0, "Medium": 1, "Low": 2, "On Track": 3}
    return result[columns].sort_values(
        "risk_level", key=lambda values: values.map(order)
    ).reset_index(drop=True)


def faculty_academic_report_generator(csv_path: str | Path) -> str:
    """Workflow 3: produce a compact, human-readable faculty report."""
    analysis = student_performance_analyzer(csv_path)
    students: pd.DataFrame = analysis["student_performance"]  # type: ignore[assignment]
    subject_averages: pd.Series = analysis["subject_averages"]  # type: ignore[assignment]
    risks = at_risk_student_detector(csv_path)
    top = students.nlargest(3, "overall_percentage")
    at_risk = risks[risks["risk_level"].isin(["High", "Medium"])]
    weakest = subject_averages.head(2)

    report = [
        "ACADEMIC PERFORMANCE REPORT",
        "=" * 27,
        f"Class size: {len(students)}",
        f"Class average: {students['overall_percentage'].mean():.2f}%",
        f"Pass rate (>= 50%): {(students['overall_percentage'] >= 50).mean() * 100:.1f}%",
        "",
        "Subject trends:",
        *[f"- {subject}: {average:.2f}%" for subject, average in subject_averages.items()],
        "",
        "Top performers:",
        *[f"- {row.name}: {row.overall_percentage:.2f}%" for row in top.itertuples()],
        "",
        "Students needing attention:",
        *(
            [f"- {row.name} — {row.risk_level} risk ({row.overall_percentage:.2f}%); "
             f"weak areas: {row.weak_subjects}" for row in at_risk.itertuples()]
            or ["- None identified at high or medium risk."]
        ),
        "",
        "Recommendations:",
        f"- Prioritize support in {', '.join(weakest.index)}.",
        "- Use weekly check-ins for high- and medium-risk students.",
        "- Recognize top performers and offer enrichment tasks.",
    ]
    return "\n".join(report)
