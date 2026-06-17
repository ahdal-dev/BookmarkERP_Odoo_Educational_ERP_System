const GRADE_OPTIONS = ['A','A-','B+','B','B-','C+','C','C-','D+','D','F','W'];

function gradeOptions(selected = 'B') {
  return GRADE_OPTIONS.map(g =>
    `<option${g === selected ? ' selected' : ''}>${g}</option>`
  ).join('');
}

function addRow(course = '', grade = 'B', semester = '') {
  const container = document.getElementById('transcript-rows');
  const div = document.createElement('div');
  div.className = 'transcript-row';
  div.innerHTML = `
    <input placeholder="e.g. CSAI 151" value="${course}">
    <select>${gradeOptions(grade)}</select>
    <input placeholder="e.g. Fall 2023" value="${semester}">
    <button class="btn-remove" onclick="removeRow(this)">✕</button>`;
  container.appendChild(div);
}

function removeRow(btn) {
  btn.closest('.transcript-row').remove();
}

function gradeClass(letter) {
  if (!letter) return 'grade-DF';
  if (letter.startsWith('A')) return 'grade-A';
  if (letter.startsWith('B')) return 'grade-B';
  if (letter.startsWith('C')) return 'grade-C';
  return 'grade-DF';
}

async function runPredict() {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '<div class="spinner">⏳ Predicting...</div>';

  const rows = document.querySelectorAll('#transcript-rows .transcript-row');
  const history = [];
  rows.forEach(row => {
    const inputs = row.querySelectorAll('input');
    const sel = row.querySelector('select');
    const course = inputs[0].value.trim();
    const semester = inputs[1].value.trim();
    if (course) history.push({ course, grade: sel.value, semester });
  });

  const payload = {
    student_id: document.getElementById('student_id').value.trim() || 'student',
    target_course: document.getElementById('target_course').value.trim(),
    cumulative_gpa: parseFloat(document.getElementById('cumulative_gpa').value) || 2.5,
    current_semester_credit_load: parseInt(document.getElementById('credit_load').value) || 15,
    transcript_history: history,
  };

  try {
    const resp = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const r = await resp.json();

    if (r.error) {
      resultDiv.innerHTML = `<div class="err-box"><strong>Error:</strong> ${r.error}</div>`;
      return;
    }

    const cls = gradeClass(r.predicted_grade);
    const chips = (r.grade_interval || []).map(g =>
      `<span class="chip${g === r.predicted_grade ? ' active' : ''}">${g}</span>`
    ).join('');

    resultDiv.innerHTML = `
      <div class="result-box ${cls}">
        <div class="grade-lbl">${r.predicted_grade}</div>
        <div class="meta">
          <strong>Course:</strong> ${r.target_course} &nbsp;|&nbsp;
          <strong>GPA Points:</strong> ${r.predicted_numeric} &nbsp;|&nbsp;
          <strong>Confidence:</strong> ${(r.confidence * 100).toFixed(1)}%
          <br>
          <strong>90% Grade Interval:</strong>
          <div class="interval">${chips}</div>
        </div>
        <div class="reasoning">
          <strong>Prerequisite:</strong> ${r.reasoning.prerequisite_grade}<br>
          <strong>Domain Average:</strong> ${r.reasoning.domain_avg}<br>
          <strong>GPA Trend:</strong> ${r.reasoning.gpa_trend}
          ${r.off_catalog ? '<br><em>⚠ Course is off-catalog — prediction uses GPA proxies only.</em>' : ''}
        </div>
      </div>`;
  } catch (err) {
    resultDiv.innerHTML = `<div class="err-box"><strong>Error:</strong> ${err.message}</div>`;
  }
}
