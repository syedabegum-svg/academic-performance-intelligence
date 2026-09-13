# Academic Performance Intelligence

A small, demo-ready Python and pandas project for analyzing a student marks CSV.

## Workflows

1. **Student Performance Analyzer**: overall percentage, subject averages, weak subjects, and insights.
2. **At-Risk Student Detector**: risk levels and practical intervention suggestions.
3. **Faculty Academic Report Generator**: concise report with trends, top performers, attention list, and recommendations.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
python3 main.py analyzer
python3 main.py at-risk
python3 main.py report
python3 main.py all
```

To use a different CSV, pass `--csv path/to/marks.csv`. It must contain `student_id`, `name`, and one or more subject columns with marks from 0 to 100.

## Test

```bash
python3 -m pytest
```
