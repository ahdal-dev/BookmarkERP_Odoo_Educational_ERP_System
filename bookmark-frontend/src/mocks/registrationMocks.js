/* ============================================================
   MOCK DATA — Registration courses
   ============================================================ */

export const mockCourses = [
  {
    id: 1, code: 'CSAI 101', title: 'Intro to AI', credits: 2, type: 'LECTURE',
    instructor: 'Prof. Khalil', schedule: 'M/W 10:00 AM - 11:30 AM',
    seats: '45 / 50 Available', status: 'Open', department: 'Computer Science',
  },
  {
    id: 2, code: 'MATH 201', title: 'Linear Algebra', credits: 3, type: 'LECTURE',
    instructor: 'Prof. Rahman', schedule: 'T/Th 1:00 PM - 2:30 PM',
    seats: '28 / 30 Available', status: 'Open', department: 'Mathematics',
  },
  {
    id: 3, code: 'ENG 105', title: 'Tech Communication', credits: 3, type: 'LECTURE',
    instructor: 'Prof. Nasser', schedule: 'T/Th 11:00 AM - 12:30 PM',
    seats: '30 / 30 (Waitlist: 4)', status: 'Waitlist', department: 'English',
  },
  {
    id: 4, code: 'PHYS 101', title: 'General Physics I', credits: 4, type: 'LECTURE',
    instructor: 'Prof. Saleh', schedule: 'M/W/F 9:00 AM - 10:30 AM',
    seats: '80 / 100', status: 'Open', department: 'Physics',
  },
  {
    id: 5, code: 'HIST 210', title: 'Modern World History', credits: 3, type: 'LECTURE',
    instructor: 'Prof. Zayed', schedule: 'M/W 2:00 PM - 3:30 PM',
    seats: '12 / 25', status: 'Open', department: 'History',
  },
  {
    id: 6, code: 'CS 212', title: 'Data Structures', credits: 3, type: 'LECTURE',
    instructor: 'Prof. Hasan', schedule: 'T/Th 4:00 PM - 5:30 PM',
    seats: '40 / 40', status: 'Closed', department: 'Computer Science',
  },
  {
    id: 7, code: 'BIO 101', title: 'Intro to Biology', credits: 3, type: 'LECTURE',
    instructor: 'Prof. Ahmad', schedule: 'M/W 8:00 AM - 9:30 AM',
    seats: '55 / 60', status: 'Open', department: 'Biology',
  },
  {
    id: 8, code: 'CHEM 201', title: 'Organic Chemistry', credits: 4, type: 'LAB',
    instructor: 'Prof. Farooq', schedule: 'T/Th 9:00 AM - 11:00 AM',
    seats: '25 / 25 (Waitlist: 2)', status: 'Waitlist', department: 'Chemistry',
  },
  {
    id: 9, code: 'ECON 101', title: 'Principles of Economics', credits: 3, type: 'LECTURE',
    instructor: 'Prof. Mansour', schedule: 'M/W/F 11:00 AM - 12:00 PM',
    seats: '90 / 120', status: 'Open', department: 'Economics',
  },
];

export const mockDepartments = [
  'All Departments', 'Computer Science', 'Mathematics', 'English', 'Physics',
  'History', 'Biology', 'Chemistry', 'Economics',
];

export const mockCredits = ['Any Credits', '2', '3', '4'];
