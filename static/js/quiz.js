/* ════════════════════════════════════════════════════════════════
   Состояние
════════════════════════════════════════════════════════════════ */
const answers  = [];   // { index, selected } — накапливаем по мере ответов
let score      = 0;
let current    = 0;

const TYPE_LABELS = {
  single: '<i class="bi bi-check2-circle me-1"></i>Одиночный выбор',
  multi:  '<i class="bi bi-check2-all me-1"></i>Множественный выбор',
  text:   '<i class="bi bi-input-cursor me-1"></i>Текстовый ответ',
};

/* ════════════════════════════════════════════════════════════════
   Инициализация
════════════════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", () => showQuestion(0));

function showQuestion(idx) {
  document.querySelectorAll(".q-block").forEach(el => el.style.display = "none");

  const block = document.getElementById(`q-${idx}`);
  if (!block) return;
  block.style.display = "block";
  block.scrollIntoView({ behavior: "smooth", block: "start" });

  // Прогресс
  const total = QUESTIONS.length;
  const pct   = Math.round(((idx + 1) / total) * 100);
  document.getElementById("progress-bar").style.width = pct + "%";
  document.getElementById("q-num").textContent        = idx + 1;

  // Метка типа
  const qtype = QUESTIONS[idx]?.type;
  document.getElementById("q-type-label").innerHTML = TYPE_LABELS[qtype] || "";
}

/* ════════════════════════════════════════════════════════════════
   Одиночный выбор
════════════════════════════════════════════════════════════════ */
function answerSingle(qIndex, key, btn) {
  const container = document.getElementById(`opts-${qIndex}`);
  if (container.dataset.answered) return;
  container.dataset.answered = "true";

  container.querySelectorAll(".option-btn").forEach(b => b.disabled = true);
  answers.push({ index: qIndex, selected: key });

  sendCheck(qIndex, key, (result) => {
    highlightSingle(container, key, result.correct_answer, result.correct);
    showFeedback(qIndex, result);
    revealNext(qIndex);
  });
}

function highlightSingle(container, selected, correctKey, isCorrect) {
  container.querySelectorAll(".option-btn").forEach(btn => {
    const k = btn.dataset.key;
    if (k === correctKey) {
      applyState(btn, "correct");
    } else if (k === selected && !isCorrect) {
      applyState(btn, "wrong");
    } else {
      btn.classList.add("opt-dim");
    }
  });
}

/* ════════════════════════════════════════════════════════════════
   Множественный выбор — toggle
════════════════════════════════════════════════════════════════ */
function toggleMulti(qIndex, key, btn) {
  const container = document.getElementById(`opts-${qIndex}`);
  if (container.dataset.answered) return;

  const active = btn.dataset.selected === "true";
  btn.dataset.selected = active ? "false" : "true";
  btn.classList.toggle("opt-selected", !active);
}

function submitMulti(qIndex) {
  const container = document.getElementById(`opts-${qIndex}`);
  if (container.dataset.answered) return;
  container.dataset.answered = "true";

  // Собираем выбранные
  const selected = [];
  container.querySelectorAll(".option-btn").forEach(btn => {
    if (btn.dataset.selected === "true") selected.push(btn.dataset.key);
  });

  container.querySelectorAll(".option-btn").forEach(b => b.disabled = true);
  document.getElementById(`submit-multi-${qIndex}`).disabled = true;

  answers.push({ index: qIndex, selected });

  sendCheck(qIndex, selected, (result) => {
    const correctSet = new Set(result.correct_answer);
    container.querySelectorAll(".option-btn").forEach(btn => {
      const k = btn.dataset.key;
      if (correctSet.has(k)) {
        applyState(btn, "correct");
      } else if (selected.includes(k)) {
        applyState(btn, "wrong");
      } else {
        btn.classList.add("opt-dim");
      }
    });
    showFeedback(qIndex, result);
    revealNext(qIndex);
  });
}

/* ════════════════════════════════════════════════════════════════
   Текстовый ввод
════════════════════════════════════════════════════════════════ */
function submitText(qIndex) {
  const container = document.getElementById(`opts-${qIndex}`);
  if (container.dataset.answered) return;

  const input = document.getElementById(`text-input-${qIndex}`);
  const value = input.value.trim();
  if (!value) { input.focus(); return; }

  container.dataset.answered = "true";
  input.disabled = true;
  document.querySelector(`#opts-${qIndex} button`).disabled = true;

  answers.push({ index: qIndex, selected: value });

  sendCheck(qIndex, value, (result) => {
    if (result.correct) {
      input.classList.add("is-valid");
    } else {
      input.classList.add("is-invalid");
    }
    showFeedback(qIndex, result);
    revealNext(qIndex);
  });
}

/* ════════════════════════════════════════════════════════════════
   POST /quests/api/check — проверяем один ответ сразу
════════════════════════════════════════════════════════════════ */
async function sendCheck(qIndex, selected, callback) {
  try {
    const res = await fetch("/quests/api/check", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic_id: TOPIC_ID,
        answers:  [{ index: qIndex, selected }],
      }),
    });
    const data   = await res.json();
    const result = data.results[0];

    if (result.correct) {
      score++;
      document.getElementById("score-display").textContent =
        `${score} / ${QUESTIONS.length}`;
    }

    callback(result);
  } catch (e) {
    console.error("Ошибка запроса:", e);
    revealNext(qIndex);
  }
}

/* ════════════════════════════════════════════════════════════════
   Фидбек под вопросом
════════════════════════════════════════════════════════════════ */
function showFeedback(qIndex, result) {
  const fb  = document.getElementById(`fb-${qIndex}`);
  fb.style.display = "block";

  let correctStr = "";
  if (result.type === "single") {
    const q    = QUESTIONS[qIndex];
    const text = q?.options?.[result.correct_answer] || result.correct_answer;
    correctStr = `<strong>${result.correct_answer}.</strong> ${text}`;
  } else if (result.type === "multi") {
    const q    = QUESTIONS[qIndex];
    correctStr = result.correct_answer
      .map(k => `<strong>${k}.</strong> ${q?.options?.[k] || k}`)
      .join(", ");
  } else {
    correctStr = `<strong>${result.correct_answer}</strong>`;
  }

  const explanation = result.explanation
    ? `<div class="mt-2 small opacity-75">${result.explanation}</div>` : "";

  if (result.correct) {
    fb.innerHTML = `
      <div class="alert alert-success d-flex gap-2 align-items-start py-2 mb-0">
        <i class="bi bi-check-circle-fill fs-5 mt-1 flex-shrink-0"></i>
        <div>
          <span class="fw-semibold">Верно!</span>${explanation}
        </div>
      </div>`;
  } else {
    fb.innerHTML = `
      <div class="alert alert-danger d-flex gap-2 align-items-start py-2 mb-0">
        <i class="bi bi-x-circle-fill fs-5 mt-1 flex-shrink-0"></i>
        <div>
          <span class="fw-semibold">Неверно.</span>
          Правильный ответ: ${correctStr}
          ${explanation}
        </div>
      </div>`;
  }
}

/* ════════════════════════════════════════════════════════════════
   Вспомогательные
════════════════════════════════════════════════════════════════ */
function applyState(btn, state) {
  btn.classList.remove("btn-outline-secondary", "opt-selected", "opt-dim");
  if (state === "correct") {
    btn.classList.add("btn-success", "text-white", "ans-correct");
    btn.querySelector(".opt-letter").style.color = "#fff";
  } else {
    btn.classList.add("btn-danger", "text-white", "ans-wrong");
    btn.querySelector(".opt-letter").style.color = "#fff";
  }
}

function revealNext(qIndex) {
  const btn = document.getElementById(`next-${qIndex}`);
  if (btn) btn.style.display = "inline-block";
}

function nextQuestion(qIndex) {
  const nextIdx = qIndex + 1;
  if (nextIdx < QUESTIONS.length) {
    current = nextIdx;
    showQuestion(nextIdx);
  } else {
    finishQuiz();
  }
}

/* ════════════════════════════════════════════════════════════════
   Финал — POST /quests/api/check со всеми ответами → результаты
════════════════════════════════════════════════════════════════ */
async function finishQuiz() {
  let data;
  try {
    const res = await fetch("/quests/api/check", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic_id: TOPIC_ID, answers }),
    });
    data = await res.json();
  } catch {
    data = { score, total: QUESTIONS.length, results: [] };
  }
  showResult(data);
}

/* ════════════════════════════════════════════════════════════════
   Экран результата
════════════════════════════════════════════════════════════════ */
function showResult(data) {
  document.getElementById("quiz-container").style.display = "none";
  document.getElementById("progress-bar").style.width    = "100%";

  const screen = document.getElementById("result-screen");
  screen.style.display = "block";
  screen.scrollIntoView({ behavior: "smooth", block: "start" });

  const { score: s, total: t, results } = data;
  const pct = Math.round((s / t) * 100);

  // Кольцо
  const offset = 327 - (pct / 100) * 327;
  setTimeout(() => {
    document.getElementById("ring-arc").style.strokeDashoffset = offset;
  }, 100);

  document.getElementById("r-score").textContent = `${s}/${t}`;
  document.getElementById("r-pct").textContent   = `${pct}%`;

  // Заголовок
  const [title, sub] =
    pct === 100 ? ["Идеально! 🏆", "Все ответы верны — отличное знание темы!"] :
    pct >= 75   ? ["Отличный результат 👍", "Совсем немного до идеала!"] :
    pct >= 50   ? ["Хороший старт 📚", "Повторите слабые места и попробуйте снова."] :
                  ["Есть над чем поработать 💡", "Изучите тему подробнее и пройдите тест снова."];

  document.getElementById("r-title").textContent = title;
  document.getElementById("r-sub").textContent   = sub;

  // Разбор ошибок
  const errors = results.filter(r => !r.correct);
  const breakdown = document.getElementById("r-breakdown");

  if (errors.length === 0) {
    breakdown.innerHTML = `
      <div class="alert alert-success text-center fw-semibold mb-0">
        <i class="bi bi-trophy-fill me-2"></i>Все ответы правильные!
      </div>`;
    return;
  }

  breakdown.innerHTML = `
    <h6 class="fw-bold text-muted mb-3">
      <i class="bi bi-journal-x me-1"></i>Разбор ошибок (${errors.length} из ${t})
    </h6>
    ${errors.map(r => {
      const q         = QUESTIONS[r.index];
      const userAns   = answers.find(a => a.index === r.index)?.selected;

      // Формируем строки «ваш ответ» и «правильно»
      let userStr, correctStr;

      if (r.type === "single") {
        const uText = q?.options?.[userAns] || userAns || "—";
        const cText = q?.options?.[r.correct_answer] || r.correct_answer;
        userStr    = `${userAns}. ${uText}`;
        correctStr = `${r.correct_answer}. ${cText}`;

      } else if (r.type === "multi") {
        const uArr = Array.isArray(userAns) ? userAns : [];
        userStr    = uArr.length
          ? uArr.map(k => `${k}. ${q?.options?.[k] || k}`).join("; ")
          : "Ничего не выбрано";
        correctStr = r.correct_answer
          .map(k => `${k}. ${q?.options?.[k] || k}`).join("; ");

      } else {
        userStr    = userAns || "—";
        correctStr = r.correct_answer;
      }

      const typePill = {
        single: "Одиночный",
        multi:  "Множественный",
        text:   "Текстовый",
      }[r.type] || r.type;

      return `
        <div class="breakdown-card card border-danger-subtle mb-3">
          <div class="card-body p-3">
            <div class="d-flex justify-content-between align-items-start mb-2 gap-2">
              <p class="fw-semibold mb-0 small text-danger-emphasis lh-sm">${q?.text || ""}</p>
              <span class="badge bg-danger-subtle text-danger flex-shrink-0">${typePill}</span>
            </div>
            <div class="d-flex flex-column gap-1 small">
              <div>
                <span class="text-muted">Ваш ответ: </span>
                <span class="text-danger fw-semibold">${userStr}</span>
              </div>
              <div>
                <span class="text-muted">Правильно: </span>
                <span class="text-success fw-semibold">${correctStr}</span>
              </div>
              ${r.explanation ? `
              <div class="mt-1 text-muted border-top pt-1">
                <i class="bi bi-lightbulb me-1"></i>${r.explanation}
              </div>` : ""}
            </div>
          </div>
        </div>`;
    }).join("")}`;
}