# Educational ERP System - MVP Epics & User Stories

## [cite_start]Epic 01: Custom Odoo Admission Management Module

**Description:**
[cite_start]Transforms the traditional paper-based admission process into a modern, accessible online experience. [cite: 49] [cite_start]Students can explore available academic programs, complete their applications from anywhere at any time, and upload required documents digitally. [cite: 50] [cite_start]The system provides instant confirmation and a personalized reference number for tracking their application's progress. [cite: 51] [cite_start]For admission staff, It streamlines the review process by centralizing all applications in one place, making it easy to evaluate candidates, communicate decisions, and manage the entire admission pipeline. [cite: 52]

| User Story ID | User Story | Sprint Assignment |
| :--- | :--- | :--- |
| **US 01.01** | [cite_start]As a prospective student, I should be able to view all active admission programs online, so I can choose the right academic program before applying. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.02** | [cite_start]As a prospective student, I should be able to fill out an online admission form with my personal information, so I can submit my application without visiting the campus. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.03** | [cite_start]As a prospective student, I should be able to upload any document related to my eligibility ex (my academic transcript, Highschool diploma) as a PDF, so I can provide required documentation digitally. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.04** | [cite_start]As a prospective student, I should be able to upload scanned documents that are automatically processed via OCR, so I can avoid manual data entry and reduce errors. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.05** | [cite_start]As a prospective student, I should receive a unique reference number after submission, so I can track my application status later. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.06** | [cite_start]As a prospective student, I should be able to check my application status using my reference number, so I can stay informed about my admission progress. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.07** | [cite_start]As an admission officer, I should be able to view all submitted applications in Odoo backend, so I can review and process applications efficiently. [cite: 54] | [cite_start]Sprint 01 [cite: 54] |
| **US 01.08** | [cite_start]As an admission officer, I should be able to change application status with workflow buttons, so I can move applications through the admission pipeline. [cite: 54] | [cite_start]Sprint 02 [cite: 54] |
| **US 01.09** | [cite_start]As an admission officer, I should be able to download applicant documents, so I can review transcripts and supporting materials offline. [cite: 54] | [cite_start]Sprint 02 [cite: 54] |
| **US 01.10** | [cite_start]As a system administrator, I should be able to configure any custom Institution rules/admission requirements per program ex (I can enforce minimum GPA and prerequisites automatically). [cite: 54] | [cite_start]Sprint 02 [cite: 54] |
| **US 01.11** | [cite_start]As a student, I should receive a student account via email, so I can access the student portal after being accepted... [cite: 54] | [cite_start]Sprint 02 [cite: 54] |

---

## [cite_start]Epic 02: Custom Odoo Secure Authentication & Authorization Module [cite: 56]

**Description:**
[cite_start]Establish a robust security foundation that protects student data while providing appropriate access to different user groups. [cite: 58] [cite_start]That covers everything from initial account creation to daily login experiences and permission management. [cite: 59] [cite_start]Students receive secure accounts after acceptance, faculty members get tools to manage their classes, and administrators gain oversight capabilities. [cite: 60] [cite_start]The system ensures that everyone sees only what they're authorized to view, students access their own records, instructors manage their courses, and advisors view their advisees' information. [cite: 61]

| User Story ID | User Story | Sprint Assignment |
| :--- | :--- | :--- |
| **US 02.01** | [cite_start]As a user, I should be able to log in with my email and password, so I can access my role-specific dashboard. [cite: 62] | [cite_start]Sprint 02 [cite: 62] |
| **US 02.02** | [cite_start]As a user, I should be able to reset my password via email, so I can regain access if I forget my credentials. [cite: 62] | [cite_start]Sprint 02 [cite: 62] |
| **US 02.03** | [cite_start]As an administrator, I should be able to assign roles and permissions to users, so I can control access to sensitive ERP modules. [cite: 62] | [cite_start]Sprint 03 [cite: 62] |
| **US 02.04** | [cite_start]As a student, I should only see my own academic records, so I can ensure data privacy. [cite: 62] | [cite_start]Sprint 03 [cite: 62] |
| **US 02.05** | [cite_start]As a system, I should log all authentication events, so I can detect suspicious activity and ensure compliance. [cite: 62] | [cite_start]Sprint 03 [cite: 62] |

---

## [cite_start]Epic 03: Custom Odoo Petition Management System Module [cite: 63]

**Description:**
[cite_start]Digitize and accelerate the handling of student academic requests that fall outside normal procedures. [cite: 65] [cite_start]Whether a student needs to enroll in a full course, appeal a grade, or request a withdrawal, The system provides a structured online process that replaces email chains and paper forms. [cite: 66] [cite_start]Students submit their requests with supporting documentation, explaining their circumstances clearly. [cite: 67] [cite_start]The system intelligently routes each petition to the appropriate decision-makers based on the request type and institutional policies. [cite: 68] [cite_start]Instructors, advisors, and department chairs receive notifications and can review requests with full context about the student's academic history. [cite: 69] [cite_start]Students can track their petition's journey from submission to final decision. [cite: 70]

| User Story ID | User Story | Sprint Assignment |
| :--- | :--- | :--- |
| **US 03.01** | [cite_start]As a student, I should be able to submit a petition for any case outside normal procedures ex:(course enrollment override, submit a grade appeal petition), so I can request entry into a full/prerequisite-restricted course or request a review of a disputed grade. [cite: 72] | [cite_start]Sprint 03 [cite: 72] |
| **US 03.02** | [cite_start]As a student, I should be able to track the status of my petition, so I can know whether it's pending, approved, or rejected. [cite: 72] | [cite_start]Sprint 04 [cite: 72] |
| **US 03.03** | [cite_start]As an instructor, I should be able to review petitions for my courses, so I can approve or reject enrollment override requests. [cite: 72] | [cite_start]Sprint 04 [cite: 72] |
| **US 03.04** | [cite_start]As an advisor, I should automatically receive petitions requiring my approval in the workflow, so I can provide timely academic guidance. [cite: 72] | [cite_start]Sprint 04 [cite: 72] |
| **US 03.05** | [cite_start]As a department chair, I should be able to override any petition decision, so I can exercise final authority on academic exceptions. [cite: 72] | [cite_start]Sprint 04 [cite: 72] |
| **US 03.06** | [cite_start]As a system, I should route petitions to the correct approvers based on rules, so I can automate the approval chain without manual assignment. [cite: 72] | [cite_start]Sprint 04 [cite: 72] |

---

## [cite_start]Epic 04: Custom Odoo Registration Management Module [cite: 73]

**Description:**
[cite_start]Develop a high concurrency course enrollment system with transaction management, seat inventory control, template-based registration, and waitlist automation integrated with the course catalog. [cite: 75] [cite_start]Students can browse available courses, check seat availability in real-time, and build a wishlist of desired classes. [cite: 76] [cite_start]The system handles thousands of students registering simultaneously without crashes or double-bookings, and includes waitlist management so students don't lose opportunities when their preferred section fills up. [cite: 77]

| User Story ID | User Story | Sprint Assignment |
| :--- | :--- | :--- |
| **US 04.01** | [cite_start]As a student, I should be able to view available courses for the upcoming semester, so I can plan my schedule before registration opens. [cite: 78] | [cite_start]Sprint 05 [cite: 78] |
| **US 04.02** | [cite_start]As a student, I should be able to add courses to my cart before registration opens, so I can quickly enroll when my time slot begins. [cite: 78] | [cite_start]Sprint 05 [cite: 78] |
| **US 04.03** | [cite_start]As a student, I should be able to register for courses with real-time seat validation, so I can avoid enrollment in full sections. [cite: 80] | [cite_start]Sprint 05 [cite: 80] |
| **US 04.04** | [cite_start]As a student, I should be able to drop a course within the adddrop/ period, so I can adjust my schedule without penalties. [cite: 80] | [cite_start]Sprint 05 [cite: 80] |
| **US 04.05** | [cite_start]As a registrar, I should be able to configure registration time slots by student priority, so I can ensure seniors register before freshmen. [cite: 80] | [cite_start]Sprint 05 [cite: 80] |