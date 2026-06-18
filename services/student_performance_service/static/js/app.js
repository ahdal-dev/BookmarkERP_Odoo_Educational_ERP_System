const GRADES = ['A','A-','B+','B','B-','C+','C','C-','D+','D','F','W'];
let semCount = 0;

function gradeOptions(sel = 'B') {
  return GRADES.map(g => `<option${g === sel ? ' selected' : ''}>${g}</option>`).join('');
}

function addCourseRow(semId, cid = '', grade = 'B', credits = 3) {
  const wrap = document.getElementById(`courses-${semId}`);
  const div = document.createElement('div');
  div.className = 'course-row';
  div.innerHTML = `
    <input placeholder="e.g. CSAI 251" value="${cid}" />
    <select>${gradeOptions(grade)}</select>
    <input type="number" min="1" max="6" value="${credits}" />
    <button class="btn-remove" onclick="this.closest('.course-row').remove()">✕</button>`;
  wrap.appendChild(div);
}

function addSemester(termName = '', termGpa = '', cumGpa = '', earnedCr = '', attemptedCr = '') {
  semCount++;
  const id = `sem-${semCount}`;
  const container = document.getElementById('semesters');
  const card = document.createElement('div');
  card.className = 'sem-card';
  card.id = id;
  card.innerHTML = `
    <div class="sem-header">
      <span class="sem-title">Semester ${semCount}</span>
      <button class="btn-remove" onclick="document.getElementById('${id}').remove()">Remove</button>
    </div>
    <div class="sem-stats">
      <label>Term Name
        <input class="f-term" placeholder="e.g. 2023 Fall" value="${termName}" />
      </label>
      <label>Term GPA
        <input class="f-tgpa" type="number" step="0.01" min="0" max="4" placeholder="0.00–4.00" value="${termGpa}" />
      </label>
      <label>Cumulative GPA
        <input class="f-cgpa" type="number" step="0.01" min="0" max="4" placeholder="0.00–4.00" value="${cumGpa}" />
      </label>
      <label>Earned Credits
        <input class="f-earn" type="number" min="0" placeholder="e.g. 15" value="${earnedCr}" />
      </label>
      <label>Attempted Credits
        <input class="f-att" type="number" min="0" placeholder="e.g. 15" value="${attemptedCr}" />
      </label>
    </div>
    <div class="courses-label">Courses taken this semester</div>
    <div id="courses-${id}"></div>
    <button class="btn-add" style="margin-top:.5rem" onclick="addCourseRow('${id}')">+ Add Course</button>`;
  container.appendChild(card);
  addCourseRow(id);
}

function collectData() {
  const semesters = [];
  document.querySelectorAll('.sem-card').forEach(card => {
    const termName      = card.querySelector('.f-term').value.trim();
    const termGpa       = parseFloat(card.querySelector('.f-tgpa').value) || null;
    const cumulativeGpa = parseFloat(card.querySelector('.f-cgpa').value) || null;
    const earnedCr      = parseInt(card.querySelector('.f-earn').value)   || 0;
    const attemptedCr   = parseInt(card.querySelector('.f-att').value)    || 0;
    if (!termName) return;

    const courses = [];
    card.querySelectorAll('.course-row').forEach(row => {
      const inputs  = row.querySelectorAll('input');
      const courseId = inputs[0].value.trim();
      const grade    = row.querySelector('select').value;
      const credits  = parseInt(inputs[1].value) || 3;
      if (courseId) courses.push({ course_id: courseId, grade, credits });
    });

    semesters.push({
      term_name:        termName,
      term_gpa:         termGpa,
      cumulative_gpa:   cumulativeGpa,
      earned_credits:   earnedCr,
      attempted_credits: attemptedCr,
      courses,
    });
  });
  return semesters;
}

async function runPredict() {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '<div class="spinner">⏳ Predicting…</div>';

  const semesters = collectData();
  if (semesters.length === 0) {
    resultDiv.innerHTML = '<div class="err-box">Please add at least one semester.</div>';
    return;
  }

  const payload = {
    student_id: document.getElementById('student_id').value.trim() || 'student',
    program:    document.getElementById('program').value.trim()    || 'Computer Science',
    school:     document.getElementById('school').value.trim()     || 'Engineering',
    entry_year: parseInt(document.getElementById('entry_year').value) || 2021,
    semesters,
  };

  try {
    const resp = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const r = await resp.json();

    if (r.detail) {
      resultDiv.innerHTML = `<div class="err-box"><strong>Error:</strong> ${r.detail}</div>`;
      return;
    }

    const riskClass  = `risk-${r.risk_level}`;
    const badgeClass = `badge-${r.risk_level}`;

    const probRows = Object.entries(r.risk_probabilities || {})
      .sort((a, b) => b[1] - a[1])
      .map(([cls, p]) => `
        <div class="prob-row">
          <span class="prob-name">${cls}</span>
          <div class="prob-bar-wrap"><div class="prob-bar bar-${cls}" style="width:${(p*100).toFixed(1)}%"></div></div>
          <span class="prob-val">${(p*100).toFixed(1)}%</span>
        </div>`).join('');

    const reas = r.reasoning || {};
    const reasonRows = [
      ['Semesters completed', reas.n_semesters_completed],
      ['Last term GPA',       reas.last_term_gpa],
      ['Cumulative GPA',      reas.cumulative_gpa],
      ['GPA trend',           reas.gpa_trend],
    ].map(([k, v]) => `<span><b>${k}</b>${v ?? '—'}</span>`).join('');

    resultDiv.innerHTML = `
      <div class="result-box ${riskClass}">
        <div class="result-top">
          <div>
            <div class="gpa-label">Predicted Next-Semester GPA</div>
            <div class="gpa-big">${r.predicted_gpa.toFixed(2)}</div>
          </div>
          <div>
            <div class="gpa-label">Risk Level</div>
            <span class="risk-badge ${badgeClass}">${r.risk_level}</span>
          </div>
          <div>
            <div class="gpa-label">Trajectory</div>
            <span class="traj-badge">${r.trajectory}</span>
          </div>
        </div>
        <div class="prob-bars">${probRows}</div>
        <div class="reasoning">${reasonRows}</div>
      </div>`;
  } catch (err) {
    resultDiv.innerHTML = `<div class="err-box"><strong>Error:</strong> ${err.message}</div>`;
  }
}

// Start with two sample semesters pre-filled
addSemester('2022 Fall',   '3.3', '3.3', '15', '15');
addCourseRow(`sem-1`, 'CSAI 151', 'B+', 3);
addCourseRow(`sem-1`, 'MATH 201', 'A',  3);
addCourseRow(`sem-1`, 'ENGL 101', 'B',  3);

addSemester('2023 Spring', '3.0', '3.15', '15', '15');
addCourseRow(`sem-2`, 'CSAI 251', 'B',  3);
addCourseRow(`sem-2`, 'MATH 301', 'B+', 3);
addCourseRow(`sem-2`, 'PHYS 101', 'C+', 3);
