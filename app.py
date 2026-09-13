import streamlit as st
import pandas as pd

from academic_intelligence import (
    load_marks,
    student_performance_analyzer,
    at_risk_student_detector,
    faculty_academic_report_generator,
)

st.set_page_config(
    page_title="Academic Performance Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Academic Performance Intelligence")
st.caption("Three repeatable workflows for smarter academic decision-making")

st.sidebar.header("Choose Workflow")

workflow = st.sidebar.radio(
    "Select:",
    [
        "Student Performance Analyzer",
        "At-Risk Student Detector",
        "Faculty Academic Report",
    ],
)

uploaded_file = st.sidebar.file_uploader(
    "Upload student marks CSV",
    type=["csv"],
)

csv_source = uploaded_file if uploaded_file is not None else "data/student_marks.csv"

marks, subjects = load_marks(csv_source)

st.sidebar.success(f"{len(marks)} students loaded")


# ---------------------------------------------------------
# WORKFLOW 1: STUDENT PERFORMANCE ANALYZER
# ---------------------------------------------------------

if workflow == "Student Performance Analyzer":

    st.header("📈 Student Performance Analyzer")

    st.write(
        "Analyze overall performance, subject averages, weak subjects, "
        "and key academic insights."
    )

    result = student_performance_analyzer(csv_source)

    performance = result["student_performance"]
    subject_averages = result["subject_averages"]
    insights = result["insights"]

    class_average = performance["overall_percentage"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Class Average",
        f"{class_average:.2f}%"
    )

    col2.metric(
        "Students Below 60%",
        int((performance["overall_percentage"] < 60).sum())
    )

    strongest_subject = max(
        subjects,
        key=lambda subject: performance[subject].mean()
    )

    col3.metric(
        "Strongest Subject",
        strongest_subject.replace("_", " ").title()
    )

    st.subheader("Student Performance")

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Subject-wise Averages")

    subject_data = pd.DataFrame(
        {
            "Subject": subjects,
            "Average": subject_averages,
        }
    )
    st.bar_chart(
        subject_data.set_index("Subject")
    )

    st.subheader("Key Insights")

    for insight in insights:
        st.write(f"• {insight}")


# ---------------------------------------------------------
# WORKFLOW 2: AT-RISK STUDENT DETECTOR
# ---------------------------------------------------------

elif workflow == "At-Risk Student Detector":

    st.header("⚠️ At-Risk Student Detector")

    st.write(
        "Identify students who need academic attention and "
        "generate intervention suggestions."
    )

    result = at_risk_student_detector(csv_source)

    risk_counts = result["risk_level"].value_counts()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "High Risk",
        int(risk_counts.get("High", 0))
    )

    col2.metric(
        "Medium Risk",
        int(risk_counts.get("Medium", 0))
    )

    col3.metric(
        "Low Risk",
        int(risk_counts.get("Low", 0))
    )

    col4.metric(
        "On Track",
        int(risk_counts.get("On Track", 0))
    )

    st.subheader("Students Requiring Attention")

    attention = result[
        result["risk_level"].isin(
            ["High", "Medium", "Low"]
        )
    ]

    st.dataframe(
        attention,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Risk Distribution")

    st.bar_chart(risk_counts)

    st.info(
        "Intervention suggestions are generated from each "
        "student's performance and weak-subject profile."
    )


# ---------------------------------------------------------
# WORKFLOW 3: FACULTY ACADEMIC REPORT
# ---------------------------------------------------------

else:

    st.header("📋 Faculty Academic Report Generator")

    st.write(
        "Generate a concise academic report for faculty review "
        "and intervention planning."
    )

    report = faculty_academic_report_generator(csv_source)

    st.subheader("Generated Academic Report")

    st.code(
        report,
        language="text"
    )

    st.download_button(
        label="⬇️ Download Academic Report",
        data=report,
        file_name="academic_performance_report.txt",
        mime="text/plain",
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Academic Performance Intelligence • Python + Pandas + Streamlit"
)
