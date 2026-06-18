const GRADES   = ['A','A-','B+','B','B-','C+','C','C-','D+','D','F','W'];
const SUBTYPES = ['LECTURE','LAB','SEMINAR','TUTORIAL','PROJECT'];
let semCount = 0;

function gradeOpts(sel = 'B') {
  return GRADES.map(g => `<option${g === sel ? ' selected' : ''}>${g}</option>`).join('');
}
function subtypeOpts(sel = 'LECTURE') {
  return SUBTYPES.map(s => `<option${s === sel ? ' selected' : ''}>${s}</option>`).join('');
}

// ── Transcript semesters ──────────────────────────────────────────────────────

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
  const id  = `sem-${semCount}`;
  const box = document.getElementById('semesters');
  const card = document.createElement('div');
  card.className = 'sem-card'; card.id = id;
  card.innerHTML = `
    <div class="sem-header">
      <span class="sem-title">Semester ${semCount}</span>
      <button class="btn-remove" onclick="document.getElementById('${id}').remove()">Remove</button>
    </div>
    <div class="sem-stats">
      <label>Term Name<input class="f-term" placeholder="e.g. 2023 Fall" value="${term}" /></label>
      <label>Term GPA<input class="f-tgpa" type="number" step="0.01" min="0" max="4" placeholder="0–4" value="${tgpa}" /></label>
      <label>Cumulative GPA<input class="f-cgpa" type="number" step="0.01" min="0" max="4" placeholder="0–4" value="${cgpa}" /></label>
      <label>Earned Credits<input class="f-earn" type="number" min="0" placeholder="e.g. 15" value="${earn}" /></label>
      <label>Attempted Credits<input class="f-att" type="number" min="0" placeholder="e.g. 15" value="${att}" /></label>
    </div>
    <div class="courses-label">Courses (course ID · grade · credits)</div>
    <div id="courses-${id}"></div>
    <button class="btn-add" style="margin-top:.5rem" onclick="addCourse('${id}')">+ Course</button>`;
  box.appendChild(card);
  addCourse(id);
}

// ── Study plan ────────────────────────────────────────────────────────────────

function addPlanCourse(cid = '', credits = 3, title = '', subtype = 'LECTURE') {
  const wrap = document.getElementById('plan-courses');
  const div  = document.createElement('div');
  div.className = 'plan-row';
  div.innerHTML = `
    <input placeholder="e.g. CSAI 351" value="${cid}" />
    <input type="number" min="1" max="6" value="${credits}" />
    <input placeholder="optional title" value="${title}" />
    <select>${subtypeOpts(subtype)}</select>
    <button class="btn-remove" onclick="this.closest('.plan-row').remove()">✕</button>`;
  wrap.appendChild(div);
}

// ── Collect form data ─────────────────────────────────────────────────────────

function collectSemesters() {
  const out = [];
  document.querySelectorAll('.sem-card').forEach(card => {
    const termName      = card.querySelector('.f-term').value.trim();
    const termGpa       = parseFloat(card.querySelector('.f-tgpa').value) || null;
    const cumulativeGpa = parseFloat(card.querySelector('.f-cgpa').value) || null;
    const earnedCr      = parseInt(card.querySelector('.f-earn').value)   || 0;
    const attemptedCr   = parseInt(card.querySelector('.f-att').value)    || 0;
    if (!termName) return;
    const courses = [];
    card.querySelectorAll('.course-row').forEach(row => {
      const ins = row.querySelectorAll('input');
      const cid = ins[0].value.trim();
      if (cid) courses.push({
        course_id: cid,
        grade:     row.querySelector('select').value,
        credits:   parseInt(ins[1].value) || 3,
      });
    });
    out.push({ term_name: termName, term_gpa: termGpa, cumulative_gpa: cumulativeGpa,
               earned_credits: earnedCr, attempted_credits: attemptedCr, courses });
  });
  return out;
}

function collectPlan() {
  const out = [];
  document.querySelectorAll('.plan-row').forEach(row => {
    const ins   = row.querySelectorAll('input');
    const cid   = ins[0].value.trim();
    if (!cid) return;
    out.push({
      course_id: cid,
      credits:   parseInt(ins[1].value) || 3,
      title:     ins[2].value.trim(),
      subtype:   row.querySelector('select').value,
    });
  });
  return out;
}

// ── Predict ───────────────────────────────────────────────────────────────────

async function runPredict() {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '<div class="spinner">⏳ Predicting…</div>';

  const semesters  = collectSemesters();
  const study_plan = collectPlan();

  if (!semesters.length) {
    resultDiv.innerHTML = '<div class="err-box">Please add at least one completed semester.</div>'; return;
  }
  if (!study_plan.length) {
    resultDiv.innerHTML = '<div class="err-box">Please add at least one course to the study plan.</div>'; return;
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
    if (r.detail) { resultDiv.innerHTML = `<div class="err-box"><b>Error:</b> ${r.detail}</div>`; return; }

    const riskClass = r.at_risk ? 'at-risk' : 'safe';
    const badgeRisk = r.at_risk
      ? '<span class="badge badge-risk">⚠ At Risk</span>'
      : '<span class="badge badge-safe">✓ On Track</span>';
    const traj = `<span class="badge badge-traj">${r.trajectory}</span>`;
    const riskPct   = (r.at_risk_probability * 100).toFixed(1);
    const safePct   = (100 - r.at_risk_probability * 100).toFixed(1);
    const fillClass = r.at_risk ? 'bar-fill-risk' : 'bar-fill-safe';

    const reas = r.reasoning || {};
    const rows = [
      ['Semesters completed',    reas.n_semesters_completed],
      ['Cumulative GPA',         reas.cumulative_gpa],
      ['Last term GPA',          reas.last_term_gpa],
      ['GPA slope',              reas.gpa_slope !== undefined ? (reas.gpa_slope > 0 ? '+' : '') + reas.gpa_slope : '—'],
      ['Plan expected GPA',      reas.plan_expected_gpa],
      ['Plan credit load',       reas.plan_credit_load],
      ['Weak-domain credits',    reas.plan_weak_domain_credits],
      ['Graduation GPA est.',    r.graduation_gpa_estimate],
    ].map(([k,v]) => `<div class="r-row"><b>${k}</b><span>${v ?? '—'}</span></div>`).join('');

    resultDiv.innerHTML = `
      <div class="result-box ${riskClass}">
        <div class="result-top">
          <div class="gpa-block">
            <div class="gpa-label">Predicted Next-Semester GPA</div>
            <div class="gpa-big">${r.predicted_gpa.toFixed(2)}</div>
            <div class="gpa-interval">90% interval: ${r.interval_lo.toFixed(2)} – ${r.interval_hi.toFixed(2)}</div>
          </div>
          <div>
            <div class="gpa-label">Risk</div>
            ${badgeRisk}
          </div>
          <div>
            <div class="gpa-label">Trajectory</div>
            ${traj}
          </div>
          <div class="risk-bar-wrap">
            <div class="risk-bar-label">P(GPA &lt; 2.0 next term)</div>
            <div class="bar-bg"><div class="${fillClass}" style="width:${riskPct}%"></div></div>
            <div class="bar-pct">${riskPct}% at-risk &nbsp;|&nbsp; ${safePct}% safe</div>
          </div>
        </div>
        <div class="reasoning">${rows}</div>
      </div>`;
  } catch (err) {
    resultDiv.innerHTML = `<div class="err-box"><b>Error:</b> ${err.message}</div>`;
  }
}

// ── Pre-fill demo data ────────────────────────────────────────────────────────
addSemester('2022 Fall',   '3.3', '3.30', '15', '15');
addCourse('sem-1', 'CSAI 151', 'B+', 3);
addCourse('sem-1', 'MATH 201', 'A',  3);
addCourse('sem-1', 'ENGL 101', 'B',  3);

addSemester('2023 Spring', '3.0', '3.15', '15', '15');
addCourse('sem-2', 'CSAI 251', 'B',  3);
addCourse('sem-2', 'MATH 301', 'B+', 3);
addCourse('sem-2', 'PHYS 101', 'C+', 3);

addPlanCourse('CSAI 351', 3, 'Machine Learning', 'LECTURE');
addPlanCourse('MATH 401', 3, 'Linear Algebra II', 'LECTURE');
addPlanCourse('CSAI 361', 3, 'Data Structures', 'LECTURE');
addPlanCourse('CSAI 361', 1, 'DS Lab', 'LAB');
