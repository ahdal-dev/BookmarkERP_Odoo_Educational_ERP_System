"""
Synthetic Data Generator for Zewail City University Educational ERP System
Based on the complete academic structure from https://www.zewailcity.edu.eg/

Includes:
- 5 Schools: Engineering, Science, CSAI, Business, CEPD
- All Undergraduate Programs (17 programs)
- All Graduate Programs (MSc, PhD, Diplomas)
- All Minors (15 minors)
- Complete Course Catalogs (300+ courses)

Author: AI-Assisted Development
Project: Zewail City Educational ERP System
"""

import json
import asyncio
import random
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from dataclasses import dataclass, asdict
from pathlib import Path

# Google Gemini imports
import google.generativeai as genai

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAecSxwbw_plgCx0LjD9uTTv7f4Zh0ijZM")
OUTPUT_DIR = Path("generated_data")
OUTPUT_DIR.mkdir(exist_ok=True)

# Configure Google Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# ============================================================
# ZEWAIL CITY COMPLETE ACADEMIC STRUCTURE
# Based on https://www.zewailcity.edu.eg/
# ============================================================

ZEWAIL_CITY_STRUCTURE = {
    "university": {
        "name": "Zewail City of Science and Technology",
        "abbreviation": "ZC",
        "ust_name": "University of Science and Technology",
        "location": "Ahmed Zewail Road, October Gardens, 6th of October City, Giza, Egypt",
        "website": "https://www.zewailcity.edu.eg/",
        "email_domain": "zewailcity.edu.eg",
        "founder": "Dr. Ahmed Zewail (Nobel Laureate)"
    },
    
    "schools": {
        "School of Engineering": {
            "code": "ENGR",
            "description": "Programs emphasizing hands-on experience, innovation, soft skills, and multidisciplinary education",
            "undergraduate_programs": [
                "Aerospace Engineering",
                "Communications and Information Engineering",
                "Environmental Engineering",
                "Nanotechnology and Nanoelectronics Engineering",
                "Renewable Energy Engineering",
                "Energy and Bioprocess Engineering"
            ],
            "graduate_programs": [
                "MSc in Artificial Intelligence Engineering",
                "MSc in Engineering Mathematics",
                "MSc in Nanotechnology and Nanoelectronics Engineering",
                "PhD in Engineering Mathematics",
                "PhD in Nanotechnology and Nanoelectronics Engineering",
                "Advanced Diploma in Artificial Intelligence Engineering",
                "Advanced Diploma in Engineering Mathematics",
                "Advanced Diploma in Nanotechnology and Nanoelectronics Engineering",
                "Basic Diploma in Artificial Intelligence Engineering",
                "Basic Diploma in Engineering Mathematics",
                "Basic Diploma in Nanotechnology and Nanoelectronics Engineering"
            ]
        },
        "School of Science": {
            "code": "SCI",
            "description": "Programs providing graduates with ability to identify, formulate, and solve technical and scientific problems",
            "undergraduate_programs": [
                "Biomedical Sciences",
                "Nano Science",
                "Physics of Universe",
                "Materials Science"
            ],
            "graduate_programs": [
                "MSc in Applied Mathematics",
                "MSc in Biomedical Sciences",
                "MSc in Nano-Science",
                "MSc in Physics",
                "PhD in Biomedical Sciences",
                "PhD in Nano-Science",
                "PhD in Physics",
                "PhD in Applied Mathematics"
            ]
        },
        "School of Computational Sciences and Artificial Intelligence": {
            "code": "CSAI",
            "description": "Analytics and data mining as core competency, mastering all aspects of computational tools",
            "undergraduate_programs": [
                "Data Science and Artificial Intelligence",
                "Software Development",
                "Information Technology"
            ],
            "graduate_programs": []
        },
        "School of Business": {
            "code": "BUS",
            "description": "Pioneering research-led education with focus on sustainable development and data analytics",
            "undergraduate_programs": [
                "Actuarial Analysis and Risk Management",
                "Finance and Investment Management",
                "Marketing, Entrepreneurship and Innovation Management",
                "Operations, Supply Chain and Technology Management"
            ],
            "graduate_programs": []
        },
        "School of Continuing Education and Professional Development": {
            "code": "CEPD",
            "description": "Professional development and continuing education programs",
            "undergraduate_programs": [],
            "graduate_programs": []
        }
    },
    
    "undergraduate_programs": {
        # School of Engineering Programs
        "Aerospace Engineering": {
            "code": "SPC",
            "school": "School of Engineering",
            "degree": "BSc in Aerospace Engineering",
            "duration_years": 4,
            "total_credits": 160,
            "specializations": [
                "Aerodynamics",
                "Propulsion Systems",
                "Flight Mechanics and Control",
                "Space Systems Engineering",
                "Aircraft Structures",
                "Avionics"
            ]
        },
        "Communications and Information Engineering": {
            "code": "CIE",
            "school": "School of Engineering",
            "degree": "BSc in Communications and Information Engineering",
            "duration_years": 4,
            "total_credits": 160,
            "specializations": [
                "Communication Technologies",
                "Artificial Intelligence",
                "High Performance Computing",
                "Robotics",
                "Signal Processing",
                "Wireless Communications"
            ]
        },
        "Environmental Engineering": {
            "code": "ENV",
            "school": "School of Engineering",
            "degree": "BSc in Environmental Engineering",
            "duration_years": 4,
            "total_credits": 160,
            "specializations": [
                "Water Resources Engineering",
                "Air Quality Engineering",
                "Waste Management",
                "Sustainable Development",
                "Environmental Impact Assessment"
            ]
        },
        "Nanotechnology and Nanoelectronics Engineering": {
            "code": "NANENG",
            "school": "School of Engineering",
            "degree": "BSc in Nanotechnology and Nanoelectronics Engineering",
            "duration_years": 4,
            "total_credits": 160,
            "specializations": [
                "Nano-VLSI Design",
                "Nano-Fabrication and MEMS",
                "Nano-photonics",
                "Quantum Devices",
                "Nanoelectronic Circuits"
            ]
        },
        "Renewable Energy Engineering": {
            "code": "REE",
            "school": "School of Engineering",
            "degree": "BSc in Renewable Energy Engineering",
            "duration_years": 4,
            "total_credits": 160,
            "specializations": [
                "Solar Energy (Concentrated Solar Power)",
                "Photovoltaic Systems (PV)",
                "Wind Energy",
                "Energy Storage and Grid Integration",
                "Smart Grids"
            ]
        },
        "Energy and Bioprocess Engineering": {
            "code": "EBE",
            "school": "School of Engineering",
            "degree": "BSc in Energy and Bioprocess Engineering",
            "duration_years": 4,
            "total_credits": 160,
            "specializations": [
                "Biofuels Production",
                "Bioprocess Design",
                "Sustainable Energy Systems",
                "Fermentation Technology",
                "Pharmaceutical Bioprocessing"
            ]
        },
        
        # School of Science Programs
        "Biomedical Sciences": {
            "code": "BMS",
            "school": "School of Science",
            "degree": "BSc in Biomedical Sciences",
            "duration_years": 4,
            "total_credits": 140,
            "concentrations": [
                "Molecular and Cell Biology",
                "Medical Sciences",
                "Computational Biology and Genomics",
                "Drug Design and Development",
                "Immunology and Microbiology"
            ]
        },
        "Nano Science": {
            "code": "NANOSC",
            "school": "School of Science",
            "degree": "BSc in Nano Science",
            "duration_years": 4,
            "total_credits": 140,
            "concentrations": [
                "Nano-medicine",
                "Bio-nanotechnology",
                "Nano Chemistry",
                "Nanophysics",
                "Nanomaterials"
            ]
        },
        "Physics of Universe": {
            "code": "PEU",
            "school": "School of Science",
            "degree": "BSc in Physics of Universe",
            "duration_years": 4,
            "total_credits": 140,
            "concentrations": [
                "Astrophysics",
                "High Energy Physics",
                "Cosmology",
                "Theoretical Physics",
                "Computational Physics"
            ]
        },
        "Materials Science": {
            "code": "MATSCI",
            "school": "School of Science",
            "degree": "BSc in Materials Science",
            "duration_years": 4,
            "total_credits": 140,
            "concentrations": [
                "Advanced Materials",
                "Functional Materials",
                "Computational Materials Science",
                "Biomaterials",
                "Electronic Materials"
            ]
        },
        
        # School of CSAI Programs
        "Data Science and Artificial Intelligence": {
            "code": "DSAI",
            "school": "School of Computational Sciences and Artificial Intelligence",
            "degree": "BSc in Data Science and Artificial Intelligence",
            "duration_years": 4,
            "total_credits": 145,
            "specializations": [
                "Machine Learning",
                "Big Data Analytics",
                "Computer Vision",
                "Natural Language Processing",
                "Deep Learning",
                "AI Applications"
            ]
        },
        "Software Development": {
            "code": "SW",
            "school": "School of Computational Sciences and Artificial Intelligence",
            "degree": "BSc in Software Development",
            "duration_years": 4,
            "total_credits": 145,
            "specializations": [
                "Web and Mobile Development",
                "Cloud Computing",
                "Software Architecture",
                "DevOps Engineering",
                "Full-Stack Development"
            ]
        },
        "Information Technology": {
            "code": "IT",
            "school": "School of Computational Sciences and Artificial Intelligence",
            "degree": "BSc in Information Technology",
            "duration_years": 4,
            "total_credits": 145,
            "specializations": [
                "Cybersecurity",
                "Network Administration",
                "Database Management",
                "IT Infrastructure",
                "Enterprise Systems"
            ]
        },
        
        # School of Business Programs
        "Actuarial Analysis and Risk Management": {
            "code": "BACT",
            "school": "School of Business",
            "degree": "BSc in Actuarial Analysis and Risk Management",
            "duration_years": 4,
            "total_credits": 140,
            "specializations": [
                "Insurance Risk Management",
                "Financial Risk Analytics",
                "Pension and Benefits",
                "Enterprise Risk Management"
            ]
        },
        "Finance and Investment Management": {
            "code": "FINC",
            "school": "School of Business",
            "degree": "BSc in Finance and Investment Management",
            "duration_years": 4,
            "total_credits": 140,
            "specializations": [
                "Investment Banking",
                "Portfolio Management",
                "Corporate Finance",
                "FinTech",
                "Financial Analytics"
            ]
        },
        "Marketing, Entrepreneurship and Innovation Management": {
            "code": "MKTG",
            "school": "School of Business",
            "degree": "BSc in Marketing, Entrepreneurship and Innovation Management",
            "duration_years": 4,
            "total_credits": 140,
            "specializations": [
                "Digital Marketing",
                "Startup Management",
                "Innovation Strategy",
                "Brand Management",
                "Social Entrepreneurship"
            ]
        },
        "Operations, Supply Chain and Technology Management": {
            "code": "SCHN",
            "school": "School of Business",
            "degree": "BSc in Operations, Supply Chain and Technology Management",
            "duration_years": 4,
            "total_credits": 140,
            "specializations": [
                "Supply Chain Analytics",
                "Operations Research",
                "Technology Management",
                "Logistics Management",
                "Quality Management"
            ]
        }
    },
    
    "graduate_programs": {
        # MSc Programs
        "MSc in Artificial Intelligence Engineering": {
            "code": "MSC-AIE",
            "school": "School of Engineering",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        "MSc in Engineering Mathematics": {
            "code": "MSC-EMATH",
            "school": "School of Engineering",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        "MSc in Nanotechnology and Nanoelectronics Engineering": {
            "code": "MSC-NANE",
            "school": "School of Engineering",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        "MSc in Applied Mathematics": {
            "code": "MSC-AMATH",
            "school": "School of Science",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        "MSc in Biomedical Sciences": {
            "code": "MSC-BMS",
            "school": "School of Science",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        "MSc in Nano-Science": {
            "code": "MSC-NANO",
            "school": "School of Science",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        "MSc in Physics": {
            "code": "MSC-PHYS",
            "school": "School of Science",
            "degree_type": "MSc",
            "duration_years": 2,
            "total_credits": 36
        },
        
        # PhD Programs
        "PhD in Engineering Mathematics": {
            "code": "PHD-EMATH",
            "school": "School of Engineering",
            "degree_type": "PhD",
            "duration_years": 4,
            "total_credits": 48
        },
        "PhD in Nanotechnology and Nanoelectronics Engineering": {
            "code": "PHD-NANE",
            "school": "School of Engineering",
            "degree_type": "PhD",
            "duration_years": 4,
            "total_credits": 48
        },
        "PhD in Biomedical Sciences": {
            "code": "PHD-BMS",
            "school": "School of Science",
            "degree_type": "PhD",
            "duration_years": 4,
            "total_credits": 48
        },
        "PhD in Nano-Science": {
            "code": "PHD-NANO",
            "school": "School of Science",
            "degree_type": "PhD",
            "duration_years": 4,
            "total_credits": 48
        },
        "PhD in Physics": {
            "code": "PHD-PHYS",
            "school": "School of Science",
            "degree_type": "PhD",
            "duration_years": 4,
            "total_credits": 48
        },
        "PhD in Applied Mathematics": {
            "code": "PHD-AMATH",
            "school": "School of Science",
            "degree_type": "PhD",
            "duration_years": 4,
            "total_credits": 48
        },
        
        # Diploma Programs
        "Advanced Diploma in Artificial Intelligence Engineering": {
            "code": "ADV-DIP-AIE",
            "school": "School of Engineering",
            "degree_type": "Advanced Diploma",
            "duration_years": 1,
            "total_credits": 24
        },
        "Basic Diploma in Artificial Intelligence Engineering": {
            "code": "BAS-DIP-AIE",
            "school": "School of Engineering",
            "degree_type": "Basic Diploma",
            "duration_years": 1,
            "total_credits": 18
        },
        "Advanced Diploma in Engineering Mathematics": {
            "code": "ADV-DIP-EMATH",
            "school": "School of Engineering",
            "degree_type": "Advanced Diploma",
            "duration_years": 1,
            "total_credits": 24
        },
        "Basic Diploma in Engineering Mathematics": {
            "code": "BAS-DIP-EMATH",
            "school": "School of Engineering",
            "degree_type": "Basic Diploma",
            "duration_years": 1,
            "total_credits": 18
        },
        "Advanced Diploma in Nanotechnology and Nanoelectronics Engineering": {
            "code": "ADV-DIP-NANE",
            "school": "School of Engineering",
            "degree_type": "Advanced Diploma",
            "duration_years": 1,
            "total_credits": 24
        },
        "Basic Diploma in Nanotechnology and Nanoelectronics Engineering": {
            "code": "BAS-DIP-NANE",
            "school": "School of Engineering",
            "degree_type": "Basic Diploma",
            "duration_years": 1,
            "total_credits": 18
        }
    },
    
    "minors": [
        {"name": "Minor in Biomedical Sciences", "code": "MIN-BMS", "credits": 18},
        {"name": "Minor in Information Engineering", "code": "MIN-IE", "credits": 18},
        {"name": "Minor in Waste Management Engineering", "code": "MIN-WME", "credits": 18},
        {"name": "Minor in Environmental Impact Assessment", "code": "MIN-EIA", "credits": 18},
        {"name": "Minor in Nanoelectronics Engineering", "code": "MIN-NANE", "credits": 18},
        {"name": "Minor in Photonics", "code": "MIN-PHOT", "credits": 18},
        {"name": "Minor in Fundamental Physics", "code": "MIN-PHYS", "credits": 18},
        {"name": "Minor in Artificial Intelligence and Big Data", "code": "MIN-AIBD", "credits": 18},
        {"name": "Minor in Game Design and Development", "code": "MIN-GDD", "credits": 18},
        {"name": "Minor in Application Development", "code": "MIN-APPD", "credits": 18},
        {"name": "Minor in Materials Science", "code": "MIN-MATS", "credits": 18},
        {"name": "Minor in Nano Science", "code": "MIN-NANO", "credits": 18},
        {"name": "Minor in Finance and Investment Management", "code": "MIN-FIM", "credits": 18},
        {"name": "Minor in Operations, Supply Chain, and Technology Management", "code": "MIN-OSCTM", "credits": 18},
        {"name": "Minor in Communications Engineering", "code": "MIN-CENG", "credits": 18}
    ]
}

# ============================================================
# HANDBOOK REFERENCES (Based on ZC Handbooks)
# ============================================================

HANDBOOK_REFERENCES = {
    "undergraduate": {
        "2025-2026": {
            "School of Engineering": [
                "Aerospace Engineering Handbook 2025-2026",
                "Communications and Information Engineering Handbook 2025-2026",
                "Environmental Engineering Handbook 2025-2026",
                "Nanotechnology and Nanoelectronics Engineering Handbook 2025-2026",
                "Renewable Energy Engineering Handbook 2025-2026",
                "Energy and Bioprocess Engineering Handbook 2025-2026"
            ],
            "School of Science": [
                "Biomedical Sciences Handbook 2025-2026",
                "Nano Science Handbook 2025-2026",
                "Physics of Universe Handbook 2025-2026",
                "Materials Science Handbook 2025-2026"
            ],
            "School of CSAI": [
                "Data Science and Artificial Intelligence Handbook 2025-2026",
                "Software Development Handbook 2025-2026",
                "Information Technology Handbook 2025-2026"
            ],
            "School of Business": [
                "Actuarial Analysis and Risk Management Handbook 2025-2026",
                "Finance and Investment Management Handbook 2025-2026",
                "Marketing, Entrepreneurship and Innovation Management Handbook 2025-2026",
                "Operations, Supply Chain and Technology Management Handbook 2025-2026"
            ]
        }
    },
    "graduate": {
        "2025-2026": {
            "School of Engineering": [
                "MSc in Artificial Intelligence Engineering Handbook 2025-2026",
                "MSc in Engineering Mathematics Handbook 2025-2026",
                "MSc in Nanotechnology and Nanoelectronics Engineering Handbook 2025-2026",
                "PhD in Engineering Mathematics Handbook 2025-2026",
                "PhD in Nanotechnology and Nanoelectronics Engineering Handbook 2025-2026"
            ],
            "School of Science": [
                "MSc in Applied Mathematics Handbook 2025-2026",
                "MSc in Biomedical Sciences Handbook 2025-2026",
                "MSc in Nano-Science Handbook 2025-2026",
                "MSc in Physics Handbook 2025-2026",
                "PhD in Biomedical Sciences Handbook 2025-2026",
                "PhD in Nano-Science Handbook 2025-2026",
                "PhD in Physics Handbook 2025-2026",
                "PhD in Applied Mathematics Handbook 2025-2026"
            ]
        }
    },
    "policies": {
        "grading_system": {
            "A": {"min_gpa": 3.70, "max_gpa": 4.00, "description": "Excellent"},
            "A-": {"min_gpa": 3.50, "max_gpa": 3.69, "description": "Excellent"},
            "B+": {"min_gpa": 3.30, "max_gpa": 3.49, "description": "Very Good"},
            "B": {"min_gpa": 3.00, "max_gpa": 3.29, "description": "Very Good"},
            "B-": {"min_gpa": 2.70, "max_gpa": 2.99, "description": "Good"},
            "C+": {"min_gpa": 2.50, "max_gpa": 2.69, "description": "Good"},
            "C": {"min_gpa": 2.00, "max_gpa": 2.49, "description": "Satisfactory"},
            "C-": {"min_gpa": 1.70, "max_gpa": 1.99, "description": "Satisfactory"},
            "D": {"min_gpa": 1.00, "max_gpa": 1.69, "description": "Poor"},
            "F": {"min_gpa": 0.00, "max_gpa": 0.99, "description": "Fail"}
        },
        "credit_requirements": {
            "engineering": {"total": 160, "major": 90, "general_education": 30, "electives": 40},
            "science": {"total": 140, "major": 80, "general_education": 30, "electives": 30},
            "csai": {"total": 145, "major": 85, "general_education": 30, "electives": 30},
            "business": {"total": 140, "major": 80, "general_education": 30, "electives": 30}
        },
        "academic_standing": {
            "good_standing": {"min_cgpa": 2.0},
            "probation": {"min_cgpa": 1.7, "max_cgpa": 1.99},
            "dismissal": {"max_cgpa": 1.69}
        }
    }
}

# ============================================================
# STUDY PLANS BY PROGRAM - USING ONLY VALID CATALOG COURSES
# Based on ZC Course Catalog and course level assignments
# Each program defines required courses per academic year
# ============================================================

STUDY_PLANS = {
    # ============================================================
    # SCHOOL OF ENGINEERING STUDY PLANS
    # ============================================================
    
    "Aerospace Engineering": {
        "code": "SPC",
        "total_credits": 160,
        "year_1": {
            "fall": ["CHEM 103", "ENGL 152", "CSCI 101","ENGR 102","ENGR 121","MATH 101","PHYS 115","PHYS 125"],
            "spring": ["CIE 101", "ENGL 153", "ENGR 105", "MATH 102","MATSCI 201","PHYS 116","PHYS 126","SPC 101"]
            },
        "year_2": {
            "fall": ["CIE 205", "ENGR 207", "MATH 201", "MATH 202","REE 202","SPC 228"],
            "spring": ["ENGR 201", "MATH 306", "REE 122", "SPC 206", "SPC 210", "SPC 238"]
            },
        "year_3": {
            "fall": ["ENGR 346", "MATH 302", "REE 302", "SPC 302", "SPC 307","SPC 337"],
            "spring": ["SCH 262", "SCH 263", "SPC 304", "SPC 315", "SPC 322","SPC 327","SPC 332"],
            "Summer":["ENGR 333"]
            },
        "year_4": {
            "fall": ["CIE 237", "SPC 417", "SPC 470", "SPC 498"],
            "fall_program_electives": 2,
            "fall_sch_electives": 2,
            "spring": ["SPC 435", "SPC 477", "SPC 499"],
            "spring_program_electives": 2,
            "spring_sch_electives": 2
            },
        "electives": {
            "program": [
                "NANENG 410", "PHYS 205", "PHYS 218",
                "SPC 411", "SPC 412", "SPC 413", "SPC 414",
                "SPC 418", "SPC 419", "SPC 420", "SPC 422",
                "SPC 424", "SPC 426", "SPC 428", "SPC 436",
                "SPC 439", "SPC 446", "SPC 447", "SPC 460",
                "SPC 497"
            ],
            "sch": [
                "ENV 301", "ENV 512", "ENV 527",
                "HIS 302", "HIS 304", "PHIL 301", "REE 503",
                "SCH 201", "SCH 202", "SCH 205", "SCH 206",
                "SCH 207", "SCH 232", "SCH 233", "SCH 234",
                "SCH 235", "SCH 244", "SCH 258", "SCH 265",
                "SCH 266"
            ],
            "elective_credits_required": 8
            }
    },
    
   "Communications and Information Engineering": {
        "code": "CIE",
        "total_credits": 160,

        "year_1": {
            "fall": ["CHEM 103", "CSCI 101", "ENGL 152","ENGR 102", "ENGR 121","MATH 101",  "PHYS 115", "PHYS 125"],
            "spring": [ "CIE 101", "CIE 110", "ENGL 153",  "MATH 102", "MATH 203", "PHYS 116", "PHYS 126",  "SCH 263"]
            },

        "year_2": {
            "fall": ["CIE 205", "CIE 206", "CIE 227", "CIE 239", "MATH 201", "MATH 202" ],
            "spring": [ "CIE 201", "CIE 237", "CIE 247", "CIE 249","PHYS 203","SCH 261", "SCH 262"]
            },

        "year_3": {
            "fall": [ "CIE 302", "CIE 317", "CIE 318", "CIE 328", "CIE 337", "MATH 302" ],
            "spring": [  "CIE 338", "CIE 347",  "CIE 349", "CIE 357",  "CIE 367", "CIE 399",  "SCH 264"  ],
            "summer": [ "ENGR 333"]
            },

        "year_4": {
            "fall": ["CIE 448","CIE 498","CIE Electives","General Education Electives" ],
            "spring": ["CIE 499","CIE Electives","General Education Electives"]
            }
    },
    
   "Environmental Engineering": {
        "code": "ENV",
        "total_credits": 160,

        "year_1": {
            "fall": ["CHEM 103", "CSCI 101", "ENGL 152","ENGR 102", "ENGR 121","MATH 101", "PHYS 115", "PHYS 125"],
            "spring": ["ENGL 153", "ENGR 105","ENV 104", "ENV 120","MATH 102","PHYS 116", "PHYS 126", "SCH 263"]
            },

        "year_2": {
            "fall": ["ENGR 207","ENV 204", "ENV 207", "ENV 224","MATH 201", "MATH 202"],
            "spring": ["ENV 219", "ENV 230","ENV 250", "ENV 257","MATH 301", "MATH 306","SCH 262"]
            },

        "year_3": {
            "fall": ["ENGR 346","ENV 302", "ENV 306","ENV 320", "ENV 323", "ENV 328","General Education Elective"],
            "spring": ["ENV 322", "ENV 325","ENV 327", "ENV 359","ENV 367", "ENV 380","SCH 261"],
            "summer": ["ENGR 333"]
            },

        "year_4": {
            "fall": [ "ENV 411", "ENV 412","ENV 415", "ENV 416","ENV 434", "ENV 440","ENV 498","ENV Electives"],
            "spring": [ "ENV 446", "ENV 460", "ENV 470","ENV 499","ENV Electives","General Education Electives"]
            }
    },
    
   "Nanotechnology and Nanoelectronics Engineering": {
        "code": "NANENG",
        "total_credits": 160,

        "year_1": {
            "fall": ["CHEM 103","CSCI 101","ENGL 152","ENGR 102","ENGR 121","MATH 101","PHYS 115","PHYS 125"],
            "spring": ["ENGL 153","MATH 102","MATH 203","NANENG 112","NANENG 171","PHYS 116","PHYS 126","PHYS 203","General Education Elective"]
            },

        "year_2": {
            "fall": ["MATH 201","MATH 202","NANENG 202","NANENG 203","PHYS 224","SCH 261","SCH 263"],
            "spring": ["NANENG 205","NANENG 211","NANENG 212","NANENG 218","NANENG 222","NANENG 231","General Education Elective"]
            },

        "year_3": {
            "fall": ["MATH 301","NANENG 301","NANENG 308","NANENG 323","NANENG 335","SCH 262"],
            "spring": ["MATH 302","MATH 306","NANENG 303","NANENG 313","NANENG 315","NANENG 325","NANENG 361"],
            "summer": ["ENGR 333"]
            },

        "year_4": {
            "fall": ["NANENG 410","NANENG 416","NANENG 430","NANENG 498","SCH 264","NANENG Focus Area Course","NANENG Elective","General Education Elective"],
            "spring": ["NANENG 406", "NANENG 419","NANENG 424","NANENG 499","NANENG Focus Area Course","NANENG Elective"]
            }
    },
    
  "Renewable Energy Engineering": {
        "code": "REE",
        "total_credits": 160,

        "year_1": {
            "fall": ["CHEM 103","CSCI 101","ENGL 152","ENGR 102","ENGR 121","MATH 101","PHYS 115","PHYS 125"],
            "spring": ["ENGL 153","ENGR 105","MATH 102","PHYS 116","PHYS 126","REE 101","REE 122","GEN_ED_ELECTIVE"]
            },

        "year_2": {
            "fall": ["ENGR 201","MATH 201","MATH 202","REE 202","REE 208","SCH 263","GEN_ED_ELECTIVE"],
            "spring": ["MATH 302","REE 203","REE 218","REE 306","REE 310","GEN_ED_ELECTIVE"]
            },

        "year_3": {
            "fall": ["ENGR 207","ENGR 346","MATH 301","REE 302","REE 311","REE 320"],
            "spring": ["MATH 306","REE 315","REE 317","REE 319","REE 321","SCH 262"],
            "summer": ["ENGR 333"]
            },

        "year_4": {
            "fall": ["REE 418","REE 425","REE 429","REE 432","REE 470","REE 498","REE_ELECTIVE"],
            "spring": ["REE 403","REE 428","REE 434","REE 499","REE_ELECTIVE","GEN_ED_ELECTIVE"]
            }
    },
    
    # "Energy and Bioprocess Engineering": {
    #     "code": "EBE",
    #     "total_credits": 160,
    #     "year_1": {
    #         "fall": ["MATH 101", "PHYS 101", "CHEM 101", "ENGL 101", "BIOL 101"],
    #         "spring": ["MATH 102", "PHYS 102", "CHEM 102", "BIOL 102", "ENGL 152"]
    #         },
    #     "year_2": {
    #         "fall": ["MATH 202", "CHEM 201", "BMS 201", "BMS 211", "BMS 215"],
    #         "spring": ["MATH 301", "BMS 202", "BMS 203", "BMS 205", "BMS 212"]
    #         },
    #     "year_3": {
    #         "fall": ["EBE 359", "BMS 301", "BMS 302", "BMS 303", "BMS 311"],
    #         "spring": ["EBE 401", "BMS 304", "BMS 313", "BMS 320", "BMS 330"]
    #        },
    #     "year_4": {
    #         "fall": ["EBE 411", "EBE 450", "BMS 415", "BMS 416", "BMS 430"],
    #         "spring": ["EBE 480", "BMS 401", "BMS 402", "BMS 404", "BMS 405"]
    #        }
    # },
    
    # ============================================================
    # SCHOOL OF SCIENCE STUDY PLANS
    # ============================================================
    
  "Biomedical Sciences": {
        "code": "BMS",
        "total_credits": 130,

        "year_1": {
            "fall": ["BIOL 101","BIOL 111","CHEM 101","CHEM 111","ENGL 152","MATH 101","PHYS 101","PHYS 111"],
            "spring": ["BIOL 102","BIOL 112","CHEM 102","CHEM 112","ENGL 153","MATH 102","PHYS 102","PHYS 112"]
            },

        "year_2": {
            "fall": ["BMS 201","BMS 202","BMS 211","BMS 212","CHEM 201", "CHEM 211", "CSCI 101","GEN_ED_ELECTIVE"],
            "spring": ["BMS 203","BMS 204","BMS 213","BMS 214","BMS_CONCENTRATION","GEN_ED_ELECTIVE"]
            },

        "year_3": {
            "fall": ["BMS 304","BMS 404","BMS_ELECTIVE","GEN_ED_ELECTIVE","BMS_CONCENTRATION"],
            "spring": ["BMS 303","BMS_CONCENTRATION","GEN_ED_ELECTIVE"],
            "summer": ["BMS 399"]
            },

        "year_4": {
            "fall": ["BMS 401","BMS_ELECTIVE","GEN_ED_ELECTIVE","BMS_CONCENTRATION"],
            "spring": ["BMS 402","BMS_ELECTIVE","GEN_ED_ELECTIVE","BMS_CONCENTRATION"]
            }
    },    

    "Nano Science": {

        "code": "NANOSC",
        "total_credits": 140,
        
        "year_1": {
                "fall": ["BIOL 101", "BIOL 111", "CHEM 101", "CHEM 111", "ENGL 152", "MATH 101", "PHYS 101", "PHYS 111"],
                "spring": ["BIOL 102", "BIOL 112", "CHEM 102", "CHEM 112", "ENGL 153", "MATH 102", "PHYS 102", "PHYS 112"]
            },
        "year_2": {
                "fall": {
                    "Nanophysics/Bio-Nanotechnology": ["CHEM 201", "CHEM 211", "CSCI 101", "MATH 201", "PHYS 201", "PHYS 211"],
                    "Nanomedicine": ["CHEM 201", "CHEM 211", "CSCI 101", "MATH 201", "BMS 202", "BMS 212"]
                },
                "spring": {
                    "Nanophysics/Bio-Nanotechnology": ["CHEM 202", "CHEM 212", "MATH 202", "MATSCI 201", "PHYS 202", "PHYS 212", "General Education Electives"],
                    "Nanomedicine": ["CHEM 202", "CHEM 212", "CHEM 203", "MATSCI 201", "BMS 204", "BMS 214", "General Education Electives"],
                    "Nanochemistry": ["CHEM 202", "CHEM 212", "CHEM 203", "MATSCI 201", "PHYS 202", "PHYS 212", "General Education Electives"]
                }
            },
        "year_3": {
                "fall": {
                    "Nanomedicine": ["NANOSC 302", "NANOSC 305", "NANOSC 308", "NANOSC 312", "NANOSC 315", "General Education Electives", "NANOSC Electives"],
                    "Nanophysics": ["NANOSC 302", "NANOSC 305", "NANOSC 306", "NANOSC 312", "NANOSC 315", "PHYS 323", "PHYS 316"],
                    "Bio-Nanotechnology": ["NANOSC 302", "NANOSC 303", "NANOSC 305", "NANOSC 306", "NANOSC 312", "NANOSC 315", "NANOSC Electives"],
                    "Nanochemistry": ["NANOSC 302", "NANOSC 303", "NANOSC 305", "NANOSC 306", "NANOSC 312", "NANOSC 315", "NANOSC Electives"]
                },
                "spring": {
                    "Nanomedicine": ["BMS 205", "NANOSC 301", "NANOSC 307", "NANOSC 309", "NANOSC 310", "General Education Electives"],
                    "Nanophysics": ["MATSCI 302", "NANOSC 301", "NANOSC 307", "PHYS 210", "PHYS 348", "General Education Electives"],
                    "Bio-Nanotechnology": ["NANOSC 301", "NANOSC 307", "NANOSC 317", "NANOSC 328", "General Education Electives"],
                    "Nanochemistry": ["NANOSC 301", "NANOSC 307", "NANOSC 322", "NANOSC 392", "General Education Electives"]
                },
                "summer": {
                    "Nanomedicine": ["NANOSC 399"],
                    "Nanophysics": ["NANOSC 399"],
                    "Bio-Nanotechnology": ["NANOSC 399"],
                    "Nanochemistry": ["NANOSC 399"]
                }
            },
       "year_4": {
                "fall": {
                    "Nanomedicine": ["NANOSC 403", "NANOSC 405", "NANOSC 417", "NANOSC 458", "NANOSC Electives", "General Education Electives"],
                    "Nanophysics": ["NANOSC 413", "NANOSC 415", "NANOSC Electives", "General Education Electives"],
                    "Bio-Nanotechnology": ["MATH 306", "NANOSC 308", "NANOSC 411", "NANOSC 458", "NANOSC Electives", "General Education Electives"],
                    "Nanochemistry": ["MATH 306", "NANOSC 308", "NANOSC 412", "NANOSC 458", "NANOSC Electives", "General Education Electives"]
                    },
                "spring": {
                    "Nanomedicine": ["NANOSC 404", "NANOSC 406", "NANOSC 498", "NANOSC Electives"],
                    "Nanophysics": ["NANOSC 416", "NANOSC 499", "NANOSC Electives"],
                    "Bio-Nanotechnology": ["NANOSC 408", "NANOSC 409", "NANOSC 498", "NANOSC Electives"],
                    "Nanochemistry": ["MATSCI 480", "NANOSC 409", "NANOSC 498", "NANOSC Electives"]
                    }
            }

    },
    
   "Physics of Universe": {
       "code": "PEU",
       "total_credits": 140,
        "year_1": {
                "fall": ["BIOL 101", "BIOL 111", "CHEM 101", "CHEM 111", "ENGL 152", "MATH 101", "PHYS 101", "PHYS 111"],
                "spring": ["BIOL 102", "BIOL 112", "CHEM 102", "CHEM 112", "ENGL 153", "MATH 102", "PHYS 102", "PHYS 112"]
            },
       "year_2": {
                "fall": ["CSCI 101", "MATH 201", "PHYS 205", "PHYS 204", "PHYS 201", "PHYS 211", "General Education Electives"],
                "spring": ["MATH 202", "PHYS 202", "PHYS 212", "PHYS 208", "PU Electives", "General Education Electives"]
            },
       "Year_3": {
                "fall": ["PHYS 311", "PHYS 316", "PHYS 323", "PU Electives", "General Education Electives"],
                "spring": {
                    "Astrophysics": ["MATSCI 302", "PHYS 308", "PHYS 327", "PHYS 356", "General Education Electives", "PU Concentration Courses", "PHYS 331"],
                    "High Energy Physics": ["MATSCI 302", "PHYS 308", "PHYS 327", "PHYS 356", "General Education Electives", "PU Concentration Courses", "PHYS 348"]
                },
                "summer": ["PHYS 399"]
            },
        "year_4": {
                "fall": {
                    "Astrophysics": ["PHYS 498", "PHYS 453", "PHYS 455", "PU Electives", "General Education Electives", "PU Concentration Courses", "ENGR 207"],
                    "High Energy Physics": ["PHYS 498", "PHYS 453", "PHYS 455", "PU Electives", "General Education Electives", "PU Concentration Courses", "PHYS 430"]
                },
                "spring": {
                    "Astrophysics": ["PHYS 405", "PHYS 499", "PU Electives", "PHYS Concentration Courses", "PHYS 416", "PHYS 438"],
                    "High Energy Physics": ["PHYS 405", "PHYS 499", "PU Electives", "PHYS Concentration Courses", "PHYS 431"]
                }
            },
        "electives": ["CIE 202", "CIE 205", "MATH 301", "MATH 302", "MATH 310", "MATH 306", "MATH 308", "MATH 403","PHYS 218", "NANOSC 413", "NANOSC 415", "PHYS 364", "PHYS 420", "PHYS 422", "PHYS 432", "PHYS 450", "CIE 470","PHYS 348", "PHYS 430", "ENGR 207", "PHYS 331"]
    },
    
    "Materials Science": {
        "code": "MATSCI",
        "total_credits": 140,
        "foundation_year": {
            "fall": ["BIOL 101", "BIOL 111", "CHEM 101", "CHEM 111", "ENGL 152", "MATH 101", "PHYS 101", "PHYS 111"],
            "spring": ["BIOL 102", "BIOL 112", "CHEM 102", "CHEM 112", "ENGL 153", "MATH 102", "PHYS 102", "PHYS 112"]
        },
        "year_2": {
            "fall": ["CHEM 201", "CHEM 211", "MATH 201", "MATSCI 204", "MATSCI 214", "PHYS 201", "PHYS 211"],
            "spring": ["CHEM 202", "CHEM 212", "MATH 202", "MATH 301", "PHYS 202", "PHYS 212", "SCH XXX"]
        },
        "year_3": {
            "Advanced Materials": {
                "fall": ["MATSCI 301", "MATSCI 305", "MATSCI 307", "MATSCI 317", "NANOSC 302", "SCH XXX"],
                "spring": ["MATSCI 302", "MATSCI 303", "MATSCI 304", "MATSCI 308", "MATSCI 318", "MATSCI 403"],
                "summer": ["MATSCI 399"]
            },
            "Materials Modeling": {
                "fall": ["MATSCI 301", "MATSCI 305", "MATSCI 307", "MATSCI 317", "MATH 302", "NANOSC 302"],
                "spring": ["MATH 306", "MATSCI 302", "MATSCI 303", "MATSCI 308", "MATSCI 318", "SCH XXX"],
                "summer": ["MATSCI 399"]
            }
        },
        "year_4": {
            "Advanced Materials": {
                "fall": ["MATSCI 407", "MATSCI 416", "MATSCI 417", "SCH XXX", "MATSCI XXX"],
                "spring": ["MATSCI 405", "MATSCI 418", "MATSCI 480", "MATSCI XXX", "SCH XXX"]
            },
            "Materials Modeling": {
                "fall": ["MATSCI 402", "MATSCI 412", "MATSCI 416", "SCH XXX", "MATSCI XXX"],
                "spring": ["MATSCI 406", "MATSCI 418", "MATSCI 480", "MATSCI XXX", "SCH XXX"]
            }
        },
        "electives": {
            "program": ["MATSCI 402", "MATSCI 405", "MATSCI 406", "MATSCI 407", "MATSCI 412", "MATSCI 417", "MATSCI 418", "MATSCI 480"],
            "sch": ["SCH XXX"],
            "elective_credits_required": 6
        }
    },
    # ============================================================
    # SCHOOL OF CSAI STUDY PLANS
    # Based on Official ZC Handbook (September 2022)
    # 132 Credit Hours: 16 Univ Req + 53 School Req + 63 Program Req
    # Includes: General Education Electives (6 Cr) + Program Electives (varies)
    # ============================================================
    
    "Data Science and Artificial Intelligence": {
        "code": "DSAI",
        "total_credits": 132,
        "year_1": {
                "fall": ["CSAI 100", "CSAI 101", "CSAI 102", "CSAI 252", "ENGL 156", "MATH 103", "SCH 163"],
                "spring": ["CSAI 151", "DSAI 103", "DSAI 104", "ENGL 157", "MATH 104", "General Education Electives"]
                },
        "year_2": {
                "fall": ["CSAI 201", "CSAI 202", "CSAI 205", "DSAI 203", "MATH 105", "SCH 261"],
                "spring": ["CSAI 251", "CSAI 253", "DSAI 201", "DSAI 202", "MATH 205", "SCH 264"]
                },
        "year_3": {
            "fall": ["CSAI 203", "CSAI 301", "DSAI 307", "DSAI 308", "MATH 303", "General Education Electives"],
            "fall_sch_electives": 2,
            "spring": ["CSAI 351", "DSAI 305", "DSAI 325", "DSAI 352", "DSAI 353","General Education Electives"],
            "spring_sch_electives": 1,
            "summer": ["CSAI 399"]
            },
        "year_4": {
            "fall": ["CSAI 302", "CSAI 498", "DSAI 402", "DSAI 403", "DSAI 456", "Data Science Program Elective"],
            "fall_program_electives": 1,
            "spring": ["CSAI 499", "DSAI 406", "DSAI 427", "Data Science Program Electives"],
            "spring_program_electives": 2
            },
        "electives": {
            "program": ["DSAI 413", "DSAI 414", "DSAI 415", "DSAI 416", "DSAI 417", "DSAI 418", "DSAI 431", "DSAI 433", "DSAI 490", "SW 402", "SW 403", "SWGCG 402", "ITNS 407", "ITNS 410"],
            "sch": ["SCH 201", "SCH 202", "SCH 205", "SCH 206", "SCH 207", "SCH 232", "SCH 234", "SCH 235", "SCH 258", "SCH 260", "SCH 265", "SCH 266", "SCH 273", "SCH 275", "SCH 277", "SCH 288", "SCH 299"],
            "elective_credits_required": 9
            }
    },
    
    "Software Development": {
        "code": "SW",
        "total_credits": 132,
        "year_1": {
            "fall": ["CSAI 100", "CSAI 101", "CSAI 102", "CSAI 252", "ENGL 156", "MATH 103", "SCH 163"],
            "spring": ["CSAI 151", "ENGL 157", "MATH 104", "PHYS 103", "SW 151", "General Education Electives"]
            },
        "year_2": {
            "fall": ["CSAI 201", "CSAI 202", "CSAI 203", "MATH 105", "PHYS 104", "SCH 261"],
            "spring": ["CSAI 204", "CSAI 251", "CSAI 253", "MATH 205", "SCH 264", "SW 251"]
            },
        "year_3": {
            "APD": {
                "fall": ["CSAI 301", "SW 252", "SW 301", "SW 302", "SWAPD 301", "General Education Electives"],
                "fall_sch_electives": 2,
                "spring": ["CSAI 302", "CSAI 351", "MATH 307", "SWAPD 351", "SWAPD 352", "CSAI 399"],
                "spring_sch_electives": 1,
                "summer": ["CSAI 399"]
            },
            "GCG": {
                "fall": ["CSAI 301", "SW 252", "SW 301", "SW 302", "SWGCG 301", "General Education Electives"],
                "spring": ["CSAI 351", "MATH 307", "SWGCG 351", "SWGCG 352", "General Education Electives"],
                "summer": ["CSAI 399"]
            },
            "HCI": {
                "fall": ["CSAI 301", "SCH 273", "SW 252", "SW 301", "SW 302", "SWHCI 301"],
                "spring": ["CSAI 351", "MATH 307", "SWHCI 351", "SWHCI 352", "General Education Electives"],
                "summer": ["CSAI 399"]
            }
        },
        "year_4": {
            "APD": {
                "fall": ["CSAI 498", "SW 401", "SW 402", "SWAPD 401", "SWAPD 402", "Application Development Elective"],
                "fall_program_electives": 1,
                "spring": ["CSAI 499", "SWAPD 452", "SWAPD 453", "Application Development Elective"],
                "spring_program_electives": 1
            },
            "GCG": {
                "fall": ["CSAI 498", "SW 401", "SW 402", "SWGCG 401", "SWGCG 402", "Gaming and Computer Graphics Elective"],
                "spring": ["CSAI 499", "SWGCG 451", "SWGCG 452", "SWGCG 453", "Gaming and Computer Graphics Elective"]
            },
            "HCI": {
                "fall": ["CSAI 498", "SW 401", "SW 402", "SWHCI 401", "SWHCI 402", "HCI Elective"],
                "spring": ["CSAI 499", "SWHCI 451", "SWHCI 452", "SWHCI 453", "HCI Elective"]
            }
       },
        "electives": {
            "program": ["SWGCG 301", "SWGCG 351", "SWGCG 453", "SWHCI 351", "SWHCI 452", "SWAPD 451", "SW 403", "DSAI 308", "ITNS 407", "ITNS 410"],
            "sch": ["SCH 201", "SCH 202", "SCH 205", "SCH 206", "SCH 207", "SCH 232", "SCH 234", "SCH 235", "SCH 258", "SCH 260", "SCH 265", "SCH 266", "SCH 273", "SCH 275", "SCH 277", "SCH 288", "SCH 299"],
            "elective_credits_required": 6
            }
    
    },
    
    "Information Technology": {
        "code": "IT",
        "total_credits": 132,
        "year_1": {
            "fall": ["CSAI 100", "CSAI 101", "CSAI 102", "CSAI 252", "ENGL 156", "MATH 103", "SCH 163"],
            "spring": ["CSAI 151", "ENGL 157", "IT 101", "IT 102", "IT 103", "MATH 104", "General Education Electives"]
        },
        "year_2": {
            "fall": ["CSAI 201", "CSAI 202", "CSAI 205", "IT 205", "MATH 105", "SCH 261"],
            "spring": ["CSAI 204", "CSAI 251", "CSAI 253", "IT 206", "IT 220", "IT 222", "SCH 264"]
        },
        "year_3": {
            "ITNS": {
                "fall": ["CSAI 203", "CSAI 301", "IT 308", "ITNS 301", "MATH 205", "General Education Electives"],
                "fall_sch_electives": 2,
                "springspring": ["CSAI 351", "IT 309", "IT 310", "ITNS 302", "CSAI 399", "ITNS Elective", "General Education Electives"],
                "spring_sch_electives": 1,
                "summer": ["CSAI 399"]
            },
            "ITCC": {
                "fall": ["CSAI 203", "CSAI 301", "IT 308", "ITCC 301", "MATH 205", "General Education Electives"],
                "spring": ["CSAI 351", "IT 309", "IT 310", "ITCC 302", "ITCC Elective", "General Education Electives"],
                "summer": ["CSAI 399"]
            }
        },
        "year_4": {
            "ITNS": {
                "fall": ["CSAI 498", "IT 402", "IT 411", "ITNS 403", "ITNS 404", "ITNS 406", "Program Elective"],
                "fall_program_electives": 1,
                "spring": ["CSAI 499", "ITNS 407", "ITNS 408", "ITNS Elective"],
                "spring_program_electives": 1
            },
            "ITCC": {
                "fall": ["CSAI 498", "IT 402", "IT 411", "ITCC 403", "ITCC 404", "ITCC 405"],
                "spring": ["CSAI 499", "ITCC 407", "ITCC 408", "ITCC Elective"]
            }
        },
        "electives": {
            "program": ["IT 401", "ITNS 410", "ITNS 411", "ITNS 412", "ITNS 413", "ITNS 414", "ITNS 415",
                        "ITCC 403", "ITCC 404", "ITCC 405", "ITCC 407", "ITCC 408"],
            "sch": ["SCH 201", "SCH 202", "SCH 205", "SCH 206", "SCH 207", "SCH 232", "SCH 234", "SCH 235",
                    "SCH 258", "SCH 260", "SCH 265", "SCH 266", "SCH 273", "SCH 275", "SCH 277", "SCH 288", "SCH 299"],
            "elective_credits_required": 6
        }
    },
    
    # ============================================================
    # SCHOOL OF BUSINESS STUDY PLANS
    # Note: Business majors have fewer major-specific courses in early years
    # Students take core business courses (BGEN, MGMT) before specializing
    # ============================================================
    "Actuarial Analysis and Risk Management": {
        "code": "BACT",
        "total_credits": 140,
        "year_1": {
            "fall": ["BGEN 101", "ECON 101", "ENGL 154", "FINC 101", "MGMT 101", "SCH 105"],
            "spring": ["BGEN 105", "BGEN 110", "ENGL 155", "MGMT 105", "MKTG 101", "SCH 110"]
        },
        "year_2": {
            "fall": ["BGEN 201", "BLAW 201", "FINC 201", "MGMT 201", "General Education Electives"],
            "spring": ["BGEN 205", "BGEN 210", "MGMT 205", "SCHN 201", "SUST 201", "General Education Electives"]
        },
        "year_3": {
            "fall": ["BACT 301", "BACT 305", "ECON 301", "FINC 315", "General Education Electives", "Sustainability Electives"],
            "spring": ["BACT 310", "BDAT 301", "BMAT 301", "ECON 305", "General Education Electives", "Sustainability Electives"],
            "summer": ["BUS 399"]
        },
        "year_4": {
            "fall": ["BACT 401", "BACT 402", "BACT 403", "General Education Electives", "Sustainability Electives"],
            "spring": ["BACT 404", "BDAT 401", "BUS 499", "General Education Electives", "Sustainability Electives"]
        },
        "electives": {
            "general_education": "Varies per semester",
            "sustainability": "Varies per semester"
        }
    },

    "Finance and Investment Management": {
        "code": "FINC",
        "total_credits": 140,
        "year_1": {
            "fall": ["BGEN 101", "ECON 101", "ENGL 154", "FINC 101", "MGMT 101", "SCH 105"],
            "spring": ["BGEN 105", "BGEN 110", "ENGL 155", "MGMT 105", "MKTG 101", "SCH 110"]
        },
        "year_2": {
            "fall": ["BGEN 201", "BLAW 201", "FINC 201", "MGMT 201", "General Education Electives"],
            "spring": ["BGEN 205", "BGEN 210", "MGMT 205", "SCHN 201", "SUST 201", "General Education Electives"]
        },
        "year_3": {
            "fall": ["ECON 310", "ECON 315", "FINC 305", "FINC 310", "General Education Electives", "Sustainability Electives"],
            "spring": ["BIFT 301", "ECON 320", "ECON 325", "FINC 315", "General Education Electives", "Sustainability Electives"],
            "summer": ["BUS 399"]
        },
        "year_4": {
            "fall": ["FINC 401", "FINC 405", "FINC 410", "General Education Electives", "Sustainability Electives"],
            "spring": ["BCSE 401", "BUS 499", "FINC 415", "General Education Electives", "Sustainability Electives"]
        },
        "electives": {
            "general_education": "Varies per semester",
            "sustainability": "Varies per semester"
        }
    },
    "Marketing, Entrepreneurship and Innovation Management": {
        "code": "MKTG",
        "total_credits": 140,
        "year_1": {
            "fall": ["BGEN 101", "ECON 101", "ENGL 154", "FINC 101", "MGMT 101", "SCH 105"],
            "spring": ["BGEN 105", "BGEN 110", "ENGL 155", "MGMT 105", "MKTG 101", "SCH 110"]
        },
        "year_2": {
            "fall": ["BGEN 201", "BLAW 201", "FINC 201", "MGMT 201", "General Education Electives"],
            "spring": ["BGEN 205", "BGEN 210", "MGMT 205", "SCHN 201", "SUST 201", "General Education Electives"]
        },
        "year_3": {
            "fall": ["BENT 301", "BENT 305", "BTEM 301", "MKTG 301", "General Education Electives"],
            "spring": ["BENT 310", "BTEM 305", "MKTG 305", "MKTG 310", "General Education Electives", "Sustainability Electives"],
            "summer": ["BUS 399"]
        },
        "year_4": {
            "fall": ["BENT 401", "MKTG 401", "MKTG 410", "General Education Electives", "Sustainability Electives"],
            "spring": ["BUS 499", "MKTG 405", "MKTG 415", "General Education Electives", "Sustainability Electives"]
        },
        "electives": {
            "general_education": "Varies per semester",
            "sustainability": "Varies per semester"
        }
    },
    
    "Operations, Supply Chain and Technology Management": {
        "code": "SCHN",
        "total_credits": 140,
        "year_1": {
            "fall": ["BGEN 101", "ECON 101", "ENGL 154", "FINC 101", "MGMT 101", "SCH 105"],
            "spring": ["BGEN 105", "BGEN 110", "ENGL 155", "MGMT 105", "MKTG 101", "SCH 110"]
        },
        "year_2": {
            "fall": ["BGEN 201", "BLAW 201", "FINC 201", "MGMT 201", "General Education Electives"],
            "spring": ["BGEN 205", "BGEN 210", "MGMT 205", "SCHN 201", "SUST 201", "General Education Electives"]
        },
        "year_3": {
            "fall": ["BCSE 301", "BLAW 301", "MGMT 301", "MGMT 311", "SCHN 305", "General Education Electives"],
            "spring": ["MGMT 305", "MGMT 310", "SCHN 301", "General Education Electives", "Sustainability Electives"],
            "summer": ["BUS 399"]
        },
        "year_4": {
            "fall": ["SCHN 401", "SCHN 405", "SCHN 410", "General Education Electives", "Sustainability Electives"],
            "spring": ["BUS 499", "MGMT 401", "MGMT 405", "General Education Electives", "Sustainability Electives"]
        },
        "electives": {
            "general_education": "Varies per semester",
            "sustainability": "Varies per semester"
        }
    }
}

# ============================================================
# COMPLETE COURSE CATALOG WITH PREREQUISITES
# (Based on ZC Course Catalog at https://www.zewailcity.edu.eg/academics/course-catalog)
# ============================================================

COURSE_CATALOG = {
    # AI ENGINEERING COURSES (Graduate)
    "AIE": {
        "AIE 501": {"name": "Artificial Intelligence Techniques", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Fundamental AI techniques including search, knowledge representation, and reasoning."},
        "AIE 502": {"name": "Machine Learning in Production", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 501"], "description": "MLOps, model deployment, monitoring, and production ML systems."},
        "AIE 503": {"name": "Deep Learning Techniques", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 501"], "description": "Neural networks, CNNs, RNNs, transformers, and deep learning frameworks."},
        "AIE 602": {"name": "Search Engine", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 501", "AIE 503"], "description": "Information retrieval, web search algorithms, and search engine architecture."},
        "AIE 603": {"name": "Speech Processing", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 503"], "description": "Speech recognition, synthesis, and natural language understanding."},
        "AIE 604": {"name": "Dialogue and Conversational Agents", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 503"], "description": "Chatbots, dialogue systems, and conversational AI."},
        "AIE 605": {"name": "Deep Learning in Computer Vision", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 503"], "description": "Image classification, object detection, segmentation using deep learning."},
        "AIE 606": {"name": "Medical Image Processing", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 605"], "description": "Medical imaging analysis, CT/MRI processing, and diagnostic AI."},
        "AIE 607": {"name": "Distributed Machine Learning", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 502"], "description": "Distributed computing for ML, parallel training, and federated learning."},
        "AIE 608": {"name": "Big Data Analytics", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 502"], "description": "Large-scale data processing, Spark, and big data ML pipelines."},
        "AIE 609": {"name": "Machine Learning for Wireless Communications", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 501"], "description": "AI applications in wireless networks, channel estimation, and 5G/6G."},
        "AIE 610": {"name": "Advanced Topics in Artificial Intelligence", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 503"], "description": "Current research topics in AI and emerging technologies."},
        "AIE 650": {"name": "Applied Engineering Project 1", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 501", "AIE 502", "AIE 503"], "description": "First part of capstone project with industry application."},
        "AIE 651": {"name": "Applied Engineering Project 2", "credits": 3, "level": "Graduate", "prerequisites": ["AIE 650"], "description": "Completion of capstone project with final deliverables."}
    },
    
    # ACTUARIAL ANALYSIS (BACT) - School of Business (Official ZC Courses)
    "BACT": {
        "BACT 301": {"name": "Principles of Risk Management", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Examines how business and society assess, control and transfer risk. Covers the risk management process including identification, analysis, treatment strategies, and crisis management."},
        "BACT 305": {"name": "Life Contingencies", "credits": 3, "level": "Junior", "prerequisites": ["BACT 301"], "description": "Basic technical tools in life insurance including whole life, term insurance, life annuities, premium calculations, multiple state and multiple life models under Markovian framework."},
        "BACT 310": {"name": "Introduction to Actuarial Practice", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Foundations of actuarial science including history, professional societies, standards of practice, codes of ethics, and communication skills required by actuaries."},
        "BACT 401": {"name": "Risk Financing Techniques", "credits": 3, "level": "Senior", "prerequisites": ["BACT 301"], "description": "Paying for losses through various techniques including insurance, alternative risk financing solutions, hedging and more."},
        "BACT 402": {"name": "Risk Analytics and Behavioral Science", "credits": 3, "level": "Senior", "prerequisites": ["BACT 301"], "description": "Holistic understanding of risk management, data analytics, and behavioral science. Covers risk tolerance, appetite, perception, predictive modeling, and machine learning for risk assessment."},
        "BACT 403": {"name": "Commercial Insurance and Management of Insurance Enterprise", "credits": 3, "level": "Senior", "prerequisites": ["BACT 301"], "description": "Comprehensive exploration of commercial insurance and fundamental principles of managing insurance enterprises, underwriting, risk analysis, and claims."},
        "BACT 404": {"name": "Casualty and Health Insurance Mathematics", "credits": 3, "level": "Senior", "prerequisites": ["BACT 305"], "description": "Mathematical principles, statistical methodologies, and actuarial techniques for casualty and health insurance risk assessment and management."}
    },
    
    # AEROSPACE/SPACE ENGINEERING (SPC) - Official ZC Course Catalog
    "SPC": {
        "SPC 101": {"name": "Introduction to Aerospace Engineering", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Introduction to topics of Aerospace Engineering and Flight Mechanics."},
        "SPC 201": {"name": "Introduction to Aerospace Engineering", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Foundations for understanding aerospace subsystems: aerodynamics, control, structure, propulsion."},
        "SPC 202": {"name": "Mechanics of Materials", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 102", "PHYS 101"], "description": "Stresses in materials due to axial, twisting, sheering, and bending loading."},
        "SPC 206": {"name": "Advanced Thermodynamics", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 105"], "description": "Advanced concepts of engineering thermodynamics, exergy, cycles, psychrometry."},
        "SPC 210": {"name": "Control Systems", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 202"], "description": "Dynamic systems modelling, response analysis, and control design."},
        "SPC 218": {"name": "Dynamics of Particles & Rigid Bodies", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 101", "MATH 102"], "description": "Kinematics and kinetics using Newtonian and energy approaches."},
        "SPC 227": {"name": "Analog & Digital Electronics", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 201"], "description": "Circuit analysis, analog and digital microelectronic circuits."},
        "SPC 228": {"name": "Engineering Dynamics", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 101", "PHYS 101"], "description": "Kinematics, kinetics, Newton's laws, momentum, energy conservation."},
        "SPC 238": {"name": "Mechanical Vibration", "credits": 3, "level": "Sophomore", "prerequisites": ["SPC 228"], "description": "Vibration of SDOF, MDOF systems and continuous structures."},
        "SPC 302": {"name": "Advanced Control Systems", "credits": 3, "level": "Junior", "prerequisites": ["SPC 210"], "description": "Control design using state-space methods, robust control."},
        "SPC 303": {"name": "Remote Sensing & Instrumentation", "credits": 2, "level": "Junior", "prerequisites": ["PHYS 102", "MATH 202"], "description": "Principles of remote sensing, platforms, sensors, data processing."},
        "SPC 304": {"name": "Orbital and Space Flight Mechanics", "credits": 2, "level": "Junior", "prerequisites": ["SPC 218"], "description": "Astrodynamics, two-body problems, space navigation and guidance."},
        "SPC 307": {"name": "Aerodynamics", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 207"], "description": "Subsonic/supersonic aerodynamics, airfoils, wings, viscous flows."},
        "SPC 308": {"name": "Supersonic & Hypersonic Fluid Dynamics", "credits": 3, "level": "Junior", "prerequisites": ["SPC 307"], "description": "Compressible fluid dynamics, shock waves, 2D flows."},
        "SPC 309": {"name": "Mechanics of Materials", "credits": 3, "level": "Junior", "prerequisites": ["MATH 102", "PHYS 101"], "description": "Stresses in elementary structures."},
        "SPC 315": {"name": "Thin-Walled Structures", "credits": 3, "level": "Junior", "prerequisites": ["SPC 202"], "description": "Structural analysis for aerospace vehicles using energy principles."},
        "SPC 316": {"name": "Aerospace Vehicles Structural Analysis & Design", "credits": 3, "level": "Junior", "prerequisites": ["SPC 309"], "description": "Intermediate structural analysis for aerospace vehicles."},
        "SPC 317": {"name": "Fluid Mechanics II", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 207"], "description": "Viscous flow, Navier-Stokes, boundary layers."},
        "SPC 318": {"name": "System Modeling & Linear Systems", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202"], "description": "Feedback control systems design for air and spacecraft."},
        "SPC 322": {"name": "Machine Design II", "credits": 3, "level": "Junior", "prerequisites": ["REE 302"], "description": "Joints, fasteners, gears, clutches, flexible machine elements."},
        "SPC 327": {"name": "Analog and Digital Electronics", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 201"], "description": "Circuit analysis, analog/digital circuits, op-amps."},
        "SPC 328": {"name": "Classical & Modern Control", "credits": 3, "level": "Junior", "prerequisites": ["SPC 318"], "description": "State-space control design, robustness, nonlinearity handling."},
        "SPC 332": {"name": "Flight Dynamics and Control", "credits": 3, "level": "Junior", "prerequisites": ["SPC 302"], "description": "Aircraft stability, control, flight vehicle stabilization."},
        "SPC 337": {"name": "Gas Dynamics", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 105", "ENGR 207"], "description": "Compressible fluid dynamics, shock waves."},
        "SPC 338": {"name": "Sensor Technology", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Sensors systems, signal conditioning, sensor architectures."},
        "SPC 348": {"name": "Mechanical Vibration", "credits": 3, "level": "Junior", "prerequisites": ["REE 208", "REE 202"], "description": "Vibration of mechanical systems."},
        "SPC 392": {"name": "Heat Transfer and Combustion", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 332", "ENGR 207"], "description": "Heat conduction, convection, radiation, combustion."},
        "SPC 406": {"name": "Advanced Thermodynamics", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 205"], "description": "Advanced thermodynamics cycles and applications."},
        "SPC 407": {"name": "Aerodynamics", "credits": 3, "level": "Senior", "prerequisites": ["REE 307"], "description": "Advanced aerodynamic performance of wings and bodies."},
        "SPC 408": {"name": "Dynamics of Aerospace Structures", "credits": 3, "level": "Senior", "prerequisites": ["SPC 309"], "description": "Mechanical vibration for aerospace structures."},
        "SPC 409": {"name": "Flight Dynamics & Control", "credits": 3, "level": "Senior", "prerequisites": ["SPC 328"], "description": "Modern aircraft stability and control."},
        "SPC 410": {"name": "Gas Dynamics", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 205", "ENGR 207"], "description": "Advanced compressible fluid dynamics."},
        "SPC 411": {"name": "Aircraft Autopilot and Guidance", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Aircraft autopilot loops, controller design."},
        "SPC 412": {"name": "Digital Control", "credits": 2, "level": "Senior", "prerequisites": ["SPC 302"], "description": "Digital control systems, z-transform, stability."},
        "SPC 413": {"name": "Attitude Determination and Control", "credits": 2, "level": "Senior", "prerequisites": ["SPC 228"], "description": "Rigid body dynamics, spacecraft attitude dynamics."},
        "SPC 414": {"name": "Optimal Control", "credits": 2, "level": "Senior", "prerequisites": ["SPC 302"], "description": "Calculus of variations, dynamic programming, Pontryagin's principle."},
        "SPC 415": {"name": "Thin Walled Structures", "credits": 3, "level": "Senior", "prerequisites": ["SPC 202"], "description": "Structural analysis of aerospace vehicles."},
        "SPC 417": {"name": "Gas Turbine Engines", "credits": 3, "level": "Senior", "prerequisites": ["SPC 206", "SPC 337"], "description": "Aerospace propulsive devices design."},
        "SPC 418": {"name": "Control Systems Design for Autonomous Vehicles", "credits": 2, "level": "Senior", "prerequisites": ["SPC 302"], "description": "Autonomous vehicle control, UAVs, ground vehicles."},
        "SPC 419": {"name": "Turbomachinery", "credits": 2, "level": "Senior", "prerequisites": ["SPC 337"], "description": "Compressors and turbines for gas turbine engines."},
        "SPC 420": {"name": "Low Speed Aerodynamics", "credits": 2, "level": "Senior", "prerequisites": ["SPC 307"], "description": "Inviscid flow, viscous boundary layers, panel methods."},
        "SPC 422": {"name": "Aircraft Performance", "credits": 2, "level": "Senior", "prerequisites": ["SPC 307"], "description": "Aircraft performance analysis, takeoff, landing, range."},
        "SPC 424": {"name": "Spacecraft and Space System Design", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Satellite and space platform design."},
        "SPC 426": {"name": "Experimental Aerodynamics", "credits": 2, "level": "Senior", "prerequisites": ["SPC 307"], "description": "Wind tunnel testing, measurement techniques."},
        "SPC 428": {"name": "Mechatronics and Robotics", "credits": 3, "level": "Senior", "prerequisites": ["SPC 210"], "description": "Robotics, vision, motion planning, kinematics."},
        "SPC 435": {"name": "Aerospace Communication Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 237"], "description": "Telecommunications for aerospace industry."},
        "SPC 436": {"name": "Computational Fluid Dynamics", "credits": 2, "level": "Senior", "prerequisites": ["MATH 306"], "description": "Finite difference methods for PDEs and fluid dynamics."},
        "SPC 439": {"name": "Aircraft Conceptual Design", "credits": 2, "level": "Senior", "prerequisites": [], "description": "System level aircraft sizing and design."},
        "SPC 446": {"name": "Advanced Materials for Aerospace Struct", "credits": 2, "level": "Senior", "prerequisites": ["SPC 315"], "description": "Composites, smart structures, piezoelectrics."},
        "SPC 447": {"name": "Advanced Aerospace Structures", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Electromagnetic wave interactions with surfaces."},
        "SPC 460": {"name": "Non-Linear Control", "credits": 2, "level": "Senior", "prerequisites": ["SPC 302"], "description": "Phase plane analysis, Lyapunov stability, sliding mode control."},
        "SPC 470": {"name": "Computer-Aided Design and Engineering", "credits": 3, "level": "Senior", "prerequisites": ["REE 312"], "description": "CAD/CAE using SolidWorks, ANSYS, COMSOL."},
        "SPC 472": {"name": "Machine Intelligence", "credits": 2, "level": "Senior", "prerequisites": [], "description": "AI for intelligent agents, learning, decision-making."},
        "SPC 477": {"name": "Airports and Airlines Management", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Aviation system, airlines and airports management."},
        "SPC 491": {"name": "Jet Propulsion", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 332", "SPC 308"], "description": "Air-breathing and rocket engine design."},
        "SPC 497": {"name": "Selected topics in Aerospace Engineering", "credits": 0, "level": "Senior", "prerequisites": [], "description": "Special topics in aerospace engineering."},
        "SPC 498": {"name": "Senior Design Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "First part of capstone design project."},
        "SPC 499": {"name": "Senior Design Project II", "credits": 3, "level": "Senior", "prerequisites": ["SPC 498"], "description": "Completion of capstone design project."},
        # Graduate Courses
        "SPC 504": {"name": "Optimal Control", "credits": 2, "level": "Graduate", "prerequisites": ["SPC 328"], "description": "Calculus of variations, dynamic programming, Pontryagin's principle for optimal control."},
        "SPC 506": {"name": "Computational Fluid Dynamics", "credits": 2, "level": "Graduate", "prerequisites": ["SPC 407"], "description": "Finite difference methods for PDEs, Navier-Stokes equations."},
        "SPC 508": {"name": "Experimental Aerodynamics", "credits": 2, "level": "Graduate", "prerequisites": ["SPC 307"], "description": "Aerodynamic testing, wind tunnel measurement techniques."},
        "SPC 509": {"name": "Aircraft Conceptual Design", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "System level aircraft sizing, airworthiness, mission requirements."},
        "SPC 510": {"name": "Low Speed Aerodynamics", "credits": 2, "level": "Graduate", "prerequisites": ["SPC 307"], "description": "Inviscid flow, viscous boundary layers, panel methods."},
        "SPC 511": {"name": "Geographical Information Systems", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "GIS concepts, GPS, spatial data acquisition and analysis."},
        "SPC 512": {"name": "Digital Control", "credits": 2, "level": "Graduate", "prerequisites": ["SPC 328"], "description": "Discrete time systems, z-transform, digital controller design."},
        "SPC 513": {"name": "Space Applications Law & Policy", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "International legal aspects of space applications and telecommunications."},
        "SPC 521": {"name": "Spacecraft Propulsion", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Rocket propulsion fundamentals, electric propulsion, ion engines."},
        "SPC 525": {"name": "Space Power Systems", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Photovoltaic, solar-thermal, nuclear power systems for satellites."},
        "SPC 526": {"name": "Advanced Materials for Aerospace Struct", "credits": 2, "level": "Graduate", "prerequisites": ["SPC 316"], "description": "Composite materials, smart structures, piezoelectrics."},
        "SPC 527": {"name": "Advanced Aerospace Structures", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Electromagnetic wave interactions with surfaces, sensor technology."},
        "SPC 535": {"name": "Space Craft Communications Systems", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 327"], "description": "Satellite communications, GEO, LEO, GNSS systems design."},
        "SPC 560": {"name": "Non-Linear Control", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Lyapunov stability, sliding mode control, nonlinear feedback control."},
        "SPC 577": {"name": "Airports and Airlines", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "International aviation system, airlines and airport management."},
        "SPC 597": {"name": "Selected topics in Aerospace Engineering", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Special topics in aerospace engineering."},
        "SPC 598": {"name": "Senior Design Project I", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "First part of graduate capstone design project."},
        "SPC 599": {"name": "Senior Design Project II", "credits": 3, "level": "Graduate", "prerequisites": ["SPC 598"], "description": "Completion of graduate capstone design project."}
    },
    
    # COMMUNICATIONS AND INFORMATION ENGINEERING (CIE) - Official ZC Course Catalog
    "CIE": {
        # Freshman/Sophomore Courses
        "CIE 101": {"name": "Fundamentals of Computer Programming", "credits": 3, "level": "Freshman", "prerequisites": ["CSCI 101"], "description": "Procedure-oriented and object-oriented programming models, data types, control structures, arrays, functions, classes, objects."},
        "CIE 110": {"name": "Introduction to Circuits and Electronics", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Fundamentals of electric and electronic circuits, circuit analysis, semiconductor devices, diodes, BJT and MOSFET transistors."},
        "CIE 201": {"name": "Advanced Electric Circuits", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 202", "CIE 110"], "description": "Circuit analysis methods, Laplace Transform, frequency selective circuits, filter synthesis."},
        "CIE 202": {"name": "Fundamentals of Computer Programming", "credits": 3, "level": "Sophomore", "prerequisites": ["CSCI 101"], "description": "Object-oriented programming approach, classes, objects, inheritance, encapsulation, polymorphism."},
        "CIE 205": {"name": "Data Structures and Algorithm Analysis", "credits": 3, "level": "Sophomore", "prerequisites": ["CIE 101"], "description": "Design and analysis of algorithms, data structures, divide-and-conquer, dynamic programming, NP-completeness."},
        "CIE 206": {"name": "Database Management System", "credits": 3, "level": "Sophomore", "prerequisites": ["CIE 101"], "description": "Database concepts, entity-relationship model, relational model normalization, SQL programming."},
        "CIE 212": {"name": "Introduction to Electronics", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 210"], "description": "Semiconductor physics, PN junction, diodes, BJT & MOSFET transistors, rectifiers and amplifiers."},
        "CIE 227": {"name": "Signals and Systems", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 101"], "description": "Discrete-time and continuous-time signals, Fourier series, Fourier transform, LTI systems."},
        "CIE 237": {"name": "Probability and Stochastic Processes", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 201", "CIE 227"], "description": "Probability theory, random variables, stochastic processes, signal processing applications."},
        "CIE 238": {"name": "Electromagnetic Fields & Waves I", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 102", "MATH 102"], "description": "Electromagnetic model, electrostatics, magnetostatics, Maxwell's equations."},
        "CIE 239": {"name": "Digital Design and Computer Architecture", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Digital electronics, Boolean algebra, combinational/sequential circuits, HDL, FPGAs, microprocessors."},
        "CIE 247": {"name": "Digital Signal Processing", "credits": 3, "level": "Sophomore", "prerequisites": ["CIE 227"], "description": "Discrete-time signal systems, z-transform, DFT, FFT, digital filter design."},
        "CIE 249": {"name": "Computer Architecture and Assembly Language", "credits": 3, "level": "Sophomore", "prerequisites": ["CIE 239"], "description": "Computer design, X86 and ARM assembly, processor datapath, memory hierarchy."},
        # Junior Courses
        "CIE 301": {"name": "Advanced Electric Circuits", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202", "ENGR 210"], "description": "Circuit analysis, Laplace Transform, filter synthesis, network theorems."},
        "CIE 302": {"name": "Operating Systems", "credits": 3, "level": "Junior", "prerequisites": ["CIE 205"], "description": "OS concepts, scheduling, synchronization, threads, memory management, file systems."},
        "CIE 317": {"name": "Machine Learning", "credits": 3, "level": "Junior", "prerequisites": ["CIE 205", "CIE 237"], "description": "Machine learning models, regression, classification, clustering, dimensionality reduction."},
        "CIE 318": {"name": "Control Systems", "credits": 3, "level": "Junior", "prerequisites": ["CIE 227"], "description": "Continuous-time and discrete-time feedback control, PID control, root locus, state space."},
        "CIE 320": {"name": "Analog Electronics", "credits": 3, "level": "Junior", "prerequisites": ["CIE 212"], "description": "Multistage analog amplifiers, differential amplifiers, frequency response, feedback."},
        "CIE 325": {"name": "Signals and Systems", "credits": 3, "level": "Junior", "prerequisites": ["MATH 101", "MATH 201"], "description": "Signal and system analysis, Fourier representations, LTI systems."},
        "CIE 327": {"name": "Probability and Stochastic Processes", "credits": 3, "level": "Junior", "prerequisites": ["CIE 227"], "description": "Probability theory, random variables, stochastic processes applications."},
        "CIE 328": {"name": "Electromagnetic Fields and Waves I", "credits": 3, "level": "Junior", "prerequisites": ["MATH 102", "PHYS 102"], "description": "Electromagnetic fields, electrostatics, magnetostatics, Maxwell's equations."},
        "CIE 337": {"name": "Communications Theory and Systems", "credits": 3, "level": "Junior", "prerequisites": ["CIE 237"], "description": "Shannon's information theory, coding, error correction, communication protocols."},
        "CIE 338": {"name": "Electromagnetic Fields and Waves II", "credits": 3, "level": "Junior", "prerequisites": ["CIE 328", "MATH 302"], "description": "Electromagnetic wave propagation, transmission lines, waveguides, antennas."},
        "CIE 339": {"name": "Digital Design and Computer Architecture", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Digital electronics, Boolean algebra, flip flops, registers, microprocessor architecture."},
        "CIE 347": {"name": "Information Theory and Coding", "credits": 3, "level": "Junior", "prerequisites": ["CIE 237"], "description": "Entropy, mutual information, channel capacity, block codes, convolutional codes."},
        "CIE 349": {"name": "Embedded Systems", "credits": 3, "level": "Junior", "prerequisites": ["CIE 249", "CIE 302"], "description": "Microcontrollers, digital I/O, sensors, A/D converters, RTOS, ROS."},
        "CIE 357": {"name": "Digital and Wireless Communications", "credits": 3, "level": "Junior", "prerequisites": ["CIE 337"], "description": "Signal space representation, digital modulation, error probabilities, multipath fading."},
        "CIE 367": {"name": "Computer Networks", "credits": 3, "level": "Junior", "prerequisites": ["CIE 237"], "description": "Network concepts, OSI model, TCP/IP, switching, routing, Ethernet, WiFi."},
        "CIE 399": {"name": "Fundamentals of Software Engineering", "credits": 2, "level": "Junior", "prerequisites": ["CIE 205", "CIE 206"], "description": "Software engineering fundamentals, requirements, design, coding, testing."},
        # Senior Courses
        "CIE 402": {"name": "Antennas Engineering", "credits": 3, "level": "Senior", "prerequisites": ["CIE 338"], "description": "Antenna theory, types, applications, electromagnetic properties, measurement techniques."},
        "CIE 404": {"name": "Cloud Computing Technology", "credits": 3, "level": "Senior", "prerequisites": ["CIE 302", "CIE 367"], "description": "Cloud infrastructure, virtualization, SaaS, PaaS, IaaS, containers, serverless."},
        "CIE 405": {"name": "Electric Machines", "credits": 3, "level": "Senior", "prerequisites": ["CIE 301"], "description": "Power converters, electrical machines, energy conversion, AC machines."},
        "CIE 406": {"name": "Computer Networks", "credits": 3, "level": "Senior", "prerequisites": ["CSCI 101", "CIE 428"], "description": "Computer communication networks, OSI model, Ethernet, protocols."},
        "CIE 408": {"name": "Embedded Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 439", "CIE 302"], "description": "ARM microcontrollers, sensors, motor control, serial communications, RTOS."},
        "CIE 412": {"name": "Propagation and Channel Modeling", "credits": 3, "level": "Senior", "prerequisites": ["CIE 402"], "description": "Radiowave propagation, channel modeling, MIMO channels, channel estimation."},
        "CIE 413": {"name": "Bioinformatics for Engineers", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102", "CIE 317", "CIE 237"], "description": "Bioinformatics, data mining, genome analysis, protein structures."},
        "CIE 416": {"name": "Satellite Communications System", "credits": 3, "level": "Senior", "prerequisites": ["CIE 437"], "description": "GEO and LEO satellites, link budget, multiple access, satellite networks."},
        "CIE 417": {"name": "Machine Learning", "credits": 3, "level": "Senior", "prerequisites": ["CIE 205", "CIE 327"], "description": "Machine learning models, regression, classification, clustering, pattern recognition."},
        "CIE 418": {"name": "Communications Circuits", "credits": 3, "level": "Senior", "prerequisites": ["CIE 320", "CIE 301"], "description": "RF communications, AM/FM/PM modulation, oscillators, mixers, modulators."},
        "CIE 419": {"name": "Computer Vision", "credits": 3, "level": "Senior", "prerequisites": ["CIE 317"], "description": "Image fundamentals, Fourier transform, segmentation, feature extraction, object recognition."},
        "CIE 420": {"name": "Robot and Machine Vision", "credits": 3, "level": "Senior", "prerequisites": ["CIE 419", "CIE 442"], "description": "Industrial vision, robot guidance, machine vision systems."},
        "CIE 425": {"name": "Information Theory and Coding", "credits": 3, "level": "Senior", "prerequisites": ["CIE 327"], "description": "Entropy, channel capacity, block codes, convolutional codes, Gaussian channel."},
        "CIE 427": {"name": "Big Data Analytics", "credits": 3, "level": "Senior", "prerequisites": ["CIE 206", "CIE 317"], "description": "Hadoop, Spark, HDFS, MapReduce, Pig, Hive, HBase, SparkML."},
        "CIE 428": {"name": "Digital and Wireless Communications", "credits": 3, "level": "Senior", "prerequisites": ["CIE 431"], "description": "Fading channels, MIMO, OFDM, spread spectrum, CDMA."},
        "CIE 430": {"name": "Sensors and Instrumentation", "credits": 3, "level": "Senior", "prerequisites": ["CIE 212"], "description": "Measurement systems, sensor types, signal conditioning, data acquisition."},
        "CIE 431": {"name": "Communications Theory and Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 325"], "description": "Information theory, communication systems, coding, error correction."},
        "CIE 436": {"name": "Electromagnetic Remote Sensing: Engineering Principles and Techniques", "credits": 3, "level": "Senior", "prerequisites": ["CIE 247", "CIE 338"], "description": "Remote sensing principles, electromagnetic wave propagation, scattering, sensing systems."},
        "CIE 437": {"name": "Digital and Wireless Communications", "credits": 3, "level": "Senior", "prerequisites": ["CIE 337"], "description": "Digital modulation, error probabilities, wireless channels, multipath fading."},
        "CIE 438": {"name": "RF and Microwave Engineering", "credits": 3, "level": "Senior", "prerequisites": ["CIE 338"], "description": "RF/microwave circuits, network analysis, impedance matching, passive/active devices."},
        "CIE 439": {"name": "Computer Architecture and Assembly Language", "credits": 3, "level": "Senior", "prerequisites": ["CIE 239"], "description": "Computer design, assembly language, processor architecture, memory hierarchy."},
        "CIE 440": {"name": "Digital Control Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 318"], "description": "Sampled data systems, Z-transform, digital PID, state space, pole placement."},
        "CIE 442": {"name": "Digital Signal Processing", "credits": 3, "level": "Senior", "prerequisites": ["CIE 227"], "description": "Discrete-time systems, z-transform, DFT, digital filter design, FFT."},
        "CIE 447": {"name": "Computer Networks", "credits": 3, "level": "Senior", "prerequisites": ["CIE 327"], "description": "Network fundamentals, OSI model, TCP/IP, switching, routing, Ethernet, WiFi."},
        "CIE 448": {"name": "IoT Systems Engineering", "credits": 3, "level": "Senior", "prerequisites": ["CIE 349", "CIE 367"], "description": "IoT systems design, embedded hardware/software, communications, data analysis."},
        "CIE 449": {"name": "Wireless Sensor Networks and IoT", "credits": 3, "level": "Senior", "prerequisites": ["CIE 357", "CIE 367"], "description": "WSN basics, MAC protocols, routing, network management, IoT applications."},
        "CIE 450": {"name": "Robotics: Transformations, Kinematics, and Dynamics", "credits": 3, "level": "Senior", "prerequisites": ["CIE 318"], "description": "Rigid body motion, manipulator kinematics, inverse kinematics, robot dynamics."},
        "CIE 451": {"name": "Mechatronics Engineering", "credits": 3, "level": "Senior", "prerequisites": ["CIE 450"], "description": "Robot mechanisms, dynamics, intelligent controls, multi-robot systems."},
        "CIE 452": {"name": "Advanced Computer Architecture", "credits": 3, "level": "Senior", "prerequisites": ["CIE 439"], "description": "Computer design, pipelining, memory hierarchies, I/O devices."},
        "CIE 453": {"name": "Natural Language Processing", "credits": 3, "level": "Senior", "prerequisites": ["CIE 317"], "description": "Text similarity, POS tagging, parsing, semantics, question answering."},
        "CIE 454": {"name": "Computer Arithmetic", "credits": 3, "level": "Senior", "prerequisites": ["CIE 205"], "description": "Number representations, arithmetic operations, hardware implementation."},
        "CIE 455": {"name": "Neural Networks and Deep Learning", "credits": 3, "level": "Senior", "prerequisites": ["CIE 317"], "description": "Deep learning, CNNs, RNNs, LSTM, GAN, Adam, Dropout."},
        "CIE 456": {"name": "Speech Analysis, synthesis, and recognition", "credits": 3, "level": "Senior", "prerequisites": ["CIE 317", "CIE 442"], "description": "Speech production, analysis, synthesis, recognition, HMM, neural networks."},
        "CIE 457": {"name": "Statistical Inference and Data Analysis", "credits": 3, "level": "Senior", "prerequisites": ["CIE 237"], "description": "Statistical inference, estimation, hypothesis testing, Bayesian inference."},
        "CIE 458": {"name": "Fundamentals of Artificial Intelligence", "credits": 3, "level": "Senior", "prerequisites": ["CIE 205", "CIE 237"], "description": "Intelligent systems, problem solving, heuristic search, game playing, MDP."},
        "CIE 459": {"name": "Parallel and Distributed Computing", "credits": 3, "level": "Senior", "prerequisites": ["CIE 249", "CIE 205"], "description": "Parallel architectures, programming paradigms, parallel algorithms."},
        "CIE 460": {"name": "Software Engineering Fundamentals", "credits": 3, "level": "Senior", "prerequisites": ["CIE 205", "CIE 206"], "description": "Software engineering, requirements, design, coding, testing."},
        "CIE 461": {"name": "Automata and Compiler Design", "credits": 3, "level": "Senior", "prerequisites": ["CIE 302"], "description": "Formal languages, finite automata, context-free grammars, compiler design."},
        "CIE 464": {"name": "Computer Graphics", "credits": 3, "level": "Senior", "prerequisites": ["CIE 205"], "description": "Ray tracing, graphics pipeline, transformations, texture mapping, animation."},
        "CIE 465": {"name": "Visualization", "credits": 3, "level": "Senior", "prerequisites": ["CIE 464"], "description": "Information visualization, data analysis algorithms, visualization techniques."},
        "CIE 467": {"name": "Mobile Communications Technologies", "credits": 3, "level": "Senior", "prerequisites": ["CIE 357"], "description": "Cellular concept, frequency reuse, handover, multiple access, 2G-5G systems."},
        "CIE 470": {"name": "Introduction to Quantum Computation and Quantum Information", "credits": 3, "level": "Senior", "prerequisites": ["MATH 201"], "description": "Quantum computation, qubits, quantum protocols, quantum circuits."},
        "CIE 474": {"name": "Distributed Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 367", "CIE 459"], "description": "Distributed systems principles, communication, synchronization, fault tolerance."},
        "CIE 477": {"name": "Cognitive Radio Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 357"], "description": "Spectrum sharing, cognitive radio, spectrum sensing, spectrum management."},
        "CIE 478": {"name": "Advanced Wireless Communication Systems", "credits": 3, "level": "Senior", "prerequisites": ["CIE 357"], "description": "Cellular systems, OFDM, spread spectrum, CDMA, diversity, equalization."},
        "CIE 481": {"name": "Information Security and Encryption", "credits": 3, "level": "Senior", "prerequisites": ["CIE 237"], "description": "Information security, encryption, access control, IoT security, network security."},
        "CIE 482": {"name": "Cryptography", "credits": 3, "level": "Senior", "prerequisites": ["MATH 308", "CIE 237"], "description": "Applied cryptography, ciphers, encryption, digital signatures, key management."},
        "CIE 491": {"name": "Selected Topics in Networks and Communications Systems", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in networks and communications."},
        "CIE 492": {"name": "Selected Topics in Electromagnetics and Remote Sensing", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in electromagnetics and remote sensing."},
        "CIE 493": {"name": "Selected Topics in Artificial Intelligence and Big Data Analytics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in AI and big data analytics."},
        "CIE 494": {"name": "Selected Topics in High Performance Computing and Visualization", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in HPC and visualization."},
        "CIE 495": {"name": "Selected topics in Robotics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in robotics."},
        "CIE 497": {"name": "Selected topics in Communications and Information Engineering", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in CIE."},
        "CIE 498": {"name": "Senior Design Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "First part of senior design project."},
        "CIE 499": {"name": "Senior Design Project II", "credits": 3, "level": "Senior", "prerequisites": ["CIE 498"], "description": "Completion of senior design project."},
        # Graduate Courses
        "CIE 502": {"name": "Propagation and Channel Modeling", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 402"], "description": "Radiowave propagation, channel modeling for wireless applications."},
        "CIE 506": {"name": "Bioinformatics for Engineers", "credits": 3, "level": "Graduate", "prerequisites": ["BIOL 102", "CIE 417"], "description": "Bioinformatics, genome analysis, protein structures."},
        "CIE 510": {"name": "Wireless Sensor Networks and IoT", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 437", "CIE 447"], "description": "WSN, IoT, MAC protocols, routing, network management."},
        "CIE 514": {"name": "Visualization", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 464"], "description": "Information visualization, data analysis, visualization techniques."},
        "CIE 524": {"name": "Mobile Communications Technologies", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 437"], "description": "Cellular systems, frequency reuse, handover, 2G-5G systems."},
        "CIE 528": {"name": "Mechatronics Engineering", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 450"], "description": "Robot mechanisms, dynamics, intelligent controls."},
        "CIE 530": {"name": "Cognitive Radio Systems", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 437"], "description": "Spectrum sharing, cognitive radio, spectrum sensing."},
        "CIE 538": {"name": "Electromagnetic Remote Sensing: Engineering Principles and Techniques", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 442", "CIE 338"], "description": "Remote sensing principles, electromagnetic wave propagation."},
        "CIE 539": {"name": "Advanced Computer Architecture", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 439"], "description": "Computer design, pipelining, memory hierarchies."},
        "CIE 547": {"name": "Cloud Computing Technology", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 302", "CIE 447"], "description": "Cloud infrastructure, virtualization, cloud services."},
        "CIE 552": {"name": "Computer Vision", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 417"], "description": "Image fundamentals, segmentation, object recognition."},
        "CIE 553": {"name": "Natural Language Processing", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 417"], "description": "Text processing, parsing, semantics, question answering."},
        "CIE 554": {"name": "Computer Arithmetic", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 205"], "description": "Computer arithmetic, hardware implementation."},
        "CIE 555": {"name": "Neural Networks and Deep Learning", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 417"], "description": "Deep learning, CNNs, RNNs, LSTM, GAN."},
        "CIE 556": {"name": "Speech Analysis, synthesis, and recognition", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 417", "CIE 442"], "description": "Speech processing, recognition, neural networks."},
        "CIE 558": {"name": "Robot and Machine Vision", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 552", "CIE 442"], "description": "Industrial vision, robot guidance."},
        "CIE 564": {"name": "Parallel and Distributed Computing", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 439", "CIE 205"], "description": "Parallel architectures, programming paradigms."},
        "CIE 574": {"name": "Distributed Systems", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 447", "CIE 564"], "description": "Distributed systems principles, communication."},
        "CIE 581": {"name": "Information Security and Encryption", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 327"], "description": "Information security, encryption."},
        "CIE 582": {"name": "Cryptography", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 327"], "description": "Applied cryptography, ciphers, encryption."},
        "CIE 591": {"name": "Selected Topics in Networks and Communications Systems", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics in networks and communications."},
        "CIE 592": {"name": "Selected Topics in Electromagnetics and Remote Sensing", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics in electromagnetics."},
        "CIE 593": {"name": "Selected Topics in Artificial Intelligence and Big Data Analytics", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics in AI and big data."},
        "CIE 594": {"name": "Selected Topics in High Performance Computing and Visualization", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics in HPC."},
        "CIE 595": {"name": "Selected topics in Robotics", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics in robotics."},
        "CIE 597": {"name": "Selected topics in Communications and Information Engineering", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics in CIE."},
        "CIE 598": {"name": "Senior Design Project I", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "Graduate senior design project part 1."},
        "CIE 599": {"name": "Senior Design Project II", "credits": 3, "level": "Graduate", "prerequisites": ["CIE 598"], "description": "Graduate senior design project part 2."}
    },
    
    # BIOMEDICAL SCIENCES (BMS) - Official ZC Course Catalog (97 courses)
    "BMS": {
        # Sophomore Level (10 courses)
        "BMS 201": {"name": "General Microbiology", "credits": 3, "level": "Sophomore", "prerequisites": ["BIOL 102"], "description": "Microorganisms, molecular biology of bacteria, microbial pathogens, microbial genetics."},
        "BMS 202": {"name": "Cell Biology", "credits": 3, "level": "Sophomore", "prerequisites": ["BIOL 102"], "description": "Cellular structure, functions, membrane, organelles, gene expression, cell cycle."},
        "BMS 203": {"name": "Principles of Genetics", "credits": 3, "level": "Sophomore", "prerequisites": ["BIOL 102"], "description": "Classical theory of heredity, molecular basis, DNA/RNA structure, recombinant DNA."},
        "BMS 204": {"name": "Biochemistry", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 201"], "description": "Structure, function, metabolism of proteins, nucleic acids, carbohydrates, lipids."},
        "BMS 205": {"name": "Human Physiology", "credits": 3, "level": "Sophomore", "prerequisites": ["BIOL 102"], "description": "Function of neural, cardiovascular, musculoskeletal, GI, endocrine systems."},
        "BMS 211": {"name": "General Microbiology Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Laboratory safety, microscopy, aseptic techniques, staining, bacterial growth."},
        "BMS 212": {"name": "Cell Biology Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Cell and tissue cultures and cell biology techniques."},
        "BMS 213": {"name": "Principles of Genetics Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Classical and molecular genetics: chi-square, gene mapping, DNA extraction, Southern blotting."},
        "BMS 214": {"name": "Biochemistry Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Protein purification, enzyme assays, kinetics, proteolysis, chromatography."},
        "BMS 215": {"name": "Human Physiology Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Nervous system, muscles, respiration, cardiac vascular, exercise physiology."},
        # Junior Level (48 courses)
        "BMS 301": {"name": "Molecular Biology", "credits": 3, "level": "Junior", "prerequisites": ["BMS 202"], "description": "Essentials of molecular biology, DNA replication, transcription, translation."},
        "BMS 302": {"name": "Functional Genomics and System Biology", "credits": 3, "level": "Junior", "prerequisites": ["BMS 202", "BMS 203", "BMS 204"], "description": "Gene function, regulation, and complex systems interactions."},
        "BMS 303": {"name": "Experimental Design and Data Analysis", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Hypothesis formulation, experiment design, data analysis and conclusions."},
        "BMS 304": {"name": "Biomedical Scientific Ethics and Safety", "credits": 2, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Ethical, social, environmental issues, biosafety regulations."},
        "BMS 311": {"name": "Molecular Biology Lab", "credits": 1, "level": "Junior", "prerequisites": [], "description": "DNA isolation, PCR, RNA isolation, gene cloning."},
        "BMS 313": {"name": "Human Anatomy Lab", "credits": 1, "level": "Junior", "prerequisites": [], "description": "Human anatomy, tissue structure, skeletal system, organ dissection."},
        "BMS 320": {"name": "Introduction to Bioinform and Prog Languag", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102", "CSCI 101", "MATH 102"], "description": "Computer science and mathematics applied to life sciences problems."},
        "BMS 321": {"name": "Programming for Computational Biology", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102", "MATH 102"], "description": "Practical programming, scientific algorithms, simulation, optimization."},
        "BMS 322": {"name": "Structural Biology", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Physical properties of proteins, nucleic acids, lipids, biological roles."},
        "BMS 323": {"name": "Comparative Biology", "credits": 3, "level": "Junior", "prerequisites": ["BMS 203"], "description": "Evolution theories and organism adaptation to environment."},
        "BMS 324": {"name": "Molecular Genetics and Cell Regulation", "credits": 3, "level": "Junior", "prerequisites": ["BMS 202"], "description": "Human genetics, gene regulation, epigenetics, genetic variations."},
        "BMS 325": {"name": "Clinical Sciences", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Clinical and translational sciences, disease presentation, clinical shadowing."},
        "BMS 326": {"name": "Molecular Mechanisms of Cell Signaling", "credits": 3, "level": "Junior", "prerequisites": ["BMS 202"], "description": "Cell signaling, signal transduction, cell fate during development and disease."},
        "BMS 327": {"name": "Neurobiology and Practicum", "credits": 3, "level": "Junior", "prerequisites": ["BMS 202"], "description": "Central nervous system, sensory and motor systems, synaptic transmission."},
        "BMS 328": {"name": "Computer Science II", "credits": 3, "level": "Junior", "prerequisites": ["CSCI 101"], "description": "Design and analysis of algorithms, data structures, NP-completeness."},
        "BMS 330": {"name": "Human Anatomy", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Basic human anatomy, organ systems, CNS, cardiovascular, respiratory."},
        "BMS 331": {"name": "Numerical Analysis and Mat Lab", "credits": 3, "level": "Junior", "prerequisites": ["MATH 201"], "description": "Numerical analysis, differentiation, integration, ODEs, Matlab."},
        "BMS 332": {"name": "Drug Discovery and Development", "credits": 3, "level": "Junior", "prerequisites": ["BMS 204"], "description": "Drug discovery process, hit identification, ADMET, clinical trials."},
        "BMS 333": {"name": "Drug Design and Computational Chemistry", "credits": 3, "level": "Junior", "prerequisites": ["BMS 204"], "description": "Lead discovery and optimization, computational chemistry foundations."},
        "BMS 333L": {"name": "Drug Design & Computational Chem Lab", "credits": 1, "level": "Junior", "prerequisites": [], "description": "Computational chemistry techniques, geometry optimization."},
        "BMS 334": {"name": "Pharmacokinetics and Pharmacodynamics", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Drug ADME properties, pharmacodynamics, PK/PD modeling."},
        "BMS 335": {"name": "Advanced Microbiology and Practicum", "credits": 3, "level": "Junior", "prerequisites": ["BMS 201"], "description": "Emerging infectious diseases, antibiotic resistance, microbial biotechnology."},
        "BMS 336": {"name": "Stem Cells and Regenerative Medicine and Practicum", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Stem cell biology, types, applications in therapy."},
        "BMS 337": {"name": "Cancer Biology and Practicum", "credits": 3, "level": "Junior", "prerequisites": ["BMS 202"], "description": "Cell proliferation, differentiation, apoptosis, metastasis, oncogenesis."},
        "BMS 339": {"name": "Principles of Pharmacology and Toxicology", "credits": 3, "level": "Junior", "prerequisites": ["BMS 204", "BMS 205"], "description": "Drug mechanisms, receptor function, signal transduction, ADME."},
        "BMS 340": {"name": "Advanced BMS Laboratory Techniques", "credits": 4, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Advanced laboratory skills, protocols, research techniques."},
        "BMS 343": {"name": "Drug Design and Computational Chemistry Lab", "credits": 1, "level": "Junior", "prerequisites": [], "description": "Lead discovery, computational chemistry techniques."},
        "BMS 344": {"name": "Human Embryology", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Embryological development, fertilization, gastrulation, organogenesis."},
        "BMS 349": {"name": "Principles of Pharmacology and Toxicology Laboratory", "credits": 1, "level": "Junior", "prerequisites": [], "description": "Pharmacological investigation techniques, functional studies."},
        "BMS 364": {"name": "Biophysics", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Physical principles in cell biology, polymer science, statistical physics."},
        "BMS 399": {"name": "Internship (For BIOMEDICAL SCIENCES PROGRAM)", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Off campus activities, research labs, hospital shadowing, pharma labs."},
        # Senior Level (32 courses)
        "BMS 401": {"name": "Senior Project I", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Research project planning and execution."},
        "BMS 401 D": {"name": "DDD Senior Project I", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Drug Design and Development senior research project."},
        "BMS 402": {"name": "Senior Project II", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Finalize project and thesis presentation."},
        "BMS 404": {"name": "Biostatistics", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 101"], "description": "Statistical methods for biomedical data analysis."},
        "BMS 405": {"name": "Medicinal and Biological Chemistry", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 203", "BMS 339"], "description": "Drug action principles, molecular mechanisms."},
        "BMS 406": {"name": "Molecular Modeling and Targeted Drug Design", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 203", "BMS 333"], "description": "Structure and ligand-based drug design, virtual screening."},
        "BMS 409": {"name": "Drug Target Identification and Validation", "credits": 3, "level": "Senior", "prerequisites": ["BMS 205", "BMS 339"], "description": "Target discovery and validation, siRNA, antisense, knockout mice."},
        "BMS 415": {"name": "Medicinal and Biological Chemistry Lab", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Synthesis of pharmaceutical substances, spectral interpretation."},
        "BMS 416": {"name": "Molecular Modeling and Targeted Drug Design lab", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Computational drug design, virtual screening, visualization tools."},
        "BMS 422": {"name": "Algorithmic Foundations of Comp Biology", "credits": 3, "level": "Senior", "prerequisites": ["BMS 321", "MATH 201"], "description": "Algorithms for genomic analysis, sequence analysis, structure prediction."},
        "BMS 423": {"name": "Integrative Biology", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202"], "description": "Integrated biosystems, comparative biology, physiological genomics."},
        "BMS 425": {"name": "Protein Structure and Function", "credits": 3, "level": "Senior", "prerequisites": ["BMS 204", "PHYS 102", "MATH 102"], "description": "Protein structure-function relationships, biophysical principles."},
        "BMS 426": {"name": "Developmental Biology and Genomics", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202", "BMS 203"], "description": "Growth and development, cell differentiation, morphogenesis."},
        "BMS 428": {"name": "Pathology", "credits": 3, "level": "Senior", "prerequisites": ["BMS 330"], "description": "Cellular and molecular basis of disease, inflammation, necrosis."},
        "BMS 428 L": {"name": "Pathology Lab", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Pathological processes, staining techniques, immunohistochemistry."},
        "BMS 429": {"name": "Molecular Immunology", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202"], "description": "Immune system, immune cell interactions, autoimmunity."},
        "BMS 430": {"name": "Advanced Strategies in Organic Synthesis", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 201", "CHEM 203"], "description": "Advanced organic chemistry, Click Chemistry, Combinatorial Chemistry."},
        "BMS 432": {"name": "Structural Elucidation and Instrumental Analysis", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 201", "BMS 201"], "description": "Mass spectrometry, LC-MS, proteomics, metabolomics."},
        "BMS 434": {"name": "Epigenetics in Health and Disease", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202"], "description": "Epigenetic control of gene expression, cellular identity, disease."},
        "BMS 435": {"name": "Legal Aspects in Drug Desig Development", "credits": 1, "level": "Senior", "prerequisites": [], "description": "National and international drug registration regulations."},
        "BMS 438": {"name": "Human Pathophysiology", "credits": 3, "level": "Senior", "prerequisites": ["BMS 330"], "description": "Pathophysiology of body systems and organ disorders."},
        "BMS 444": {"name": "Metagenomics", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202"], "description": "Gene sequencing, microbial genomes, taxonomic characterization."},
        "BMS 448": {"name": "Pathology Lab", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Pathological processes, staining, immunohistochemistry."},
        "BMS 451": {"name": "Biology of Ageing", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202", "BMS 301"], "description": "Theories of aging, aging disorders, molecular biology of aging."},
        "BMS 452": {"name": "Mitochondria in Health and Disease", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202", "BMS 301"], "description": "Mitochondrial function, mitogenesis, mitochondrial diseases."},
        "BMS 455": {"name": "Cellular and Molecular Imaging", "credits": 3, "level": "Senior", "prerequisites": ["BMS 204"], "description": "Biomedical imaging, MRI, tomography, fluorescent microscopy."},
        "BMS 456": {"name": "Forensic Biology", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202", "BMS 204"], "description": "Molecular biology and chemistry for forensic investigations."},
        "BMS 457": {"name": "Clinical Nutrition", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102"], "description": "Food and health, nutrition disorders, obesity, diabetes."},
        "BMS 458": {"name": "Fermentation", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Fermentation technology, bioprocess development, gene expression."},
        "BMS 459": {"name": "Pathogens and Host Defense", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102"], "description": "Pathogen biology, disease mechanisms, diagnostic tools."},
        "BMS 460": {"name": "Development and Commercialization", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Product development from discovery to market."},
        "BMS 462": {"name": "Pharmacogenomics", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202", "BMS 204"], "description": "Genetic variations and drug response, cytochrome P450."},
        "BMS 463": {"name": "Vaccines", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Vaccine types, construction technologies, biosafety."},
        "BMS 465": {"name": "Virology", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102"], "description": "Viral structure, replication, transcription, assembly."},
        "BMS 467": {"name": "Bacteriophages as Antibacterial Agent", "credits": 3, "level": "Senior", "prerequisites": ["BMS 201"], "description": "Phage therapy, pharmacokinetics, safety, applications."},
        "BMS 468": {"name": "Bioorganic & Natural Products Chemistry", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Natural products, biosynthesis, molecular recognition."},
        "BMS 469": {"name": "Targeted Metabolism & Redox Biology", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Mitochondrial biology, bioenergetics, redox signaling."},
        "BMS 470": {"name": "Animal Models of Diseases", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Scientific, ethical, legal aspects of animal research."},
        "BMS 471": {"name": "Clinical Trials Design, Administration and Management", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 202", "BMS 333"], "description": "Clinical trial theory, design, financing, monitoring."},
        "BMS 472": {"name": "Pharmaceutics", "credits": 4, "level": "Senior", "prerequisites": [], "description": "Drug design, molecular modeling, virtual screening."},
        "BMS 473": {"name": "Foundations of Computational and Systems Biology", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 101", "MATH 102", "CSCI 101"], "description": "Mathematical models, computational analysis, genomics."},
        "BMS 474": {"name": "Genomics and Data Sciences", "credits": 3, "level": "Senior", "prerequisites": ["MATH 201", "BMS 321"], "description": "Numerical methods for linear algebra, differential equations."},
        "BMS 475": {"name": "Bio Chemistry of Hormones and Vitamins", "credits": 3, "level": "Senior", "prerequisites": ["BMS 204"], "description": "Advanced biochemistry, signaling, metabolic regulation."},
        "BMS 477": {"name": "The Human Genome and Disease", "credits": 3, "level": "Senior", "prerequisites": ["BMS 202", "BMS 203"], "description": "DNA damage, repair mechanisms, genomic instability."},
        "BMS 496": {"name": "Selected Topics in BMS", "credits": 1, "level": "Senior", "prerequisites": [], "description": "In-depth training on selected biomedical topics."},
        "BMS 499": {"name": "Selected Topics in BMS", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in biomedical sciences."},
        # Graduate Level (9 courses)
        "BMS 500 A": {"name": "Directed Research Field Study", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Off campus DDD research activities, industry, international labs."},
        "BMS 500 B": {"name": "Directed Research Field Study", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Off campus DDD research activities, industry, international labs."},
        "BMS 500 C": {"name": "Directed Research Field Study", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Off campus DDD research activities, industry, international labs."},
        "BMS 500 D": {"name": "Directed Research Field Study", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Off campus DDD research activities, industry, international labs."},
        "BMS 501": {"name": "Senior Project II", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Research project planning and execution."},
        "BMS 502": {"name": "Senior Project III", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Finalize project and thesis presentation."},
        "BMS 503": {"name": "Genome Stability & Drug Development", "credits": 3, "level": "Graduate", "prerequisites": ["BMS 203", "BMS 204", "BMS 301"], "description": "Genome stability, siRNA screening, drug targets."},
        "BMS 504": {"name": "Targeting DNA Repair in Person Medicine", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "DNA repair drug targets, synthetic lethality, personalized medicine."},
        "BMS 506": {"name": "Molecular Modeling and Targeted Drug Des", "credits": 4, "level": "Graduate", "prerequisites": ["PHYS 101", "CHEM 202", "BMS 333"], "description": "Advanced drug design, molecular modeling, virtual screening."},
        "BMS 701": {"name": "Computational Methods in Biomedical Sciences", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Machine learning, algorithms, genomics, drug simulation."}
    },
    
    # NANOSCIENCE (NANOSC) - Official ZC Course Catalog (46 courses)
    "NANOSC": {
        # Junior Level (20 courses)
        "NANOSC 301": {"name": "Spectroscopy of Nanomaterials", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Electromagnetic spectrum, radiation-matter interaction, spectroscopy techniques."},
        "NANOSC 302": {"name": "Modern Characterization Techniques I", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Atomic absorption, electronic absorption, fluorescence spectroscopy, UV-vis, IR, NMR."},
        "NANOSC 303": {"name": "Quantum Mechanics", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 102"], "description": "Schroedinger's equation, quantum waves, particle in a box, angular momentum, hydrogen atom."},
        "NANOSC 304": {"name": "Emerging Nanomaterials", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 201"], "description": "Graphene, fullerene, carbon nanotubes, polymeric nanoparticles, quantum dots."},
        "NANOSC 305": {"name": "Synthesis/Fabrication of Nanomaterials", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Top-down and bottom-up nanostructuring, lithographic techniques, self-assembly."},
        "NANOSC 306": {"name": "Statistical Mechanics & Therm Nanscale S", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Thermodynamics and statistical mechanics for nanoscale systems, Boltzmann distributions."},
        "NANOSC 307": {"name": "Nanosciences Research Lab Rotations", "credits": 1, "level": "Junior", "prerequisites": [], "description": "Research lab rotations with different researchers at Zewail City."},
        "NANOSC 308": {"name": "Introduction to Polymer Science", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Polymer structure, polymerization kinetics, polymer processing technologies."},
        "NANOSC 309": {"name": "Principles of Pharmacokinetics", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Pharmacokinetics modeling, drug action, dosing regimens."},
        "NANOSC 310": {"name": "Computer Aided Drug Design", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Lead identification and optimization, quantum statistical approaches, computational techniques."},
        "NANOSC 312": {"name": "Modern Characterization Techniques Lab I", "credits": 1, "level": "Junior", "prerequisites": [], "description": "UV-vis-NIR, FTIR, Raman, X-ray diffraction, SEM, TEM, AFM."},
        "NANOSC 313": {"name": "Advanced Characterization Techniques", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 201", "PHYS 202"], "description": "Electron and optical microscopy, X-Ray techniques, 1D and 2D NMR, mass spectrometry."},
        "NANOSC 315": {"name": "Synthesis/Fabrication of Nanomateria Lab", "credits": 1, "level": "Junior", "prerequisites": [], "description": "Fabrication of polymer nanoparticles, nanocomposites, thin films, Ferro-fluids."},
        "NANOSC 317": {"name": "Special Topics in Bio-Nanotechnology", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102", "CHEM 201"], "description": "Biomolecular structures, DNA nanotechnology, drug delivery, biosensors, synthetic biology."},
        "NANOSC 322": {"name": "Chemistry & Physics of Nanomaterials", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 101"], "description": "Physical chemistry nanoprocess, nano-synthesis, nano-formulations."},
        "NANOSC 328": {"name": "Biological Nanomaterials", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 202"], "description": "Nanofibres, microtubules, viruses, ribosomes from nanoscience perspective."},
        "NANOSC 392": {"name": "Introduction to Nanochemistry", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 202"], "description": "Supramolecular chemistry and inorganic nanostructures."},
        "NANOSC 399": {"name": "Internship (For NANO SCIENCE PROGRAM)", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Experiential learning integrating classroom knowledge with professional practice."},
        # Senior Level (28 courses)
        "NANOSC 401": {"name": "Nanotexicology", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 305"], "description": "Nanotoxicology, nanoparticle characterization, toxicokinetics, risk assessment."},
        "NANOSC 402": {"name": "Nanoimaging", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 302", "NANOSC 305"], "description": "Nanoparticles for in vitro and in vivo diagnostic imaging and therapy."},
        "NANOSC 403": {"name": "Special Topics in Nanomedicine", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 305", "BIOL 102"], "description": "Bioimaging, drug delivery, tissue engineering, nanotoxicology, regulatory aspects."},
        "NANOSC 404": {"name": "Principles of Pharmacology", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102", "BMS 204"], "description": "Pharmacology principles, toxicology, ecotoxicology, nanoparticle bioaccumulation."},
        "NANOSC 405": {"name": "Nanopharmaceutics", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 305"], "description": "Drug development, pharmaceutical formulations, biocompatible nanomaterials."},
        "NANOSC 406": {"name": "Nanomat for Reg Med Tissue Engin", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 305"], "description": "Tissue engineering, stem cells, polymer technology, biologically active scaffolds."},
        "NANOSC 407": {"name": "Special Topics in Bio-Nanotechnology", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 305", "BIOL 102"], "description": "Biomolecular structures, DNA origami, drug delivery, tissue engineering, biosensors."},
        "NANOSC 408": {"name": "Synthetic Biology", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Cell reprogramming, design-build-test cycle, transcriptional and translational regulation."},
        "NANOSC 409": {"name": "Surfaces and colloidal Science", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Surface characteristics, thin films, colloidal processes, microfluidics, lab-on-a-chip."},
        "NANOSC 411": {"name": "Bio-Nanotechnology Lab", "credits": 1, "level": "Senior", "prerequisites": ["NANOSC 315", "NANOSC 317"], "description": "Recent directions of bionanotechnology laboratory."},
        "NANOSC 412": {"name": "Nanochemistry Lab", "credits": 1, "level": "Senior", "prerequisites": ["NANOSC 392"], "description": "Solid state chemistry, nanochemistry synthesis, characterization, functionalization."},
        "NANOSC 413": {"name": "Photonics & Laser Physics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 202"], "description": "Optical physics, diffraction, atomic physics, laser physics, optical fibres, photonic crystals."},
        "NANOSC 415": {"name": "Elect & Mag Properties of Nano Materials", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 202"], "description": "Electron transport, dielectric nanomaterials, semiconductors, energy band models."},
        "NANOSC 416": {"name": "Modeling of Nano Materials", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 202"], "description": "DFT modeling for electronic, mechanical, optical, magnetic properties of nanomaterials."},
        "NANOSC 417": {"name": "Nanomedicine Lab", "credits": 1, "level": "Senior", "prerequisites": ["NANOSC 305", "BIOL 102"], "description": "Drug delivery, scaffolds, regenerative medicine, biosensors."},
        "NANOSC 420": {"name": "Physics of Nanostructured Semiconductors", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 202"], "description": "Electronic, vibrational, transport, optical characteristics of semiconductors."},
        "NANOSC 421": {"name": "Nanostructured Mat & Nanosc Thin Film", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 302", "NANOSC 305"], "description": "Materials science of micro- and nanoscale thin films, failure mechanisms."},
        "NANOSC 424": {"name": "Kinetics & Energetics Nanobiological Syt", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 202", "BIOL 102"], "description": "Energy transduction, electron transport, oxidation/reduction, biochemical kinetics."},
        "NANOSC 425": {"name": "Quantum Theory for Nanoscale Systems", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 202"], "description": "Solid-state quantum theory, Schrödinger equation for periodic potentials, tunneling."},
        "NANOSC 426": {"name": "Colloidal Nanoscience", "credits": 3, "level": "Senior", "prerequisites": ["CHEM 202"], "description": "Colloidal processes, intermolecular forces, microfluidics, polymersomes."},
        "NANOSC 427": {"name": "Biol Routes of Nanomat Syn & Gr of NS Ma", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102"], "description": "Biological synthesis routes for nanomaterials, molecular self-assembly."},
        "NANOSC 428": {"name": "Biological Nanomaterials", "credits": 3, "level": "Senior", "prerequisites": ["NANOSC 304", "BIOL 102"], "description": "Nanofibres, microtubules, viruses, ribosomes as nanoscale chemical systems."},
        "NANOSC 431": {"name": "Nanobiology", "credits": 3, "level": "Senior", "prerequisites": ["BIOL 102"], "description": "Biosensors, bio-MEMS/NEMS, biomolecular electronics, nano-biological systems."},
        "NANOSC 433": {"name": "Nano- & Biophotonics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 202"], "description": "Light-matter interaction, nanoscale bioimaging, super-resolution microscopy."},
        "NANOSC 458": {"name": "Nanoscience Capstone Research Project I", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Research project in laboratory setting, written paper and oral presentation."},
        "NANOSC 497": {"name": "Selected Topics in Nanoscience", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Research project on current topics in nanoscience."},
        "NANOSC 498": {"name": "Nanoscience Capstone Research Project II", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Part 2 of capstone research project."},
        "NANOSC 499": {"name": "Nanoscience Capstone Research Project", "credits": 4, "level": "Senior", "prerequisites": [], "description": "4 credit research project with thesis and oral presentation."}
    },
    
    # PHYSICS OF THE UNIVERSE (PEU) - Official ZC Course Catalog (40 courses)
    "PEU": {
        # Sophomore Level (7 courses)
        "PEU 204": {"name": "Analytical Mechanics", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 101"], "description": "Lagrangian and Hamiltonian formalisms, rigid bodies, perturbation theory, chaotic dynamics."},
        "PEU 205": {"name": "Introduction to Modern Astrophysics", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 101"], "description": "Basic observational and theoretical methods, techniques, technical language of astronomy."},
        "PEU 207": {"name": "Earth & Atmospheric Sciences", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Physics and chemistry of Earth and atmosphere, geology, vulcanism, atmospheric flows."},
        "PEU 210": {"name": "Advanced Electromagnetism", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 102"], "description": "Electrostatics, magnetism, Maxwell equations, electromagnetic waves, waveguides."},
        "PEU 218": {"name": "Vector Calculus", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 102"], "description": "Vector algebra, line/surface/volume integrals, gradient, divergence, curl, tensors."},
        "PEU 223": {"name": "Rock and Minerals", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Earth crust composition, rock types, mineralogy, crystallography."},
        "PEU 228": {"name": "Vector Calculus", "credits": 2, "level": "Sophomore", "prerequisites": ["MATH 102"], "description": "Vector algebra, integrals, gradient, divergence, curl, curvilinear coordinates."},
        # Junior Level (16 courses)
        "PEU 304": {"name": "Electrodynamics I", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 102"], "description": "Electrostatics, magnetostatics, time-varying fields, Maxwell's equations."},
        "PEU 308": {"name": "Electrodynamics II", "credits": 3, "level": "Junior", "prerequisites": ["PEU 208"], "description": "Electromagnetic wave propagation, waveguides, retarded potentials, relativistic electrodynamics."},
        "PEU 311": {"name": "Thermal and Statistical Physics", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 201"], "description": "Boltzmann transport equation, statistical physics, macroscopic properties of many-body systems."},
        "PEU 315": {"name": "Geophysics", "credits": 3, "level": "Junior", "prerequisites": ["PEU 207"], "description": "Gravitational field, geomagnetism, seismology, plate tectonics, oil exploration."},
        "PEU 316": {"name": "Mathematical Physics I", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Fourier analysis, special functions, Green's functions."},
        "PEU 323": {"name": "Quantum Mechanics I", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 202"], "description": "Schrodinger equation, square well, harmonic oscillator, hydrogen atom, angular momentum."},
        "PEU 326": {"name": "Mathematical Physics II", "credits": 3, "level": "Junior", "prerequisites": ["PEU 346", "MATH 201", "MATH 202"], "description": "Differential equations, linear algebra, eigenvalue problems, numerical methods, Mathematica, MatLab."},
        "PEU 327": {"name": "Observational Astrophysics Laboratory", "credits": 2, "level": "Junior", "prerequisites": ["PEU 205"], "description": "Astronomical data collection and analysis, statistical concepts, measurement precision."},
        "PEU 329": {"name": "Earth & Atmospheric Sciences II", "credits": 3, "level": "Junior", "prerequisites": ["PEU 207"], "description": "Thermodynamics and hydrostatics of atmosphere, meteorology, governing equations."},
        "PEU 331": {"name": "Stellar Structure and Evolution", "credits": 3, "level": "Junior", "prerequisites": ["PEU 205"], "description": "Main sequence stellar theory, star formation, end states."},
        "PEU 340": {"name": "Atmospheric Sciences Lab", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Laboratory experiments in atmospheric physics."},
        "PEU 346": {"name": "Mathematical Physics I", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202"], "description": "Fourier analysis, special functions, Green's functions."},
        "PEU 348": {"name": "Quantum Mechanics II", "credits": 3, "level": "Junior", "prerequisites": ["PEU 323"], "description": "Eigen functions, perturbation theory, scattering theory, Quantum Field Theory intro."},
        "PEU 356": {"name": "Mathematical Physics II", "credits": 4, "level": "Junior", "prerequisites": ["MATH 201"], "description": "Analytical and numerical methods, differential equations, computational techniques."},
        "PEU 364": {"name": "Biological Physics", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102"], "description": "Physical basis of biological molecules, biophysics of proteins, nucleic acids, lipids."},
        "PEU 399": {"name": "Internship", "credits": 2, "level": "Junior", "prerequisites": [], "description": "External training in industry or research institution on physics-related projects."},
        # Senior Level (17 courses)
        "PEU 404": {"name": "Senior Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Research project applying physics knowledge and scientific methods."},
        "PEU 405": {"name": "Cosmology", "credits": 3, "level": "Senior", "prerequisites": ["PEU 205"], "description": "Friedmann models, early universe, inflation, cosmic microwave background, dark matter."},
        "PEU 407": {"name": "Climatology & Climate Change", "credits": 3, "level": "Senior", "prerequisites": ["PEU 207"], "description": "Climate and weather systems, weather forecasting, climate change."},
        "PEU 412": {"name": "Oceanography", "credits": 3, "level": "Senior", "prerequisites": ["PEU 207"], "description": "Ocean basins, circulation, plate tectonics, hurricanes, El Niño, waves and tides."},
        "PEU 414": {"name": "Senior Project II", "credits": 2, "level": "Senior", "prerequisites": ["PEU 404"], "description": "Continuation of research project in physics."},
        "PEU 416": {"name": "Galactic & Extragalactic Astrophysics", "credits": 3, "level": "Senior", "prerequisites": ["PEU 205"], "description": "Galaxies, stellar content, kinematics, interstellar medium, dark matter, gravitational lensing."},
        "PEU 420": {"name": "The Solar System", "credits": 3, "level": "Senior", "prerequisites": ["PEU 205"], "description": "Origins of sun and solar system, planets, atmospheres, satellites, asteroids, comets."},
        "PEU 422": {"name": "Astrophysical Fluid Dynamics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Fluid dynamics for astronomical phenomena, stellar structure, accretion discs."},
        "PEU 430": {"name": "Quantum Mechanics III", "credits": 3, "level": "Senior", "prerequisites": ["PEU 348"], "description": "Time-independent perturbation theory, variational principle, WKB, scattering, Dirac equation."},
        "PEU 431": {"name": "Quantum Field Theory and Particle Phys", "credits": 6, "level": "Senior", "prerequisites": ["PEU 323"], "description": "QFT formalism, Feynman diagrams, QED, gauge theory, Standard Model."},
        "PEU 432": {"name": "Advanced Dynamics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 101"], "description": "Hamiltonian/Lagrangian mechanics, chaos, bifurcations, phase space structure."},
        "PEU 438": {"name": "Compact Objects & High Energy Astrophysics", "credits": 3, "level": "Senior", "prerequisites": ["PEU 205"], "description": "Neutron stars, pulsars, black holes, supernovae, gamma-ray bursts."},
        "PEU 450": {"name": "Computational Physics", "credits": 3, "level": "Senior", "prerequisites": ["CSCI 101"], "description": "Computational methods for physics, astronomy and atmospheric science."},
        "PEU 453": {"name": "Gravity & General Relativity", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Spacetime, core principles of general relativity, experimental evidence."},
        "PEU 455": {"name": "Mathematical Physics III", "credits": 3, "level": "Senior", "prerequisites": ["PEU 316"], "description": "Calculus of variations, integral equations, topology, group theory."},
        "PEU 498": {"name": "Senior Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Research project in physics."},
        "PEU 499": {"name": "Senior Project II", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Continuation of senior research project."}
    },
    
    # MATERIALS SCIENCE (MATSCI) - Official ZC Course Catalog (43 courses)
    "MATSCI": {
        # Sophomore Level (5 courses)
        "MATSCI 201": {"name": "Fundamentals of Materials Science and Engineering", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 101", "PHYS 101"], "description": "Atomic structure, crystallography, defects, and materials properties."},
        "MATSCI 204": {"name": "Inorganic chemistry", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 102"], "description": "Coordination chemistry, transition metals, and bonding theories."},
        "MATSCI 214": {"name": "Inorganic chemistry lab", "credits": 1, "level": "Sophomore", "prerequisites": ["MATSCI 204"], "description": "Laboratory experiments in inorganic chemistry."},
        "MATSCI 255": {"name": "Introduction to Nanomaterials Synthesis", "credits": 2, "level": "Sophomore", "prerequisites": ["CHEM 101"], "description": "Fundamentals of nanomaterials synthesis techniques."},
        "MATSCI 255 L": {"name": "Advanced Nanomaterials Synthesis", "credits": 2, "level": "Sophomore", "prerequisites": ["MATSCI 255"], "description": "Advanced nanomaterials synthesis laboratory."},
        # Junior Level (12 courses)
        "MATSCI 301": {"name": "Catalysis", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Heterogeneous and homogeneous catalysis, industrial applications."},
        "MATSCI 302": {"name": "Solid State Physics", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 102"], "description": "Crystal structures, electronic band theory, and phonons."},
        "MATSCI 303": {"name": "Macromolecular Chemistry", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Polymer synthesis, characterization, and properties."},
        "MATSCI 304": {"name": "Modern Characterization Techniques II", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Advanced materials characterization methods."},
        "MATSCI 305": {"name": "Quantum Chemistry", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Molecular quantum mechanics and computational methods."},
        "MATSCI 306": {"name": "Organic Polymer Chemistry", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Chemistry of organic polymers and polymerization."},
        "MATSCI 307": {"name": "Introduction to scientific computing", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Numerical methods and computational techniques for science."},
        "MATSCI 308": {"name": "Computational modeling", "credits": 3, "level": "Junior", "prerequisites": ["MATSCI 307"], "description": "DFT, molecular dynamics, and materials simulation."},
        "MATSCI 317": {"name": "Introduction to scientific computing lab", "credits": 1, "level": "Junior", "prerequisites": ["MATSCI 307"], "description": "Laboratory for scientific computing."},
        "MATSCI 318": {"name": "Computational modeling lab", "credits": 1, "level": "Junior", "prerequisites": ["MATSCI 308"], "description": "Laboratory for computational modeling."},
        "MATSCI 399": {"name": "Internship (For MATERIALS SCIENCE PROGRAM)", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Supervised internship in materials science industry."},
        # Senior Level (26 courses)
        "MATSCI 402": {"name": "Advanced Organic Chemistry", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Advanced reaction mechanisms and synthesis strategies."},
        "MATSCI 403": {"name": "Physical chemistry and Kinetics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Physical chemistry principles and kinetics."},
        "MATSCI 404": {"name": "Electrochemistry", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Electrochemical cells, kinetics, and applications."},
        "MATSCI 405": {"name": "X-ray Diffraction", "credits": 3, "level": "Senior", "prerequisites": [], "description": "X-ray crystallography and diffraction analysis."},
        "MATSCI 406": {"name": "Environmental Chemistry", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Chemical processes in the environment."},
        "MATSCI 407": {"name": "Biochemistry", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Biochemistry fundamentals and applications."},
        "MATSCI 408": {"name": "Thin Film Preparation & Characterization", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Thin film deposition, surface characterization, and applications."},
        "MATSCI 409": {"name": "Surface Science", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Surface chemistry and surface analysis techniques."},
        "MATSCI 410": {"name": "Photochemistry and Photophysics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Photochemical and photophysical processes."},
        "MATSCI 412": {"name": "Sensors and Actuators", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Principles and applications of sensors and actuators."},
        "MATSCI 413": {"name": "Materials for Energy Conversion and Storage", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Solar cells, batteries, fuel cells, and energy materials."},
        "MATSCI 414": {"name": "Corrosion and Corrosion Protection", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Corrosion mechanisms and protection methods."},
        "MATSCI 415": {"name": "Industrial Chemistry", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Industrial chemical processes and applications."},
        "MATSCI 416": {"name": "Lab on Chip (Microfluidics)", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Microfluidics and lab-on-chip technologies."},
        "MATSCI 417": {"name": "Cosmetics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Chemistry and formulation of cosmetic products."},
        "MATSCI 418": {"name": "Drug Discovery and Delivery", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Principles of drug discovery and delivery systems."},
        "MATSCI 419": {"name": "Nano devices", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Nanoscale devices and their applications."},
        "MATSCI 420": {"name": "Selected Topics in Advanced Materials", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Contemporary topics in materials science research."},
        "MATSCI 421": {"name": "Selected Topics in Biomedical Science", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Biomedical materials and applications."},
        "MATSCI 422": {"name": "Selected Topics in Environmental Science", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Contemporary topics in environmental science."},
        "MATSCI 423": {"name": "Composite materials", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Composite materials science and engineering."},
        "MATSCI 424": {"name": "Carbon Materials", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Carbon-based materials and their applications."},
        "MATSCI 425": {"name": "Materials for Solar energy conversion and utilization", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Materials for solar energy applications."},
        "MATSCI 426": {"name": "Selected Topics in Advanced Technology: Materials for Electronics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Advanced materials for electronic applications."},
        "MATSCI 427": {"name": "Introduction to Tissue Engineering", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Fundamentals of tissue engineering."},
        "MATSCI 430": {"name": "Material Properties and Material Selection", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Material properties and selection criteria."},
        "MATSCI 480": {"name": "Self-assembled Systems", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Self-assembly principles and applications."},
        "MATSCI 498": {"name": "Selected topics in advanced materials", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Selected topics in advanced materials research."}
    },
    
    # DATA SCIENCE AND AI (DSAI) - Official ZC Course Catalog
    "DSAI": {
        "DSAI 103": {"name": "Data Acquisition in Data Science (ETL)", "credits": 3, "level": "Freshman", "prerequisites": ["CSAI 101"], "description": "Data acquisition process including extraction, transformation, and loading of data into target systems."},
        "DSAI 104": {"name": "Knowledge Representation and Reasoning", "credits": 2, "level": "Freshman", "prerequisites": ["CSAI 101"], "description": "Knowledge representation in symbolic form for automated reasoning, abductive reasoning, and constraint satisfaction."},
        "DSAI 201": {"name": "Data Mining and Information Retrieval", "credits": 3, "level": "Sophomore", "prerequisites": ["CSAI 202"], "description": "Analysis of massive data volumes to extract trends, patterns, and correlations. Text and web mining applications."},
        "DSAI 202": {"name": "Data Governance", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Principles of data governance, metadata, data quality, master data management, and data ethics."},
        "DSAI 203": {"name": "Data Integration and Visualization", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Data consolidation from multiple sources, visual representation methods for complex data understanding."},
        "DSAI 305": {"name": "Interpretability and Explainability in AI", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 253"], "description": "Key differences between explainability and interpretability, techniques for improving ML interpretability."},
        "DSAI 307": {"name": "Statistical Inference", "credits": 2, "level": "Junior", "prerequisites": ["MATH 105"], "description": "Drawing conclusions about populations from samples: estimation, confidence intervals, and hypothesis testing."},
        "DSAI 308": {"name": "Deep Learning", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 253"], "description": "Building neural networks, CNNs, RNNs, LSTM, GAN, Adam, Dropout and practical applications."},
        "DSAI 325": {"name": "Introduction to Information Theory", "credits": 3, "level": "Junior", "prerequisites": ["MATH 105"], "description": "Shannon entropy, mutual information, error correcting codes, data compression, and applications to ML."},
        "DSAI 352": {"name": "Computer Vision", "credits": 3, "level": "Junior", "prerequisites": ["DSAI 308"], "description": "Image fundamentals, Fourier transform, image segmentation, feature extraction, and object recognition."},
        "DSAI 353": {"name": "Natural Language Processing", "credits": 3, "level": "Junior", "prerequisites": ["DSAI 308"], "description": "Text similarity, POS tagging, parsing, semantics, question answering, and sentiment analysis."},
        "DSAI 402": {"name": "Reinforcement Learning", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 308"], "description": "RL framework, bandit problems, dynamic programming, Monte Carlo methods, and TD learning."},
        "DSAI 403": {"name": "Nature Inspired Computation", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Cellular automata, evolutionary computing, swarm intelligence, artificial life, and complex networks."},
        "DSAI 406": {"name": "Machine Learning Engineering for Production (MLOps)", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 308"], "description": "Design and implement ML production systems, data pipelines, model deployment, and monitoring."},
        "DSAI 413": {"name": "Multimedia Analytics", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 308"], "description": "Multimedia feature extraction, semantic classification, speech recognition, and video indexing."},
        "DSAI 414": {"name": "Social Analytics", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 308"], "description": "Social media modeling and analytics, identifying influencers, trending topics, and network visualization."},
        "DSAI 415": {"name": "Cloud Software Development", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 308"], "description": "Develop secure, scalable cloud applications using AWS/Azure/GCP, serverless microservices architecture."},
        "DSAI 416": {"name": "GIS and Spatial Analytics", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 308"], "description": "Geographical Information Systems, spatial analysis techniques, ArcGIS for data preparation and visualization."},
        "DSAI 417": {"name": "Chatbots", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 456"], "description": "Building chatbots using Dialogflow, NLP integration, FAQ and reservation chatbot development."},
        "DSAI 418": {"name": "Conversational Agents", "credits": 3, "level": "Senior", "prerequisites": ["DSAI 456"], "description": "Design and development of conversational agents, spoken dialogue systems, and human-robot interaction."},
        "DSAI 427": {"name": "Big Data Analytics", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 253"], "description": "Hadoop, Spark, HDFS, YARN, MapReduce, Pig, Hive, HBase, and real-time data processing."},
        "DSAI 431": {"name": "Fuzzy Logic and Fuzzy Systems", "credits": 3, "level": "Senior", "prerequisites": ["MATH 205"], "description": "Fuzzy connectives, fuzzy reasoning, fuzzy implications, and intelligent control applications."},
        "DSAI 433": {"name": "Game Theory", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 301"], "description": "Nash equilibrium, subgame perfection, Bayesian equilibrium, repeated games, and economic applications."},
        "DSAI 456": {"name": "Speech Recognition", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Speech analysis and synthesis, spectral analysis, HMM, neural networks, and speaker recognition."},
        "DSAI 473": {"name": "Data Warehousing", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Data warehouse architecture, Kimball and Inmon methodologies, ETL processes, and schema design."},
        "DSAI 490": {"name": "Selected Topics in Data Science and AI", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Special topics in Data Science and AI of interest, can be repeated with different topics."}
    },
    
    # SOFTWARE DEVELOPMENT (SWDEV)
    # SOFTWARE ENGINEERING (SW) - Official ZC Course Catalog (32 courses)
    "SW": {
        # Core SW Courses (8 courses)
        "SW 151": {"name": "Computer Architecture and Organization", "credits": 3, "level": "Sophomore", "prerequisites": ["CSAI 102"], "description": "Harvard and Von Neumann architectures, instruction sets, X86 and ARM assembly, memory hierarchy, I/O devices."},
        "SW 251": {"name": "User Experience and Interaction Design", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "HCI theories to analyze and enhance program designs, user interaction."},
        "SW 252": {"name": "Embedded Systems", "credits": 3, "level": "Sophomore", "prerequisites": ["SW 151"], "description": "Embedded systems hardware and firmware design, processor selection, code debugging."},
        "SW 301": {"name": "Object-Oriented Analysis and Design", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 151"], "description": "Object-oriented paradigm, modeling, requirements development, analysis, and design."},
        "SW 302": {"name": "User Interface Development", "credits": 3, "level": "Junior", "prerequisites": ["SW 251"], "description": "Building user interfaces, prototyping tools, MVC, layout, usability evaluation."},
        "SW 401": {"name": "Parallel and Distributed Computing", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 151"], "description": "Parallel and distributed architectures, programming paradigms, parallel algorithms."},
        "SW 402": {"name": "Software Project Management", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Software life cycle methodologies, cost estimation, risk management approaches."},
        "SW 403": {"name": "AI in Modern Software Engineering", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 203", "CSAI 253"], "description": "AI-powered tools for code generation, testing, documentation, multi-agent systems."},
        # Software Application Development Track (8 courses)
        "SWAPD 301": {"name": "Software Systems Requirements Development", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 203"], "description": "Requirements elicitation, modeling, specification, analysis, documentation, and review."},
        "SWAPD 351": {"name": "Software Architecture and Design", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 203"], "description": "Enterprise-scale software systems design, architectural styles, UML, design patterns."},
        "SWAPD 352": {"name": "Web Applications Development", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 202"], "description": "Web architecture, multi-tier applications, HTML, CSS, JavaScript, frontend and backend frameworks."},
        "SWAPD 401": {"name": "Software Testing, Validation, and Quality Assurance", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Software verification, validation, testing techniques, quality assurance."},
        "SWAPD 402": {"name": "Mobile Application Development", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 201"], "description": "Mobile application development foundations, design and programming skills."},
        "SWAPD 451": {"name": "Software Maintenance", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 203"], "description": "Maintenance and evolution of software systems, refactoring, regression testing."},
        "SWAPD 452": {"name": "Enterprise Application Development", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 202"], "description": "Enterprise application architecture, design patterns, transaction processing, deployment."},
        "SWAPD 453": {"name": "IoT Applications Development", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 252"], "description": "Internet of Things, device gateway, security, edge computing, communications protocols."},
        # Graphics and Computer Games Track (8 courses)
        "SWGCG 301": {"name": "Computer Graphics and Multimedia Systems", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 201"], "description": "Multimedia systems, 2D/3D models, viewing, clipping, rasterization."},
        "SWGCG 351": {"name": "Game Design and Development", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Digital media, game production, engine programming, storytelling, animation."},
        "SWGCG 352": {"name": "Computer and Physics-Based Animation", "credits": 3, "level": "Junior", "prerequisites": ["SWGCG 301"], "description": "Physics-based animation, rigid/deformable solids, liquids, cloth, inverse kinematics."},
        "SWGCG 401": {"name": "Design and Geometric Modeling for Visualization and Communication", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Basic design elements, geometric analysis and modeling, graphic visualization."},
        "SWGCG 402": {"name": "Visual Effects Production", "credits": 3, "level": "Senior", "prerequisites": ["SWGCG 352"], "description": "Visual effects from pre-production to post-production, compositing, dynamic effects."},
        "SWGCG 451": {"name": "Model Creation and Character Animation", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 201"], "description": "3D character production, organic modeling, texturing, skeleton building, animation."},
        "SWGCG 452": {"name": "Physics-Based Vision and Rendering", "credits": 3, "level": "Senior", "prerequisites": ["SWGCG 301"], "description": "Light and color phenomena, physics-based rendering, ray tracing, texture mapping."},
        "SWGCG 453": {"name": "Mobile and Casual Game Development", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 201"], "description": "Mobile game genres, hardware features, casual game patterns, game engines."},
        # Human-Computer Interaction Track (8 courses)
        "SWHCI 301": {"name": "Prototyping Algorithmic Experiences", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 251"], "description": "Iterative prototyping in HCI, data-driven systems, machine learning, spatial computing."},
        "SWHCI 351": {"name": "Statistical Graphics and Visualization", "credits": 3, "level": "Junior", "prerequisites": ["MATH 105"], "description": "Graphics creation and presentation, interactive graphics, animations, network graphics."},
        "SWHCI 352": {"name": "User-Focused Sensing Systems", "credits": 3, "level": "Junior", "prerequisites": ["SW 251"], "description": "Smart sensing devices, embedded computing, computer vision, activity recognition."},
        "SWHCI 401": {"name": "Human Information Processing and Artificial Intelligence", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 301"], "description": "Human information processing, AI methodologies, expert systems, neural networks."},
        "SWHCI 402": {"name": "AI Based Products and Services", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 301"], "description": "AI technologies for design processes, AI-enhanced products and services."},
        "SWHCI 451": {"name": "Cognitive Modeling for HCI", "credits": 3, "level": "Senior", "prerequisites": ["SCH 273"], "description": "Human problem-solving simulation, cognitive modeling software, parameter estimation."},
        "SWHCI 452": {"name": "Designing Extended Reality Experience", "credits": 3, "level": "Senior", "prerequisites": ["SW 251"], "description": "Extended Reality (XR) basics, hardware, applications, psychology, challenges."},
        "SWHCI 453": {"name": "Human Factors", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Human factors in complex systems design, sensory systems, perception, motor performance."}
    },
    
    # INFORMATION TECHNOLOGY (IT) - Official ZC Course Catalog (39 courses)
    "IT": {
        # Core IT Courses (11 courses)
        "IT 101": {"name": "Shell and Script Programming with UNIX", "credits": 2, "level": "Freshman", "prerequisites": ["CSAI 101"], "description": "UNIX shell scripting, Bash, sed, awk, Python and Perl scripting."},
        "IT 102": {"name": "Ethical Hacking and Defense", "credits": 2, "level": "Freshman", "prerequisites": ["CSAI 101"], "description": "Hacking techniques, TCP/IP protocol, port scanning, network attacks, defense mechanisms."},
        "IT 103": {"name": "Fundamentals of Information and Communication Systems", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Digital communications, Fourier transform, sampling, modulation, wireless systems."},
        "IT 205": {"name": "Enterprise System Architecture", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Enterprise architecture design, requirements analysis, UML, lifecycle methodologies."},
        "IT 206": {"name": "Fundamentals of IT Governance and Risk Management", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "IT governance, risk management, transforming IT from expense to investment."},
        "IT 220": {"name": "Networks installation and Maintenance", "credits": 2, "level": "Sophomore", "prerequisites": ["CSAI 252"], "description": "Computer hardware and network maintenance, troubleshooting, upgrades."},
        "IT 222": {"name": "Fundamentals of Multimedia Creation, Storage and Transfer", "credits": 2, "level": "Sophomore", "prerequisites": ["CSAI 252"], "description": "Digital multimedia concepts, capture, creation, manipulation, transfer."},
        "IT 308": {"name": "Cloud Computing Architecture", "credits": 2, "level": "Junior", "prerequisites": ["CSAI 201"], "description": "Cloud architectural principles, scalability, automation, security, reliability."},
        "IT 309": {"name": "IT User-Experience Design", "credits": 3, "level": "Junior", "prerequisites": [], "description": "UX/UI design, information architecture, user scenarios, usability testing."},
        "IT 310": {"name": "Foundations of Cybersecurity and Security Management", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 252"], "description": "Access control, DoS attacks, VPN, cryptographic algorithms, security policies."},
        "IT 401": {"name": "Data Centers", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 252"], "description": "Data center types, infrastructure, Tier I-IV, management, security, cloud comparison."},
        "IT 402": {"name": "Fundamentals of Cybersecurity and Encryption", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Cyber security scope, cryptography, encryption algorithms, key management."},
        "IT 411": {"name": "Enterprise Resources Planning", "credits": 3, "level": "Senior", "prerequisites": [], "description": "ERP systems, SAP, business process support, GUI navigation."},
        # IT Cloud Computing Track - ITCC (14 courses)
        "ITCC 301": {"name": "Linux System Administration", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Linux installation, command line, file management, users, permissions, networking."},
        "ITCC 302": {"name": "Cloud Infrastructure Administration", "credits": 3, "level": "Junior", "prerequisites": ["IT 308"], "description": "Digital transformation, virtual data centers, cloud deployment models, orchestration."},
        "ITCC 403": {"name": "Security Testing for Cloud Applications", "credits": 3, "level": "Senior", "prerequisites": ["IT 310"], "description": "Security testing foundations, attack models, static analysis, test case generation."},
        "ITCC 404": {"name": "Windows Enterprise Administration", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Active Directory, network infrastructure, PKI, virtualization, Windows updates."},
        "ITCC 405": {"name": "Virtualization and Cloud Security", "credits": 3, "level": "Senior", "prerequisites": ["IT 308"], "description": "Virtualization mechanisms, hypervisors, cloud service models, security standards."},
        "ITCC 406": {"name": "Migrating Data and Applications to the Cloud", "credits": 3, "level": "Senior", "prerequisites": ["IT 308"], "description": "Cloud migration, workload selection, AWS/Microsoft/Google tools, DevOps."},
        "ITCC 407": {"name": "Cloud Services Management", "credits": 3, "level": "Senior", "prerequisites": ["IT 308"], "description": "Cloud planning, governance, risk management, multi-cloud strategy, CI/CD."},
        "ITCC 408": {"name": "Application Development and Scripting in the Cloud", "credits": 3, "level": "Senior", "prerequisites": ["IT 308"], "description": "Contact center scripts, inbound/outbound interactions, scripting best practices."},
        "ITCC 410": {"name": "Software Development Operations in Cloud Environments", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 203", "IT 308"], "description": "Software development lifecycle in cloud environments."},
        "ITCC 411": {"name": "SaaS, IaaS and PaaS", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Cloud service models comparison, SaaS, IaaS, PaaS, business requirements."},
        "ITCC 412": {"name": "Advanced Cloud Security", "credits": 3, "level": "Senior", "prerequisites": ["IT 308", "IT 310"], "description": "Advanced cloud security, secure architecture design, incident response."},
        "ITCC 413": {"name": "IT Security and Policy Planning", "credits": 3, "level": "Senior", "prerequisites": ["IT 310"], "description": "Security technologies, policies, privacy, copyright, compliance."},
        "ITCC 414": {"name": "IS Strategy Management and Acquisition", "credits": 3, "level": "Senior", "prerequisites": [], "description": "IS infrastructure, acquisition, development, implementation of IT systems."},
        # IT Network Security Track - ITNS (14 courses)
        "ITNS 301": {"name": "Network Administration", "credits": 2, "level": "Junior", "prerequisites": ["CSAI 252"], "description": "LAN and WAN design, installation, administration, and maintenance."},
        "ITNS 302": {"name": "IoT Systems and Application Development", "credits": 3, "level": "Junior", "prerequisites": ["CSAI 252"], "description": "IoT services, device gateway, shadows, HTTP/MQTT protocols, analytics."},
        "ITNS 403": {"name": "Storage Area Networks", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 252"], "description": "Storage technologies, FC-SAN, IP-SAN, NAS, RAID, backup, security."},
        "ITNS 404": {"name": "Network Performance Monitoring and Troubleshooting", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 252"], "description": "Network KPIs, monitoring, troubleshooting, throughput, latency, jitter."},
        "ITNS 406": {"name": "Network Resilience and Hardening", "credits": 3, "level": "Senior", "prerequisites": ["CSAI 252"], "description": "Network resilience, fault handling, hardening, vulnerability reduction."},
        "ITNS 407": {"name": "IT Audit and Risk Management", "credits": 3, "level": "Senior", "prerequisites": [], "description": "IT audit principles, governance, risk assessment, frameworks, standards."},
        "ITNS 408": {"name": "Network Security", "credits": 3, "level": "Senior", "prerequisites": ["IT 310"], "description": "Router security, AAA, TACACS+, RADIUS, ACLs, firewalls, IPS, IPsec VPN."},
        "ITNS 410": {"name": "Penetration Testing", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Web application hacking, XSS, SQL injection, authentication attacks, forensics."},
        "ITNS 411": {"name": "Network Programming", "credits": 3, "level": "Senior", "prerequisites": [], "description": "TCP/UDP sockets, IPC, client-server design, SSL, network security."},
        "ITNS 412": {"name": "IT Compliance and Quality Management", "credits": 3, "level": "Senior", "prerequisites": [], "description": "IT compliance, quality policy, planning, assurance, control, improvement."},
        "ITNS 413": {"name": "Emerging Networking Technologies", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Networking hardware installation, configuration, troubleshooting, protocols."},
        "ITNS 414": {"name": "Cyber Forensics", "credits": 3, "level": "Senior", "prerequisites": ["IT 310"], "description": "Digital forensics, cybercrime, evidence collection, preservation, analysis."},
        "ITNS 415": {"name": "Wireless Security", "credits": 3, "level": "Senior", "prerequisites": ["IT 310"], "description": "Wireless network security, cryptography, vulnerabilities, countermeasures."}
    },
    
    # ENVIRONMENTAL ENGINEERING (ENV) - Official ZC Course Catalog (85 courses)
    "ENV": {
        # Freshman/Sophomore Level (13 courses)
        "ENV 104": {"name": "Chemistry for Environmental Engineers", "credits": 3, "level": "Freshman", "prerequisites": ["CHEM 103"], "description": "Environmental organic and inorganic compounds, stability, reactions, kinetics, equilibria."},
        "ENV 120": {"name": "Microbiology and Environmental Health", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Environmental microbiology, biofilms, biodegradation, bioremediation, fermentation."},
        "ENV 203": {"name": "Environmental Chemistry", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 201"], "description": "Analytical chemistry for environment, water and wastewater analysis, BOD, COD."},
        "ENV 204": {"name": "Environmental Engineering Chemistry", "credits": 3, "level": "Sophomore", "prerequisites": ["ENV 104"], "description": "Pollutant classification, air, water, soil pollution control, instrumental techniques."},
        "ENV 207": {"name": "Material and Energy Balances", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 205"], "description": "Conservation of mass and energy, unit operations, waste minimization."},
        "ENV 213": {"name": "Environmental Chemistry Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Water analysis for DO, pH, conductivity, turbidity, heavy metals, COD, BOD."},
        "ENV 219": {"name": "Climate Dynamics", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Physical climatology, global energy budget, atmosphere and ocean circulations."},
        "ENV 220": {"name": "Environmental Microbiology", "credits": 3, "level": "Sophomore", "prerequisites": ["BIOL 101"], "description": "Prokaryotic microorganisms, metabolism, community dynamics, water and soil microbiology."},
        "ENV 221": {"name": "Environmental Microbiology Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Laboratory safety, microscopy, aseptic techniques, staining, bacterial growth."},
        "ENV 224": {"name": "Ecology for Environmental Engineers", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Ecological processes at organism, population, community, and ecosystem levels."},
        "ENV 230": {"name": "Phase Equilibria for Engineers", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 105"], "description": "Thermodynamics, vapor-liquid equilibrium, equations of state, activity coefficients."},
        "ENV 250": {"name": "Hydraulic Engineering", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 207"], "description": "Pressurized flow, pumping systems, free-surface flow, culvert design."},
        "ENV 257": {"name": "Reactions Engineering", "credits": 3, "level": "Sophomore", "prerequisites": ["ENV 207"], "description": "Stoichiometry, kinetics, isothermal reactors, batch, CSTR, PFR, PBR design."},
        # Junior Level (22 courses)
        "ENV 301": {"name": "Environmental Laws, Policies, and Economics", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Environmental legislation, Environmental Protection Act, sustainable development."},
        "ENV 302": {"name": "Environmental Laws and Policies", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Egyptian environmental laws, international conventions, environmental management."},
        "ENV 303": {"name": "Environmental Chemistry", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 201"], "description": "Water and wastewater analysis, sampling, pH, hardness, BOD, COD, nitrogen."},
        "ENV 306": {"name": "Engineering Hydrology", "credits": 3, "level": "Junior", "prerequisites": ["ENV 250", "MATH 301"], "description": "Hydrologic cycle, precipitation, evaporation, runoff, groundwater flow."},
        "ENV 319": {"name": "Environmental Climatology", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 102", "PHYS 101"], "description": "Physical climatology, climate variations, atmospheric composition, anthropogenic change."},
        "ENV 320": {"name": "Water Treatment Engineering", "credits": 3, "level": "Junior", "prerequisites": ["ENV 204", "ENV 250"], "description": "Surface and groundwater treatment, coagulation, flocculation, filtration, disinfection."},
        "ENV 322": {"name": "Wastewater Treatment Engineering", "credits": 3, "level": "Junior", "prerequisites": ["ENV 120", "ENV 204"], "description": "Municipal and industrial wastewater characterization, treatment processes."},
        "ENV 323": {"name": "Municipal Solid Waste Management", "credits": 3, "level": "Junior", "prerequisites": ["ENV 207"], "description": "Waste characteristics, collection, transfer, recycling, composting, landfilling."},
        "ENV 324": {"name": "Ecology", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 101", "CHEM 102"], "description": "Ecosystems behavior, desert, river, oceanic ecosystems, sustainability."},
        "ENV 325": {"name": "Mass Transfer Operations", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 346"], "description": "Mass transfer theory, gas-liquid contacts, absorption, stripping, distillation."},
        "ENV 327": {"name": "Hazardous Waste Management", "credits": 2, "level": "Junior", "prerequisites": ["ENV 323"], "description": "Hazardous waste treatment, disposal, risk assessment, pollution prevention."},
        "ENV 328": {"name": "Sampling and Monitoring of Environmental Pollutants", "credits": 2, "level": "Junior", "prerequisites": ["ENV 204"], "description": "Pollutant sampling, advanced instrumentation, air and water analysis."},
        "ENV 330": {"name": "Phase Equilibria for Engineers", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 205"], "description": "Thermodynamics, vapor-liquid equilibrium, equations of state, activity models."},
        "ENV 346": {"name": "Heat Transfer", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202", "ENGR 205"], "description": "Conduction, convection, radiation, energy storage systems."},
        "ENV 348": {"name": "Aquatic Environments", "credits": 3, "level": "Junior", "prerequisites": ["CHEM 102", "BIOL 101"], "description": "Freshwater and marine systems, conservation, marine protected areas of Egypt."},
        "ENV 350": {"name": "Hydraulic Engineering", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 207"], "description": "Water and sewer systems, open channel flow, pumps and lift stations."},
        "ENV 356": {"name": "Soil & Water Chemistry", "credits": 3, "level": "Junior", "prerequisites": ["BMS 201", "CHEM 201"], "description": "Soil-water interactions, sorption, complex formation, redox processes."},
        "ENV 357": {"name": "Reactions Engineering", "credits": 3, "level": "Junior", "prerequisites": ["ENV 207"], "description": "Homogeneous reactors, CSTRs in series, temperature effects, heterogeneous catalysis."},
        "ENV 359": {"name": "Bioprocess Engineering", "credits": 3, "level": "Junior", "prerequisites": ["ENV 220", "ENV 207"], "description": "Enzyme kinetics, bioreaction kinetics, bioreactors, biomass energy."},
        "ENV 367": {"name": "Environmental Impact Assessment", "credits": 3, "level": "Junior", "prerequisites": ["ENV 302"], "description": "EIA principles, case studies, computer applications, EIA report writing."},
        "ENV 380": {"name": "Urban Water Systems Design", "credits": 3, "level": "Junior", "prerequisites": ["ENV 306", "ENV 320"], "description": "Water distribution, wastewater collection, stormwater drainage design."},
        # Senior Level (29 courses)
        "ENV 406": {"name": "Surface & Groundwater Water Hydrology", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 207"], "description": "Physico-chemical and biological processes, flow dynamics, site characterization."},
        "ENV 411": {"name": "Process Synthesis and Simulation", "credits": 3, "level": "Senior", "prerequisites": ["ENV 230", "ENV 325"], "description": "Process design, synthesis, simulation, cost estimation, profitability analysis."},
        "ENV 412": {"name": "Sustainability for Engineers", "credits": 2, "level": "Senior", "prerequisites": ["ENV 302", "SCH 262"], "description": "Economic, environmental, social sustainability, life cycle assessment."},
        "ENV 415": {"name": "Water and Wastewater Treatment Lab", "credits": 1, "level": "Senior", "prerequisites": ["ENV 420", "ENV 422"], "description": "Process technology, mass balance, reactor models, kinetics."},
        "ENV 416": {"name": "Environmental Chemical Unit Operations Lab", "credits": 1, "level": "Senior", "prerequisites": ["ENV 257", "ENV 325"], "description": "Mass transfer, separation, chemical reaction engineering experiments."},
        "ENV 419": {"name": "Introduction to Integrated Water Resources Management", "credits": 3, "level": "Senior", "prerequisites": ["ENV 306"], "description": "IWRM concept, irrigation management, water economics, policy, legislation."},
        "ENV 420": {"name": "Water Treatment Engineering", "credits": 3, "level": "Senior", "prerequisites": ["ENV 303", "ENV 350"], "description": "Surface and ground water treatment, coagulation, filtration, disinfection."},
        "ENV 422": {"name": "Wastewater Treatment Engineering", "credits": 3, "level": "Senior", "prerequisites": ["ENV 220", "ENV 303"], "description": "Wastewater characterization, physical, chemical, biological processes."},
        "ENV 423": {"name": "Municipal Solid Waste Management", "credits": 3, "level": "Senior", "prerequisites": ["ENV 207"], "description": "Waste generation, collection, transport, disposal, sanitary landfill."},
        "ENV 425": {"name": "Mass Transfer Operations", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 346"], "description": "Absorption, stripping, flash, distillation, extraction, membrane separation."},
        "ENV 427": {"name": "Hazardous Waste Management", "credits": 2, "level": "Senior", "prerequisites": ["ENV 207"], "description": "Hazardous waste classification, treatment, disposal, medical waste management."},
        "ENV 430": {"name": "Urban Development and Environmental Planning", "credits": 3, "level": "Senior", "prerequisites": ["ENV 323"], "description": "Urban planning, environmental sustainability, green buildings, smart infrastructure."},
        "ENV 434": {"name": "Safety and Risk Analysis", "credits": 3, "level": "Senior", "prerequisites": ["MATH 301", "ENGR 207"], "description": "Process safety, toxicology, industrial hygiene, hazard identification."},
        "ENV 440": {"name": "Advanced Separation Processes", "credits": 3, "level": "Senior", "prerequisites": ["ENV 325"], "description": "Adsorption, membrane, ionic separation, multicomponent effects."},
        "ENV 446": {"name": "Water Desalination", "credits": 3, "level": "Senior", "prerequisites": ["ENV 320", "ENV 440"], "description": "Seawater desalination, MSF, MED, RO, NF, fouling, post-treatment."},
        "ENV 451": {"name": "Industrial Bioprocesses", "credits": 3, "level": "Senior", "prerequisites": ["ENV 359"], "description": "Biorefineries, techno-economic analysis, upstream and downstream processing."},
        "ENV 454": {"name": "Life Cycle Assessment", "credits": 3, "level": "Senior", "prerequisites": ["ENV 207"], "description": "LCA framework, environmental footprint, methodology, software tools."},
        "ENV 456": {"name": "Coastal Environmental Management", "credits": 3, "level": "Senior", "prerequisites": ["ENV 219"], "description": "Waves, currents, sediment transport, coastal vulnerability, climate change."},
        "ENV 457": {"name": "Environmental Impact Assessment", "credits": 3, "level": "Senior", "prerequisites": ["ENV 301"], "description": "EIA principles and application, case studies, computer applications."},
        "ENV 458": {"name": "Energy from Biomass and Waste", "credits": 3, "level": "Senior", "prerequisites": ["ENV 359"], "description": "Biogas, bioethanol, biodiesel production from waste and biomass."},
        "ENV 459": {"name": "Environmental Remote Sensing", "credits": 3, "level": "Senior", "prerequisites": ["ENV 219"], "description": "Remote sensing principles, data acquisition, airborne and satellite platforms."},
        "ENV 460": {"name": "Water-Quality Engineering in Natural Systems", "credits": 2, "level": "Senior", "prerequisites": ["ENV 204", "ENV 306"], "description": "Fate and transport in rivers, lakes, groundwater, remediation."},
        "ENV 461": {"name": "Soil and Groundwater Remediation", "credits": 3, "level": "Senior", "prerequisites": ["ENV 204", "ENV 306"], "description": "Contaminated soil and groundwater remediation, site investigation."},
        "ENV 465": {"name": "Environmental Project Management", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Project scope, time, cost, quality, risk, procurement management."},
        "ENV 470": {"name": "Air Quality and Pollution Engineering", "credits": 3, "level": "Senior", "prerequisites": ["ENV 319", "ENV 207"], "description": "Air pollution control, emissions, meteorology, dispersion modeling."},
        "ENV 475": {"name": "Industrial Reaction Engineering", "credits": 3, "level": "Senior", "prerequisites": ["ENV 257"], "description": "Heterogeneous reacting systems, fluid-solid reactors, scale-up."},
        "ENV 480": {"name": "Urban Water Systems Design", "credits": 3, "level": "Senior", "prerequisites": ["ENV 406", "ENV 420"], "description": "Water distribution, wastewater collection, stormwater drainage, software."},
        "ENV 497": {"name": "Selected Topics in Environmental Engineering", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Contemporary topics in environmental engineering."},
        "ENV 498": {"name": "Senior Design Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Problem identification, solution generation, sustainability requirements."},
        "ENV 499": {"name": "Senior Design Project II", "credits": 3, "level": "Senior", "prerequisites": ["ENV 498"], "description": "Detailed design of senior project solution."},
        # Graduate Level (21 courses)
        "ENV 506": {"name": "Water Desalination", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 420", "ENV 425"], "description": "Seawater desalination technologies, thermal and membrane processes."},
        "ENV 510": {"name": "Process Analysis and Simulation", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 330", "ENV 425"], "description": "Process simulation, dynamic analysis, cost evaluation, conceptual design."},
        "ENV 512": {"name": "Green Economy", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Environmental risks, sustainable development, green economy strategies."},
        "ENV 514": {"name": "Soil & Environmental Physics", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 406"], "description": "Soil hydro-physical properties, mass and energy exchange, measurement methods."},
        "ENV 518": {"name": "Introd to Environmental Systems Analysis", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 207", "MATH 202"], "description": "Environmental systems, economics, mass and energy balances, risk analysis."},
        "ENV 519": {"name": "Introduction to Integrated Water Resources Management", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 406"], "description": "IWRM, irrigation management, water economics, transboundary water."},
        "ENV 520": {"name": "Separation Processes", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 425"], "description": "Diffusional separation, distillation, absorption, adsorption, membrane."},
        "ENV 522": {"name": "Industrial Bio-Processes", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 359"], "description": "Enzymes and microbes for industrial products, bioreactors, biofuels."},
        "ENV 523": {"name": "Transport and Fate of Chemicals in the Environment", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 406", "ENV 470"], "description": "Intermedia transport, hydrology, air pollution modeling, exposure pathways."},
        "ENV 524": {"name": "Life Cycle Assessment", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "LCA methodology, software tools, databases, critical review."},
        "ENV 527": {"name": "Appropriate Technology", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "High tech vs traditional solutions, technological innovation implementation."},
        "ENV 528": {"name": "Pollution Sampling, Analysis and Monitoring", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 203"], "description": "Pollutant sampling, advanced analytical techniques, emissions measurement."},
        "ENV 530": {"name": "Urban Development & Environmental Planning", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Urban planning, environmental sustainability, infrastructure planning."},
        "ENV 538": {"name": "Soil and Groundwater Contamination Survey and Remediation", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 406"], "description": "Soil and groundwater remediation theory and application."},
        "ENV 555": {"name": "Coastal Environmental Management", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 319", "ENV 350"], "description": "Water waves, surf zone hydrodynamics, tides, sediment transport."},
        "ENV 556": {"name": "Soil & Water Chemistry", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 220", "CHEM 201"], "description": "Soil-water interactions, sorption, complex formation, redox processes."},
        "ENV 558": {"name": "Energy from Biomass and Waste", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 359"], "description": "Waste-to-energy, biogas, bioethanol, biodiesel, thermal conversion."},
        "ENV 559": {"name": "Remote Sensing for the Environment", "credits": 3, "level": "Graduate", "prerequisites": ["PHYS 102", "MATH 202"], "description": "Remote sensing principles, data analysis, terrain investigations."},
        "ENV 597": {"name": "Selected topics in Environmental Eng.", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics not covered elsewhere in curriculum."},
        "ENV 598": {"name": "Senior Design Project I", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "Environmental engineering design project initiation."},
        "ENV 599": {"name": "Senior Design Project II", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 598"], "description": "Final design of major environmental engineering project."}
    },
    
    # NANOTECHNOLOGY AND NANOELECTRONICS ENGINEERING (NANENG) - Official ZC Course Catalog (89 courses)
    "NANENG": {
        # Freshman Level (2 courses)
        "NANENG 112": {"name": "C/C++ Programming Lab", "credits": 1, "level": "Freshman", "prerequisites": ["CSCI 101"], "description": "Object-oriented programming, algorithms, flowcharts, C/C++ programming fundamentals."},
        "NANENG 171": {"name": "Materials Properties for Nanoelectronics", "credits": 2, "level": "Freshman", "prerequisites": ["CHEM 102"], "description": "Introduction to nanotechnology, nanoelectronics, nanofabrication, material properties at nanoscale."},
        # Sophomore Level (10 courses)
        "NANENG 201": {"name": "C/C++ Programming Language", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "C/C++ programming, object-oriented design, algorithms, problem solving."},
        "NANENG 202": {"name": "Digital Logic", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Numbering systems, logic gates, Boolean algebra, combinational and sequential circuits, Verilog."},
        "NANENG 203": {"name": "Electric Circuits", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 102"], "description": "Circuit analysis, Kirchhoff's laws, Thevenin/Norton theorems, AC/DC, phasors, Laplace transform."},
        "NANENG 204": {"name": "Digital Logic Design", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Digital circuit design and implementation, CAD tools, simulation and testing."},
        "NANENG 205": {"name": "Physics of Semiconductors", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 224", "MATH 202"], "description": "Band theory, carrier statistics, drift-diffusion, mobility, metal-semiconductor contacts."},
        "NANENG 211": {"name": "Electrical Power Circuits and Machines", "credits": 2, "level": "Sophomore", "prerequisites": ["NANENG 203", "PHYS 106"], "description": "DC/AC machines, transformers, three-phase circuits, protection, electric vehicles, BLDC motors."},
        "NANENG 212": {"name": "Applied Digital Control", "credits": 3, "level": "Sophomore", "prerequisites": ["NANENG 112", "MATH 202"], "description": "Continuous/discrete control systems, PID, DC motor control, z-plane analysis, Arduino."},
        "NANENG 218": {"name": "Thermofluids for Nanoelectronics", "credits": 2, "level": "Sophomore", "prerequisites": ["PHYS 203"], "description": "Fluid mechanics and heat transfer for nanoelectronics, heat sinks, CVD processes."},
        "NANENG 222": {"name": "Electronic Circuit Design", "credits": 3, "level": "Sophomore", "prerequisites": ["NANENG 203"], "description": "Diodes, BJTs, FETs operation, DC/AC analysis, amplifiers, current mirrors, inverters."},
        "NANENG 231": {"name": "Electromagnetics", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 202", "PHYS 106"], "description": "Maxwell's equations, electrostatics, magnetostatics, electromagnetic energy and waves."},
        "NANENG 245": {"name": "Introduction to Discrete Mathematics", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Proofs, induction, recursion, number theory, RSA cryptography, graph theory, probability."},
        # Junior Level (14 courses)
        "NANENG 301": {"name": "Micro/Nano Fabrication Techniques", "credits": 3, "level": "Junior", "prerequisites": ["NANENG 171"], "description": "CMOS fabrication, lithography, thin film deposition, etching, cleanroom processes, TCAD."},
        "NANENG 303": {"name": "Computer Architecture and Design", "credits": 2, "level": "Junior", "prerequisites": ["NANENG 202", "NANENG 112"], "description": "RISC processor design, instruction sets, assembly, datapath, pipelines, memory hierarchy."},
        "NANENG 305": {"name": "Physics Of Semiconductors", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 202", "MATH 202"], "description": "Quantum mechanics, band theory, carrier statistics and transport mechanisms."},
        "NANENG 307": {"name": "Physics of Electronic Materials", "credits": 3, "level": "Junior", "prerequisites": ["NANENG 305"], "description": "Electronic material structure, bonding, thermal, electrical, dielectric, magnetic properties."},
        "NANENG 308": {"name": "Solid State Devices", "credits": 3, "level": "Junior", "prerequisites": ["NANENG 205"], "description": "PN junctions, heterojunctions, FETs, MOSFETs, HEMTs, short channel and nanoscale effects."},
        "NANENG 312": {"name": "C/C++ Programming Lab", "credits": 1, "level": "Junior", "prerequisites": ["CSCI 101"], "description": "Object-oriented programming laboratory exercises in C/C++."},
        "NANENG 313": {"name": "Educational Cleanroom Lab", "credits": 1, "level": "Junior", "prerequisites": ["NANENG 171"], "description": "Hands-on cleanroom fabrication: oxidation, diffusion, etching, sputtering, lithography."},
        "NANENG 315": {"name": "MEMS Design and Fabrication", "credits": 3, "level": "Junior", "prerequisites": ["NANENG 301"], "description": "MEMS/NEMS fabrication, transduction mechanisms, sensors for various physical quantities."},
        "NANENG 322": {"name": "Electronic Circuit Design", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 201"], "description": "Diodes, BJTs, FETs, amplifiers, current mirrors, digital switches."},
        "NANENG 323": {"name": "Analog Integrated Circuit Design", "credits": 3, "level": "Junior", "prerequisites": ["NANENG 222", "NANENG 212"], "description": "CMOS analog IC design, amplifiers, biasing, current mirrors, differential pairs, op-amps."},
        "NANENG 325": {"name": "ASIC and FPGA Design", "credits": 3, "level": "Junior", "prerequisites": ["NANENG 202"], "description": "HDL coding, FPGA architectures, ASIC design flow, synthesis, tape-out projects."},
        "NANENG 331": {"name": "Electromagnetics", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 201", "MATH 202"], "description": "Maxwell's equations, boundary conditions, electro/magneto-quasistatics, EM waves."},
        "NANENG 335": {"name": "Introduction to Photonics", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 201"], "description": "Light-material interaction, Fresnel equations, waveguides, optical fibers, polarization."},
        "NANENG 361": {"name": "Communications Theory and Systems", "credits": 3, "level": "Junior", "prerequisites": ["MATH 301"], "description": "Shannon information theory, coding, error correction, channel noise, communication protocols."},
        # Senior Level (36 courses)
        "NANENG 401": {"name": "MEMS Design and Fabrication", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 301"], "description": "Advanced MEMS/NEMS, transduction mechanisms, infrared/radiation/motion sensors."},
        "NANENG 402": {"name": "Modern Characterization Techniques", "credits": 2, "level": "Senior", "prerequisites": ["CHEM 102", "PHYS 202", "MATSCI 201"], "description": "Optical microscopy, spectroscopy, SEM, TEM, AFM, ellipsometry, X-ray, thermal analysis."},
        "NANENG 404": {"name": "Modern Characterization Techniques.", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Optical microscopy, spectroscopy, SEM, TEM, STEM, AFM, ellipsometry, characterizations."},
        "NANENG 406": {"name": "Modeling of Nanodevices", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 308", "MATH 306"], "description": "SOI FETs, FinFETs, nanowires, Tunnel FETs, TCAD simulation, Verilog-A compact models."},
        "NANENG 410": {"name": "Real-Time Embedded System and Microcontroller Design", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 204", "NANENG 312"], "description": "Real-time computing, cyber-physical systems, timeliness, reliability, safety."},
        "NANENG 416": {"name": "VLSI Design Lab", "credits": 2, "level": "Senior", "prerequisites": ["NANENG 323", "NANENG 325"], "description": "Full ASIC tapeout flow, analog/mixed signal/digital design, postlayout simulation."},
        "NANENG 419": {"name": "Introduction to Artificial Intelligence", "credits": 2, "level": "Senior", "prerequisites": ["MATH 301", "NANENG 112"], "description": "AI fundamentals, machine learning, deep learning, neural networks, intelligent agents."},
        "NANENG 421": {"name": "Analog Integrated Circuit Design", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 322"], "description": "CMOS analog IC analysis and design, amplifiers, frequency response."},
        "NANENG 422": {"name": "ASIC and FPGA Design", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 204"], "description": "Digital design flow, VHDL/Verilog, FPGA architectures, ASIC synthesis, tape-out."},
        "NANENG 424": {"name": "Photovoltaics and Photonic Devices", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 205"], "description": "Solar cells, photodiodes, LEDs, laser diodes, optical fibers, characterization."},
        "NANENG 426": {"name": "Quantum Computer Programming", "credits": 3, "level": "Senior", "prerequisites": ["CSCI 101", "MATH 201"], "description": "Quantum computation fundamentals, qubits, quantum algorithms, IBM Qiskit implementation."},
        "NANENG 427": {"name": "Lasers and Optical Coherence", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 203", "PHYS 201"], "description": "Laser systems, resonators, ABCD matrix, atomic energy levels, gain/loss, coherence."},
        "NANENG 430": {"name": "Principles of Microwave and Waveguides", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 331"], "description": "Transmission lines, Smith Chart, waveguide analysis, microstrip, couplers, filters."},
        "NANENG 431": {"name": "Computational Photonics", "credits": 3, "level": "Senior", "prerequisites": ["MATH 306", "NANENG 112"], "description": "Transfer matrix, FDTD, beam propagation, plane wave expansion, finite element methods."},
        "NANENG 433": {"name": "Computer Architecture & Assembly Language", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 204", "NANENG 312"], "description": "Computer design, instruction sets, assembly, datapath, memory hierarchy, parallel processing."},
        "NANENG 435": {"name": "Nanophotonics", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 335"], "description": "Silicon photonic devices, photonic crystals, plasmonics, metamaterials."},
        "NANENG 436": {"name": "Advanced MEMS Design and Fabrication Techniques", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 315"], "description": "Complete MEMS devices, multi-physics modeling, polyMUMPs design rules, mask layouts."},
        "NANENG 437": {"name": "Organic Electronics and Photovoltaics", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 205"], "description": "Organic electronic and optoelectronic devices, photophysics, charge transport, OLEDs, OPV."},
        "NANENG 438": {"name": "CMOS Nanofabrication", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 301", "NANENG 313"], "description": "Metal/High-k integration, ALD, advanced lithography, OPC, RET, copper interconnects."},
        "NANENG 439": {"name": "Advanced Digital ASIC Design", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 325"], "description": "HDL, professional Verilog, FPGA/ASIC design flow, synthesis, power grid, clock design."},
        "NANENG 440": {"name": "Nanofabrication Vacuum and Equipment Tech", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 301"], "description": "Top-down, bottom-up nanofabrication, equipment design, vacuum systems, process control."},
        "NANENG 441": {"name": "Testing, Verification and Reliability", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 325"], "description": "Digital circuit testing, DFT, scan, BIST, fault simulation, reliability testing."},
        "NANENG 442": {"name": "Devices and VLSI for Smart Power ICs", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 308", "NANENG 222"], "description": "Smart power ICs, LDMOS, IGBTs, power converters, electric vehicle applications, TCAD."},
        "NANENG 445": {"name": "RF/Mixed Signal ICs", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 323"], "description": "RF IC design, LNAs, mixers, oscillators, PLLs, frequency synthesizers, power amplifiers."},
        "NANENG 446": {"name": "Optical MEMS", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 315"], "description": "Optical MEMS fabrication, optical systems on-chip, optofluidics, lab-on-chip."},
        "NANENG 447": {"name": "Physical Design and EDA Algorithms", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 112", "NANENG 325"], "description": "VLSI physical design, partitioning, placement, floor planning, routing, SPICE simulation."},
        "NANENG 448": {"name": "Mixed Signal and Low Power VLSI", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 323"], "description": "ADCs/DACs, switched-capacitor circuits, VGAs, filters, PLLs, neural recording amplifiers."},
        "NANENG 449": {"name": "Microfluidics and Biochips", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 301", "NANENG 218"], "description": "Microfluidic platforms, particle manipulation, microfabrication, biochips, flow cytometry."},
        "NANENG 455": {"name": "Adv. Nanodevices Fabrication Techniques", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 301", "NANENG 313"], "description": "FinFETs, GAA-FETs, solar cells, quantum dots, e-beam lithography, IC packaging, AI in fab."},
        "NANENG 461": {"name": "Communications Theory and Systems", "credits": 3, "level": "Senior", "prerequisites": ["MATH 301"], "description": "Shannon information theory, coding, error correction, ICT standards and trends."},
        "NANENG 462": {"name": "Optical Communication Systems", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 461"], "description": "Optical fibers, losses, dispersion, transmitters, receivers, digital communication, networks."},
        "NANENG 470": {"name": "Introduction to silicon integrated photonics", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 335", "NANENG 231"], "description": "Silicon photonic ICs, waveguides, splitters, interferometers, modulators, biosensing."},
        "NANENG 471": {"name": "Solar photovoltaics technology", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 205"], "description": "PV principles, crystalline silicon, thin-film, organic, perovskites, quantum dot solar cells."},
        "NANENG 497": {"name": "Selected topics in Nanotechnology Eng.", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Quantum devices, spin-devices, junctionless, tunneling devices, printed electronics."},
        "NANENG 498": {"name": "NANENG Senior Design Project 1", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Senior design project initiation."},
        "NANENG 499": {"name": "NANENG Senior Design Project 2", "credits": 3, "level": "Senior", "prerequisites": ["NANENG 498"], "description": "Senior design project completion."},
        # Graduate Level (27 courses)
        "NANENG 501": {"name": "Advanced Digital ASIC Design", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 422"], "description": "HDL, professional Verilog, FPGA/ASIC design flow, synthesis algorithms, power management."},
        "NANENG 503": {"name": "Physical Design and EDA Algorithms", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 312", "NANENG 422"], "description": "VLSI physical design, partitioning, placement, routing, SPICE simulation, compact models."},
        "NANENG 511": {"name": "Nano Photonics", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 335"], "description": "Light-nanoscale material interaction, photonic crystals, plasmonics, metamaterials."},
        "NANENG 512": {"name": "Applied Digital Control and Drives", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 312", "MATH 202"], "description": "Linear control systems, mathematical analysis, stability, root locus, digital control."},
        "NANENG 513": {"name": "Adv. Nanodevices Fabrication Techniques", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 301"], "description": "Metal/High-k, ALD, advanced lithography, Cu interconnects, high voltage devices, TFTs."},
        "NANENG 514": {"name": "Organic Electronics and Photovoltaics", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 301", "NANENG 305"], "description": "Organic electronic devices, photophysics, charge transport, OLEDs, organic solar cells."},
        "NANENG 515": {"name": "Adv. MEMS Design & Fabrication Techniques", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 401"], "description": "Advanced MEMS applications, NEMS, design/fabrication/characterization challenges."},
        "NANENG 520": {"name": "Advanced Devices", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 308"], "description": "SOI FETs, FinFETs, multigate systems, junctionless transistors, high-voltage modeling."},
        "NANENG 522": {"name": "Advanced RF/Mixed Signal ICs", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 421"], "description": "RF IC design, LNAs, mixers, oscillators, PLLs, power amplifiers, layout considerations."},
        "NANENG 523": {"name": "Nanofabrication Vacuum & Equipment Tech", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 301"], "description": "Top-down, bottom-up nanofabrication, equipment design, vacuum systems, automation."},
        "NANENG 524": {"name": "Testing, Verification and Reliability", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 422"], "description": "Digital circuit testing, DFT, scan, BIST, fault simulation, reliability analysis."},
        "NANENG 525": {"name": "Optical MEMS", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 430"], "description": "Optical MEMS fabrication, optical systems on-chip, optofluidics, lab-on-chip, optical forces."},
        "NANENG 527": {"name": "Devices and VLSI for Smart Power ICs", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 308", "NANENG 322"], "description": "Smart power ICs, power devices, LDMOS, IGBTs, inverters, DC-DC converters, EV applications."},
        "NANENG 530": {"name": "Computational Photonics", "credits": 3, "level": "Graduate", "prerequisites": ["MATH 306", "NANENG 312"], "description": "Transfer matrix, FDTD, beam propagation, FEM, computational electromagnetics."},
        "NANENG 533": {"name": "Mixed Signal and Low Power VLSI", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 421"], "description": "ADCs/DACs, switched-capacitor circuits, filters, PLLs, biomedical analog circuits."},
        "NANENG 535": {"name": "Integrated Nanophotonics", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 511"], "description": "Semiconductor optoelectronics, laser diodes, photonic components, modulators, detectors."},
        "NANENG 540": {"name": "Microfluidics and Biochips", "credits": 3, "level": "Graduate", "prerequisites": ["BIOL 101", "NANENG 301"], "description": "Microfluidic platforms, particle manipulation, microfabrication, biochips, flow cytometry."},
        "NANENG 597": {"name": "Selected topics in Nanotechnology Eng.", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Quantum devices, spin-devices, junctionless devices, printed electronics, biosensors."},
        "NANENG 598": {"name": "Senior Design Project I", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "Graduate design project planning and experimentation."},
        "NANENG 599": {"name": "Senior Design Project II", "credits": 3, "level": "Graduate", "prerequisites": ["NANENG 598"], "description": "Graduate design project completion and presentation."},
        "NANENG 623": {"name": "Modeling of Nanofabrication Processes and Equipment", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Cleanroom contamination control, vacuum technology, sputtering, RTP, CMP, PDKs."},
        "NANENG 625": {"name": "Advanced Real-Time Embedded Systems", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "PIC, ARM Cortex-M4, FreeRTOS, debugging, porting, TinyML, embedded Linux."},
        "NANENG 705": {"name": "Ph.D. Directed Research", "credits": 9, "level": "Graduate", "prerequisites": [], "description": "Ph.D. directed research in nanotechnology and nanoelectronics."},
        "NANENG 722": {"name": "Selected Topics on Advanced Photonic Devices", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Light-matter interaction, LEDs, PV cells, photodetectors, lasers, organic semiconductors."},
        "NANENG 723": {"name": "Selected Topics in Modeling of Nanofabrication Processes and Equipment", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "AI/ML for process control, digital twin, intelligent cleanroom management."},
        "NANENG 725": {"name": "Selected Topics in Real-Time Embedded Systems", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "PIC, ARM Cortex-M4, FreeRTOS, debugging, porting, TinyML, embedded security."}
    },
    
    # RENEWABLE ENERGY ENGINEERING (REE) - Official ZC Course Catalog
    "REE": {
        # Freshman Level
        "REE 101": {"name": "Renewable Energy Systems", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Overview of renewable energy technologies including wind turbines, photovoltaic systems, and solar hot water systems."},
        "REE 122": {"name": "Introduction to Manufacturing Processes", "credits": 3, "level": "Freshman", "prerequisites": ["ENGR 102"], "description": "Metal casting, forming, joining, machining, and processing polymers and composites."},
        # Sophomore Level
        "REE 201": {"name": "Renewable Energy Systems", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Operation and performance of renewable energy technologies."},
        "REE 202": {"name": "Mechanics of Materials", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 101", "PHYS 101"], "description": "Stresses in materials due to axial, twisting, shearing, and bending loading."},
        "REE 203": {"name": "Advanced Circuits Design", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGR 201"], "description": "AC circuits, phasor analysis, three-phase systems, frequency domain analysis, and transmission lines."},
        "REE 208": {"name": "Engineering Dynamics", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 101", "PHYS 105"], "description": "Kinematics, kinetics, Newton's laws, momentum, work and energy conservation."},
        "REE 218": {"name": "Mechanical Vibrations", "credits": 3, "level": "Sophomore", "prerequisites": ["REE 208"], "description": "Vibration of single and multiple degree of freedom systems, damping and control."},
        "REE 222": {"name": "Introduction to Manufacturing Processes", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Metal casting, forming, joining, machining, metrology, and powder metallurgy."},
        # Junior Level
        "REE 302": {"name": "Machine Design", "credits": 3, "level": "Junior", "prerequisites": ["REE 202", "ENGR 121"], "description": "Design considerations, material selection, stress analysis, fatigue failure, and machine elements."},
        "REE 306": {"name": "Advanced Thermodynamics", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 105"], "description": "Exergy analysis, thermodynamic cycles, psychrometry, and chemical reactions."},
        "REE 307": {"name": "Fluid Mechanics II", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 207"], "description": "Viscous flow, pipe networks, Navier-Stokes equation, and boundary layers."},
        "REE 308": {"name": "Mechanical Vibrations", "credits": 3, "level": "Junior", "prerequisites": ["REE 208"], "description": "Vibration of single and multiple degree of freedom systems and continuous structures."},
        "REE 309": {"name": "Renewable Energy Systems", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Operation and performance of wind turbines, photovoltaic systems, and solar hot water systems."},
        "REE 310": {"name": "Control Systems", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202"], "description": "Dynamic systems modeling, feedback control, stability analysis, and control design."},
        "REE 311": {"name": "Electric Machines", "credits": 3, "level": "Junior", "prerequisites": ["REE 203"], "description": "Electrical machines theory, DC and AC machines, and renewable energy applications."},
        "REE 312": {"name": "Machine Design II", "credits": 3, "level": "Junior", "prerequisites": ["REE 302"], "description": "Geometric dimensioning, joints, fasteners, gears, clutches, brakes, and couplings."},
        "REE 315": {"name": "Power Plant Technology", "credits": 3, "level": "Junior", "prerequisites": ["REE 306"], "description": "Fossil, nuclear, hydro, solar, and wind generation systems."},
        "REE 317": {"name": "Advanced Fluid Mechanics", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 207"], "description": "Differential analysis, dimensional analysis, flow over bodies, and turbomachines."},
        "REE 319": {"name": "Power Systems", "credits": 3, "level": "Junior", "prerequisites": ["REE 311"], "description": "Power system modeling, power flow analysis, and fault analysis."},
        "REE 320": {"name": "Advanced Control Systems", "credits": 3, "level": "Junior", "prerequisites": ["REE 310"], "description": "State-space methods, feedback control design, and digital control systems."},
        "REE 321": {"name": "Power Electronics", "credits": 3, "level": "Junior", "prerequisites": ["REE 203"], "description": "Power semiconductor devices, converters, inverters, and renewable energy applications."},
        "REE 322": {"name": "Advanced Circuits Design", "credits": 3, "level": "Junior", "prerequisites": ["ENGR 201", "MATH 202"], "description": "Active and passive analog filter design using operational amplifiers."},
        # Senior Level
        "REE 403": {"name": "Renewable Energy Law and Economics", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Legal regulation of energy markets and economic evaluation of energy projects."},
        "REE 405": {"name": "Electric Machines", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 201", "MATH 202"], "description": "Power converters, electrical machines theory, and renewable energy applications."},
        "REE 406": {"name": "Advanced Thermodynamics", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 205"], "description": "Exergy analysis, thermodynamic cycles, psychrometry, and combustion."},
        "REE 407": {"name": "Aerodynamics", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 207"], "description": "Subsonic and supersonic flows, boundary layers, and airfoil theory."},
        "REE 409": {"name": "Advanced Control Systems", "credits": 3, "level": "Senior", "prerequisites": ["REE 310"], "description": "State-space design, robust control, and nonlinearity handling."},
        "REE 411": {"name": "Power Electronics", "credits": 3, "level": "Senior", "prerequisites": ["REE 322"], "description": "Power semiconductor devices, converters, and renewable energy applications."},
        "REE 415": {"name": "Power Plant Technology", "credits": 3, "level": "Senior", "prerequisites": ["REE 406"], "description": "Fossil, nuclear, hydro, solar, and wind power generation systems."},
        "REE 418": {"name": "Aerodynamics of Wind Turbines", "credits": 3, "level": "Senior", "prerequisites": ["REE 317"], "description": "Wind turbine rotor design, blade element momentum theory, and structural analysis."},
        "REE 419": {"name": "Power Systems", "credits": 3, "level": "Senior", "prerequisites": ["REE 311"], "description": "Distribution systems, power flow, stability, and illumination engineering."},
        "REE 420": {"name": "Power Electronics", "credits": 3, "level": "Senior", "prerequisites": ["REE 322"], "description": "Power converters, inverters, and renewable energy field applications."},
        "REE 421": {"name": "System Engineering", "credits": 2, "level": "Senior", "prerequisites": [], "description": "System engineering approaches, project planning, and management processes."},
        "REE 422": {"name": "Optics and Photonics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 102", "MATH 202"], "description": "Optical principles, photonic devices, and light interaction with materials."},
        "REE 425": {"name": "Thermal Solar Energy", "credits": 3, "level": "Senior", "prerequisites": ["REE 315"], "description": "Solar concentration technologies for heating, steam production, and power generation."},
        "REE 428": {"name": "Energy Storage", "credits": 3, "level": "Senior", "prerequisites": ["REE 315"], "description": "Fuel cells, batteries, lithium-ion technology, and energy storage systems."},
        "REE 429": {"name": "Smart Grid", "credits": 3, "level": "Senior", "prerequisites": ["REE 319"], "description": "Renewable integration, grid codes, distributed generation, and microgrids."},
        "REE 430": {"name": "Rotor Aerodynamics", "credits": 3, "level": "Senior", "prerequisites": ["REE 407"], "description": "Wind turbine rotor design and analysis using blade element momentum theory."},
        "REE 432": {"name": "Photovoltaic Systems", "credits": 3, "level": "Senior", "prerequisites": ["REE 321"], "description": "Photoelectric conversion, PV technologies, inverters, and grid integration."},
        "REE 434": {"name": "Wind Energy Systems", "credits": 3, "level": "Senior", "prerequisites": ["REE 319"], "description": "Wind meteorology, wind plant design, and grid integration."},
        "REE 466": {"name": "Machine Design", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 221"], "description": "Design considerations, material selection, stress analysis, and shaft design."},
        "REE 470": {"name": "Computer-Aided Design and Engineering", "credits": 3, "level": "Senior", "prerequisites": ["REE 312"], "description": "CAD for mechanical engineering, FEA, and CFD using SolidWorks, ANSYS, COMSOL."},
        "REE 476": {"name": "Heating, Ventilation, and Air Conditioning Systems", "credits": 2, "level": "Senior", "prerequisites": ["REE 306"], "description": "HVAC system types, components, energy efficiency, and design principles."},
        "REE 477": {"name": "Modern Control Techniques", "credits": 2, "level": "Senior", "prerequisites": ["REE 320"], "description": "Nonlinear systems, adaptive control, and model predictive control."},
        "REE 478": {"name": "Industrial Control", "credits": 2, "level": "Senior", "prerequisites": ["REE 320"], "description": "PLCs, DCS, SCADA systems, and industrial communication networks."},
        "REE 479": {"name": "Mechanical System Design", "credits": 2, "level": "Senior", "prerequisites": ["REE 208"], "description": "Kinematics, mechanism design, power transmission, and flywheel energy storage."},
        "REE 480": {"name": "Sustainable Energy Development", "credits": 2, "level": "Senior", "prerequisites": [], "description": "Energy systems assessment, renewable and conventional technologies, and sustainability."},
        "REE 481": {"name": "Carbon Dioxide Sequestration", "credits": 2, "level": "Senior", "prerequisites": ["PEU 311"], "description": "Carbon capture technologies, storage methods, and environmental impacts."},
        "REE 482": {"name": "Renewable Resources Management", "credits": 2, "level": "Senior", "prerequisites": ["REE 429"], "description": "Management of soil, water, plants, and bioenergy sources."},
        "REE 483": {"name": "Geothermal Energy", "credits": 2, "level": "Senior", "prerequisites": ["REE 315"], "description": "Geothermal systems, heat pumps, and ground source heat systems."},
        "REE 484": {"name": "Modeling and Control of Voltage Source Converters", "credits": 2, "level": "Senior", "prerequisites": ["REE 321"], "description": "Renewable power generation dynamics and voltage source converter control."},
        "REE 485": {"name": "Applications of Voltage Source Converters", "credits": 2, "level": "Senior", "prerequisites": ["REE 484"], "description": "FACTS, renewable energy, energy storage, EVs, and HVDC applications."},
        "REE 486": {"name": "Hydroelectric, Tidal and Wave Energy", "credits": 2, "level": "Senior", "prerequisites": ["REE 470"], "description": "Water hydraulics, hydropower generation, and turbine selection."},
        "REE 487": {"name": "Bio Fuels and Bio Mass", "credits": 2, "level": "Senior", "prerequisites": ["REE 315"], "description": "Biofuel technologies, biomass combustion, gasification, and algae biofuel."},
        "REE 488": {"name": "Hydrogen Systems", "credits": 2, "level": "Senior", "prerequisites": ["REE 315", "REE 321"], "description": "Hydrogen production, transport, conversion, and storage."},
        "REE 489": {"name": "Nuclear Energy", "credits": 2, "level": "Senior", "prerequisites": ["REE 315", "REE 470"], "description": "Nuclear reactor design, thermal analysis, and safety."},
        "REE 490": {"name": "Electric Power Generation, Distribution and Utilization", "credits": 2, "level": "Senior", "prerequisites": ["REE 319"], "description": "Distribution systems, cable ampacity, voltage drop, and illumination."},
        "REE 491": {"name": "Renewable Energy Economic Analysis and Feasibility Study", "credits": 2, "level": "Senior", "prerequisites": ["REE 403"], "description": "Cost-benefit analysis, time value of money, and project evaluation."},
        "REE 492": {"name": "Energy Conservation and Efficiency", "credits": 2, "level": "Senior", "prerequisites": ["REE 319"], "description": "Energy analysis, efficiency management, and waste energy recovery."},
        "REE 493": {"name": "Turbine Blade Design", "credits": 2, "level": "Senior", "prerequisites": ["REE 418"], "description": "Turbine blade aerodynamics, structural design, and wind resource modeling."},
        "REE 494": {"name": "Special Topics in Adv Thermal Systems", "credits": 2, "level": "Senior", "prerequisites": ["REE 425"], "description": "Solar thermal energy conversion, radiation measurement, and applications."},
        "REE 495": {"name": "Electric Vehicles", "credits": 2, "level": "Senior", "prerequisites": ["REE 321"], "description": "Power converters in EVs, battery management, motor drives, and chargers."},
        "REE 496": {"name": "Selected Topics in Renewable Energy Engineering", "credits": 0, "level": "Senior", "prerequisites": [], "description": "Selected topics of interest not covered elsewhere in the curriculum."},
        "REE 498": {"name": "Senior Design Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Problem identification, solution generation, and project planning."},
        "REE 499": {"name": "Senior Design Project II", "credits": 3, "level": "Senior", "prerequisites": ["REE 498"], "description": "Detailed technical design and final project report."},
        # Graduate Level
        "REE 501": {"name": "Sustainable Energy Development", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Energy systems, renewable technologies, and sustainability assessment."},
        "REE 503": {"name": "Renewable Energy Law and Economics", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Energy market regulation and economic evaluation of energy projects."},
        "REE 506": {"name": "Carbon Dioxide Sequestration", "credits": 2, "level": "Graduate", "prerequisites": ["PEU 311"], "description": "Carbon capture, storage technologies, and environmental impacts."},
        "REE 515": {"name": "Thermal Solar Energy", "credits": 3, "level": "Graduate", "prerequisites": ["REE 415"], "description": "Solar concentration technologies and cross-cutting themes."},
        "REE 517": {"name": "Renewable Resources Management", "credits": 2, "level": "Graduate", "prerequisites": ["REE 322"], "description": "Management of renewable natural resources and bioenergy."},
        "REE 520": {"name": "Wind Energy", "credits": 2, "level": "Graduate", "prerequisites": ["REE 407"], "description": "Wind meteorology, energy extraction, and wind plant development."},
        "REE 521": {"name": "Smart Grid", "credits": 3, "level": "Graduate", "prerequisites": ["REE 419"], "description": "Renewable integration, grid codes, and smart microgrids."},
        "REE 522": {"name": "Geothermal Energy", "credits": 2, "level": "Graduate", "prerequisites": ["PEU 207"], "description": "Geothermal systems, heat pumps, and ground source configurations."},
        "REE 523": {"name": "Dynamics and Control of Renew Power Gen", "credits": 2, "level": "Graduate", "prerequisites": ["REE 560"], "description": "Wind and solar power dynamics and voltage source converter control."},
        "REE 524": {"name": "Hydroelectric, Tidal and Wave Energy", "credits": 2, "level": "Graduate", "prerequisites": ["ENV 346"], "description": "Hydraulics, hydropower generation, and turbine efficiency."},
        "REE 525": {"name": "Geothermal Energy", "credits": 2, "level": "Graduate", "prerequisites": ["REE 410", "ENGR 207"], "description": "Geothermal layout, design, and ground heat exchanger configurations."},
        "REE 526": {"name": "Bio-Fuels & Bio Mass", "credits": 2, "level": "Graduate", "prerequisites": ["BIOL 102", "PHYS 201"], "description": "Biofuel technologies and sustainability assessment."},
        "REE 528": {"name": "Propane, Natural Gas & Bio Gas", "credits": 2, "level": "Graduate", "prerequisites": ["REE 301"], "description": "Mining, transport, conversion, and storage of natural gas."},
        "REE 530": {"name": "Nuclear Energy", "credits": 2, "level": "Graduate", "prerequisites": ["PHYS 202", "CHEM 202"], "description": "Nuclear reactor design, thermal analysis, and safety."},
        "REE 532": {"name": "Photovoltaic Systems", "credits": 3, "level": "Graduate", "prerequisites": ["REE 422"], "description": "Photoelectric conversion, PV technologies, and market analysis."},
        "REE 534": {"name": "Electric Power Generation, Distribution and Utilization", "credits": 2, "level": "Graduate", "prerequisites": ["REE 419"], "description": "Distribution systems, stability, and illumination engineering."},
        "REE 540": {"name": "Renewable Energy Economic Analysis and Feasibility Study", "credits": 2, "level": "Graduate", "prerequisites": ["REE 309"], "description": "Cost-benefit analysis and project evaluation methods."},
        "REE 543": {"name": "Energy Conservation & Efficiency", "credits": 2, "level": "Graduate", "prerequisites": ["REE 419"], "description": "Energy efficiency management and waste energy recovery."},
        "REE 555": {"name": "Turbine Blade Design", "credits": 2, "level": "Graduate", "prerequisites": ["REE 466", "SPC 408"], "description": "Turbine blade aerodynamics and structural integrity analysis."},
        "REE 560": {"name": "Special Topics in Adv Generator Control", "credits": 2, "level": "Graduate", "prerequisites": ["REE 411"], "description": "Renewable power generation and voltage source converter control."},
        "REE 561": {"name": "Special Topics in Adv Thermal Systems", "credits": 2, "level": "Graduate", "prerequisites": [], "description": "Solar thermal energy conversion and applications."},
        "REE 577": {"name": "Electric Vehicles", "credits": 2, "level": "Graduate", "prerequisites": ["REE 411"], "description": "Power converters in EVs, battery management, and chargers."},
        "REE 590": {"name": "Selected Topics in Renewable Energy Eng", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics of interest in renewable energy engineering."},
        "REE 598": {"name": "Senior Design Project I", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "Problem identification and solution generation for capstone project."},
        "REE 599": {"name": "Senior Design Project II", "credits": 3, "level": "Graduate", "prerequisites": ["REE 598"], "description": "Final design and project report completion."}
    },
    
    # ENERGY AND BIOPROCESS ENGINEERING (EBPE)
    # Note: Official ZC code is "EBE" (Energy and Bioprocess Engineering)
    "EBE": {
        # Junior Level
        "EBE 359": {"name": "Bioprocess Engineering", "credits": 3, "level": "Junior", "prerequisites": ["ENV 220", "ENV 207"], "description": "Enzymatic reactions, microbial growth kinetics, bioreactors, and wastewater treatment."},
        # Senior Level
        "EBE 401": {"name": "Control Systems", "credits": 3, "level": "Senior", "prerequisites": ["MATH 202"], "description": "Dynamic systems modeling, feedback control, and stability analysis."},
        "EBE 411": {"name": "Thermal Solar Energy", "credits": 3, "level": "Senior", "prerequisites": ["ENGR 207", "ENV 346", "ENGR 205"], "description": "Solar concentration technologies for heating, steam production, and power generation."},
        "EBE 450": {"name": "Unit Operations Lab", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Lab experiments on adsorption, reaction, distillation, and water treatment."},
        "EBE 480": {"name": "Separation Processes", "credits": 2, "level": "Senior", "prerequisites": ["ENV 425"], "description": "Distillation, absorption, adsorption, and membrane processes."},
        # Graduate Level
        "EBE 505": {"name": "Industrial Bio-Processes", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 359"], "description": "Enzymes and microbes for manufacturing industrial products and biofuels."},
        "EBE 522": {"name": "Fuel Cells and Battery Technology", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 207", "CHEM 202"], "description": "Electrochemistry, fuel cell design, PEMFC, SOFC, and battery performance."},
        "EBE 524": {"name": "Energy and Bio-Process Engineering Lab", "credits": 1, "level": "Graduate", "prerequisites": ["EBE 359"], "description": "Fermentation, absorption, energy storage and conversion experiments."},
        "EBE 530": {"name": "Process Design and Simulation", "credits": 3, "level": "Graduate", "prerequisites": ["ENV 346"], "description": "Flow sheeting, equipment selection, piping, plant layout, and simulators."},
        "EBE 550": {"name": "Process Dynamics and Control", "credits": 2, "level": "Graduate", "prerequisites": ["MATH 202", "ENV 207"], "description": "Dynamic process modeling, feedback and feedforward control strategies."},
        "EBE 597": {"name": "Selected topics in Energy & Bioprocess Engineering", "credits": 3, "level": "Graduate", "prerequisites": [], "description": "Selected topics of interest not covered elsewhere in the curriculum."},
        "EBE 598": {"name": "Senior Design Project I", "credits": 1, "level": "Graduate", "prerequisites": [], "description": "Problem identification, solution generation, and project planning."},
        "EBE 599": {"name": "Senior Design Project II", "credits": 3, "level": "Graduate", "prerequisites": ["EBE 598"], "description": "Final design and project report completion."}
    },
    
    # Note: Official ZC code is "FINC" (Finance)
    "FINC": {
        # Freshman Level
        "FINC 101": {"name": "Financial Accounting", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Accounting cycle, financial statement presentation, assets, liabilities, and equity."},
        # Sophomore Level
        "FINC 201": {"name": "Principles of Finance", "credits": 3, "level": "Sophomore", "prerequisites": ["FINC 101"], "description": "Business investment decisions, sources of finance, cost of capital, and dividends."},
        # Junior Level
        "FINC 305": {"name": "Financial Reporting", "credits": 3, "level": "Junior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Accounting, finance, economics, and business strategy for financial decision-making."},
        "FINC 310": {"name": "Corporate Finance", "credits": 3, "level": "Junior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Corporate investment evaluation, financing, value creation, and shareholder strategies."},
        "FINC 315": {"name": "Financial Markets, Institutions and Economic Activity", "credits": 3, "level": "Junior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Financial innovation, algorithmic trading, fintech, and risk management."},
        # Senior Level
        "FINC 401": {"name": "Investment Theory", "credits": 3, "level": "Senior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Portfolio diversification, short and long-term investments, and mutual funds."},
        "FINC 405": {"name": "Derivative Securities", "credits": 3, "level": "Senior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Forwards, futures, swaps, options, and risk management strategies."},
        "FINC 410": {"name": "Fixed Income Securities", "credits": 3, "level": "Senior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Bonds, treasury notes, floating rate notes, and callable bonds."},
        "FINC 415": {"name": "Blockchain and Digital Currencies", "credits": 3, "level": "Senior", "prerequisites": ["FINC 101", "FINC 201"], "description": "Cryptocurrency fundamentals, Bitcoin, blockchain technology, and smart contracts."}
    },
    
    # Note: Official ZC code is "MKTG" (Marketing)
    "MKTG": {
        # Freshman Level
        "MKTG 101": {"name": "Principles of Marketing", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Marketing function, customer needs, target markets, and marketing programs."},
        # Junior Level
        "MKTG 301": {"name": "Market research and consumer behavior", "credits": 3, "level": "Junior", "prerequisites": ["MKTG 101"], "description": "Market research methods, consumer psychology, and advertising."},
        "MKTG 305": {"name": "Strategic and B2B Marketing", "credits": 3, "level": "Junior", "prerequisites": ["MKTG 101"], "description": "Business-to-business marketing principles and strategic frameworks."},
        "MKTG 310": {"name": "Brand and sales Management", "credits": 3, "level": "Junior", "prerequisites": ["MKTG 101"], "description": "Sales communication, distribution, pricing, promotion, and buyer motivation."},
        # Senior Level
        "MKTG 401": {"name": "Marketing Communications", "credits": 3, "level": "Senior", "prerequisites": ["MKTG 101"], "description": "Communication decisions, creative brief, message writing, and media strategies."},
        "MKTG 405": {"name": "Digital Marketing", "credits": 3, "level": "Senior", "prerequisites": ["MKTG 101"], "description": "Digital marketing principles for business growth and online presence."},
        "MKTG 410": {"name": "Product Management", "credits": 3, "level": "Senior", "prerequisites": ["MKTG 101"], "description": "New product development, idea generation, sales forecasting, and launch tactics."},
        "MKTG 415": {"name": "Marketing Analytics", "credits": 3, "level": "Senior", "prerequisites": ["MKTG 101"], "description": "Marketing insights, segmentation, customer lifetime analysis, and conjoint analysis."}
    },
    
    # Note: Official ZC code is "BENT" (Business Entrepreneurship)
    "BENT": {
        # Junior Level
        "BENT 301": {"name": "Advanced and Corporate Entrepreneurship", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Entrepreneurial skills within organizations for competitive advantage."},
        "BENT 305": {"name": "Entrepreneurial Finance", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Financial knowledge for starting, building, and harvesting a venture."},
        "BENT 310": {"name": "Digital Start-Ups and Ecosystems", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Value creation in digital platforms and platform business strategies."},
        # Senior Level
        "BENT 401": {"name": "Social Entrepreneurship and sustainability", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Entrepreneurial thinking through social, environmental, and economic sustainability."}
    },
    
    # SUPPLY CHAIN (SCHN) - Official ZC Courses
    "SCHN": {
        # Sophomore Level
        "SCHN 201": {"name": "Supply Chain Management", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "This course will provide students with the knowledge and the tools necessary to develop, implement, and sustain strategies for managing supply chain issues."},
        # Junior Level
        "SCHN 301": {"name": "Information Technology Management", "credits": 3, "level": "Junior", "prerequisites": [], "description": "The course purpose is to provide the substance and skill necessary to make sound business decisions relating to information systems and to work with senior line managers in the resolution of issues and problems in this area."},
        "SCHN 305": {"name": "Models and Business Simulations", "credits": 3, "level": "Junior", "prerequisites": [], "description": "The purpose of the course is to have students understand the general principles of Business simulation model design and concepts of computer simulation. The course introduces students to simulation types, mathematical model types and simulation software and languages."},
        "SCHN 310": {"name": "Fundamentals of Supply Chain Management", "credits": 3, "level": "Junior", "prerequisites": ["SCHN 201"], "description": "This course will provide an overview of the basic principles of supply chain management, giving students an understanding of supply chain processes from sourcing to finished goods and customers to suppliers."},
        # Senior Level
        "SCHN 401": {"name": "Production Planning Procurement and Supply Management", "credits": 3, "level": "Senior", "prerequisites": ["SCHN 201"], "description": "This course equips students with knowledge of fundamental issues in production and inventory planning and control in manufacturing firms, at the same time, developing the students' modeling and analytical skills."},
        "SCHN 405": {"name": "Logistics Management", "credits": 3, "level": "Senior", "prerequisites": ["SCHN 201"], "description": "Provides a deep analysis of many logistics services to include: global logistics, customer service and order management, distribution/fulfillment operations, demand and inventory planning and management, network analysis and design, and transportation operations."},
        "SCHN 410": {"name": "Information Technology in Supply Chains", "credits": 3, "level": "Senior", "prerequisites": ["SCHN 201"], "description": "In this course, students will learn to strategically think about integrated supply-chain, procurement, and service management strategies for organizations that rely, at least partially, on Internet and information technology."}
    },
    
    # SCH - SCHOOL HUMANITIES/GENERAL EDUCATION COURSES
    # Official ZC Courses from https://zcadminpanel.zewailcity.edu.eg/api/courses
    # Required for all undergraduate programs across all schools
    "SCH": {
        # Freshman Level - Foundation Humanities
        "SCH 105": {"name": "Critical Thinking", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Develops analytical and logical reasoning skills. Students learn to evaluate arguments, identify fallacies, and construct well-reasoned conclusions."},
        "SCH 110": {"name": "Creativity and Innovation", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Explores creative thinking processes and innovation methodologies. Students develop skills for generating novel ideas and solutions."},
        "SCH 163": {"name": "Sustainability, Social and Ethical Issues in Computing", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Examines ethical considerations and social responsibilities in computing. Topics include privacy, security ethics, and sustainable technology practices."},
        
        # Sophomore Level - General Education
        "SCH 201": {"name": "World Literature", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Survey of major works of world literature from diverse cultures and time periods. Develops critical reading and analysis skills."},
        "SCH 202": {"name": "Music Aesthetics", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Introduction to music theory, appreciation, and aesthetic principles. Students explore various musical traditions and their cultural contexts."},
        "SCH 203": {"name": "Entrepreneurship & Small Business Management", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Fundamentals of starting and managing small businesses. Topics include business planning, financing, marketing, and operations for entrepreneurs."},
        "SCH 205": {"name": "Arabic Creative Writing", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Develops creative writing skills in Arabic language. Students explore various genres including poetry, short stories, and narrative essays."},
        "SCH 206": {"name": "Introduction to Visual Arts", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Survey of visual arts including painting, sculpture, and digital art. Students develop appreciation and basic skills in visual expression."},
        "SCH 207": {"name": "Analytical Philosophy", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Introduction to analytical philosophy methods and key concepts. Topics include logic, language analysis, and philosophical argumentation."},
        "SCH 232": {"name": "Introduction to Psychology", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Fundamentals of human psychology including cognition, behavior, personality, and mental processes. Foundation for understanding human behavior."},
        "SCH 233": {"name": "Engineering Economical Analysis", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Economic principles applied to engineering decisions. Topics include cost analysis, time value of money, and economic evaluation of projects."},
        "SCH 234": {"name": "History and Philosophy of Science", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Explores the historical development of scientific thought and philosophical foundations of scientific methodology and knowledge."},
        "SCH 235": {"name": "The Creative Mind", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Study of creativity from psychological and cognitive perspectives. Explores theories of creative thinking and methods to enhance creativity."},
        "SCH 244": {"name": "Leadership & Professionalism", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Develops leadership skills and professional conduct. Topics include team leadership, communication, ethics, and career development."},
        "SCH 258": {"name": "Arabic Literature", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Survey of classical and modern Arabic literature. Students analyze major works and explore literary traditions of the Arab world."},
        "SCH 260": {"name": "Philosophical Thinking", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Introduction to philosophical inquiry and critical thinking methods. Explores fundamental questions about knowledge, reality, and ethics."},
        "SCH 261": {"name": "Engineering Project Management", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Principles of managing engineering projects. Topics include planning, scheduling, resource allocation, and project control techniques."},
        "SCH 262": {"name": "Engineering Project Economics", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Economic analysis for engineering projects. Covers cost estimation, budgeting, financial planning, and economic feasibility studies."},
        "SCH 263": {"name": "Engineering Ethics and Safety", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Professional ethics in engineering practice. Topics include safety standards, liability, environmental responsibility, and ethical decision-making."},
        "SCH 264": {"name": "Introduction to Entrepreneurship and Small Business Management", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Overview of entrepreneurship and small business principles. Students develop business plans and learn startup fundamentals."},
        "SCH 265": {"name": "Geography of Egypt", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Study of Egypt's physical and human geography. Topics include climate, resources, demographics, urbanization, and regional development."},
        "SCH 266": {"name": "Sociology", "credits": 2, "level": "Sophomore", "prerequisites": [], "description": "Introduction to sociological concepts and theories. Examines social structures, institutions, culture, and patterns of social behavior."},
        
        # Junior Level - Advanced Humanities
        "SCH 273": {"name": "Cognitive Psychology", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Study of human cognitive processes including perception, attention, memory, language, problem-solving, and decision-making."},
        "SCH 275": {"name": "The Creative Mind", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Advanced study of creativity and creative processes. Explores cognitive mechanisms underlying creative thought and innovation."},
        "SCH 277": {"name": "Positive Psychology", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Scientific study of human flourishing and well-being. Topics include happiness, resilience, strengths, and optimal human functioning."},
        "SCH 288": {"name": "Business Ethics", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Ethical issues in business and corporate responsibility. Topics include stakeholder theory, sustainability, and ethical decision frameworks."},
        "SCH 299": {"name": "Special Topics in Humanities", "credits": 2, "level": "Junior", "prerequisites": [], "description": "Selected advanced topics in humanities varying by semester. Provides deep exploration of specialized humanities subjects."}
    },
    
    # MANAGEMENT (MGMT) - Official ZC Courses
    "MGMT": {
        # Freshman Level
        "MGMT 101": {"name": "Principles of Management", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "This course presents the principles, techniques, and concepts needed for managerial analysis and decision-making. It highlights the effective management of planning, organizing, influencing, and controlling related to the internal and external environment."},
        "MGMT 105": {"name": "Leadership and Professional Ethics", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "This course provides an overview of various philosophical approaches to ethical decision-making and practical applications involving ethical problems that arise in business. Topics include the major ethical constructs, approaches to self-knowledge and practical leadership skills."},
        # Sophomore Level
        "MGMT 201": {"name": "Human Resources Management", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "The course develops a critical understanding of the role and functions of the various human resource activities in an organisation, providing students with a comprehensive review of key HRM concepts, techniques and issues."},
        "MGMT 205": {"name": "Project Management", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "It focuses on how projects contribute to the strategic goals of the organization. It enables learners to comprehend and apply a project plan's components, such as managing risk, scheduling resources, managing progress, and controlling projects."},
        # Junior Level
        "MGMT 301": {"name": "Operations Management", "credits": 3, "level": "Junior", "prerequisites": ["BGEN 105", "BGEN 110"], "description": "The course studies the fundamental process for the production of goods and services in organizations with emphasis on understanding its relationship to other business areas. The course uses quantitative tools in production/operations for effective decision-making."},
        "MGMT 305": {"name": "Advanced Organizational Behavior", "credits": 3, "level": "Junior", "prerequisites": ["MGMT 101", "MGMT 201"], "description": "The course explores human behavior at the individual, group and organizational level. Topics include personality and values, attitudes and job satisfaction, perception and decision-making, motivation and reward systems, group behavior, organizational communication."},
        "MGMT 310": {"name": "General Management Processes/Change", "credits": 3, "level": "Junior", "prerequisites": ["MGMT 101", "MGMT 201"], "description": "This course focuses on implementation and the way that general managers get things done. They work through processes—sequences of tasks and activities that unfold over time, like strategic planning, business development, and budgeting."},
        "MGMT 311": {"name": "Quantitative Methods for Business", "credits": 3, "level": "Junior", "prerequisites": ["BGEN 105", "BGEN 110"], "description": "This course covers deterministic models and techniques to optimally solve complex managerial problems. Topics include linear programming, graphical solution and the simplex algorithm, as well as related analytical topics such as duality theory and sensitivity analysis."},
        # Senior Level
        "MGMT 401": {"name": "HR Data Analytics", "credits": 3, "level": "Senior", "prerequisites": ["MGMT 101", "MGMT 201"], "description": "In this course, participants will gain a solid understanding of the power of people analytics. They will have the ability to leverage the tools and the know-how of people analytics and metrics to solve issues in the workplace and turn data into visual insights."},
        "MGMT 405": {"name": "Performance, Compensation and Career Management", "credits": 3, "level": "Senior", "prerequisites": ["MGMT 101", "MGMT 201"], "description": "This course is intended to provide students and practicing managers with a complete, comprehensive review of essential personnel management concepts and techniques. It is designed to familiarize the student with the major functional areas in Human Resources."}
    },
    
    # GENERAL EDUCATION AND COMMON COURSES - Official ZC Courses
    
    # MATHEMATICS (MATH) - Official ZC Courses
    "MATH": {
        # Freshman Level
        "MATH 101": {"name": "Calculus I", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Calculus I course discusses the definite integral, applications of definite integrals to different physical problems, calculus of important transcendental functions, techniques of integrations, Numerical Integration and Improper integrals."},
        "MATH 102": {"name": "Calculus II", "credits": 3, "level": "Freshman", "prerequisites": ["MATH 101"], "description": "Calculus II course discusses convergence and divergence of sequences and series, power series, Taylor series, parametric equations, polar coordinates, lines and planes in space, functions of several variables, partial derivatives, multiple integrals."},
        "MATH 103": {"name": "Calculus for Computational Sciences", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Students study both major branches, differential calculus and integral calculus. Covers Limits, Continuity derivatives and integrals, Implicit differentiation, Applications of derivatives to optimization problems."},
        "MATH 104": {"name": "Linear Algebra", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Introduction to systems of simultaneous equations and the use of matrices to describe multidimensional spaces, matrix algebra, vector spaces and bases sets, eigenvalues and eigenvectors."},
        "MATH 105": {"name": "Probability and Statistics", "credits": 3, "level": "Freshman", "prerequisites": ["MATH 103"], "description": "Introduces students to the basic concepts of probability and statistics for computational science and artificial intelligence fields and analysis of experimental data."},
        # Sophomore Level
        "MATH 201": {"name": "Linear Algebra and Vector Geometry", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Introduction to systems of simultaneous equations, matrix algebra, vector spaces and Bases, eigenvalues and eigenvectors, orthogonality and least squares."},
        "MATH 202": {"name": "Ordinary Differential Equations", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 102"], "description": "Demonstrates the usefulness of differential equations as mathematical models for real world problems in science and engineering. Covers first order, second order and higher order ordinary differential equations."},
        "MATH 203": {"name": "Introduction to Discrete Mathematics", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Covers Proofs, mathematical induction, recursion, Euclid algorithm, Prime numbers, modular arithmetic, Fermat Little theorem, Public-key cryptography, RSA."},
        "MATH 205": {"name": "Discrete Mathematics for Computational Sciences", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Covers Proofs, mathematical induction, recursion, Prime numbers, modular arithmetic, Fermat Little theorem, Public-key cryptography, RSA, Relations, Elementary graph theory."},
        # Junior Level
        "MATH 301": {"name": "Probability and Statistics", "credits": 3, "level": "Junior", "prerequisites": ["MATH 102"], "description": "Introduces students to the basic concepts of probability and statistics for engineering fields. Covers statistical reasoning, hypothesis testing, ANOVA, correlation and regression."},
        "MATH 302": {"name": "Partial Differential Equations and Complex Analysis", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202"], "description": "Introduction to PDEs, special functions like Bessel and Legendre, Sturm-Liouville problem, solutions using separation of variables, integral transforms, Green's function. Complex analysis: analytical functions, Cauchy-Riemann equations, contour integrals."},
        "MATH 303": {"name": "Linear and Non-linear Programming for Computational Sciences", "credits": 3, "level": "Junior", "prerequisites": ["MATH 103", "MATH 104"], "description": "Formulate mathematical models and develop efficient algorithms to solve linear and nonlinear optimization problems. Explores simplex methods, interior-point methods, gradient methods, Newton methods."},
        "MATH 305": {"name": "Abstract Algebra", "credits": 3, "level": "Junior", "prerequisites": ["MATH 201"], "description": "Introduction to abstract mathematical thinking through study of groups, rings and other abstract mathematical objects. Covers linear groups and group representations."},
        "MATH 306": {"name": "Numerical Analysis", "credits": 3, "level": "Junior", "prerequisites": ["MATH 201", "MATH 202"], "description": "Numerical methods for solving algebraic, transcendental, and differential equations using Matlab. Covers curve fitting, regression, interpolation models, and linear programming."},
        "MATH 306N": {"name": "Numerical Analysis", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202", "MATH 102"], "description": "Numerical methods aided by technology to solve algebraic equations, calculate derivatives and integrals numerically, curve fitting and optimization."},
        "MATH 307": {"name": "Numerical Methods", "credits": 3, "level": "Junior", "prerequisites": ["MATH 104"], "description": "Numerical methods using MATLAB to solve algebraic, transcendental, and differential equations. Covers curve fitting, regression, interpolation and optimization."},
        "MATH 308": {"name": "Discrete Mathematics", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Covers Proofs, mathematical induction, recursion, Prime numbers, modular arithmetic, Public-key cryptography, RSA, Elementary graph theory, De Bruijn sequences and Gray codes."},
        "MATH 310": {"name": "Abstract Algebra", "credits": 3, "level": "Junior", "prerequisites": ["MATH 201"], "description": "Introduction to abstract mathematical thinking. Study of groups, rings and algebraic structures. Provides mathematical maturity and enables learners to build mathematical thinking."},
        # Senior Level
        "MATH 403": {"name": "Introduction to Real Analysis and Topology", "credits": 3, "level": "Senior", "prerequisites": ["MATH 101", "MATH 201"], "description": "Provides solid foundation for real analysis and introduction to topology. Covers real numbers, sequences, continuity, differentiability, integrability and metric spaces."},
        "MATH 404": {"name": "Linear and Non-linear Programming", "credits": 3, "level": "Senior", "prerequisites": ["MATH 102"], "description": "Develop efficient algorithms to solve linear and nonlinear optimization problems especially convex optimization. Covers optimality conditions, duality, simplex methods, Newton and Quasi-Newton methods."}
    },
    # PHYSICS (PHYS) - Official ZC Courses (50 courses)
    "PHYS": {
        # Freshman Level
        "PHYS 101": {"name": "Introduction to Classical Mechanics", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Introduces students to classical Newtonian formalism for mechanics, including kinematics, conservation of energy and momentum, Newton's laws of motion, force diagrams, friction, rotational motion and angular momentum."},
        "PHYS 102": {"name": "Introduction to Electromagnetism", "credits": 3, "level": "Freshman", "prerequisites": ["PHYS 101", "MATH 101"], "description": "Covers classical electromagnetism, from electric charges and Coulomb's law to Maxwell's equations and electromagnetic waves, including Gauss' law, Ohm's Law and elementary DC circuits."},
        "PHYS 103": {"name": "Physics 1", "credits": 3, "level": "Freshman", "prerequisites": ["MATH 103"], "description": "Introduces students to principles and applications of mechanics, heat, and sound. The course contains lab work to develop an understanding of the scientific method."},
        "PHYS 104": {"name": "Physics 2", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Discusses principles and applications of light, electricity, and magnetism. The course contains lab work to develop an understanding of the scientific method."},
        "PHYS 105": {"name": "Introduction to Classical Mechanics for Engineers", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Classical Newtonian formalism for mechanics with laboratory to conduct experiments involving data collection and reporting, and error analysis."},
        "PHYS 106": {"name": "Introduction to Electromagnetism for Engineers", "credits": 3, "level": "Freshman", "prerequisites": ["PHYS 115", "PHYS 105"], "description": "Covers classical electromagnetism from electric charges to electromagnetic induction with laboratory experiments."},
        "PHYS 111": {"name": "Introduction to Classical Mechanics Lab", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory concurrent with PHYS 101. Experiments include classical mechanics involving data collection and reporting, and error analysis."},
        "PHYS 112": {"name": "Introduction to Electromagnetism Lab", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory concurrent with PHYS 102. Experiments include classical electromagnetism involving data collection and reporting, and error analysis."},
        "PHYS 113": {"name": "Physics 1 (Theory)", "credits": 2, "level": "Freshman", "prerequisites": ["MATH 103"], "description": "Classical Newtonian formalism for mechanics, including kinematics, conservation of energy and momentum, Newton's laws of motion."},
        "PHYS 115": {"name": "Introduction to Classical Mechanics for Engineers (Lab)", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory associated with PHYS 125 to conduct experiments involving data collection, reporting, and error analysis."},
        "PHYS 116": {"name": "Introduction to Electromagnetism for Engineers (Lab)", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory associated with PHYS 126 to conduct experiments involving data collection, reporting, and error analysis."},
        "PHYS 123": {"name": "Physics 1 (Lab)", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory associated with PHYS 113 to conduct experiments involving data collection, reporting, and error analysis."},
        "PHYS 125": {"name": "Introduction to Classical Mechanics for Engineers (Theory)", "credits": 2, "level": "Freshman", "prerequisites": [], "description": "Classical Newtonian formalism for mechanics, including kinematics, conservation of energy and momentum, Newton's laws of motion, rotational motion."},
        "PHYS 126": {"name": "Introduction to Electromagnetism for Engineers (Theory)", "credits": 2, "level": "Freshman", "prerequisites": ["PHYS 125", "PHYS 105"], "description": "Classical electromagnetism, from electric charges and Coulomb's law to Maxwell's equations, including Gauss' law and electromagnetic induction."},
        # Sophomore Level
        "PHYS 201": {"name": "Thermodynamics, Wave Motion and Optics", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 102"], "description": "Introduction to classical physics with modules in thermodynamics, thermal physics, ideal gases entropy, wave mechanics, interference, standing waves, optics, and fluid mechanics."},
        "PHYS 202": {"name": "Modern Physics", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 102"], "description": "Basic concepts of quantum mechanics including wave-particle duality, de Broglie wavelength, Schrodinger equation, Uncertainty Principle, and introduction to special and general relativity."},
        "PHYS 203": {"name": "Introduction to Thermodynamics, Wave Motion and Optics for Engineers", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 105", "PHYS 125"], "description": "Concludes introduction to classical physics with thermodynamics, wave mechanics, optics, and fluid mechanics with laboratory component."},
        "PHYS 204": {"name": "Analytical Mechanics", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 101"], "description": "Modern, generalized mathematical expression of Newtonian classical mechanics, including Lagrangian and Hamiltonian formalisms and applications."},
        "PHYS 205": {"name": "Introduction to Modern Astrophysics", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 101"], "description": "Introduces students to the basic observational and theoretical methods, techniques and technical language of astronomy."},
        "PHYS 208": {"name": "Electrodynamics I", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 102"], "description": "Divided into Electrostatics, Magnetostatics and Time-Varying fields. Covers electric field, divergence and curl, Electric potential, Laplace equation, magnetic fields and Maxwell's equations."},
        "PHYS 210": {"name": "Advanced Electromagnetism", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 102"], "description": "Advanced classical electromagnetic theory: electrostatics, multipoles, Laplace and Poisson equations, boundary value problems, magnetism, Faraday's Law, electromagnetic waves, waveguides."},
        "PHYS 211": {"name": "Thermodynamics, Wave Motion and Optics Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Laboratory course accompanying PHYS 201. Experiments in thermodynamics, waves, optics and fluid mechanics."},
        "PHYS 212": {"name": "Modern Physics Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Laboratory course accompanying PHYS 202. Experiments in Modern Physics involving data collection and reporting, and error analysis."},
        "PHYS 218": {"name": "Vector Calculus", "credits": 3, "level": "Sophomore", "prerequisites": ["MATH 102"], "description": "Covers vector calculus and applications in classical mechanics and electrodynamics. Topics include Vector Algebra, Line/Surface/Volume Integrals, Gradient, Divergence, Curl, Tensors."},
        "PHYS 224": {"name": "Introduction to Modern Physics for Engineers", "credits": 3, "level": "Sophomore", "prerequisites": ["PHYS 203"], "description": "Basic concepts of quantum mechanics including wave-particle duality, de Broglie wavelength, Schrodinger equation, and atomic physics with laboratory component."},
        # Junior Level
        "PHYS 308": {"name": "Electrodynamics II", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 208"], "description": "Advanced topics of classical electromagnetism. Covers electromagnetic wave propagation, wave guides, retarded potentials, Jefimenko's equations, dipole radiation, relativistic electrodynamics."},
        "PHYS 311": {"name": "Thermal and Statistical Physics", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 201"], "description": "Boltzmann transport equation. Statistical physics permits prediction of macroscopic properties of many-body systems by studying statistics of individual constituents."},
        "PHYS 316": {"name": "Mathematical Physics I", "credits": 3, "level": "Junior", "prerequisites": [], "description": "Mathematical methods of particular interest in physics, astronomy, and atmospheric science, including Fourier analysis, special functions, and Green's function."},
        "PHYS 323": {"name": "Quantum Mechanics I", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 202"], "description": "Theory of quantum mechanics using Schrodinger equation for square well, harmonic oscillator and hydrogen atom. Covers angular momentum, tunneling, spin, quantization."},
        "PHYS 326": {"name": "Mathematical Physics II", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 346", "MATH 201", "MATH 202"], "description": "Analytical methods and numerical component teaching computational techniques. Includes Mathematica and MatLab for mathematical computation."},
        "PHYS 327": {"name": "Observational Astrophysics Laboratory", "credits": 2, "level": "Junior", "prerequisites": ["PHYS 205"], "description": "Practical experience in basic observational and computational aspects of astronomical data collection and analysis."},
        "PHYS 331": {"name": "Stellar Structure and Evolution", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 205"], "description": "Covers the basics of main sequence stellar theory, with simple descriptions of star formation and end states."},
        "PHYS 346": {"name": "Mathematical Physics I", "credits": 3, "level": "Junior", "prerequisites": ["MATH 202"], "description": "Mathematical methods including Fourier analysis, special functions, and Green's functions."},
        "PHYS 348": {"name": "Quantum Mechanics II", "credits": 3, "level": "Junior", "prerequisites": ["PHYS 323"], "description": "Continuation of Advanced Quantum Mechanics I, including Eigen functions, perturbation and scattering theory, and introduction to Quantum Field Theory."},
        "PHYS 356": {"name": "Mathematical Physics II", "credits": 4, "level": "Junior", "prerequisites": ["MATH 201"], "description": "Analytical methods and numerical techniques for solving problems of mathematical physics."},
        "PHYS 364": {"name": "Biological Physics", "credits": 3, "level": "Junior", "prerequisites": ["BIOL 102", "CHEM 202", "PHYS 201"], "description": "Physical basis underlying structure, dynamics and function of biological molecules, intermolecular interactions, biophysical properties of proteins, nucleic acids and lipids."},
        "PHYS 399": {"name": "Internship", "credits": 2, "level": "Junior", "prerequisites": [], "description": "External training in a national or international industry or research institution on physics related project."},
        # Senior Level
        "PHYS 405": {"name": "Cosmology", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 205"], "description": "Cosmological observations, Friedmann models, the early universe and particle physics, inflation, hot big bang, cosmic microwave background, dark matter dynamics."},
        "PHYS 416": {"name": "Galactic & Extragalactic Astrophysics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 205"], "description": "Basic content and phenomenological description of galaxies from experimental observations, including classification, stellar content, kinematics, spectral properties."},
        "PHYS 420": {"name": "The Solar System", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 205"], "description": "Origins and history of the sun and solar system, geological description of planets, their atmospheres and satellites, asteroids and comets."},
        "PHYS 422": {"name": "Astrophysical Fluid Dynamics", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Introduction to fluid dynamics for astronomical phenomena, from stellar structure to supernovae blast wave, accretion discs, sound waves, supersonic waves."},
        "PHYS 430": {"name": "Quantum Mechanics III", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 348"], "description": "Sequel to Quantum Mechanics I, II. Covers Time-independent perturbation theory, variational principle, WKB approximation, Scattering, Dirac equation."},
        "PHYS 431": {"name": "Quantum Field Theory and Particle Physics", "credits": 6, "level": "Senior", "prerequisites": ["PHYS 323"], "description": "Basic formalism of quantum field theory. Feynman diagrams for high energy particle physics. Covers Lagrangian Field Theory, Klein-Gordon Field, Dirac Field, QED, Standard Electroweak Theory."},
        "PHYS 432": {"name": "Advanced Dynamics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 101"], "description": "Hamiltonian/Lagrangian representation of classical mechanics; stability of trajectories and transition to chaos; qualitative dynamics and phase space structure."},
        "PHYS 438": {"name": "Compact Objects & High Energy Astrophysics", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 205"], "description": "Physics of neutron stars, pulsars, black holes and active centers of galaxies; supernovae and gamma-ray bursts."},
        "PHYS 450": {"name": "Computational Physics", "credits": 3, "level": "Senior", "prerequisites": ["CSCI 101"], "description": "Computational methods of special interest in physics, astronomy and atmospheric science."},
        "PHYS 453": {"name": "Gravity & General Relativity", "credits": 3, "level": "Senior", "prerequisites": [], "description": "Gravity and general relativity; dealing with spacetime; core principles of general relativity; and experimental evidence regarding the theory."},
        "PHYS 455": {"name": "Mathematical Physics III", "credits": 3, "level": "Senior", "prerequisites": ["PHYS 316"], "description": "Continuation of PHYS 346, covering calculus of variations, integral equations, topology and group theory."},
        "PHYS 498": {"name": "Senior Project I", "credits": 1, "level": "Senior", "prerequisites": [], "description": "Research project applying knowledge of physics and scientific methods to a specific small scientific project."},
        "PHYS 499": {"name": "Senior Project II", "credits": 2, "level": "Senior", "prerequisites": ["PHYS 498"], "description": "Continuation of research project applying knowledge of physics and scientific methods."}
    },
    
    # CHEMISTRY (CHEM) - Official ZC Courses
    "CHEM": {
        # Freshman Level
        "CHEM 101": {"name": "Chemistry I", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Covers basics of general and physical chemistry. Includes atomic structure and periodicity, states of matter, chemical stoichiometry, chemical bonding, molecular structures, electrochemistry, acid-base chemistry."},
        "CHEM 102": {"name": "Chemistry II", "credits": 3, "level": "Freshman", "prerequisites": ["CHEM 101"], "description": "Covers introduction to inorganic and nuclear chemistry, spectroscopy, photochemistry, chemical thermodynamics, chemical equilibrium, kinetics, surface chemistry, quantum theory, polymers."},
        "CHEM 103": {"name": "Introduction to Chemistry for Engineers", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Introduces engineering students to basics of general and physical chemistry with lab component covering stoichiometry, acid-base titrations, pH measurements, oxidation-reduction reactions."},
        "CHEM 111": {"name": "Chemistry I Lab", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory concurrent with CHEM 101. Experiments cover fundamentals of general, physical and organic chemistry."},
        "CHEM 112": {"name": "Chemistry II Lab", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory concurrent with CHEM 102. Experiments cover chemical thermodynamics, equilibrium, kinetics, molecular modeling, chromatography."},
        # Sophomore Level
        "CHEM 201": {"name": "Organic Chemistry", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 101"], "description": "Modern description of molecules, molecular orbital theory, hybridization, structure and function of organic compounds, stereochemistry, ring systems and aromaticity, polymers."},
        "CHEM 202": {"name": "Analytical & Physical Chemistry", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 101"], "description": "Core concepts in physical chemistry, thermodynamics, electrochemistry and principles of chemical equilibrium."},
        "CHEM 203": {"name": "Organic Chemistry II", "credits": 3, "level": "Sophomore", "prerequisites": ["CHEM 201"], "description": "Fundamental overview of organic chemistry covering structure, function, reactions, mechanisms, and synthesis of organic compounds."},
        "CHEM 211": {"name": "Organic Chemistry Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Experiments designed to reinforce CHEM 201 concepts. Includes synthesis of simple organic molecules, estimation of purity, phytochemical tests."},
        "CHEM 212": {"name": "Analytical & Physical Chemistry Lab", "credits": 1, "level": "Sophomore", "prerequisites": [], "description": "Laboratory demonstrating CHEM 202 concepts. Students learn modern instrumentation and techniques in spectroscopy, electrochemistry, thermodynamics and kinetics."}
    },
    
    # ENGLISH (ENGL) - Official ZC Courses
    "ENGL": {
        # Remedial Level (0 credits)
        "ENGL 002": {"name": "Remedial English 1", "credits": 0, "level": "Freshman", "prerequisites": [], "description": "Pass/fail course addressing four skills of Reading, Listening, Writing and Speaking. Covers identifying main ideas, reading strategies, conversation techniques, writing coherently."},
        "ENGL 003": {"name": "Remedial English 2", "credits": 0, "level": "Freshman", "prerequisites": ["ENGL 002"], "description": "Pass/fail course for B1 learners developing listening, reading, speaking, and writing skills within integrated skills approach."},
        "ENGL 004": {"name": "Remedial English 3", "credits": 0, "level": "Freshman", "prerequisites": ["ENGL 003"], "description": "Pass/fail course developing students' writing and speaking productive skills within integrated pedagogical approach."},
        # Freshman Level
        "ENGL 101": {"name": "English for Science", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Introduces use of English in technical reading and writing. Covers sentence patterns and grammatical structures for scientific concepts like definition, classification, causation."},
        # Sophomore Level
        "ENGL 151": {"name": "Scientific Writing", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 152"], "description": "Enhances skills for scientific research design and writing. Covers scientific collocations, research approaches, scientific articles, grant proposals, avoiding plagiarism."},
        "ENGL 152": {"name": "Effective Speaking and Composition", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 004"], "description": "Introduces rhetoric strategies, enhances skills in identifying, evaluating, and producing arguments. Develops critical thinking, research skills, and public speaking."},
        "ENGL 153": {"name": "Scientific Writing", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 152"], "description": "Step-by-step process for scientific research design and writing: avoid wordy writing, integrate scientific collocations, review articles, write research grant proposals."},
        "ENGL 154": {"name": "Business English 1", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 004"], "description": "Helps students improve ability to communicate effectively in international workplace contexts, practicing Reading, Writing, Listening & Speaking."},
        "ENGL 155": {"name": "Business English 2", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 154"], "description": "Continues improving ability to communicate effectively in international workplace contexts across all four communication skills."},
        "ENGL 156": {"name": "Technical English 1", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 004"], "description": "Focuses on oral public communications, presentation skills, rhetoric strategies, argumentation, persuasion, debating skills."},
        "ENGL 157": {"name": "Technical English 2", "credits": 2, "level": "Sophomore", "prerequisites": ["ENGL 156"], "description": "Covers technical writing: ethical/legal considerations, effective writing process, persuasive techniques, document design, project reports, journal articles."},
        "ENGL 201": {"name": "Rhetoric & Composition", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Introduces meaning and strategies of rhetoric to aid students in comprehending and evaluating different types of arguments. Develops critical thinking, reading, and writing skills."},
        "ENGL 202": {"name": "Advanced Scientific Writing", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGL 201", "ENGL 101"], "description": "Helps students express their research orientations, experiments, and findings effectively."},
        "ENGL 203": {"name": "Public Speaking", "credits": 3, "level": "Sophomore", "prerequisites": ["ENGL 101", "ENGL 202"], "description": "Enhances public speaking skills with attention to ethics and audience awareness. Prepares for speeches, conference presentations, and lectures."}
    },
    
    # BIOLOGY (BIOL) - Official ZC Courses
    "BIOL": {
        # Freshman Level
        "BIOL 101": {"name": "Biology I", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Foundation to general concepts of life and cellular biology. Covers cellular basis of life, cellular functions in different organisms, core concepts of evolutional biology."},
        "BIOL 102": {"name": "Biology II", "credits": 3, "level": "Freshman", "prerequisites": ["BIOL 101"], "description": "Fundamentals of cellular structure and function related to molecular biology. Covers modern molecular biology, genes and gene expression, DNA replication and repair, genomes."},
        "BIOL 111": {"name": "Biology I Lab", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory concurrent with BIOL 101. Experiments include metric system, microscopy, cellular respiration, photosynthesis, scientific method, enzymes, mitosis and meiosis."},
        "BIOL 112": {"name": "Biology II Lab", "credits": 1, "level": "Freshman", "prerequisites": [], "description": "Laboratory concurrent with BIOL 102. Experiments include bacterial transformation, plasmid extraction, and gel electrophoresis."}
    },
    
    # BUSINESS GENERAL (BGEN) - Official ZC Courses
    "BGEN": {
        # Freshman Level
        "BGEN 101": {"name": "Business Mathematics", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Mathematical concepts and applications for business careers. Topics include finance charges, cash discounts, depreciation, compound interest, net present value, annuities, statistics."},
        "BGEN 105": {"name": "Calculus for Business Applications", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Basic study of limits and continuity, differentiation, optimization and graphing, integration of elementary functions, with emphasis on applications in business."},
        "BGEN 110": {"name": "Foundations of Statistical Inference", "credits": 3, "level": "Freshman", "prerequisites": [], "description": "Statistical inference is the process of drawing conclusions about populations or scientific truths from data using statistical modeling and data oriented strategies."},
        # Sophomore Level
        "BGEN 201": {"name": "Data Analytics", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Prepares students to gather, describe, and analyze data, and use advanced statistical tools to make decisions on operations, risk management, finance, marketing."},
        "BGEN 205": {"name": "Machine Learning", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Introduction to fundamental methods at the core of modern machine learning. Covers theoretical foundations and essential algorithms for supervised and unsupervised learning."},
        "BGEN 210": {"name": "Programming", "credits": 3, "level": "Sophomore", "prerequisites": [], "description": "Introduces basic concepts and techniques of developing programs for problem solving. Students learn to design, implement, test, debug, and document programs."}
    },
    
}


# ============================================================
# RULE-BASED SYNTHETIC DATA GENERATION
# ============================================================

class RuleBasedDataGenerator:
    """Generate Zewail City-specific synthetic data using deterministic rules"""
    
    # Egyptian names
    MALE_NAMES = [
        "Ahmed", "Mohamed", "Omar", "Youssef", "Karim", "Hassan", "Ali", 
        "Mahmoud", "Ibrahim", "Khaled", "Amr", "Tamer", "Sherif", "Tarek",
        "Mostafa", "Adham", "Seif", "Yasser", "Walid", "Hazem", "Bassem",
        "Ziad", "Marwan", "Yousef", "Adam", "Abdullah", "Fares", "Nour",
        "Ramy", "Eslam", "Hossam", "Ayman", "Emad", "Samir", "Ossama"
    ]
    FEMALE_NAMES = [
        "Fatma", "Nour", "Sara", "Hana", "Mariam", "Layla", "Dina", 
        "Rania", "Heba", "Yasmin", "Salma", "Mona", "Amira", "Noha",
        "Aya", "Rana", "Nada", "Habiba", "Malak", "Jana", "Farida",
        "Lina", "Menna", "Yara", "Shahd", "Zeina", "Nadia", "Ghada",
        "Mai", "Norhan", "Aliaa", "Perihan", "Shaimaa", "Asmaa"
    ]
    LAST_NAMES = [
        "Mohamed", "Ahmed", "Hassan", "Ali", "Ibrahim", "Mahmoud", 
        "Abdel-Rahman", "El-Sayed", "Mostafa", "Khalil", "Mansour", "Osman",
        "El-Masry", "Fouad", "Zaki", "Fathy", "Soliman", "Naguib", "Farouk",
        "Helmy", "Badawy", "Hamdy", "Shawky", "Saleh", "Ramadan", "Hussein",
        "Amin", "Gaber", "Fahmy", "Kamal", "Saber", "Rashad", "Nasr"
    ]
    
    GOVERNORATES = [
        "Cairo", "Giza", "Alexandria", "Qalyubia", "Dakahlia", "Sharqia",
        "Gharbia", "Monufia", "Beheira", "Kafr El-Sheikh", "Damietta",
        "Port Said", "Ismailia", "Suez", "Fayoum", "Beni Suef", "Minya",
        "Asyut", "Sohag", "Qena", "Luxor", "Aswan", "Red Sea"
    ]
    
    def __init__(self):
        self.student_counter = 202200001
        self.structure = ZEWAIL_CITY_STRUCTURE
        self.catalog = COURSE_CATALOG
        
    def generate_national_id(self, birth_date: datetime, gender: str) -> str:
        century = "2" if birth_date.year < 2000 else "3"
        year = str(birth_date.year)[-2:]
        month = f"{birth_date.month:02d}"
        day = f"{birth_date.day:02d}"
        governorate = f"{random.randint(1, 27):02d}"
        sequence = f"{random.randint(1, 999):03d}"
        gender_digit = str(random.choice([1, 3, 5, 7, 9]) if gender == "Male" else random.choice([2, 4, 6, 8]))
        check_digit = str(random.randint(0, 9))
        return f"{century}{year}{month}{day}{governorate}{sequence}{gender_digit}{check_digit}"
    
    def generate_students(self, count: int) -> List[Dict]:
        students = []
        undergrad_programs = list(self.structure["undergraduate_programs"].keys())
        grad_programs = list(self.structure["graduate_programs"].keys())
        minors = self.structure["minors"]
        
        for i in range(count):
            gender = random.choice(["Male", "Female"])
            first_name = random.choice(self.MALE_NAMES if gender == "Male" else self.FEMALE_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            
            is_graduate = random.random() < 0.15
            
            if is_graduate:
                grad_program = random.choice(grad_programs)
                program_info = self.structure["graduate_programs"][grad_program]
                school = program_info["school"]
                student_type = program_info["degree_type"]
                program = grad_program
                age = random.randint(23, 35)
                academic_year = random.randint(1, program_info["duration_years"])
                specialization = None
            else:
                program = random.choice(undergrad_programs)
                program_info = self.structure["undergraduate_programs"][program]
                school = program_info["school"]
                student_type = "Undergraduate"
                age = random.randint(18, 25)
                academic_year = random.randint(1, 4)
                if "specializations" in program_info:
                    specialization = random.choice(program_info["specializations"])
                elif "concentrations" in program_info:
                    specialization = random.choice(program_info["concentrations"])
                else:
                    specialization = None
            
            birth_year = 2026 - age
            birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
            admission_year = 2026 - academic_year
            admission_date = datetime(admission_year, 9, random.randint(1, 15))
            high_school_gpa = round(random.uniform(88.0, 99.5), 1)
            
            minor = None
            if not is_graduate and academic_year >= 2 and random.random() < 0.3:
                minor = random.choice(minors)["name"]
            
            student = {
                "student_id": str(self.student_counter),
                "full_name": f"{first_name} {last_name}",
                "email": f"{first_name.lower()}.{last_name.lower()}@zewailcity.edu.eg",
                "phone": f"+20{random.choice(['10', '11', '12', '15'])}{random.randint(10000000, 99999999)}",
                "national_id": self.generate_national_id(birth_date, gender),
                "date_of_birth": birth_date.strftime("%Y-%m-%d"),
                "gender": gender,
                "address": f"{random.choice(self.GOVERNORATES)}, Egypt",
                "school": school,
                "program": program,
                "specialization": specialization,
                "academic_year": academic_year,
                "gpa": round(random.uniform(2.0, 4.0), 2),
                "high_school_gpa": high_school_gpa,
                "enrollment_status": random.choices(["Active", "On Leave", "Graduated", "Suspended"], weights=[85, 5, 8, 2])[0],
                "admission_date": admission_date.strftime("%Y-%m-%d"),
                "student_type": student_type,
                "minor": minor
            }
            students.append(student)
            self.student_counter += 1
        
        return students
    
    def generate_courses(self, count: int = None) -> List[Dict]:
        courses = []
        all_catalog_courses = []
        
        for dept, dept_courses in self.catalog.items():
            for course_id, info in dept_courses.items():
                all_catalog_courses.append({
                    "course_id": course_id,
                    "course_name": info["name"],
                    "credits": info["credits"],
                    "department": dept,
                    "level": info["level"]
                })
        
        if count and count < len(all_catalog_courses):
            selected_courses = random.sample(all_catalog_courses, count)
        else:
            selected_courses = all_catalog_courses
        
        for course in selected_courses:
            dept = course["department"]
            school = "General Education"
            if dept in ["SPC", "CIE", "ENV", "NANENG", "REE", "EBE"]:
                school = "School of Engineering"
            elif dept in ["BMS", "NANOSC", "PEU", "MATSCI"]:
                school = "School of Science"
            elif dept in ["DSAI", "SW", "IT"]:
                school = "School of Computational Sciences and Artificial Intelligence"
            elif dept in ["BACT", "FINC", "MKTG", "BENT", "SCHN", "MGMT"]:
                school = "School of Business"
            elif dept == "AIE":
                school = "School of Engineering (Graduate)"
            
            days = random.choice(["Sun-Tue", "Mon-Wed", "Sun-Wed", "Tue-Thu"])
            start_hour = random.choice([8, 9, 10, 11, 13, 14, 15, 16])
            duration = 1.5 if course["credits"] <= 3 else 2
            end_hour = start_hour + duration
            schedule = f"{days} {start_hour:02d}:00-{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
            
            courses.append({
                "course_id": course["course_id"],
                "course_name": course["course_name"],
                "credits": course["credits"],
                "department": dept,
                "school": school,
                "level": course["level"],
                "prerequisites": [],
                "instructor_id": f"ZC-FAC{random.randint(100, 999):03d}",
                "capacity": random.choice([25, 30, 35, 40, 50, 60]),
                "schedule": schedule,
                "semester": random.choice(["Fall 2025", "Spring 2026"])
            })
        
        return courses
    
    def get_courses_for_student(self, student: Dict, courses: List[Dict]) -> List[Dict]:
        """
        Get appropriate courses for a student based on their study plan.
        Follows official ZC study plans by program and academic year.
        Includes semester-specific elective course selection (program + SCH electives).
        """
        program = student["program"]
        academic_year = student["academic_year"]
        is_graduate = student["student_type"] in ["MSc", "PhD"]
        
        # Build lookup of available courses by course_id
        course_lookup = {c["course_id"]: c for c in courses}
        
        # For graduate students, select from their department's graduate courses
        if is_graduate:
            grad_courses = [c for c in courses if c["level"] == "Graduate" and 
                          (program.lower() in c["course_name"].lower() or 
                           c["department"] in ["AIE", "DSAI", "SW", "BMS", "NANENG", "REE", "CIE", "ENV"])]
            if len(grad_courses) < 2:
                grad_courses = [c for c in courses if c["level"] == "Graduate"]
            return random.sample(grad_courses, min(random.randint(2, 4), len(grad_courses))) if grad_courses else []
        
        # For undergraduates, use STUDY_PLANS
        if program not in STUDY_PLANS:
            # Fallback for programs not in study plan
            level_courses = [c for c in courses if 
                           (academic_year == 1 and c["level"] == "Freshman") or
                           (academic_year == 2 and c["level"] == "Sophomore") or
                           (academic_year == 3 and c["level"] == "Junior") or
                           (academic_year == 4 and c["level"] == "Senior")]
            if not level_courses:
                level_courses = courses
            return random.sample(level_courses, min(random.randint(4, 6), len(level_courses)))
        
        # Get student's study plan
        study_plan = STUDY_PLANS[program]
        year_key = f"year_{academic_year}"
        
        if year_key not in study_plan:
            # Fallback if year not defined
            return random.sample(courses, min(random.randint(4, 6), len(courses)))
        
        # Collect planned courses for this year (both semesters)
        planned_course_ids = []
        year_plan = study_plan[year_key]
        planned_course_ids.extend(year_plan.get("fall", []))
        planned_course_ids.extend(year_plan.get("spring", []))
        
        # Match planned courses with available courses
        selected_courses = []
        selected_course_ids = set()
        
        for course_id in planned_course_ids:
            # Try exact match first
            if course_id in course_lookup:
                selected_courses.append(course_lookup[course_id])
                selected_course_ids.add(course_id)
            else:
                # Try to find a course with similar code pattern
                dept_code = course_id.split()[0] if " " in course_id else course_id[:3]
                matching = [c for c in courses if c["department"] == dept_code]
                if matching:
                    available_matching = [c for c in matching if c["course_id"] not in selected_course_ids]
                    if available_matching:
                        course = random.choice(available_matching)
                        selected_courses.append(course)
                        selected_course_ids.add(course["course_id"])
        
        # Add semester-specific electives for Year 3 and Year 4 students
        if academic_year >= 3 and "electives" in study_plan:
            electives_info = study_plan["electives"]
            program_electives = electives_info.get("program", [])
            sch_electives = electives_info.get("sch", [])
            
            # Get semester-specific elective counts
            fall_prog_electives = year_plan.get("fall_program_electives", 0)
            spring_prog_electives = year_plan.get("spring_program_electives", 0)
            fall_sch_electives = year_plan.get("fall_sch_electives", 0)
            spring_sch_electives = year_plan.get("spring_sch_electives", 0)
            
            total_prog_electives = fall_prog_electives + spring_prog_electives
            total_sch_electives = fall_sch_electives + spring_sch_electives
            
            # Add program-specific electives
            if total_prog_electives > 0:
                available_prog_electives = [
                    course_lookup[e_id] for e_id in program_electives 
                    if e_id in course_lookup and e_id not in selected_course_ids
                ]
                if available_prog_electives:
                    num_to_select = min(total_prog_electives, len(available_prog_electives))
                    chosen_prog = random.sample(available_prog_electives, num_to_select)
                    for c in chosen_prog:
                        selected_courses.append(c)
                        selected_course_ids.add(c["course_id"])
            
            # Add SCH (humanities/general education) electives
            if total_sch_electives > 0:
                available_sch_electives = [
                    course_lookup[e_id] for e_id in sch_electives 
                    if e_id in course_lookup and e_id not in selected_course_ids
                ]
                if available_sch_electives:
                    num_to_select = min(total_sch_electives, len(available_sch_electives))
                    chosen_sch = random.sample(available_sch_electives, num_to_select)
                    for c in chosen_sch:
                        selected_courses.append(c)
                        selected_course_ids.add(c["course_id"])
        
        # If we found enough courses from the study plan, use them
        if len(selected_courses) >= 4:
            # Limit to 4-8 courses (higher for years with electives)
            max_courses = 8 if academic_year >= 3 else 6
            num_courses = min(random.randint(5, max_courses), len(selected_courses))
            return random.sample(selected_courses, num_courses)
        
        # Supplement with level-appropriate courses if needed
        level_map = {1: "Freshman", 2: "Sophomore", 3: "Junior", 4: "Senior"}
        target_level = level_map.get(academic_year, "Freshman")
        level_courses = [c for c in courses if c["level"] == target_level and c["course_id"] not in selected_course_ids]
        
        while len(selected_courses) < 5 and level_courses:
            course = random.choice(level_courses)
            selected_courses.append(course)
            selected_course_ids.add(course["course_id"])
            level_courses.remove(course)
        
        return selected_courses
    
    def generate_registrations(self, students: List[Dict], courses: List[Dict]) -> List[Dict]:
        """
        Generate registrations following official ZC study plans.
        Each student is registered for courses appropriate to their major and year.
        """
        registrations = []
        reg_counter = 1
        
        for student in students:
            # Get courses based on student's study plan
            selected_courses = self.get_courses_for_student(student, courses)
            
            # If no courses found, fallback to random selection
            if not selected_courses:
                num_courses = random.randint(2, 4) if student["student_type"] in ["MSc", "PhD"] else random.randint(4, 6)
                selected_courses = random.sample(courses, min(num_courses, len(courses)))
            
            for course in selected_courses:
                reg_date = datetime(2025, 8, random.randint(20, 31))
                status = random.choices(["Enrolled", "Completed", "Dropped", "Waitlisted"], weights=[40, 45, 10, 5])[0]
                
                if status == "Completed":
                    grade = random.choices(["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"], weights=[18, 15, 15, 15, 10, 10, 8, 5, 3, 1])[0]
                elif status == "Enrolled":
                    grade = "IP"
                elif status == "Dropped":
                    grade = "W"
                else:
                    grade = ""
                
                registrations.append({
                    "registration_id": f"REG2025{reg_counter:05d}",
                    "student_id": student["student_id"],
                    "course_id": course["course_id"],
                    "semester": course["semester"],
                    "registration_date": reg_date.strftime("%Y-%m-%d"),
                    "status": status,
                    "grade": grade
                })
                reg_counter += 1
        
        return registrations
    
    def generate_admission_applications(self, count: int) -> List[Dict]:
        applications = []
        programs = list(self.structure["undergraduate_programs"].keys())
        
        for i in range(count):
            gender = random.choice(["Male", "Female"])
            first_name = random.choice(self.MALE_NAMES if gender == "Male" else self.FEMALE_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            program = random.choice(programs)
            program_info = self.structure["undergraduate_programs"][program]
            hs_gpa = round(random.uniform(70.0, 99.5), 1)
            
            if hs_gpa >= 95:
                status_weights = [10, 15, 60, 5, 10]
            elif hs_gpa >= 90:
                status_weights = [20, 25, 35, 10, 10]
            elif hs_gpa >= 85:
                status_weights = [25, 30, 15, 20, 10]
            else:
                status_weights = [15, 20, 5, 50, 10]
            
            status = random.choices(["Pending", "Under Review", "Approved", "Rejected", "Waitlisted"], weights=status_weights)[0]
            
            applications.append({
                "application_id": f"APP2025{i+1:05d}",
                "applicant_name": f"{first_name} {last_name}",
                "email": f"{first_name.lower()}.{last_name.lower()}@gmail.com",
                "phone": f"+20{random.choice(['10', '11', '12', '15'])}{random.randint(10000000, 99999999)}",
                "high_school_gpa": hs_gpa,
                "program_applied": program,
                "school": program_info["school"],
                "application_status": status,
                "application_date": datetime(2025, random.randint(5, 8), random.randint(1, 28)).strftime("%Y-%m-%d"),
                "review_notes": "" if status == "Pending" else f"Application reviewed for {program}"
            })
        
        return applications
    
    def generate_petitions(self, students: List[Dict], count: int) -> List[Dict]:
        petitions = []
        petition_types = [
            "Course Overload", "Schedule Conflict", "Late Registration", "Course Drop",
            "Gap Year Request", "Grade Appeal", "Prerequisite Waiver", "Credit Transfer",
            "Program Change", "Minor Addition", "Thesis Extension", "Leave of Absence"
        ]
        
        for i in range(count):
            student = random.choice(students)
            petition_type = random.choice(petition_types)
            status = random.choices(["Pending", "Under Review", "Approved", "Denied"], weights=[30, 25, 35, 10])[0]
            
            petitions.append({
                "petition_id": f"PET2025{i+1:05d}",
                "student_id": student["student_id"],
                "petition_type": petition_type,
                "description": f"Student requests {petition_type.lower()} for academic year 2025-2026.",
                "status": status,
                "submitted_date": datetime(2025, random.randint(8, 12), random.randint(1, 28)).strftime("%Y-%m-%d"),
                "reviewed_by": f"Dr. {random.choice(self.MALE_NAMES)} {random.choice(self.LAST_NAMES)}" if status != "Pending" else "Pending Review",
                "resolution_notes": "" if status == "Pending" else f"{petition_type} request {status.lower()}."
            })
        
        return petitions


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def save_to_json(data: List[Dict], filename: str):
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(data)} records to {filepath}")

def save_to_csv(data: List[Dict], filename: str):
    if not data:
        return
    filepath = OUTPUT_DIR / filename
    flat_data = []
    for record in data:
        flat_record = {}
        for key, value in record.items():
            if isinstance(value, list):
                flat_record[key] = "; ".join(str(v) for v in value)
            else:
                flat_record[key] = value
        flat_data.append(flat_record)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
        writer.writeheader()
        writer.writerows(flat_data)
    print(f"✅ Saved {len(data)} records to {filepath}")

def save_structure_reference(filename: str = "zewail_city_structure.json"):
    filepath = OUTPUT_DIR / filename
    # Merge structure with handbook references
    full_structure = {**ZEWAIL_CITY_STRUCTURE, "handbooks": HANDBOOK_REFERENCES}
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(full_structure, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved Zewail City structure to {filepath}")

def save_course_catalog(filename: str = "zewail_city_course_catalog.json"):
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(COURSE_CATALOG, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved course catalog ({sum(len(c) for c in COURSE_CATALOG.values())} courses) to {filepath}")


# ============================================================
# MAIN EXECUTION
# ============================================================

def generate_with_rules(target_students: int = 1000):
    """Generate synthetic data using rule-based approach"""
    print("=" * 60)
    print("ZEWAIL CITY SYNTHETIC DATA GENERATOR")
    print("Based on https://www.zewailcity.edu.eg/")
    print("=" * 60)
    
    print("\n📁 Saving reference data...")
    save_structure_reference()
    save_course_catalog()
    
    generator = RuleBasedDataGenerator()
    
    print(f"\n📊 Generating {target_students} Students...")
    students = generator.generate_students(target_students)
    save_to_json(students, "rule_students.json")
    save_to_csv(students, "rule_students.csv")
    
    print("\n📚 Generating Courses from Catalog...")
    courses = generator.generate_courses()
    save_to_json(courses, "rule_courses.json")
    save_to_csv(courses, "rule_courses.csv")
    
    print("\n📝 Generating Registrations...")
    registrations = generator.generate_registrations(students, courses)
    save_to_json(registrations, "rule_registrations.json")
    save_to_csv(registrations, "rule_registrations.csv")
    
    print("\n📋 Generating Admission Applications...")
    applications = generator.generate_admission_applications(int(target_students * 0.5))
    save_to_json(applications, "rule_applications.json")
    save_to_csv(applications, "rule_applications.csv")
    
    print("\n📄 Generating Petitions...")
    petitions = generator.generate_petitions(students, int(target_students * 0.2))
    save_to_json(petitions, "rule_petitions.json")
    save_to_csv(petitions, "rule_petitions.csv")
    
    print("\n" + "=" * 60)
    print("✅ Generation complete!")
    print("=" * 60)
    print(f"   📊 Students: {len(students)}")
    print(f"   📚 Courses: {len(courses)}")
    print(f"   📝 Registrations: {len(registrations)}")
    print(f"   📋 Applications: {len(applications)}")
    print(f"   📄 Petitions: {len(petitions)}")
    print("=" * 60)
    
    return {
        "students": students,
        "courses": courses,
        "registrations": registrations,
        "applications": applications,
        "petitions": petitions
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic data for Zewail City Educational ERP")
    parser.add_argument("--students", type=int, default=1000, help="Number of students to generate")
    
    args = parser.parse_args()
    generate_with_rules(args.students)
