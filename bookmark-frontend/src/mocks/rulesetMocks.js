/* ============================================================
   MOCK DATA — Institutional Ruleset
   ============================================================ */

export const mockRuleset = {
  autoEnroll: true,
  prerequisiteCheck: false,
  waitlistManagement: true,
  gpa: '3.5 / 4.0',
  applicationStatus: 'Active – Accepting Submissions',
  prerequisites: [
    { name: 'Calculus I', checked: true },
    { name: 'English Composition', checked: true },
    { name: 'Bio 101', checked: false },
  ],
  capacityPercent: 88,
  registrationWindows: [
    { tier: 'Tier 1', openDate: '5/17/23', closeDate: '12/17/23', capacity: 100, color: 'var(--color-lime)' },
    { tier: 'Tier 2', openDate: '6/29/23', closeDate: '10/29/23', capacity: 75, color: 'var(--color-yellow)' },
    { tier: 'Tier 3', openDate: '5/21/23', closeDate: '10/11/23', capacity: 100, color: 'var(--color-coral)' },
  ],
};
