import PlaceholderView from '../_shared/PlaceholderView';

/* Shared faculty landing view for Instructor / Advisor / Chair.
   Renders role-specific widgets based on user.role.
   See docs/User_stories/Missing_Views_ToDo.md (Sections 4-6). */

export default function FacultyDashboardPage() {
  return (
    <PlaceholderView
      title="Faculty Dashboard"
      subtitle="Assigned courses, advisee cohorts, and the petition review queue will appear here — tailored to your faculty role."
      accent="#e8613a"
    />
  );
}
