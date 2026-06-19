"""Shared 4.0 grade scale used across the academic module."""

# Letter grade → grade points (4.0 scale).
GRADE_SCALE = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0,
    'F': 0.0,
}

# Selection options for the grade field (ordered best → worst).
GRADE_SELECTION = [(g, g) for g in GRADE_SCALE]
