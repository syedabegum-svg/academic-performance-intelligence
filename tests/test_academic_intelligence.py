from pathlib import Path

from academic_intelligence import at_risk_student_detector, faculty_academic_report_generator


CSV = Path(__file__).parents[1] / "data" / "student_marks.csv"


def test_at_risk_detector_flags_high_risk_students():
    risks = at_risk_student_detector(CSV)
    arjun = risks.loc[risks["student_id"] == "S007"].iloc[0]
    assert arjun["risk_level"] == "High"
    assert "mathematics" in arjun["weak_subjects"]


def test_faculty_report_has_core_sections():
    report = faculty_academic_report_generator(CSV)
    assert "Subject trends:" in report
    assert "Top performers:" in report
    assert "Students needing attention:" in report
