/* ============================================================
   MOCK DATA — Admissions pipeline
   ============================================================ */

export const mockAdmissions = {
  columns: [
    {
      id: 'new', title: 'NEW APPLICATION', color: 'var(--color-lime)',
      cards: [
        { id: 'a1', name: 'Julianne Abernathy', ref: 'ADM-2024-0012', program: 'M.S. Architecture', starred: false, accentColor: 'var(--color-lime)' },
        { id: 'a2', name: 'Xavier Thorne', ref: 'ADM-2024-0015', program: 'B.A. Philosophy', starred: false, accentColor: 'var(--color-lime)' },
      ],
    },
    {
      id: 'missing', title: 'MISSING DOCUMENTS', color: 'var(--color-coral)',
      cards: [
        { id: 'a3', name: 'Elias Vance', ref: 'ADM-2024-0018', program: 'Ph.D. Economics', warning: 'Missing: Official Transcript', accentColor: 'var(--color-coral)' },
      ],
    },
    {
      id: 'review', title: 'IN REVIEW', color: 'var(--color-yellow)',
      cards: [
        { id: 'a4', name: 'Clara Nightingale', ref: 'ADM-2024-0020', program: 'LL.M. Global Law', avatars: [{ name: 'Rev A', initial: 'A' }, { name: 'Rev B', initial: 'B' }], accentColor: 'var(--color-yellow)' },
      ],
    },
    {
      id: 'accepted', title: 'ACCEPTED', color: 'var(--color-lime)',
      cards: [],
    },
  ],
};
