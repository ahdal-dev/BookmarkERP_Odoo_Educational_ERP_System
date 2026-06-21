# Database Entity-Relationship Diagram

Bookmark Academic ERP uses Odoo's PostgreSQL schema extended by three custom modules:
`edu_mang_academic`, `edu_mang_notification`, and `edu_mang_waitlist`.

## Core Entity Relationships

```mermaid
erDiagram
    RES_USERS {
        int id PK
        string name
        string email
        string login
        float cumulative_gpa
        int earned_credits
        string class_year
        string academic_standing
    }

    EDUCATION_PROGRAM {
        int id PK
        string name
        string code
        int duration
        bool active
        int admission_count
    }

    EDUCATION_COURSE {
        int id PK
        string name
        string code
        int capacity
        int enrolled_count
        int waitlist_count
        date registration_start
        date registration_end
        int program_id FK
    }

    EDUCATION_REGISTRATION {
        int id PK
        int student_id FK
        int course_id FK
        string state
        date registration_date
        string grade
        float grade_points
        bool on_hold
    }

    EDUCATION_REGISTRATION_TIER {
        int id PK
        string name
        string class_year
        datetime window_start
        datetime window_end
        int priority
    }

    EDU_NOTIFICATION {
        int id PK
        int user_id FK
        string title
        string message
        string notification_type
        bool is_read
        datetime created_at
    }

    ADMISSION_APPLICATION {
        int id PK
        string reference
        string applicant_name
        string email
        string state
        int program_id FK
        datetime submitted_at
    }

    EDUCATION_PETITION {
        int id PK
        int student_id FK
        int course_id FK
        string petition_type
        string state
        string reason
        datetime created_at
    }

    RES_USERS ||--o{ EDUCATION_REGISTRATION : "enrolls in"
    RES_USERS ||--o{ EDU_NOTIFICATION : "receives"
    RES_USERS ||--o{ EDUCATION_PETITION : "submits"
    EDUCATION_COURSE ||--o{ EDUCATION_REGISTRATION : "has registrations"
    EDUCATION_COURSE ||--o{ EDUCATION_PETITION : "referenced in"
    EDUCATION_COURSE }o--o{ EDUCATION_COURSE : "has prerequisites"
    EDUCATION_PROGRAM ||--o{ EDUCATION_COURSE : "contains"
    EDUCATION_PROGRAM ||--o{ ADMISSION_APPLICATION : "applied to"
```

## Redis Data Structures

| Key Pattern | Type | Purpose |
|---|---|---|
| `token:blocklist:{jti}` | String (TTL) | Revoked JWT tokens |
| `active_session:{uid}:{jti}` | String (TTL) | Active session tracking for concurrent user count |
| `rate_limit:*` | String | SlowAPI rate limit counters |

## Custom Module Summary

| Module | Models Added | Purpose |
|---|---|---|
| `edu_mang_academic` | grade/grade_points on Registration; GPA/credits/standing on Users; Registration Tier | Grades, GPA computation, seniority-based registration windows, prerequisite enforcement |
| `edu_mang_notification` | edu.notification | In-app notifications on admission/registration/petition events |
| `edu_mang_waitlist` | (extends education.registration) | FIFO waitlist promotion, auto-notification on promotion |
