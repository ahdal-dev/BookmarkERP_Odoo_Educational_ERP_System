/* ============================================================
   MOCK DATA — Petitions (student + admin)
   ============================================================ */

export const mockPetitionTypes = [
  'Late Course Drop',
  'Exam Reschedule',
  'Credit Transfer',
  'Grade Appeal',
  'Leave of Absence',
];

export const mockStatusHistory = [
  { id: 1, status: 'In Review', name: 'Course Overload Request', date: '06/11/2023', description: 'Requesting approval for 21 credit hours' },
  { id: 2, status: 'Completed', name: 'Exam Reschedule', date: '06/11/2023', description: 'Medical emergency rescheduling approved' },
  { id: 3, status: 'Denied', name: 'Late Withdrawal', date: '06/11/2023', description: 'Past deadline for late course withdrawal' },
];

export const mockRecentPetitions = [
  { id: 1, status: 'Approved', title: 'Student Petition', date: '2 days ago' },
  { id: 2, status: 'Pending', title: 'Pending Petition', date: '5 days ago' },
  { id: 3, status: 'Denied', title: 'Petition Appeal', date: '1 week ago' },
];

// Admin tracking data
export const mockPetitionsAdmin = [
  {
    id: 9402, ref: '#9402', studentName: 'Julianne Devis',
    type: 'Late Course Drop', date: 'Oct 12', urgency: 'Critical',
    urgencyColor: 'coral', accentColor: 'var(--color-coral)',
    detail: {
      title: 'Late Course Drop Request',
      department: 'Department of Accounting',
      justification: '"Late course drop request due to unforeseen personal circumstances that have significantly impacted my ability to maintain academic performance in this course. I have documentation supporting my request and have spoken with my academic advisor."',
      attachment: { name: 'Julianne_Devis_transcript.pdf', type: 'PDF' },
      activity: [
        { color: 'var(--color-lime)', text: 'Initial review completed', actor: 'Julianne Devis' },
        { color: 'var(--color-coral)', text: 'Flagged for department review', actor: 'System' },
        { color: 'var(--color-coral)', text: 'Critical priority assigned', actor: 'Registrar' },
      ],
    },
  },
  {
    id: 9398, ref: '#9398', studentName: 'Marcus Thorne',
    type: 'Exam Reschedule', date: 'Oct 11', urgency: 'Normal',
    urgencyColor: 'green', accentColor: 'var(--color-lime)',
    detail: {
      title: 'Exam Reschedule Request',
      department: 'Department of Engineering',
      justification: '"Requesting exam reschedule due to a scheduling conflict with a mandatory professional certification exam."',
      attachment: { name: 'Marcus_Thorne_schedule.pdf', type: 'PDF' },
      activity: [
        { color: 'var(--color-lime)', text: 'Request submitted', actor: 'Marcus Thorne' },
      ],
    },
  },
  {
    id: 9395, ref: '#9395', studentName: 'Elena Lunt',
    type: 'Credit Transfer', date: 'Oct 10', urgency: 'Low',
    urgencyColor: 'yellow', accentColor: 'var(--color-yellow)',
    detail: {
      title: 'Credit Transfer Request',
      department: 'Department of Liberal Arts',
      justification: '"Requesting transfer of 6 credits from an accredited international institution."',
      attachment: { name: 'Elena_Lunt_transcript.pdf', type: 'PDF' },
      activity: [
        { color: 'var(--color-lime)', text: 'Documents received', actor: 'System' },
      ],
    },
  },
];
