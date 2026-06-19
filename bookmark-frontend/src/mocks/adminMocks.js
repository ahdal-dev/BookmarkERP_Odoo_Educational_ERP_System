// Mock data for all admin dashboard pages — no live API calls needed

export const mockCommandKPIs = {
  totalUsers: '12,482',
  totalUsersDelta: '+3% from last month',
  activeToday: '3,109',
  activeTodayPct: '88% of capacity',
  aiRequests: '8,741',
  aiRequestsDelta: '+12% this week',
  openTickets: 23,
  criticalTickets: 3,
  systemUptime: '99.94',
  securityScore: 94,
};

export const mockAIServiceSummary = [
  { name: 'OCR Service', slug: 'ocr', status: 'Online', uptime: '99.8', requests: 847 },
  { name: 'Grade Prediction', slug: 'grade-pred', status: 'Online', uptime: '99.9', requests: 312 },
  { name: 'RAG Chatbot', slug: 'chatbot', status: 'Degraded', uptime: '97.2', requests: 2100 },
  { name: 'Embedding Engine', slug: 'embedding', status: 'Online', uptime: '99.9', requests: 541 },
];

export const mockRecentSecurityEvents = [
  { id: 1, severity: 'high', message: '3 failed login attempts on admin@bookmark.edu', time: '12 min ago' },
  { id: 2, severity: 'medium', message: 'Permission change — Registrar role modified', time: '1h ago' },
  { id: 3, severity: 'low', message: 'New API key issued for OCR Integration', time: '3h ago' },
  { id: 4, severity: 'low', message: '14 idle admin sessions auto-terminated', time: '8h ago' },
];

export const mockAdmissionSummary = {
  newApplications: 47,
  inReview: 23,
  missingDocs: 11,
  approvedToday: 8,
};

export const mockUserGrowth = [
  { label: 'Jan', value: 9800 }, { label: 'Feb', value: 10200 },
  { label: 'Mar', value: 10800 }, { label: 'Apr', value: 11100 },
  { label: 'May', value: 11600 }, { label: 'Jun', value: 12482 },
];

// Roles & Permissions

export const mockRoles = [
  { id: 1, name: 'Super Admin', slug: 'super_admin', userCount: 2, accessLevel: 'Full Access', color: 'coral', description: 'Unrestricted access to all system modules and settings.' },
  { id: 2, name: 'Admin', slug: 'admin', userCount: 8, accessLevel: 'High Access', color: 'lime', description: 'Manage users, AI services, and operational settings.' },
  { id: 3, name: 'Registrar', slug: 'registrar', userCount: 14, accessLevel: 'Mid Access', color: 'black', description: 'Manage student records, courses, and registration windows.' },
  { id: 4, name: 'Instructor', slug: 'instructor', userCount: 312, accessLevel: 'Scoped', color: 'green', description: 'View and grade own courses. Read-only access to student info.' },
  { id: 5, name: 'Student', slug: 'student', userCount: 11890, accessLevel: 'Limited', color: 'yellow', description: 'Self-service portal: grades, registration, petitions, chatbot.' },
  { id: 6, name: 'Admission Officer', slug: 'admission_officer', userCount: 18, accessLevel: 'Mid Access', color: 'black', description: 'Review and process student applications and documents.' },
];

export const mockPermissionMatrix = [
  { module: 'User Management', superAdmin: 'RW', admin: 'RW', registrar: 'R', instructor: '—', student: '—' },
  { module: 'Role Management', superAdmin: 'RW', admin: 'RW', registrar: '—', instructor: '—', student: '—' },
  { module: 'AI Services Config', superAdmin: 'RW', admin: 'RW', registrar: '—', instructor: '—', student: '—' },
  { module: 'AI Stats View', superAdmin: 'RW', admin: 'RW', registrar: '—', instructor: 'R', student: '—' },
  { module: 'Knowledge Base', superAdmin: 'RW', admin: 'RW', registrar: 'R', instructor: '—', student: '—' },
  { module: 'Analytics (Full)', superAdmin: 'RW', admin: 'RW', registrar: '—', instructor: '—', student: '—' },
  { module: 'Security Center', superAdmin: 'RW', admin: 'RW', registrar: '—', instructor: '—', student: '—' },
  { module: 'API Keys', superAdmin: 'RW', admin: 'RW', registrar: '—', instructor: '—', student: '—' },
  { module: 'Course Management', superAdmin: 'RW', admin: 'RW', registrar: 'RW', instructor: 'R', student: 'R' },
  { module: 'Grade Management', superAdmin: 'RW', admin: 'RW', registrar: 'RW', instructor: 'RW*', student: 'R*' },
  { module: 'Petitions Review', superAdmin: 'RW', admin: 'RW', registrar: 'RW', instructor: '—', student: 'Sub' },
  { module: 'Admissions', superAdmin: 'RW', admin: 'RW', registrar: 'RW', instructor: '—', student: '—' },
  { module: 'Feature Flags', superAdmin: 'RW', admin: 'R', registrar: '—', instructor: '—', student: '—' },
  { module: 'System Settings', superAdmin: 'RW', admin: 'R', registrar: '—', instructor: '—', student: '—' },
  { module: 'Backups', superAdmin: 'RW', admin: 'R', registrar: '—', instructor: '—', student: '—' },
];

// AI Services

export const mockAIServices = [
  {
    id: 1, name: 'OCR Engine', slug: 'ocr', type: 'OCR',
    endpoint: 'http://ocr-service:8001/api/v1', modelVersion: 'tesseract-4.1 / custom-v3',
    status: 'Online', isEnabled: true, uptime: 99.8, avgLatency: 1.2,
    p99Latency: 4.1, requestsToday: 847, successRate: 94.2, errorRate: 2.1,
    tokensConsumed: 0, lastError: 'LOW_CONFIDENCE — scan_0041.jpg (conf: 0.61)',
  },
  {
    id: 2, name: 'Grade Prediction', slug: 'grade-pred', type: 'Prediction',
    endpoint: 'http://grade-pred:8002/api/v1', modelVersion: 'xgboost-v2.3.1',
    status: 'Online', isEnabled: true, uptime: 99.9, avgLatency: 0.89,
    p99Latency: 2.1, requestsToday: 312, successRate: 99.8, errorRate: 0.2,
    tokensConsumed: 0, lastError: null,
  },
  {
    id: 3, name: 'RAG Chatbot', slug: 'chatbot', type: 'RAG',
    endpoint: 'http://rag-service:8003/api/v1', modelVersion: 'llm-mistral-7b',
    status: 'Degraded', isEnabled: true, uptime: 97.2, avgLatency: 3.8,
    p99Latency: 12.0, requestsToday: 2100, successRate: 94.8, errorRate: 5.2,
    tokensConsumed: 1240000, lastError: 'TIMEOUT — req-8812 (12.4s > SLA 10s)',
  },
  {
    id: 4, name: 'Embedding Engine', slug: 'embedding', type: 'Embedding',
    endpoint: 'http://embed-service:8004/api/v1', modelVersion: 'sentence-transformers-v2',
    status: 'Online', isEnabled: true, uptime: 99.9, avgLatency: 0.24,
    p99Latency: 0.8, requestsToday: 541, successRate: 99.9, errorRate: 0.1,
    tokensConsumed: 0, lastError: null,
  },
];

export const mockAIErrorLogs = [
  { time: '09:41:12', code: 'FILE_TOO_LARGE', service: 'OCR', detail: 'student_transcript_v2.pdf (12MB)' },
  { time: '09:38:44', code: 'LOW_CONFIDENCE', service: 'OCR', detail: 'scan_0041.jpg  confidence: 0.61' },
  { time: '09:12:01', code: 'TIMEOUT', service: 'RAG Chatbot', detail: 'req-8812 elapsed: 12.4s' },
  { time: '08:55:33', code: 'TIMEOUT', service: 'RAG Chatbot', detail: 'req-8790 elapsed: 11.1s' },
  { time: '07:22:18', code: 'MODEL_ERROR', service: 'Grade Prediction', detail: 'Missing feature: prev_gpa' },
];

// Knowledge Base

export const mockKBStats = {
  totalDocs: 1482,
  indexed: 1447,
  indexedPct: 97,
  pending: 35,
  avgTopK: 3,
  retrievalRelevance: 94,
  coverage: 88.4,
};

export const mockKBCollections = [
  { id: 1, name: 'All Documents', count: 1482 },
  { id: 2, name: 'Admission Policies', count: 87 },
  { id: 3, name: 'Academic Regulations', count: 234 },
  { id: 4, name: 'Course Catalogs', count: 412 },
  { id: 5, name: 'FAQs', count: 198 },
  { id: 6, name: 'Faculty Handbooks', count: 91 },
  { id: 7, name: 'Uncategorized', count: 460 },
];

export const mockKBDocuments = [
  { id: 1, name: 'Admission Policy 2024-25.pdf', collection: 'Admission Policies', status: 'Indexed', size: '1.2 MB', uploadedBy: 'admin@bookmark.edu', indexedAt: 'Jun 10, 2024', chunks: 48 },
  { id: 2, name: 'CS Program Requirements.pdf', collection: 'Course Catalogs', status: 'Indexed', size: '3.4 MB', uploadedBy: 'registrar@bookmark.edu', indexedAt: 'Jun 8, 2024', chunks: 112 },
  { id: 3, name: 'Financial Aid Handbook 2024.pdf', collection: 'Uncategorized', status: 'Pending', size: '2.1 MB', uploadedBy: 'admin@bookmark.edu', indexedAt: '—', chunks: 0 },
  { id: 4, name: 'FAQ - Registration Process.docx', collection: 'FAQs', status: 'Indexed', size: '0.4 MB', uploadedBy: 'admin@bookmark.edu', indexedAt: 'Jun 5, 2024', chunks: 22 },
  { id: 5, name: 'Academic Integrity Policy.pdf', collection: 'Academic Regulations', status: 'Indexed', size: '0.8 MB', uploadedBy: 'registrar@bookmark.edu', indexedAt: 'May 28, 2024', chunks: 31 },
  { id: 6, name: 'Scholarship Requirements 2025.pdf', collection: 'Admission Policies', status: 'Failed', size: '1.9 MB', uploadedBy: 'admin@bookmark.edu', indexedAt: '—', chunks: 0 },
];

// Analytics

export const mockAnalyticsKPIs = {
  totalUsers: { value: '12,482', delta: '+3%', trend: 'up' },
  activeUsers: { value: '3,109', delta: '+8%', trend: 'up' },
  newRegistrations: { value: '284', delta: '+14%', trend: 'up' },
  ocrRequests: { value: '847', delta: '-2%', trend: 'down' },
  ocrSuccessRate: { value: '94.2%', delta: '+0.8%', trend: 'up' },
  chatbotSessions: { value: '2,100', delta: '+18%', trend: 'up' },
  applicationsSubmitted: { value: '47', delta: '+5', trend: 'up' },
  applicationsApproved: { value: '8', delta: '', trend: 'neutral' },
  avgProcessingTime: { value: '3.2 days', delta: '-0.4d', trend: 'up' },
  apiRequests: { value: '1.24M', delta: '+9%', trend: 'up' },
  systemUptime: { value: '99.94%', delta: '', trend: 'neutral' },
  errorRate: { value: '0.8%', delta: '-0.2%', trend: 'up' },
  avgResponseTime: { value: '248ms', delta: '-12ms', trend: 'up' },
};

export const mockAnalyticsByPeriod = {
  '24h': {
    totalUsers: { value: '12,482', delta: 'Live count', trend: 'up' },
    activeUsers: { value: '1,847', delta: 'Right now', trend: 'up' },
    newRegistrations: { value: '7', delta: '+7 today', trend: 'up' },
    applicationsSubmitted: { value: '14', delta: 'Today', trend: 'up' },
    applicationsApproved: { value: '3', delta: '', trend: 'neutral' },
    avgProcessingTime: { value: '3.2 days', delta: '', trend: 'neutral' },
    apiRequests: { value: '18.2K', delta: 'Last 24h', trend: 'up' },
    systemUptime: { value: '100%', delta: '24h window', trend: 'up' },
    errorRate: { value: '0.4%', delta: 'Today', trend: 'up' },
    avgResponseTime: { value: '231ms', delta: '', trend: 'up' },
    ocrRequests: { value: '84', delta: 'Today', trend: 'up' },
    ocrSuccessRate: { value: '96.4%', delta: '+2.2%', trend: 'up' },
    chatbotSessions: { value: '142', delta: 'Today', trend: 'up' },
  },
  '7d': {
    totalUsers: { value: '12,482', delta: '+94 this week', trend: 'up' },
    activeUsers: { value: '4,213', delta: '+12%', trend: 'up' },
    newRegistrations: { value: '94', delta: '+8%', trend: 'up' },
    applicationsSubmitted: { value: '231', delta: '+15%', trend: 'up' },
    applicationsApproved: { value: '42', delta: '+5', trend: 'up' },
    avgProcessingTime: { value: '3.1 days', delta: '-0.1d', trend: 'up' },
    apiRequests: { value: '124K', delta: '+11%', trend: 'up' },
    systemUptime: { value: '99.7%', delta: '7d avg', trend: 'up' },
    errorRate: { value: '1.2%', delta: '+0.4%', trend: 'down' },
    avgResponseTime: { value: '271ms', delta: '+23ms', trend: 'down' },
    ocrRequests: { value: '412', delta: '+6%', trend: 'up' },
    ocrSuccessRate: { value: '93.8%', delta: '-0.4%', trend: 'down' },
    chatbotSessions: { value: '890', delta: '+14%', trend: 'up' },
  },
  '30d': {
    totalUsers: { value: '12,482', delta: '+3%', trend: 'up' },
    activeUsers: { value: '3,109', delta: '+8%', trend: 'up' },
    newRegistrations: { value: '284', delta: '+14%', trend: 'up' },
    applicationsSubmitted: { value: '847', delta: '+5%', trend: 'up' },
    applicationsApproved: { value: '156', delta: '+12', trend: 'up' },
    avgProcessingTime: { value: '3.2 days', delta: '-0.4d', trend: 'up' },
    apiRequests: { value: '1.24M', delta: '+9%', trend: 'up' },
    systemUptime: { value: '99.94%', delta: '30d avg', trend: 'up' },
    errorRate: { value: '0.8%', delta: '-0.2%', trend: 'up' },
    avgResponseTime: { value: '248ms', delta: '-12ms', trend: 'up' },
    ocrRequests: { value: '847', delta: '-2%', trend: 'down' },
    ocrSuccessRate: { value: '94.2%', delta: '+0.8%', trend: 'up' },
    chatbotSessions: { value: '2,100', delta: '+18%', trend: 'up' },
  },
  '90d': {
    totalUsers: { value: '12,482', delta: '+1,240 in 90d', trend: 'up' },
    activeUsers: { value: '6,891', delta: '+22%', trend: 'up' },
    newRegistrations: { value: '1,240', delta: '+18%', trend: 'up' },
    applicationsSubmitted: { value: '3,420', delta: '+22%', trend: 'up' },
    applicationsApproved: { value: '612', delta: '+8%', trend: 'up' },
    avgProcessingTime: { value: '3.4 days', delta: '+0.2d', trend: 'down' },
    apiRequests: { value: '4.8M', delta: '+31%', trend: 'up' },
    systemUptime: { value: '99.6%', delta: '90d avg', trend: 'up' },
    errorRate: { value: '1.4%', delta: '+0.6%', trend: 'down' },
    avgResponseTime: { value: '334ms', delta: '+86ms', trend: 'down' },
    ocrRequests: { value: '3,102', delta: '+12%', trend: 'up' },
    ocrSuccessRate: { value: '93.1%', delta: '-1.1%', trend: 'down' },
    chatbotSessions: { value: '8,940', delta: '+34%', trend: 'up' },
  },
};

export const mockUserGrowth90d = [
  { label: 'Oct', value: 9800 },
  { label: 'Nov', value: 10200 },
  { label: 'Dec', value: 10600 },
  { label: 'Jan', value: 11100 },
  { label: 'Feb', value: 11700 },
  { label: 'Mar', value: 12482 },
];

export const openTicketCount = 3;

export const mockAdmissionFunnel = [
  { stage: 'Applied', count: 847, pct: 100 },
  { stage: 'Docs Submitted', count: 712, pct: 84 },
  { stage: 'In Review', count: 541, pct: 64 },
  { stage: 'Interview', count: 312, pct: 37 },
  { stage: 'Accepted', count: 198, pct: 23 },
  { stage: 'Enrolled', count: 156, pct: 18 },
];

export const mockServiceHealthTable = [
  { service: 'Auth Service', uptime: '100%', p50: '45ms', p99: '120ms', errors: '0.1%', status: 'Online' },
  { service: 'Registration Svc', uptime: '99.9%', p50: '120ms', p99: '380ms', errors: '0.4%', status: 'Online' },
  { service: 'OCR Engine', uptime: '99.8%', p50: '1.2s', p99: '4.1s', errors: '2.1%', status: 'Online' },
  { service: 'RAG Chatbot', uptime: '97.2%', p50: '3.8s', p99: '12.0s', errors: '5.2%', status: 'Degraded' },
  { service: 'Grade Prediction', uptime: '99.9%', p50: '890ms', p99: '2.1s', errors: '0.2%', status: 'Online' },
  { service: 'Embedding Engine', uptime: '99.9%', p50: '240ms', p99: '800ms', errors: '0.1%', status: 'Online' },
  { service: 'Admissions Svc', uptime: '99.7%', p50: '200ms', p99: '650ms', errors: '0.6%', status: 'Online' },
];

// Security Center

export const mockSecurityScore = 94;

export const mockSecurityAlerts = [
  { id: 1, severity: 'high', message: '3 failed login attempts on admin@bookmark.edu', time: '12 min ago', resolved: false },
  { id: 2, severity: 'medium', message: 'Unusual API access from IP 185.234.12.88', time: '45 min ago', resolved: false },
  { id: 3, severity: 'low', message: 'Password reset requested for 12 accounts', time: '2h ago', resolved: false },
  { id: 4, severity: 'low', message: 'New device login — admin account', time: '5h ago', resolved: true },
];

export const mockAuditLogs = [
  { id: 1, timestamp: 'Jun 19 10:14:22', user: 'admin@bookmark.edu', action: 'ROLE_CHANGED', resource: 'USR-00312', ip: '192.168.1.1' },
  { id: 2, timestamp: 'Jun 19 09:58:01', user: '185.234.12.88', action: 'LOGIN_FAILED ×3', resource: 'Auth', ip: '185.234.12.88' },
  { id: 3, timestamp: 'Jun 19 09:41:00', user: 'registrar@bookmark.edu', action: 'EXPORT_DATA', resource: 'Users CSV', ip: '10.0.0.5' },
  { id: 4, timestamp: 'Jun 19 08:30:00', user: 'system', action: 'BACKUP_COMPLETED', resource: 'DB Full', ip: '—' },
  { id: 5, timestamp: 'Jun 18 23:00:00', user: 'system', action: 'AUTO_LOCK', resource: '14 sessions', ip: '—' },
  { id: 6, timestamp: 'Jun 18 15:22:10', user: 'admin@bookmark.edu', action: 'API_KEY_CREATED', resource: 'Mobile App Key', ip: '192.168.1.1' },
  { id: 7, timestamp: 'Jun 18 11:04:55', user: 'superadmin@bookmark.edu', action: 'FEATURE_FLAG_TOGGLED', resource: 'rag_chat_streaming', ip: '192.168.1.2' },
];

export const mockActiveSessions = [
  { id: 1, user: 'admin@bookmark.edu', role: 'Admin', ip: '192.168.1.1', device: 'Chrome / Windows', location: 'Cairo, EG', started: '09:30 AM', lastActive: '2 min ago' },
  { id: 2, user: 'registrar@bookmark.edu', role: 'Registrar', ip: '10.0.0.5', device: 'Firefox / macOS', location: 'Cairo, EG', started: '08:15 AM', lastActive: '5 min ago' },
  { id: 3, user: 'instructor01@bookmark.edu', role: 'Instructor', ip: '10.0.0.22', device: 'Chrome / Linux', location: 'Giza, EG', started: '10:01 AM', lastActive: '1 min ago' },
];

export const mockAPIKeys = [
  { id: 1, name: 'OCR Integration', prefix: 'bk_ocr_****', scope: '/api/ocr/*', created: 'Jan 12, 2024', lastUsed: '2h ago', isActive: true },
  { id: 2, name: 'Mobile App Key', prefix: 'bk_mob_****', scope: '/api/v2/*', created: 'Mar 3, 2024', lastUsed: '5 min ago', isActive: true },
  { id: 3, name: 'Analytics Export', prefix: 'bk_exp_****', scope: '/api/export/*', created: 'Jun 1, 2024', lastUsed: 'Never', isActive: true },
  { id: 4, name: 'Legacy Integration', prefix: 'bk_lgc_****', scope: '/api/v1/*', created: 'Nov 1, 2023', lastUsed: '92 days ago', isActive: false },
];

// System Settings

export const mockFeatureFlags = [
  { id: 1, name: 'ai_grade_prediction_v2', status: true, rollout: 100, description: 'New XGBoost-based prediction model with improved RMSE' },
  { id: 2, name: 'rag_chat_streaming', status: true, rollout: 75, description: 'Enable streaming token-by-token chatbot responses' },
  { id: 3, name: 'multi_campus_mode', status: false, rollout: 0, description: 'Campus switcher UI and scoped data isolation' },
  { id: 4, name: 'waitlist_automation_v2', status: true, rollout: 100, description: 'Priority-based automatic enrollment from waitlist' },
  { id: 5, name: 'ocr_batch_processing', status: false, rollout: 0, description: 'Allow bulk document OCR pipeline (up to 50 files)' },
  { id: 6, name: 'dark_mode_ui', status: true, rollout: 50, description: 'A/B test: dark theme toggle for student portal' },
  { id: 7, name: 'ai_chatbot_voice_input', status: false, rollout: 0, description: 'Voice-to-text input for the RAG chatbot interface' },
];

export const mockBackups = [
  { id: 1, date: 'Jun 19 — 02:00 AM', type: 'Full DB', size: '2.4 GB', status: 'Success' },
  { id: 2, date: 'Jun 18 — 02:00 AM', type: 'Full DB', size: '2.3 GB', status: 'Success' },
  { id: 3, date: 'Jun 17 — 02:00 AM', type: 'Full DB', size: '2.3 GB', status: 'Failed' },
  { id: 4, date: 'Jun 16 — 02:00 AM', type: 'Full DB', size: '2.2 GB', status: 'Success' },
];

export const mockSystemSettings = {
  institutionName: 'Bookmark University',
  language: 'English',
  timezone: 'UTC+3 — Cairo',
  academicYearFormat: 'YYYY-YYYY',
  maintenanceMode: false,
  registrationOpen: true,
  autoBackup: true,
  backupFrequency: 'Daily at 02:00 AM',
  backupRetention: '30 days',
};

// Content & Config
export const mockAnnouncements = [
  { id: 1, title: 'Spring 2025 Registration Opens', audience: 'All Students', status: 'Published', date: '2025-03-01', pinned: true },
  { id: 2, title: 'System Maintenance Window — April 5', audience: 'All Users', status: 'Scheduled', date: '2025-04-05', pinned: false },
  { id: 3, title: 'New AI Assistant Features Available', audience: 'Faculty', status: 'Published', date: '2025-02-20', pinned: false },
  { id: 4, title: 'Scholarship Deadline Reminder', audience: 'Prospective Students', status: 'Draft', date: '2025-03-15', pinned: false },
  { id: 5, title: 'Campus Closure — Public Holiday', audience: 'All Users', status: 'Published', date: '2025-03-25', pinned: true },
];

export const mockEmailTemplates = [
  { id: 1, name: 'Welcome Email', trigger: 'User Created', lastEdited: '2025-01-15', active: true },
  { id: 2, name: 'Application Received', trigger: 'Application Submit', lastEdited: '2025-02-01', active: true },
  { id: 3, name: 'Password Reset', trigger: 'Manual / Auth Event', lastEdited: '2025-01-10', active: true },
  { id: 4, name: 'Registration Confirmation', trigger: 'Course Enrolment', lastEdited: '2025-02-18', active: true },
  { id: 5, name: 'Admission Decision — Accept', trigger: 'Officer Action', lastEdited: '2025-01-28', active: true },
  { id: 6, name: 'Admission Decision — Reject', trigger: 'Officer Action', lastEdited: '2025-01-28', active: false },
];

export const mockPrograms = [
  { id: 1, code: 'CS-BSC', name: 'B.Sc. Computer Science', department: 'Computing', credits: 132, status: 'Active', enrolled: 412 },
  { id: 2, code: 'IS-BSC', name: 'B.Sc. Information Systems', department: 'Computing', credits: 126, status: 'Active', enrolled: 318 },
  { id: 3, code: 'MBA-G', name: 'Master of Business Administration', department: 'Business', credits: 60, status: 'Active', enrolled: 204 },
  { id: 4, code: 'CE-BSC', name: 'B.Sc. Civil Engineering', department: 'Engineering', credits: 140, status: 'Active', enrolled: 287 },
  { id: 5, code: 'ARCH-BSC', name: 'B.Sc. Architecture', department: 'Design', credits: 150, status: 'Under Review', enrolled: 0 },
];

// Support & Operations
export const mockTickets = [
  { id: 'TKT-1048', subject: 'Cannot access registration portal', user: 'Ahmed Hassan', role: 'Student', priority: 'High', status: 'Open', created: '2025-03-10 09:14' },
  { id: 'TKT-1047', subject: 'AI chatbot returns wrong course info', user: 'Sara Khalil', role: 'Student', priority: 'Medium', status: 'In Progress', created: '2025-03-10 08:30' },
  { id: 'TKT-1046', subject: 'Grade sheet export broken', user: 'Dr. Youssef', role: 'Faculty', priority: 'High', status: 'Open', created: '2025-03-09 17:45' },
  { id: 'TKT-1045', subject: 'Password reset email not received', user: 'Nour Ibrahim', role: 'Student', priority: 'Low', status: 'Resolved', created: '2025-03-09 14:20' },
  { id: 'TKT-1044', subject: 'Odoo sync delay on admissions data', user: 'Registrar Office', role: 'Registrar', priority: 'High', status: 'In Progress', created: '2025-03-09 11:00' },
  { id: 'TKT-1043', subject: 'Duplicate student records created', user: 'Admission Officer', role: 'Officer', priority: 'High', status: 'Resolved', created: '2025-03-08 16:30' },
];

export const mockFeedback = [
  { id: 1, from: 'Ahmed Hassan', role: 'Student', rating: 4, comment: 'The AI assistant is very helpful for finding courses.', date: '2025-03-09', feature: 'AI Assistant' },
  { id: 2, from: 'Dr. Mona Saad', role: 'Faculty', rating: 5, comment: 'Grade management is smooth and intuitive.', date: '2025-03-08', feature: 'Grades Module' },
  { id: 3, from: 'Sara Khalil', role: 'Student', rating: 2, comment: 'Registration portal timed out twice during peak hours.', date: '2025-03-07', feature: 'Registration' },
  { id: 4, from: 'Registrar Office', role: 'Registrar', rating: 3, comment: 'Export feature needs more format options.', date: '2025-03-06', feature: 'Reports' },
];

export const mockServiceStatus = [
  { name: 'Frontend Portal', uptime: '99.9%', lastIncident: 'None', status: 'Operational' },
  { name: 'FastAPI Gateway', uptime: '99.7%', lastIncident: '2025-02-14', status: 'Operational' },
  { name: 'Odoo ERP Backend', uptime: '98.2%', lastIncident: '2025-03-01', status: 'Operational' },
  { name: 'AI / RAG Service', uptime: '97.4%', lastIncident: '2025-03-08', status: 'Degraded' },
  { name: 'OCR Microservice', uptime: '99.1%', lastIncident: 'None', status: 'Operational' },
  { name: 'PostgreSQL DB', uptime: '100%', lastIncident: 'None', status: 'Operational' },
];
