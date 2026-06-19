/* ============================================================
   MOCK DATA — Faculty (instructor / advisor / chair)
   Shared across dashboard, roster, petition queue/review, chair board,
   advisee list/profile, and department records.
   ============================================================ */

export const assignedCourses = [
  { id: 'CSAI301', code: 'CSAI 301', name: 'Advanced Algorithms', schedule: 'M/W 10:00–11:30', room: 'B204', credits: 3, enrolled: 45, capacity: 50, waitlist: 3 },
  { id: 'CSAI220', code: 'CSAI 220', name: 'Data Structures', schedule: 'T/R 09:00–10:30', room: 'A110', credits: 3, enrolled: 50, capacity: 50, waitlist: 6 },
  { id: 'CSAI410', code: 'CSAI 410', name: 'Machine Learning', schedule: 'M/W 13:00–14:30', room: 'C301', credits: 4, enrolled: 32, capacity: 40, waitlist: 0 },
];

export const rosters = {
  CSAI301: [
    { sid: 'STU-2024-011', name: 'Aya Hassan', email: 'aya.hassan@zc.edu', date: 'Aug 28, 2026', status: 'Enrolled' },
    { sid: 'STU-2024-042', name: 'Omar Khaled', email: 'omar.khaled@zc.edu', date: 'Aug 28, 2026', status: 'Enrolled' },
    { sid: 'STU-2023-118', name: 'Lina Saad', email: 'lina.saad@zc.edu', date: 'Aug 29, 2026', status: 'Enrolled' },
    { sid: 'STU-2024-204', name: 'Marcus Thorne', email: 'marcus.t@zc.edu', date: 'Sep 02, 2026', status: 'Waitlisted' },
  ],
};

// Petitions awaiting faculty review. `tier` indicates current owner.
export const facultyPetitions = [
  {
    id: '9402', ref: '#9402', studentName: 'Julianne Devis', sid: 'STU-2023-118',
    type: 'Late Drop', date: 'Oct 12, 2026', urgency: 'Critical', tier: 'instructor',
    course: 'CSAI 301 — Advanced Algorithms', department: 'Computer Science',
    justification: 'Requesting a late course drop due to a documented medical emergency that prevented attendance for three consecutive weeks. Supporting clinic documentation attached.',
    snapshot: { gpa: 3.41, credits: 15, standing: 'Good Standing' },
    documents: [{ name: 'medical_note.pdf' }, { name: 'advisor_email.pdf' }],
    trail: [
      { color: 'var(--color-lime)', text: 'Submitted by student', actor: 'Oct 12, 2026' },
      { color: 'var(--color-coral)', text: 'Flagged Critical by system', actor: 'Oct 12, 2026' },
    ],
    priorDecisions: [],
  },
  {
    id: '9398', ref: '#9398', studentName: 'Marcus Thorne', sid: 'STU-2024-204',
    type: 'Prereq Override', date: 'Oct 11, 2026', urgency: 'Normal', tier: 'instructor',
    course: 'CSAI 410 — Machine Learning', department: 'Computer Science',
    justification: 'I completed an equivalent linear-algebra course at a partner institution and would like the prerequisite waived so I can enroll this term.',
    snapshot: { gpa: 3.78, credits: 12, standing: 'Good Standing' },
    documents: [{ name: 'transfer_transcript.pdf' }],
    trail: [{ color: 'var(--color-lime)', text: 'Submitted by student', actor: 'Oct 11, 2026' }],
    priorDecisions: [],
  },
  {
    id: '9395', ref: '#9395', studentName: 'Elena Lunt', sid: 'STU-2022-077',
    type: 'Course Overload', date: 'Oct 10, 2026', urgency: 'Low', tier: 'advisor',
    course: 'Multiple', department: 'Computer Science',
    justification: 'Requesting approval to register for 21 credit hours this term to stay on track for early graduation.',
    snapshot: { gpa: 3.92, credits: 18, standing: 'Good Standing' },
    documents: [],
    trail: [
      { color: 'var(--color-lime)', text: 'Submitted by student', actor: 'Oct 10, 2026' },
      { color: 'var(--color-lime)', text: 'Instructor approved', actor: 'Oct 11, 2026' },
    ],
    priorDecisions: [{ tier: 'Instructor', action: 'Approved', reason: 'Strong academic record.' }],
  },
];

// Escalated petitions for the chair board, keyed by lane.
export const chairPetitions = {
  Escalated: [
    { id: '9402', ref: '#9402', studentName: 'Julianne Devis', type: 'Late Drop', date: 'Oct 12', prior: 'Instructor: Rejected · Advisor: Rejected' },
  ],
  'Under Review': [
    { id: '9377', ref: '#9377', studentName: 'Sara Nabil', type: 'Grade Appeal', date: 'Oct 08', prior: 'Instructor: Rejected · Advisor: Escalated' },
  ],
  Overridden: [
    { id: '9350', ref: '#9350', studentName: 'Youssef Ali', type: 'Late Drop', date: 'Oct 02', prior: 'Chair: Overrode → Approved' },
  ],
  Closed: [
    { id: '9322', ref: '#9322', studentName: 'Nour Adel', type: 'Course Overload', date: 'Sep 26', prior: 'Approved at Advisor tier' },
  ],
};

export const advisees = [
  { sid: 'STU-2024-011', name: 'Aya Hassan', major: 'B.Sc. Computer Science', gpa: 3.72, petition: true },
  { sid: 'STU-2024-042', name: 'Omar Khaled', major: 'B.Sc. Computer Science', gpa: 2.41, petition: false },
  { sid: 'STU-2023-118', name: 'Lina Saad', major: 'B.Sc. Computer Science', gpa: 3.10, petition: true },
  { sid: 'STU-2022-077', name: 'Elena Lunt', major: 'B.Sc. Computer Science', gpa: 3.92, petition: false },
  { sid: 'STU-2024-204', name: 'Marcus Thorne', major: 'B.Sc. Data Science', gpa: 3.55, petition: false },
  { sid: 'STU-2023-090', name: 'Hana Fares', major: 'B.Sc. Computer Science', gpa: 2.18, petition: true },
];

export const deptStudents = [
  { sid: 'STU-2024-011', name: 'Aya Hassan', year: 'Sophomore', gpa: 3.72, credits: 45, standing: 'Good Standing', petitions: 1 },
  { sid: 'STU-2024-042', name: 'Omar Khaled', year: 'Sophomore', gpa: 2.41, credits: 42, standing: 'Probation', petitions: 0 },
  { sid: 'STU-2023-118', name: 'Lina Saad', year: 'Junior', gpa: 3.10, credits: 78, standing: 'Good Standing', petitions: 2 },
  { sid: 'STU-2022-077', name: 'Elena Lunt', year: 'Senior', gpa: 3.92, credits: 110, standing: 'Good Standing', petitions: 0 },
  { sid: 'STU-2023-090', name: 'Hana Fares', year: 'Junior', gpa: 2.18, credits: 70, standing: 'Suspension Risk', petitions: 1 },
];

export function gpaVariant(gpa) {
  if (gpa >= 3.5) return 'green';
  if (gpa >= 2.5) return 'yellow';
  return 'coral';
}

export const URGENCY_VARIANT = { Critical: 'coral', Normal: 'green', Low: 'yellow' };
