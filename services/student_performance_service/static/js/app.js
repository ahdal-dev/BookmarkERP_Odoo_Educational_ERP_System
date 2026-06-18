const GRADES   = ['A','A-','B+','B','B-','C+','C','C-','D+','D','F','W'];
const SUBTYPES = ['LECTURE','LAB','SEMINAR','TUTORIAL','PROJECT'];
let semCount = 0;

function gradeOpts(sel = 'B') {
  return GRADES.map(g => `<option${g === sel ? ' selected' : ''}>${g}</option>`).join('');
}
function subtypeOpts(sel = 'LECTURE') {
  return SUBTYPES.map(s => `<option${s === sel ? ' selected' : ''}>${s}</option>`).join('');
}

// ── Transcript ────────────────────────────────────────────────────────────────

function addCourse(semId, cid = '', grade = 'B', credits = 3) {
  const wrap = document.getElementById(`courses-${semId}`);
  const div  = document.createElement('div');
  div.className = 'course-row';
  div.innerHTML = `
    <input placeholder="e.g. CSAI 251" value="${cid}" />
    <select>${gradeOpts(grade)}</select>
    <input type="number" min="1" max="6" value="${credits}" />
    <button class="btn-remove" onclick="this.closest('.course-row').remove()">✕</button>`;
  wrap.appendChild(div);
}

function addSemester(term='', tgpa='', cgpa='', earn='', att='') {
  semCount++;
  const id = `sem-${semCount}`;
  const card = document.createElement('div');
  card.className = 'sem-card'; card.id = id;
  card.innerHTML = `
    <div class="sem-header">
      <span class="sem-title">Semester ${semCount}</span>
      <button class="btn-remove" onclick="document.getElementById('${id}').remove()">Remove</button>
    </div>
    <div class="sem-stats">
      <label>Term<input class="f-term" placeholder="e.g. 2023 Fall" value="${term}" /></label>
      <label>Term GPA<input class="f-tgpa" type="number" step="0.01" min="0" max="4" value="${tgpa}" /></label>
      <label>Cumulative GPA<input class="f-cgpa" type="number" step="0.01" min="0" max="4" value="${cgpa}" /></label>
      <label>Earned Cr.<input class="f-earn" type="number" min="0" value="${earn}" /></label>
      <label>Attempted Cr.<input class="f-att" type="number" min="0" value="${att}" /></label>
    </div>
    <div class="courses-label">Courses (ID · grade · credits)</div>
    <div id="courses-${id}"></div>
    <button class="btn-add" style="margin-top:.4rem" onclick="addCourse('${id}')">+ Course</button>`;
  document.getElementById('semesters').appendChild(card);
  addCourse(id);
}

// ── Study plan ────────────────────────────────────────────────────────────────

function addPlanCourse(cid = '', credits = 3, title = '', subtype = 'LECTURE') {
  const div = document.createElement('div');
  div.className = 'plan-row';
  div.innerHTML = `
    <input placeholder="e.g. CSAI 351" value="${cid}" />
    <input type="number" min="1" max="6" value="${credits}" />
    <input placeholder="optional title" value="${title}" />
    <select>${subtypeOpts(subtype)}</select>
    <button class="btn-remove" onclick="this.closest('.plan-row').remove()">✕</button>`;
  document.getElementById('plan-courses').appendChild(div);
}

// ── Collect ───────────────────────────────────────────────────────────────────

function collectSemesters() {
  return [...document.querySelectorAll('.sem-card')].flatMap(card => {
    const term = card.querySelector('.f-term').value.trim();
    if (!term) return [];
    const courses = [...card.querySelectorAll('.course-row')].flatMap(row => {
      const ins = row.querySelectorAll('input');
      const cid = ins[0].value.trim();
      return cid ? [{ course_id: cid, grade: row.querySelector('select').value, credits: parseInt(ins[1].value)||3 }] : [];
    });
    return [{
      term_name:        term,
      term_gpa:         parseFloat(card.querySelector('.f-tgpa').value) || null,
      cumulative_gpa:   parseFloat(card.querySelector('.f-cgpa').value) || null,
      earned_credits:   parseInt(card.querySelector('.f-earn').value)   || 0,
      attempted_credits:parseInt(card.querySelector('.f-att').value)    || 0,
      courses,
    }];
  });
}

function collectPlan() {
  return [...document.querySelectorAll('.plan-row')].flatMap(row => {
    const ins = row.querySelectorAll('input');
    const cid = ins[0].value.trim();
    return cid ? [{ course_id: cid, credits: parseInt(ins[1].value)||3, title: ins[2].value.trim(), subtype: row.querySelector('select').value }] : [];
  });
}

// ── Render result ─────────────────────────────────────────────────────────────

function riskClass(level) {
  return level === 'High' ? 'high' : level === 'Medium' ? 'medium' : 'low';
}
function riskBadge(r) {
  if (r.at_risk)              return `<span class="badge badge-risk">At Risk</span>`;
  if (r.risk_level==='Medium') return `<span class="badge badge-warn">Watch</span>`;
  return `<span class="badge badge-safe">On Track</span>`;
}
function trajBadge(t) {
  return `<span class="badge badge-blue">${t}</span>`;
}

function renderResult(r) {
  const rc    = riskClass(r.risk_level);
  const pct   = (r.at_risk_probability * 100).toFixed(1);
  const sm    = r.student_message || {};
  const llmRecs  = r.llm_recommendations || [];
  const ruleRecs = r.recommendations || [];
  const isLLM    = llmRecs.length > 0 && JSON.stringify(llmRecs) !== JSON.stringify(ruleRecs);
  const recs     = isLLM ? llmRecs : ruleRecs;

  const recIcons = ['💡','📚','⚡','🎯'];
  const recItems = recs.map((rec, i) =>
    `<li class="rec-item${isLLM ? ' rec-item-llm' : ''}"><span class="rec-icon">${recIcons[i % recIcons.length]}</span>${rec}</li>`
  ).join('');

  const reas = r.reasoning || {};
  const pa   = r.plan_analysis || {};

  const detailRows1 = [
    ['Cumulative GPA',    reas.cumulative_gpa],
    ['Last term GPA',     reas.last_term_gpa],
    ['GPA slope',         reas.gpa_slope !== undefined ? (reas.gpa_slope > 0 ? '+' : '') + reas.gpa_slope : '—'],
    ['Graduation GPA est.',r.graduation_gpa_estimate],
  ].map(([k,v]) => `<div class="detail-row"><b>${k}</b><span>${v ?? '—'}</span></div>`).join('');

  const detailRows2 = [
    ['Load',          pa.load_assessment],
    ['Difficulty',    pa.difficulty_note],
    ['Alignment',     pa.strength_alignment],
    ['Weak credits',  pa.credits_in_weak_subjects],
  ].map(([k,v]) => `<div class="detail-row"><b>${k}</b><span>${v ?? '—'}</span></div>`).join('');

  const flagsHtml = (r.flags || []).length
    ? (r.flags || []).map(f => `<span class="flag-chip">${f.replace(/_/g,' ')}</span>`).join('')
    : '<span style="color:#a0aec0;font-size:.78rem">none</span>';

  return `
  <div class="result-card ${rc}">

    <div class="hero">
      <div>
        <div style="font-size:.72rem;color:#718096;margin-bottom:.1rem">Predicted GPA</div>
        <div class="gpa-big">${r.predicted_gpa.toFixed(2)}</div>
        <div class="gpa-sub">90% interval: ${r.interval_lo.toFixed(2)} – ${r.interval_hi.toFixed(2)}</div>
      </div>
      <div class="divider"></div>
      <div class="stat-col">
        <div class="stat-label">Status</div>
        <div>${riskBadge(r)}</div>
      </div>
      <div class="stat-col">
        <div class="stat-label">Trajectory</div>
        <div>${trajBadge(r.trajectory)}</div>
      </div>
    </div>

    <div class="risk-row">
      <div class="risk-bar-label">Probability of GPA falling below 2.0 next term</div>
      <div class="bar-track"><div class="bar-fill ${rc}" style="width:${pct}%"></div></div>
      <div class="bar-caption">${pct}% chance of a difficult term</div>
    </div>

    <div class="recs-section${isLLM ? ' recs-section-llm' : ''}">
      <div class="recs-title">Recommendations</div>
      <ul class="rec-list">${recItems}</ul>
    </div>

    <div class="details-toggle">
      <span style="font-size:.78rem;color:#a0aec0">Standing · Plan analysis · Flags</span>
      <button onclick="toggleDetails(this)">Show details ▾</button>
    </div>
    <div class="details-panel">
      <div class="details-grid">
        <div class="detail-group">
          <h4>Student Standing</h4>
          ${detailRows1}
        </div>
        <div class="detail-group">
          <h4>Plan Analysis</h4>
          ${detailRows2}
        </div>
      </div>
      <div style="margin-top:1rem">
        <div class="detail-group"><h4 style="margin-bottom:.4rem">Warning Flags</h4></div>
        <div class="flags-wrap">${flagsHtml}</div>
      </div>
    </div>

  </div>`;
}

function toggleDetails(btn) {
  const panel = btn.closest('.result-card').querySelector('.details-panel');
  const open  = panel.classList.toggle('open');
  btn.textContent = open ? 'Hide details ▴' : 'Show details ▾';
}

// ── Predict ───────────────────────────────────────────────────────────────────

async function runPredict() {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '<div class="spinner">Analyzing your plan…</div>';

  const semesters  = collectSemesters();
  const study_plan = collectPlan();

  if (!study_plan.length) {
    resultDiv.innerHTML = '<div class="err-box">Add at least one course to your study plan.</div>'; return;
  }

  const payload = {
    student_id: document.getElementById('student_id').value.trim() || 'student',
    program:    document.getElementById('program').value.trim()    || 'Computer Science',
    school:     document.getElementById('school').value.trim()     || 'Engineering',
    entry_year: parseInt(document.getElementById('entry_year').value) || 2021,
    semesters,
    study_plan,
  };

  try {
    const resp = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const r = await resp.json();

    if (!resp.ok || r.detail) {
      const errPayload = { status: resp.status, error: r.detail || 'Unknown error' };
      console.group('%c POST /predict  ERROR', 'color:#e53e3e;font-weight:700;font-size:13px');
      console.log(JSON.stringify(errPayload, null, 2));
      console.groupEnd();
      resultDiv.innerHTML = `<div class="err-box"><b>Error ${resp.status}:</b> ${r.detail}</div>`;
      return;
    }

    console.group('%c POST /predict  SUCCESS', 'color:#38a169;font-weight:700;font-size:13px');
    console.log(JSON.stringify(r, null, 2));
    console.groupEnd();

    resultDiv.innerHTML = renderResult(r);
  } catch (err) {
    resultDiv.innerHTML = `<div class="err-box"><b>Error:</b> ${err.message}</div>`;
  }
}

// ── Test scenarios ────────────────────────────────────────────────────────────

const SCENARIOS = {
  good: {
    info: { student_id: 'S-GOOD-01', program: 'Computer Science', school: 'Engineering', entry_year: 2021 },
    semesters: [
      { term: '2022 Fall',   tgpa: 3.8, cgpa: 3.80, earn: 18, att: 18,
        courses: [['CSAI 101','A',3],['MATH 101','A-',3],['ENGL 101','A',3],['PHYS 101','B+',3],['CSAI 111','A',3],['CSAI 120','A',3]] },
      { term: '2023 Spring', tgpa: 3.7, cgpa: 3.75, earn: 18, att: 18,
        courses: [['CSAI 201','A-',3],['MATH 201','A',3],['CSAI 211','A',3],['PHYS 102','B+',3],['CSAI 220','A-',3],['ENGL 201','A',3]] },
      { term: '2023 Fall',   tgpa: 3.6, cgpa: 3.72, earn: 15, att: 15,
        courses: [['CSAI 301','A-',3],['MATH 301','B+',3],['CSAI 311','A',3],['CSAI 320','A-',3],['CSAI 330','A',3]] },
    ],
    plan: [['CSAI 401','Advanced AI',3,'LECTURE'],['MATH 401','Real Analysis',3,'LECTURE'],['CSAI 411','Deep Learning',3,'LECTURE'],['CSAI 420','Distributed Systems',3,'LECTURE'],['CSAI 430','Security',3,'LECTURE']],
  },

  medium: {
    info: { student_id: 'S-MED-01', program: 'Computer Science', school: 'Engineering', entry_year: 2021 },
    semesters: [
      { term: '2022 Fall',   tgpa: 2.9, cgpa: 2.90, earn: 15, att: 15,
        courses: [['CSAI 101','B',3],['MATH 101','C+',3],['ENGL 101','B+',3],['PHYS 101','C',3],['CSAI 111','B-',3]] },
      { term: '2023 Spring', tgpa: 3.1, cgpa: 3.00, earn: 15, att: 15,
        courses: [['CSAI 201','B+',3],['MATH 201','B-',3],['CSAI 211','B',3],['PHYS 102','C+',3],['CSAI 220','B',3]] },
      { term: '2023 Fall',   tgpa: 2.8, cgpa: 2.93, earn: 15, att: 15,
        courses: [['CSAI 301','C+',3],['MATH 301','B',3],['CSAI 311','B-',3],['CSAI 320','C+',3],['CSAI 330','B',3]] },
    ],
    plan: [['CSAI 401','Advanced AI',3,'LECTURE'],['MATH 401','Real Analysis',3,'LECTURE'],['CSAI 411','Deep Learning',3,'LECTURE'],['CSAI 420','Distributed Systems',3,'LECTURE']],
  },

  risk: {
    info: { student_id: 'S-RISK-01', program: 'Computer Science', school: 'Engineering', entry_year: 2021 },
    semesters: [
      { term: '2022 Fall',   tgpa: 2.1, cgpa: 2.10, earn: 12, att: 15,
        courses: [['CSAI 101','C-',3],['MATH 101','D',3],['ENGL 101','C',3],['PHYS 101','F',3],['CSAI 111','C',3]] },
      { term: '2023 Spring', tgpa: 1.9, cgpa: 2.00, earn: 12, att: 15,
        courses: [['CSAI 201','C',3],['MATH 101','C-',3],['PHYS 101','D+',3],['CSAI 111','W',3]] },
      { term: '2023 Fall',   tgpa: 1.8, cgpa: 1.95, earn: 9,  att: 15,
        courses: [['CSAI 301','D+',3],['MATH 201','D',3],['CSAI 201','F',3],['CSAI 211','C-',3],['CSAI 220','W',3]] },
    ],
    plan: [['CSAI 401','Advanced AI',3,'LECTURE'],['MATH 301','Calculus III',3,'LECTURE'],['CSAI 411','Deep Learning',3,'LECTURE'],['CSAI 201','OOP (retake)',3,'LECTURE'],['PHYS 201','Physics II (retake)',3,'LECTURE'],['CSAI 450','Networks',3,'LECTURE']],
  },

  retake: {
    info: { student_id: 'S-RET-01', program: 'Computer Science', school: 'Engineering', entry_year: 2021 },
    semesters: [
      { term: '2022 Fall',   tgpa: 2.5, cgpa: 2.50, earn: 15, att: 15,
        courses: [['CSAI 101','B-',3],['MATH 101','C',3],['CSAI 201','F',3],['PHYS 101','D',3],['ENGL 101','B',3]] },
      { term: '2023 Spring', tgpa: 2.7, cgpa: 2.60, earn: 15, att: 15,
        courses: [['CSAI 201','C-',3],['MATH 101','C+',3],['CSAI 111','B-',3],['PHYS 101','C',3],['CSAI 220','B',3]] },
    ],
    plan: [['CSAI 201','OOP (3rd attempt)',3,'LECTURE'],['MATH 101','Calculus I (retake)',3,'LECTURE'],['PHYS 101','Physics I (retake)',3,'LECTURE'],['CSAI 301','Data Structures',3,'LECTURE']],
  },
};

function loadScenario(key) {
  const s = SCENARIOS[key];
  if (!s) return;

  // Fill student info
  document.getElementById('student_id').value = s.info.student_id;
  document.getElementById('program').value    = s.info.program;
  document.getElementById('school').value     = s.info.school;
  document.getElementById('entry_year').value = s.info.entry_year;

  // Clear and rebuild semesters
  document.getElementById('semesters').innerHTML = '';
  semCount = 0;
  s.semesters.forEach(sem => {
    addSemester(sem.term, sem.tgpa, sem.cgpa, sem.earn, sem.att);
    const id = `sem-${semCount}`;
    // Remove the default blank course added by addSemester
    document.getElementById(`courses-${id}`).innerHTML = '';
    sem.courses.forEach(([cid, grade, cr]) => addCourse(id, cid, grade, cr));
  });

  // Clear and rebuild plan
  document.getElementById('plan-courses').innerHTML = '';
  s.plan.forEach(([cid, title, cr, subtype]) => addPlanCourse(cid, cr, title, subtype));

  document.getElementById('result').innerHTML = '';
}

// ── Demo data ─────────────────────────────────────────────────────────────────
addSemester('2022 Fall',   '3.3', '3.30', '15', '15');
addCourse('sem-1', 'CSAI 151', 'B+', 3);
addCourse('sem-1', 'MATH 201', 'A',  3);
addCourse('sem-1', 'ENGL 101', 'B',  3);

addSemester('2023 Spring', '3.0', '3.15', '15', '15');
addCourse('sem-2', 'CSAI 251', 'B',  3);
addCourse('sem-2', 'MATH 301', 'B+', 3);
addCourse('sem-2', 'PHYS 101', 'C+', 3);

addPlanCourse('CSAI 351', 3, 'Machine Learning',  'LECTURE');
addPlanCourse('MATH 401', 3, 'Linear Algebra II', 'LECTURE');
addPlanCourse('CSAI 361', 3, 'Data Structures',   'LECTURE');
addPlanCourse('CSAI 361', 1, 'DS Lab',            'LAB');
