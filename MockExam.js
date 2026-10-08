/* ==========================================================================
   GDD MOCK EXAM ARENA - CORE ENGINE (JAVASCRIPT)
   ========================================================================== */

// STATE MANAGEMENT (Single Source of Truth: Dữ liệu được nạp động từ question.csv và source/)
const STATE = {
    allQuestions: [],
    currentExamQuestions: [],
    mode: "STUDY", // "STUDY" hoặc "EXAM"
    currentIndex: 0,
    userAnswers: {}, // index -> { chosenOptionIndex, isCorrect, options }
    timerInterval: null,
    timeRemainingSeconds: 0,
    totalDurationSeconds: 0,
    strictForward: true,
    codeCache: {},
    tempMultiSelections: {} // index -> Set of chosen option indices
};

// DOM ELEMENTS
const DOM = {
    lobbyScreen: document.getElementById('lobby-screen'),
    examScreen: document.getElementById('exam-screen'),
    resultScreen: document.getElementById('result-screen'),

    // Branding & Header
    pageTitle: document.getElementById('page-title'),
    brandLogo: document.getElementById('brand-logo'),
    brandTitle: document.getElementById('brand-title'),
    brandSubtext: document.getElementById('brand-subtext'),
    historyBtnText: document.getElementById('history-btn-text'),

    // Lobby
    lobbyHeading: document.getElementById('lobby-heading'),
    lobbyDesc: document.getElementById('lobby-desc'),
    btnStartStudy: document.querySelector('.btn-start-study'),
    btnRetryMistakes: document.getElementById('btn-retry-mistakes'),
    mistakesCountBadge: document.getElementById('mistakes-count-badge'),
    btnStartExam: document.querySelector('.btn-start-exam'),
    inputQCount: document.getElementById('exam-question-count'),
    inputTimeLimit: document.getElementById('exam-time-limit'),
    maxQBadge: document.getElementById('max-q-badge'),
    checkStrictForward: document.getElementById('exam-strict-forward'),
    loadedStatusText: document.getElementById('loaded-status-text'),

    // Exam Arena
    currentModePill: document.getElementById('current-mode-pill'),
    topicPill: document.getElementById('question-topic-pill'),
    diffPill: document.getElementById('question-diff-pill'),
    formatPill: document.getElementById('question-format-pill'),
    typePill: document.getElementById('question-type-pill'),
    currentQIndex: document.getElementById('current-q-index'),
    totalQCount: document.getElementById('total-q-count'),
    progressBarFill: document.getElementById('progress-bar-fill'),
    timerBox: document.getElementById('timer-box'),
    timerDisplay: document.getElementById('timer-display'),

    questionText: document.getElementById('question-text'),
    codeWrapper: document.getElementById('code-wrapper'),
    codeFilename: document.getElementById('code-filename'),
    codeBlock: document.getElementById('code-block'),
    optionsGrid: document.getElementById('options-grid'),
    explanationBox: document.getElementById('explanation-box'),
    expHeading: document.getElementById('exp-heading'),
    expContent: document.getElementById('exp-content'),

    btnPrevQuestion: document.getElementById('btn-prev-question'),
    btnNextQuestion: document.getElementById('btn-next-question'),
    btnFinishExam: document.getElementById('btn-finish-exam'),
    btnQuitStudy: document.getElementById('btn-quit-study'),

    // Result
    trophyBadge: document.getElementById('trophy-badge'),
    resultRankTitle: document.getElementById('result-rank-title'),
    resultRankDesc: document.getElementById('result-rank-desc'),
    resultScoreNum: document.getElementById('result-score-num'),
    resultScoreDenom: document.getElementById('result-score-denom'),
    resultScorePercent: document.getElementById('result-score-percent'),
    resultScoreMeta: document.getElementById('result-score-meta'),
    reviewList: document.getElementById('review-list'),
    btnRestartExam: document.getElementById('btn-restart-exam'),
    btnBackLobby: document.getElementById('btn-back-lobby'),

    // CSV Import & History
    btnImportCsv: document.getElementById('btn-import-csv'),
    csvFileInput: document.getElementById('csv-file-input'),
    btnShowHistory: document.getElementById('btn-show-history'),
    historyModal: document.getElementById('history-modal'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnCloseHistoryBottom: document.getElementById('btn-close-history-bottom'),
    btnClearHistory: document.getElementById('btn-clear-history'),
    historyTable: document.getElementById('history-table'),
    historyTableBody: document.getElementById('history-table-body'),
    historyEmpty: document.getElementById('history-empty'),
    historyModalTitle: document.getElementById('history-modal-title')
};

// ==========================================================================
// CƠ CHẾ THEME HỌC THUẬT MẶC ĐỊNH & SECRET GDD OVERRIDE
// ==========================================================================
const DEFAULT_THEME = {
    page_title: "Hệ Thống Thi Thử Trắc Nghiệm C++ OOP",
    brand_logo: "💻",
    brand_title: "HỆ THỐNG THI THỬ TRẮC NGHIỆM C++ OOP",
    brand_subtext: "",
    lobby_heading: "CHỌN CHẾ ĐỘ THI THỬ",
    lobby_desc: "Vui lòng chọn chế độ làm bài phù hợp để bắt đầu luyện tập hoặc kiểm tra kiến thức!",
    history_btn: "📜 Lịch Sử Thi",
    history_modal_title: "📜 LỊCH SỬ THI THỬ",
    history_empty_msg: "Chưa có bản lưu kết quả nào. Hãy hoàn thành một bài thi thử trước nhé!",
    user_label: "bạn",
    mistakes_btn_tooltip_empty: "Hiện không có câu sai nào trong danh sách!",
    mistakes_btn_tooltip_has: "Bạn đang có {count} câu làm sai cần ôn tập lại!",
    ranks: {
        under_50: {
            trophy: "🛡️",
            title: "KẾT QUẢ: CẦN CỐ GẮNG ÔN TẬP THÊM!",
            desc: "Hãy ôn lại các khái niệm cơ bản về lập trình hướng đối tượng và làm lại các câu bị sai nhé."
        },
        under_80: {
            trophy: "📘",
            title: "XẾP LOẠI: ĐẠT YÊU CẦU (KHÁ)!",
            desc: "Bạn đã nắm được các kiến thức cốt lõi. Hãy chú ý hơn đến các trường hợp biên và cạm bẫy cú pháp."
        },
        under_100: {
            trophy: "🌟",
            title: "XẾP LOẠI: GIỎI!",
            desc: "Rất tốt! Bạn đã làm chủ hầu hết các quy tắc, chỉ cần rà soát lại một vài chi tiết nhỏ."
        },
        perfect: {
            trophy: "🏆",
            title: "XẾP LOẠI: XUẤT SẮC (100%)!",
            desc: "Hoàn hảo tuyệt đối! Bạn đã hoàn thành chính xác toàn bộ câu hỏi trong bài thi thử."
        }
    }
};

let ACTIVE_THEME = Object.assign({}, DEFAULT_THEME);

function getUserLabel() {
    return (ACTIVE_THEME && ACTIVE_THEME.user_label) || DEFAULT_THEME.user_label;
}

async function tryLoadSecretTheme() {
    try {
        let res = await fetch('gdd_secrets.json');
        if (!res.ok) {
            res = await fetch('gdd_secret.json');
        }
        if (res.ok) {
            const secretData = await res.json();
            if (secretData && secretData.enabled) {
                ACTIVE_THEME = Object.assign({}, DEFAULT_THEME, secretData);
                applyActiveTheme();
            }
        }
    } catch (e) {
        // gdd_secrets.json không tồn tại -> Giữ nguyên giao diện học thuật mặc định
    }
}

function applyActiveTheme() {
    if (DOM.pageTitle && ACTIVE_THEME.page_title) {
        DOM.pageTitle.textContent = ACTIVE_THEME.page_title;
        document.title = ACTIVE_THEME.page_title;
    }
    if (DOM.brandLogo && ACTIVE_THEME.brand_logo) {
        DOM.brandLogo.textContent = ACTIVE_THEME.brand_logo;
    }
    if (DOM.brandTitle && ACTIVE_THEME.brand_title) {
        DOM.brandTitle.textContent = ACTIVE_THEME.brand_title;
    }
    if (DOM.brandSubtext) {
        if (ACTIVE_THEME.brand_subtext && ACTIVE_THEME.brand_subtext.trim()) {
            DOM.brandSubtext.textContent = ACTIVE_THEME.brand_subtext;
            DOM.brandSubtext.style.display = 'block';
        } else {
            DOM.brandSubtext.style.display = 'none';
        }
    }
    if (DOM.historyBtnText && ACTIVE_THEME.history_btn) {
        DOM.historyBtnText.textContent = ACTIVE_THEME.history_btn;
    }
    if (DOM.historyModalTitle && ACTIVE_THEME.history_modal_title) {
        DOM.historyModalTitle.textContent = ACTIVE_THEME.history_modal_title;
    }
    if (DOM.historyEmpty && ACTIVE_THEME.history_empty_msg) {
        DOM.historyEmpty.textContent = ACTIVE_THEME.history_empty_msg;
    }
    if (DOM.lobbyHeading && ACTIVE_THEME.lobby_heading) {
        DOM.lobbyHeading.textContent = ACTIVE_THEME.lobby_heading;
    }
    if (DOM.lobbyDesc && ACTIVE_THEME.lobby_desc) {
        DOM.lobbyDesc.textContent = ACTIVE_THEME.lobby_desc;
    }
    updateMistakesButtonUI();
}

// ==========================================================================
// KHỞI ĐỘNG VÀ NẠP DỮ LIỆU ĐỘNG TỪ BÊN NGOÀI
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    updateMaxQuestionLimit();
    updateMistakesButtonUI();
    tryFetchCsvFile();
    tryFetchMistakesFromServer();
    tryFetchMasteryFromServer();
    tryLoadSecretTheme();
});

// Tự động nạp question.csv từ máy chủ nội bộ (Không lưu trùng lặp)
async function tryFetchCsvFile() {
    try {
        const response = await fetch('question.csv');
        if (response.ok) {
            const csvText = await response.text();
            const parsed = parseCsvToQuestions(csvText);
            if (parsed.length > 0) {
                STATE.allQuestions = parsed;
                updateMaxQuestionLimit();
                updateMistakesButtonUI();
                updateLobbyStatus(`Đã kết nối thành công: Tự động nạp <strong>${parsed.length} câu hỏi</strong> từ question.csv!`);
                return;
            }
        }
    } catch (e) {
        updateLobbyStatus(`⚠️ Đang mở qua file:// cục bộ. Hãy chạy file <strong>start_arena.bat</strong> để kết nối máy chủ tự động nạp đề!`);
    }
}

// Đồng bộ danh sách câu sai từ server nếu có
async function tryFetchMistakesFromServer() {
    try {
        const res = await fetch('/api/mistakes');
        if (res.ok) {
            const serverMistakes = await res.json();
            if (Array.isArray(serverMistakes) && serverMistakes.length > 0) {
                const current = new Set(getMistakeQuestionIds());
                serverMistakes.forEach(id => current.add(parseInt(id)));
                localStorage.setItem(MISTAKES_STORAGE_KEY, JSON.stringify(Array.from(current)));
                updateMistakesButtonUI();
            }
        }
    } catch (e) {
        // Chế độ file:// hoặc máy chủ tĩnh không có API
    }
}

// Xử lý nạp file CSV thủ công nếu người dùng chọn file từ máy
DOM.btnImportCsv.addEventListener('click', () => {
    DOM.csvFileInput.click();
});

DOM.csvFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        const text = event.target.result;
        const parsed = parseCsvToQuestions(text);
        if (parsed.length > 0) {
            STATE.allQuestions = parsed;
            updateMaxQuestionLimit();
            updateMistakesButtonUI();
            alert(`🎉 Nạp thành công ${parsed.length} câu hỏi từ ${file.name}!`);
            updateLobbyStatus(`Đã nạp <strong>${parsed.length} câu hỏi</strong> từ file tùy chỉnh: ${file.name}`);
        } else {
            alert('⚠️ File CSV không đúng định dạng hoặc không có câu hỏi hợp lệ!');
        }
    };
    reader.readAsText(file);
});

function updateLobbyStatus(msg) {
    DOM.loadedStatusText.innerHTML = msg;
}

function updateMaxQuestionLimit() {
    const total = STATE.allQuestions.length;
    if (DOM.maxQBadge) {
        DOM.maxQBadge.textContent = `(Tối đa: ${total})`;
    }
    if (DOM.inputQCount) {
        DOM.inputQCount.max = total;
        if (parseInt(DOM.inputQCount.value) > total || parseInt(DOM.inputQCount.value) <= 0) {
            DOM.inputQCount.value = Math.min(5, total);
        }
    }
}

// ==========================================================================
// CSV PARSER (Hỗ trợ 11 cột cũ và 12 cột mới, opt1 luôn là đáp án đúng)
// ==========================================================================
function parseCsvToQuestions(csvText) {
    // 1. Phân tách các ô và hàng CSV theo chuẩn RFC 4180 (Bảo toàn xuống dòng \n bên trong dấu ngoặc kép "")
    const rows = [];
    let curRow = [];
    let curField = '';
    let inQuotes = false;

    for (let i = 0; i < csvText.length; i++) {
        const c = csvText[i];
        if (c === '"') {
            if (inQuotes && csvText[i + 1] === '"') {
                curField += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (c === ',' && !inQuotes) {
            curRow.push(curField.trim());
            curField = '';
        } else if ((c === '\r' || c === '\n') && !inQuotes) {
            if (c === '\r' && csvText[i + 1] === '\n') {
                i++;
            }
            curRow.push(curField.trim());
            curField = '';
            if (curRow.some(f => f.length > 0)) {
                rows.push(curRow);
            }
            curRow = [];
        } else {
            curField += c;
        }
    }
    if (curField.length > 0 || curRow.length > 0) {
        curRow.push(curField.trim());
        if (curRow.some(f => f.length > 0)) {
            rows.push(curRow);
        }
    }

    if (rows.length < 2) return [];

    const header = rows[0];
    const hasTypeCol = header.some(h => h.trim().toLowerCase() === 'question_type');

    const questions = [];
    // Bỏ qua dòng tiêu đề (Header: row 0)
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (row.length < 6) continue;

        let id, topic, difficulty, question_type, question, code_file, optStartIndex, explanation;

        if (hasTypeCol) {
            // Định dạng mới 12 cột: id,topic,difficulty,question_type,question,code_file,opt1..opt5,explanation
            id = parseInt(row[0]) || i;
            topic = row[1] || 'OOP';
            difficulty = row[2] || 'Medium';
            question_type = row[3] || 'Output';
            question = row[4] || 'Câu hỏi';
            code_file = row[5] ? row[5].trim() : '';
            optStartIndex = 6;
            explanation = row[11] || 'Chưa có giải thích.';
        } else {
            // Định dạng cũ 11 cột: id,topic,difficulty,question,code_file,opt1..opt5,explanation
            id = parseInt(row[0]) || i;
            topic = row[1] || 'OOP';
            difficulty = row[2] || 'Medium';
            question = row[3] || 'Câu hỏi';
            code_file = row[4] ? row[4].trim() : '';
            question_type = code_file ? 'Code' : 'Concept_Apply';
            optStartIndex = 5;
            explanation = row[10] || 'Chưa có giải thích.';
        }

        let isMulti = false;
        let correctCount = 1;
        const multiMatch = (question_type || '').match(/^(?:Multi_Select|Multi_Choice|Multi)[:_]?(\d+)?$/i);
        if (multiMatch) {
            isMulti = true;
            correctCount = multiMatch[1] !== undefined ? parseInt(multiMatch[1], 10) : 2;
        }

        // Thu thập các options (Nếu isMulti thì correctCount options đầu tiên là đúng, ngược lại opt1 luôn đúng)
        const rawOptions = [];
        for (let optIdx = optStartIndex; optIdx < optStartIndex + 5; optIdx++) {
            if (row[optIdx] && row[optIdx].trim().length > 0) {
                rawOptions.push(row[optIdx].trim());
            }
        }

        // Ít nhất phải có 2 lựa chọn
        if (rawOptions.length < 2) continue;

        questions.push({
            id,
            topic,
            difficulty,
            question_type,
            isMulti,
            correctCount: Math.min(correctCount, rawOptions.length),
            question,
            code_file,
            rawOptions, // Trong đó correctCount phần tử đầu tiên LUÔN là đáp án đúng!
            explanation
        });
    }
    return questions;
}

// Xáo trộn các phương án (Hỗ trợ câu đơn opt1 đúng và câu chọn nhiều correctCount ý đầu đúng)
function prepareShuffledOptions(rawOptions, correctCount = 1) {
    const items = rawOptions.map((text, idx) => ({
        text,
        isCorrect: (idx < correctCount)
    }));
    shuffleArray(items);
    return items;
}

// ==========================================================================
// ĐIỀU HƯỚNG MÀN HÌNH & CHẾ ĐỘ THI
// ==========================================================================
function initEventListeners() {
    DOM.btnStartStudy.addEventListener('click', () => startSession('STUDY'));
    if (DOM.btnRetryMistakes) {
        DOM.btnRetryMistakes.addEventListener('click', () => startSession('MISTAKE_STUDY'));
    }
    DOM.btnStartExam.addEventListener('click', () => startSession('EXAM'));

    DOM.btnPrevQuestion.addEventListener('click', () => navigateQuestion(-1));
    DOM.btnNextQuestion.addEventListener('click', () => navigateQuestion(1));
    DOM.btnFinishExam.addEventListener('click', confirmFinishExam);
    DOM.btnQuitStudy.addEventListener('click', handleQuitStudy);

    DOM.btnRestartExam.addEventListener('click', restartCurrentSession);
    DOM.btnBackLobby.addEventListener('click', returnToLobby);

    // Modal Lịch sử
    DOM.btnShowHistory.addEventListener('click', openHistoryModal);
    DOM.btnCloseModal.addEventListener('click', closeHistoryModal);
    DOM.btnCloseHistoryBottom.addEventListener('click', closeHistoryModal);
    DOM.btnClearHistory.addEventListener('click', clearExamHistory);
}

function startSession(mode) {
    STATE.mode = mode;
    STATE.currentIndex = 0;
    STATE.userAnswers = {};
    STATE.tempMultiSelections = {};
    clearInterval(STATE.timerInterval);

    // Chuẩn bị danh sách câu hỏi
    let selectedPool = [...STATE.allQuestions];

    if (mode === 'EXAM') {
        const totalAvailable = STATE.allQuestions.length;
        const countVal = parseInt(DOM.inputQCount.value);
        const minutes = parseInt(DOM.inputTimeLimit.value);

        // KIỂM TRA SỐ LƯỢNG CÂU HỎI
        if (isNaN(countVal) || countVal <= 0) {
            alert(`⚠️ ${getUserLabel()} ơi, số lượng câu thi phải lớn hơn 0 nhé!`);
            DOM.inputQCount.focus();
            return;
        }

        if (countVal > totalAvailable) {
            alert(`⛔ KHÔNG THỂ VÀO THI!\n\nSố lượng câu ${getUserLabel()} muốn thi (${countVal} câu) đang VƯỢT QUÁ số câu hiện có trong ngân hàng (${totalAvailable} câu)!\n\nVui lòng nhập số nhỏ hơn hoặc bằng ${totalAvailable} nhé ${getUserLabel()}!`);
            DOM.inputQCount.focus();
            return;
        }

        // KIỂM TRA THỜI GIAN
        if (isNaN(minutes) || minutes <= 0) {
            alert(`⚠️ ${getUserLabel()} ơi, thời gian làm bài phải từ 1 phút trở lên nhé!`);
            DOM.inputTimeLimit.focus();
            return;
        }

        DOM.btnQuitStudy.classList.add('hidden');
        // BẢO VỆ PHÒNG THI: Không được thoát ngang xương, cảnh báo nếu đóng/tải lại trang
        window.onbeforeunload = function (e) {
            e.preventDefault();
            return `${getUserLabel()} đang trong phòng thi! Nếu rời đi kết quả sẽ không được ghi nhận!`;
        };

        // Bốc thăm câu hỏi theo thuật toán Gacha trọng số thích ứng (Adaptive Weighted Gacha)
        STATE.currentExamQuestions = sampleQuestionsByMastery(selectedPool, countVal);

        // Cài đặt thời gian
        STATE.timeRemainingSeconds = minutes * 60;
        STATE.totalDurationSeconds = STATE.timeRemainingSeconds;
        STATE.strictForward = DOM.checkStrictForward.checked;

        DOM.timerBox.classList.remove('hidden');
        startExamTimer();
    } else if (mode === 'MISTAKE_STUDY') {
        const mistakeIds = getMistakeQuestionIds();
        const pool = STATE.allQuestions.filter(q => mistakeIds.includes(q.id));
        if (pool.length === 0) {
            alert(`🎉 ${getUserLabel()} ơi, hiện tại không có câu sai nào trong danh sách cần làm lại!`);
            return;
        }

        DOM.btnQuitStudy.classList.remove('hidden');
        window.onbeforeunload = null;

        STATE.currentExamQuestions = pool;
        STATE.strictForward = false;
        DOM.timerBox.classList.add('hidden');
    } else {
        // STUDY MODE: Thoải mái học tập, có nút thoát về sảnh bất cứ lúc nào!
        DOM.btnQuitStudy.classList.remove('hidden');
        window.onbeforeunload = null;

        // Ưu tiên câu có độ thông thạo thấp (cần rèn luyện) lên trước
        const studyPool = [...selectedPool];
        shuffleArray(studyPool);
        const mastery = getQuestionMasteryMap();
        studyPool.sort((a, b) => (mastery[String(a.id)] || 0) - (mastery[String(b.id)] || 0));

        STATE.currentExamQuestions = studyPool;
        STATE.strictForward = false;
        DOM.timerBox.classList.add('hidden');
    }

    // Chuẩn bị các phương án xáo trộn cho từng câu hỏi & Tải trước (Prefetch) mã nguồn
    STATE.currentExamQuestions.forEach(q => {
        q.shuffledOptions = prepareShuffledOptions(q.rawOptions, q.isMulti ? q.correctCount : 1);
        if (q.code_file && q.code_file.trim()) {
            prefetchCodeFile(q.code_file.trim());
        }
    });

    // Chuyển màn hình
    switchScreen('EXAM_ARENA');
    renderCurrentQuestion();
}

function switchScreen(screenName) {
    DOM.lobbyScreen.classList.add('hidden');
    DOM.examScreen.classList.add('hidden');
    DOM.resultScreen.classList.add('hidden');

    if (screenName === 'LOBBY') DOM.lobbyScreen.classList.remove('hidden');
    if (screenName === 'EXAM_ARENA') DOM.examScreen.classList.remove('hidden');
    if (screenName === 'RESULT') DOM.resultScreen.classList.remove('hidden');
}

// ==========================================================================
// RENDER CÂU HỎI VÀ ĐÁP ÁN
// ==========================================================================
async function renderCurrentQuestion() {
    const q = STATE.currentExamQuestions[STATE.currentIndex];
    const total = STATE.currentExamQuestions.length;

    // Cập nhật Header
    if (STATE.mode === 'STUDY') {
        DOM.currentModePill.textContent = 'CHẾ ĐỘ HỌC TẬP';
    } else if (STATE.mode === 'MISTAKE_STUDY') {
        DOM.currentModePill.textContent = 'LÀM LẠI CÂU SAI';
    } else {
        DOM.currentModePill.textContent = 'PHÒNG THI THẬT';
    }
    DOM.topicPill.textContent = q.topic || 'OOP';

    // Cập nhật Độ khó và Phối màu
    DOM.diffPill.textContent = q.difficulty || 'Medium';
    DOM.diffPill.className = 'difficulty-pill';
    const dLower = (q.difficulty || '').toLowerCase();
    if (dLower === 'easy') DOM.diffPill.classList.add('diff-easy');
    else if (dLower === 'medium') DOM.diffPill.classList.add('diff-medium');
    else if (dLower === 'calculation') DOM.diffPill.classList.add('diff-calc');
    else if (dLower === 'trap') DOM.diffPill.classList.add('diff-trap');
    else if (dLower === 'smokescreen') DOM.diffPill.classList.add('diff-smoke');
    else if (dLower === 'boss') DOM.diffPill.classList.add('diff-boss');

    // Cập nhật Thể loại (Code vs Lý thuyết)
    if (DOM.formatPill) {
        if (q.code_file && q.code_file.trim().length > 0) {
            DOM.formatPill.textContent = '💻 CODE';
            DOM.formatPill.className = 'format-pill';
        } else {
            DOM.formatPill.textContent = '📖 LÝ THUYẾT';
            DOM.formatPill.className = 'format-pill format-theory';
        }
    }

    // Cập nhật Dạng bài (question_type)
    if (DOM.typePill) {
        if (q.isMulti) {
            DOM.typePill.textContent = '☑️ CHỌN NHIỀU';
            DOM.typePill.style.borderColor = '#A855F7';
            DOM.typePill.style.color = '#C084FC';
        } else {
            DOM.typePill.textContent = q.question_type || (q.code_file ? 'Code' : 'Lý Thuyết');
            DOM.typePill.style.borderColor = '';
            DOM.typePill.style.color = '';
        }
    }

    DOM.currentQIndex.textContent = STATE.currentIndex + 1;
    DOM.totalQCount.textContent = total;

    const progressPercent = ((STATE.currentIndex + 1) / total) * 100;
    DOM.progressBarFill.style.width = `${progressPercent}%`;

    // Hiển thị nội dung câu hỏi
    DOM.questionText.textContent = q.question;

    // Hiển thị Code Snippet
    if (q.code_file && q.code_file.trim().length > 0) {
        DOM.codeWrapper.classList.remove('hidden');
        DOM.codeFilename.textContent = q.code_file;
        DOM.codeBlock.textContent = '// Đang tải mã nguồn...';
        loadCodeSnippet(q.code_file);
    } else {
        DOM.codeWrapper.classList.add('hidden');
    }

    // Render danh sách Options (3 đến 5 đáp án)
    DOM.optionsGrid.innerHTML = '';
    DOM.optionsGrid.classList.toggle('is-multi-select', !!q.isMulti);
    const alphabet = ['A', 'B', 'C', 'D', 'E'];
    const currentSavedAnswer = STATE.userAnswers[STATE.currentIndex];

    // Đối với câu Chọn nhiều (Multi-Select): Khởi tạo tập chọn tạm thời nếu chưa có
    if (q.isMulti && !STATE.tempMultiSelections[STATE.currentIndex]) {
        if (currentSavedAnswer && currentSavedAnswer.chosenIndices) {
            STATE.tempMultiSelections[STATE.currentIndex] = new Set(currentSavedAnswer.chosenIndices);
        } else {
            STATE.tempMultiSelections[STATE.currentIndex] = new Set();
        }
    }
    const currentTempSet = q.isMulti ? (STATE.tempMultiSelections[STATE.currentIndex] || new Set()) : null;

    q.shuffledOptions.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = `option-btn ${q.isMulti ? 'multi-option' : ''}`;

        // Kiểm tra xem option này có đang được chọn không
        let isChosen = false;
        if (q.isMulti) {
            if (currentSavedAnswer && currentSavedAnswer.chosenIndices) {
                isChosen = currentSavedAnswer.chosenIndices.includes(idx);
            } else if (currentTempSet) {
                isChosen = currentTempSet.has(idx);
            }
        } else {
            isChosen = (currentSavedAnswer && currentSavedAnswer.chosenIndex === idx);
        }

        if (isChosen) {
            btn.classList.add('selected');
        }

        let tagHtml = '';

        // Trong chế độ STUDY MODE & MISTAKE_STUDY, nếu đã trả lời thì hiện đánh giá
        if ((STATE.mode === 'STUDY' || STATE.mode === 'MISTAKE_STUDY') && currentSavedAnswer) {
            btn.disabled = true;
            if (q.isMulti) {
                if (opt.isCorrect && isChosen) {
                    btn.classList.add('correct-reveal');
                    tagHtml = `<span class="multi-tag tag-correct">✓ ĐÚNG</span>`;
                } else if (opt.isCorrect && !isChosen) {
                    btn.classList.add('missed-reveal');
                    tagHtml = `<span class="multi-tag tag-missed">⚠️ BỎ SÓT</span>`;
                } else if (!opt.isCorrect && isChosen) {
                    btn.classList.add('wrong-reveal');
                    tagHtml = `<span class="multi-tag tag-wrong">✗ DÍNH BẪY</span>`;
                } else {
                    btn.classList.add('dimmed-reveal');
                }
            } else {
                if (opt.isCorrect) {
                    btn.classList.add('correct-reveal');
                } else if (isChosen) {
                    btn.classList.add('wrong-reveal');
                }
            }
        } else {
            if (q.isMulti) {
                btn.addEventListener('click', () => handleMultiOptionToggle(idx));
            } else {
                btn.addEventListener('click', () => handleOptionClick(idx));
            }
        }

        btn.innerHTML = `
            ${q.isMulti ? `<span class="option-checkbox ${isChosen ? 'checked' : ''}"></span>` : ''}
            <span class="option-key ${q.isMulti ? 'checkbox-key' : ''}">${alphabet[idx]}</span>
            <span class="option-text">${escapeHtml(opt.text)}</span>
            ${tagHtml}
        `;

        DOM.optionsGrid.appendChild(btn);
    });

    // Thêm nút "XÁC NHẬN CHỌN" cho câu chọn nhiều trong STUDY / MISTAKE_STUDY nếu chưa nộp
    if (q.isMulti && (STATE.mode === 'STUDY' || STATE.mode === 'MISTAKE_STUDY') && !currentSavedAnswer) {
        const confirmWrap = document.createElement('div');
        confirmWrap.className = 'multi-confirm-wrap';
        confirmWrap.innerHTML = `
            <button class="btn-primary btn-confirm-multi" id="btn-confirm-multi">
                XÁC NHẬN CHỌN ☑️
            </button>
        `;
        confirmWrap.querySelector('#btn-confirm-multi').addEventListener('click', handleConfirmMulti);
        DOM.optionsGrid.appendChild(confirmWrap);
    }

    // Giải thích (Chỉ hiện trong Study Mode & MISTAKE_STUDY khi đã trả lời)
    if ((STATE.mode === 'STUDY' || STATE.mode === 'MISTAKE_STUDY') && currentSavedAnswer) {
        DOM.explanationBox.classList.remove('hidden');
        if (q.isMulti && DOM.expHeading) {
            const { chosenIndices, isCorrect } = currentSavedAnswer;
            const correctTotal = q.shuffledOptions.filter(o => o.isCorrect).length;
            const truePositive = (chosenIndices || []).filter(i => q.shuffledOptions[i].isCorrect).length;
            const falsePositive = (chosenIndices || []).filter(i => !q.shuffledOptions[i].isCorrect).length;
            const missed = correctTotal - truePositive;

            if (isCorrect) {
                DOM.expHeading.innerHTML = `<span style="color: #10B981;">🎉 HOÀN HẢO (+1đ):</span> ${correctTotal === 0 ? 'Bạn đã nhận diện chính xác: Không có đáp án nào đúng trong câu này!' : `Bạn đã chọn chính xác toàn bộ ${correctTotal} ý đúng!`}`;
            } else {
                DOM.expHeading.innerHTML = `<span style="color: #F59E0B;">⚠️ CHƯA HOÀN HẢO (0đ):</span> ${correctTotal === 0 ? `Câu này KHÔNG có đáp án nào đúng (bạn đã dính bẫy ${falsePositive} ý sai)` : (chosenIndices.length === 0 ? `Bạn không chọn ý nào trong khi câu hỏi có ${correctTotal} ý đúng (bỏ sót cả ${correctTotal} ý)` : `Chọn đúng ${truePositive}/${correctTotal} ý${missed > 0 ? ` (bỏ sót ${missed})` : ''}${falsePositive > 0 ? ` (dính bẫy ${falsePositive})` : ''}`)} • Đã lưu vào hàng chờ câu sai!`;
            }
        } else if (DOM.expHeading) {
            DOM.expHeading.textContent = 'BÍ KÍP GIẢI MÃ CẠM BẪY';
        }
        DOM.expContent.textContent = q.explanation;
    } else {
        DOM.explanationBox.classList.add('hidden');
    }

    // Nút điều khiển chân trang
    updateFooterButtons();
}

async function prefetchCodeFile(filename) {
    if (STATE.codeCache[filename]) return;
    try {
        const response = await fetch(`source/${filename}`);
        if (response.ok) {
            const text = await response.text();
            STATE.codeCache[filename] = text;
        }
    } catch (e) {}
}

async function loadCodeSnippet(filename) {
    if (STATE.codeCache[filename]) {
        DOM.codeBlock.innerHTML = highlightCppCode(STATE.codeCache[filename]);
        return;
    }

    DOM.codeBlock.textContent = '// Đang tải mã nguồn...';

    try {
        const response = await fetch(`source/${filename}`);
        if (response.ok) {
            const text = await response.text();
            STATE.codeCache[filename] = text;
            DOM.codeBlock.innerHTML = highlightCppCode(text);
        } else {
            DOM.codeBlock.innerHTML = `<span style="color: #6A9955; font-style: italic;">// File source/${escapeHtml(filename)} chưa được tạo hoặc không tìm thấy.</span>`;
        }
    } catch (e) {
        DOM.codeBlock.innerHTML = `<span style="color: #6A9955; font-style: italic;">// Không thể fetch source/${escapeHtml(filename)} qua file:// cục bộ. Hãy chạy start_arena.bat!</span>`;
    }
}

// ==========================================================================
// BỘ TÔ MÀU CÚ PHÁP C++ THEO PHONG CÁCH VS CODE DARK+ (CHUẨN BẢNG MÀU)
// ==========================================================================
function highlightCppCode(rawCode) {
    if (!rawCode) return '';

    // Regex bắt các loại token theo thứ tự ưu tiên
    const TOKEN_REGEX = /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(#[a-zA-Z_]+(?:\s*<[^>]+>|\s*"[^"]+")?)|(\b(?:0x[0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?[fFlLuU]*)\b)|(\b(?:if|else|for|while|do|switch|case|default|break|continue|return|goto|try|catch|throw)\b)|(\b(?:class|struct|union|enum|typename|template|typedef|namespace|using|public|private|protected|virtual|override|explicit|friend|operator|inline|const|constexpr|static|volatile|extern|auto|void|int|long|short|char|float|double|bool|signed|unsigned|size_t|uint32_t|int32_t|nullptr|true|false|this|new|delete)\b)|(\b(?:std|cout|cin|endl|cerr|string|vector|map|set|pair|ostream|istream)\b)|(\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\())|(\b[A-Z][a-zA-Z0-9_]*\b)|(<<|>>|::|->|\+\+|--|==|!=|<=|>=|&&|\|\||[+\-*/%&=<>!^~?:])|([a-zA-Z_][a-zA-Z0-9_]*)|([\s\S])/g;

    return rawCode.replace(TOKEN_REGEX, (match, comment, str, preproc, num, ctrl, kw, builtin, fn, type, op, id, other) => {
        if (comment) {
            return `<span style="color: #6A9955; font-style: italic;">${escapeHtml(comment)}</span>`;
        }
        if (str) {
            return `<span style="color: #CE9178;">${escapeHtml(str)}</span>`;
        }
        if (preproc) {
            const matchInc = preproc.match(/^(#[a-zA-Z_]+)(\s*)(<[^>]+>|"[^"]+")?(.*)$/);
            if (matchInc) {
                const [, dir, sp, hdr, extra] = matchInc;
                let out = `<span style="color: #C586C0; font-weight: 500;">${escapeHtml(dir)}</span>${sp}`;
                if (hdr) out += `<span style="color: #CE9178;">${escapeHtml(hdr)}</span>`;
                if (extra) out += escapeHtml(extra);
                return out;
            }
            return `<span style="color: #C586C0; font-weight: 500;">${escapeHtml(preproc)}</span>`;
        }
        if (num) {
            return `<span style="color: #B5CEA8;">${num}</span>`;
        }
        if (ctrl) {
            return `<span style="color: #C586C0; font-weight: 500;">${ctrl}</span>`;
        }
        if (kw) {
            return `<span style="color: #569CD6; font-weight: 500;">${kw}</span>`;
        }
        if (builtin) {
            return `<span style="color: #4EC9B0;">${builtin}</span>`;
        }
        if (fn) {
            return `<span style="color: #DCDCAA;">${fn}</span>`;
        }
        if (type) {
            return `<span style="color: #4EC9B0;">${type}</span>`;
        }
        if (op) {
            return `<span style="color: #D4D4D4;">${escapeHtml(op)}</span>`;
        }
        if (id) {
            return `<span style="color: #9CDCFE;">${id}</span>`;
        }
        return escapeHtml(other);
    });
}

// Xử lý khi click chọn đáp án
function handleOptionClick(optIndex) {
    const q = STATE.currentExamQuestions[STATE.currentIndex];
    const chosenOption = q.shuffledOptions[optIndex];
    const isFirstAttempt = !STATE.userAnswers[STATE.currentIndex];

    STATE.userAnswers[STATE.currentIndex] = {
        chosenIndex: optIndex,
        isCorrect: chosenOption.isCorrect,
        chosenText: chosenOption.text,
        correctText: q.shuffledOptions.find(o => o.isCorrect).text
    };

    if (STATE.mode === 'STUDY' || STATE.mode === 'MISTAKE_STUDY') {
        // Cập nhật độ thông thạo nếu là lần thử đầu tiên của câu này trong phiên học
        if (isFirstAttempt) {
            updateQuestionMastery(q.id, chosenOption.isCorrect);
        }

        // STUDY MODE & MISTAKE_STUDY: Hiện ngay lập tức đúng hay sai
        if (STATE.mode === 'MISTAKE_STUDY' && chosenOption.isCorrect) {
            // Câu nào đã trả lời đúng thì loại bỏ khỏi danh sách câu sai
            removeMistakeQuestionId(q.id);
        }
        renderCurrentQuestion();
    } else {
        // EXAM MODE: Đánh dấu đã chọn, người dùng có thể tự do đổi đáp án trước khi bấm qua câu
        const allButtons = DOM.optionsGrid.querySelectorAll('.option-btn');
        allButtons.forEach((btn, idx) => {
            btn.classList.toggle('selected', idx === optIndex);
        });
    }

    updateFooterButtons();
}

// Xử lý khi click toggle một đáp án trong câu Chọn nhiều (Multi-Select)
function handleMultiOptionToggle(optIndex) {
    const q = STATE.currentExamQuestions[STATE.currentIndex];
    if (!STATE.tempMultiSelections[STATE.currentIndex]) {
        STATE.tempMultiSelections[STATE.currentIndex] = new Set();
    }
    const tempSet = STATE.tempMultiSelections[STATE.currentIndex];

    if (tempSet.has(optIndex)) {
        tempSet.delete(optIndex);
    } else {
        tempSet.add(optIndex);
    }

    // Cập nhật ngay class và checkbox trực tiếp trên nút
    const allButtons = DOM.optionsGrid.querySelectorAll('.option-btn');
    const targetBtn = allButtons[optIndex];
    if (targetBtn) {
        const isSelected = tempSet.has(optIndex);
        targetBtn.classList.toggle('selected', isSelected);
        const chk = targetBtn.querySelector('.option-checkbox');
        if (chk) chk.classList.toggle('checked', isSelected);
    }

    // Trong EXAM MODE: Tự động lưu lựa chọn hiện tại vào userAnswers
    if (STATE.mode === 'EXAM') {
        saveCurrentExamMultiAnswer();
    }

    updateFooterButtons();
}

// Lưu câu trả lời của câu chọn nhiều trong phòng thi thật (K >= 0)
function saveCurrentExamMultiAnswer() {
    const q = STATE.currentExamQuestions[STATE.currentIndex];
    const alphabet = ['A', 'B', 'C', 'D', 'E'];
    const chosenIndices = Array.from(STATE.tempMultiSelections[STATE.currentIndex] || []).sort((a, b) => a - b);
    const correctIndices = q.shuffledOptions.map((o, i) => o.isCorrect ? i : null).filter(i => i !== null);

    const isCorrect = (chosenIndices.length === correctIndices.length) &&
                      chosenIndices.every(i => correctIndices.includes(i));

    STATE.userAnswers[STATE.currentIndex] = {
        isMulti: true,
        chosenIndices,
        chosenIndex: chosenIndices[0] !== undefined ? chosenIndices[0] : -1,
        isCorrect,
        chosenText: chosenIndices.length > 0
            ? chosenIndices.map(i => `${alphabet[i]}. ${q.shuffledOptions[i].text}`).join(' | ')
            : 'Không chọn ý nào (0 ý)',
        correctText: correctIndices.length > 0
            ? correctIndices.map(i => `${alphabet[i]}. ${q.shuffledOptions[i].text}`).join(' | ')
            : 'Không có đáp án nào đúng'
    };
}

// Xác nhận câu trả lời chọn nhiều trong STUDY MODE & MISTAKE_STUDY
function handleConfirmMulti() {
    const q = STATE.currentExamQuestions[STATE.currentIndex];
    const alphabet = ['A', 'B', 'C', 'D', 'E'];
    const chosenIndices = Array.from(STATE.tempMultiSelections[STATE.currentIndex] || []).sort((a, b) => a - b);
    const correctIndices = q.shuffledOptions.map((o, i) => o.isCorrect ? i : null).filter(i => i !== null);

    const isCorrect = (chosenIndices.length === correctIndices.length) &&
                      chosenIndices.every(i => correctIndices.includes(i));

    const isFirstAttempt = !STATE.userAnswers[STATE.currentIndex];

    STATE.userAnswers[STATE.currentIndex] = {
        isMulti: true,
        chosenIndices,
        chosenIndex: chosenIndices[0] !== undefined ? chosenIndices[0] : -1,
        isCorrect,
        chosenText: chosenIndices.length > 0
            ? chosenIndices.map(i => `${alphabet[i]}. ${q.shuffledOptions[i].text}`).join(' | ')
            : 'Không chọn ý nào (0 ý)',
        correctText: correctIndices.length > 0
            ? correctIndices.map(i => `${alphabet[i]}. ${q.shuffledOptions[i].text}`).join(' | ')
            : 'Không có đáp án nào đúng'
    };

    if (isFirstAttempt) {
        updateQuestionMastery(q.id, isCorrect);
    }

    if (STATE.mode === 'MISTAKE_STUDY' && isCorrect) {
        removeMistakeQuestionId(q.id);
    }

    renderCurrentQuestion();
    updateFooterButtons();
}

function updateFooterButtons() {
    const isFirst = STATE.currentIndex === 0;
    const isLast = STATE.currentIndex === STATE.currentExamQuestions.length - 1;

    // Nút Câu Trước (Bị ẩn hoàn toàn nếu ở chế độ thi 1 chiều)
    if (STATE.strictForward && STATE.mode === 'EXAM') {
        DOM.btnPrevQuestion.classList.add('hidden');
    } else {
        DOM.btnPrevQuestion.classList.toggle('hidden', isFirst);
    }

    // Nút Tiếp hoặc Nộp Bài
    if (isLast) {
        DOM.btnNextQuestion.classList.add('hidden');
        DOM.btnFinishExam.classList.remove('hidden');
    } else {
        DOM.btnNextQuestion.classList.remove('hidden');
        DOM.btnFinishExam.classList.add('hidden');

        // Tùy biến nhãn nút ở chế độ 1 chiều
        if (STATE.strictForward && STATE.mode === 'EXAM') {
            DOM.btnNextQuestion.innerHTML = 'Xác Nhận & Qua Câu ➡️';
        } else {
            DOM.btnNextQuestion.innerHTML = 'Câu Tiếp Theo ➡️';
        }
    }
}

function navigateQuestion(direction) {
    // Nếu ở chế độ 1 chiều và đi tiếp mà chưa chọn đáp án:
    if (direction > 0 && STATE.strictForward && STATE.mode === 'EXAM') {
        const q = STATE.currentExamQuestions[STATE.currentIndex];
        if (q.isMulti) {
            // Đối với câu Chọn nhiều trong chế độ 1 chiều: Nếu chưa tick ô nào, tự động ghi nhận là "Không chọn ý nào (0 ý)" thay vì hỏi bỏ qua
            saveCurrentExamMultiAnswer();
        } else {
            const hasAnswered = STATE.userAnswers[STATE.currentIndex];
            if (!hasAnswered) {
                if (!confirm(`${getUserLabel()} chưa chọn đáp án cho câu này! Vì đang thi ở Chế độ 1 Chiều nên sẽ không thể quay lại câu này được nữa. ${getUserLabel()} có chắc chắn muốn bỏ qua không?`)) {
                    return;
                }
            }
        }
    }

    const newIdx = STATE.currentIndex + direction;
    if (newIdx >= 0 && newIdx < STATE.currentExamQuestions.length) {
        STATE.currentIndex = newIdx;
        renderCurrentQuestion();
    }
}

// ==========================================================================
// ĐỒNG HỒ ĐẾM NGƯỢC (TIMER)
// ==========================================================================
function startExamTimer() {
    updateTimerDisplay();
    STATE.timerInterval = setInterval(() => {
        STATE.timeRemainingSeconds--;
        updateTimerDisplay();

        if (STATE.timeRemainingSeconds <= 0) {
            clearInterval(STATE.timerInterval);
            alert(`⏰ ĐÃ HẾT GIỜ LÀM BÀI! Hệ thống sẽ tự động thu bài của ${getUserLabel()} ngay bây giờ!`);
            finishExam();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(STATE.timeRemainingSeconds / 60);
    const seconds = STATE.timeRemainingSeconds % 60;
    DOM.timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

    if (STATE.timeRemainingSeconds <= 60) {
        DOM.timerBox.classList.remove('normal');
    } else {
        DOM.timerBox.classList.add('normal');
    }
}

// ==========================================================================
// NỘP BÀI VÀ TÍNH ĐIỂM
// ==========================================================================
function confirmFinishExam() {
    const currentQ = STATE.currentExamQuestions[STATE.currentIndex];
    if (currentQ && currentQ.isMulti) {
        saveCurrentExamMultiAnswer();
    }

    const answeredCount = Object.keys(STATE.userAnswers).length;
    const total = STATE.currentExamQuestions.length;

    if (answeredCount < total && STATE.mode === 'EXAM') {
        const confirmMsg = `${getUserLabel()} mới chỉ trả lời ${answeredCount}/${total} câu hỏi. ${getUserLabel()} có chắc chắn muốn nộp bài sớm không?`;
        if (!confirm(confirmMsg)) return;
    }

    finishExam();
}

function finishExam() {
    window.onbeforeunload = null; // Gỡ bỏ khóa bảo vệ phòng thi khi đã nộp bài
    clearInterval(STATE.timerInterval);

    // Tính điểm
    const total = STATE.currentExamQuestions.length;
    let correctCount = 0;
    const failedQuestionIds = [];

    // Đối với câu Chọn nhiều: Mặc định nếu không chọn gì thì tính là "Không chọn ý nào (0 ý)" thay vì bỏ qua
    STATE.currentExamQuestions.forEach((q, idx) => {
        if (q.isMulti && !STATE.userAnswers[idx]) {
            const correctIndices = q.shuffledOptions.map((o, i) => o.isCorrect ? i : null).filter(i => i !== null);
            STATE.userAnswers[idx] = {
                isMulti: true,
                chosenIndices: [],
                chosenIndex: -1,
                isCorrect: (q.correctCount === 0),
                chosenText: 'Không chọn ý nào (0 ý)',
                correctText: correctIndices.length > 0
                    ? correctIndices.map(i => `${['A','B','C','D','E'][i]}. ${q.shuffledOptions[i].text}`).join(' | ')
                    : 'Không có đáp án nào đúng'
            };
        }
    });

    STATE.currentExamQuestions.forEach((q, idx) => {
        const ans = STATE.userAnswers[idx];
        if (ans && ans.isCorrect) {
            correctCount++;
        } else {
            failedQuestionIds.push(q.id);
        }
    });

    const percent = Math.round((correctCount / total) * 100);
    const durationSpentSeconds = STATE.totalDurationSeconds - STATE.timeRemainingSeconds;
    const durationSpentStr = formatSeconds(durationSpentSeconds);

    // Lưu vào Lịch sử thi đấu (LocalStorage & Server)
    let modeLabel = 'Học Tập';
    if (STATE.mode === 'MISTAKE_STUDY') modeLabel = 'Làm Lại Câu Sai';
    else if (STATE.mode === 'EXAM') modeLabel = STATE.strictForward ? 'Thi Thử (1 Chiều)' : 'Thi Thử';

    const examRecord = {
        id: 'exam_' + Date.now(),
        date: new Date().toLocaleString('vi-VN'),
        timestamp: new Date().toISOString(),
        mode: modeLabel,
        score: `${correctCount}/${total}`,
        score_count: correctCount,
        total_count: total,
        percent: percent,
        duration: durationSpentStr,
        failed_question_ids: failedQuestionIds,
        questions_attempted: STATE.currentExamQuestions.map((q, idx) => ({
            id: q.id,
            user_answer: STATE.userAnswers[idx] ? STATE.userAnswers[idx].chosenText : null,
            is_correct: STATE.userAnswers[idx] ? STATE.userAnswers[idx].isCorrect : false
        }))
    };

    saveExamResultToHistory({
        date: examRecord.date,
        mode: examRecord.mode,
        score: examRecord.score,
        percent: `${percent}%`,
        duration: durationSpentStr
    });

    syncExamToServer(examRecord);

    // Cập nhật điểm thông thạo ngầm định của từng câu hỏi (Adaptive Mastery Streaks)
    const masteryResults = STATE.currentExamQuestions.map((q, idx) => ({
        id: q.id,
        isCorrect: STATE.userAnswers[idx] ? STATE.userAnswers[idx].isCorrect : false
    }));
    batchUpdateMastery(masteryResults);

    // Nếu ở chế độ THI THỬ (EXAM), câu nào làm sai thì thêm vào danh sách câu sai (chỉ 1 lần)
    if (STATE.mode === 'EXAM' && failedQuestionIds.length > 0) {
        addMistakeQuestionIds(failedQuestionIds);
    }

    // Render Màn hình kết quả
    renderResultScreen(correctCount, total, percent, durationSpentStr);
    switchScreen('RESULT');
}

function renderResultScreen(score, total, percent, durationStr) {
    DOM.resultScoreNum.textContent = score;
    DOM.resultScoreDenom.textContent = `/ ${total}`;
    DOM.resultScorePercent.textContent = `${percent}%`;
    DOM.resultScoreMeta.innerHTML = `Thời gian làm bài: <strong>${durationStr}</strong> • Chế độ: <strong>${STATE.mode === 'STUDY' ? 'Học Tập' : 'Thi Thử'}</strong>`;

    // Lấy danh hiệu theo theme đang hoạt động (Academic hoặc GDD)
    const ranks = ACTIVE_THEME.ranks || DEFAULT_THEME.ranks;
    let rankInfo;

    if (percent < 50) {
        rankInfo = ranks.under_50;
    } else if (percent < 80) {
        rankInfo = ranks.under_80;
    } else if (percent < 100) {
        rankInfo = ranks.under_100;
    } else {
        rankInfo = ranks.perfect;
    }

    DOM.trophyBadge.textContent = rankInfo.trophy;
    DOM.resultRankTitle.textContent = rankInfo.title;
    DOM.resultRankDesc.textContent = rankInfo.desc;

    // Render danh sách chi tiết các câu đã làm
    DOM.reviewList.innerHTML = '';
    STATE.currentExamQuestions.forEach((q, idx) => {
        const ans = STATE.userAnswers[idx];
        const isCorrect = ans && ans.isCorrect;
        const item = document.createElement('div');
        item.className = `review-item ${isCorrect ? 'is-correct' : 'is-wrong'}`;

        const chosenText = ans ? ans.chosenText : '<em>Chưa trả lời (Bỏ qua)</em>';
        let correctText = '';
        if (q.isMulti) {
            const correctOpts = q.rawOptions.slice(0, q.correctCount);
            correctText = correctOpts.length > 0 ? correctOpts.join(' | ') : 'Không có đáp án nào đúng';
        } else {
            correctText = q.rawOptions[0];
        }

        const typeLabel = q.isMulti ? ` • ☑️ Chọn Nhiều (${q.correctCount} ý đúng)` : (q.question_type ? ` • ${q.question_type}` : '');
        const formatLabel = q.code_file ? '💻 Code' : '📖 Lý Thuyết';

        item.innerHTML = `
            <div class="review-item-header">
                <span><strong>Câu ${idx + 1}</strong> [${q.topic} • ${q.difficulty} • ${formatLabel}${typeLabel}]</span>
                <span style="color: ${isCorrect ? 'var(--success)' : 'var(--danger)'}; font-weight: 700;">
                    ${isCorrect ? '✓ CHÍNH XÁC (+1đ)' : '✗ CHƯA ĐÚNG (0đ)'}
                </span>
            </div>
            <div class="review-q-text">${escapeHtml(q.question)}</div>
            ${q.code_file ? `
                <div class="review-code-wrapper">
                    <details class="review-code-details">
                        <summary>💻 Xem lại mã nguồn C++ [<strong>${escapeHtml(q.code_file)}</strong>]</summary>
                        <div class="code-wrapper review-code-box">
                            <div class="code-header">
                                <span class="code-dot dot-red"></span>
                                <span class="code-dot dot-yellow"></span>
                                <span class="code-dot dot-green"></span>
                                <span class="code-filename">${escapeHtml(q.code_file)}</span>
                            </div>
                            <pre class="code-content"><code class="review-code-block">${STATE.codeCache[q.code_file] ? highlightCppCode(STATE.codeCache[q.code_file]) : '// Đang tải mã nguồn...'}</code></pre>
                        </div>
                    </details>
                </div>
            ` : ''}
            <div class="review-answer-row">Lựa chọn của ${getUserLabel()}: <strong style="color: ${isCorrect ? '#A7F3D0' : '#FECACA'}">${escapeHtml(chosenText)}</strong></div>
            ${!isCorrect ? `<div class="review-answer-row">Đáp án chuẩn xác: <strong style="color: #A7F3D0">${escapeHtml(correctText)}</strong></div>` : ''}
            <div style="font-size: 0.85rem; color: #9CA3AF; margin-top: 0.5rem; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 0.5rem;">
                💡 <strong>Giải mã cạm bẫy:</strong> ${escapeHtml(q.explanation)}
            </div>
        `;
        DOM.reviewList.appendChild(item);
    });
}

function restartCurrentSession() {
    startSession(STATE.mode);
}

function handleQuitStudy() {
    if (confirm(`${getUserLabel()} có muốn tạm dừng buổi học này và quay về sảnh chờ không?`)) {
        returnToLobby();
    }
}

function returnToLobby() {
    window.onbeforeunload = null;
    clearInterval(STATE.timerInterval);
    updateMistakesButtonUI();
    switchScreen('LOBBY');
}

// ==========================================================================
// LOCAL STORAGE & SERVER SYNC DANH SÁCH CÂU HỎI LÀM SAI (MISTAKE BANK)
// ==========================================================================
const MISTAKES_STORAGE_KEY = 'GDD_MISTAKE_IDS_v1';

function getMistakeQuestionIds() {
    try {
        const raw = localStorage.getItem(MISTAKES_STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

async function syncMistakesToServer(mistakeIds) {
    try {
        await fetch('/api/mistakes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mistakeIds)
        });
    } catch (e) {
        // Chế độ file:// hoặc offline
    }
}

async function syncExamToServer(examRecord) {
    try {
        await fetch('/api/save-exam', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(examRecord)
        });
    } catch (e) {
        // Chế độ file:// hoặc offline
    }
}

function addMistakeQuestionIds(newIds) {
    if (!newIds || newIds.length === 0) return;
    const current = new Set(getMistakeQuestionIds());
    newIds.forEach(id => current.add(parseInt(id)));
    const updated = Array.from(current);
    localStorage.setItem(MISTAKES_STORAGE_KEY, JSON.stringify(updated));
    updateMistakesButtonUI();
    syncMistakesToServer(updated);
}

function removeMistakeQuestionId(id) {
    const targetId = parseInt(id);
    const updated = getMistakeQuestionIds().filter(existingId => existingId !== targetId);
    localStorage.setItem(MISTAKES_STORAGE_KEY, JSON.stringify(updated));
    updateMistakesButtonUI();
    syncMistakesToServer(updated);
}

function updateMistakesButtonUI() {
    if (!DOM.btnRetryMistakes) return;
    const ids = getMistakeQuestionIds();
    // Lọc những câu thực sự có mặt trong ngân hàng câu hỏi
    const validCount = ids.filter(id => STATE.allQuestions.some(q => q.id === id)).length;

    if (DOM.mistakesCountBadge) {
        DOM.mistakesCountBadge.textContent = `(${validCount})`;
    }

    if (validCount > 0) {
        DOM.btnRetryMistakes.disabled = false;
        const template = ACTIVE_THEME.mistakes_btn_tooltip_has || DEFAULT_THEME.mistakes_btn_tooltip_has;
        DOM.btnRetryMistakes.title = template.replace('{count}', validCount);
    } else {
        DOM.btnRetryMistakes.disabled = true;
        DOM.btnRetryMistakes.title = ACTIVE_THEME.mistakes_btn_tooltip_empty || DEFAULT_THEME.mistakes_btn_tooltip_empty;
    }
}

// Xuất các hàm ra phạm vi toàn cục để script ngoài hoặc MCP Server có thể gọi trực tiếp
window.addMistakeQuestionIds = addMistakeQuestionIds;
window.getMistakeQuestionIds = getMistakeQuestionIds;

// ==========================================================================
// LOCAL STORAGE & SERVER SYNC ĐỘ THÔNG THẠO CÂU HỎI (ADAPTIVE MASTERY)
// ==========================================================================
const MASTERY_STORAGE_KEY = 'GDD_QUESTION_MASTERY_v1';

function getQuestionMasteryMap() {
    try {
        const raw = localStorage.getItem(MASTERY_STORAGE_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch (e) {
        return {};
    }
}

function getQuestionStreak(id) {
    const map = getQuestionMasteryMap();
    return map[String(id)] || 0;
}

function updateQuestionMastery(questionId, isCorrect) {
    const map = getQuestionMasteryMap();
    const key = String(questionId);
    if (isCorrect) {
        map[key] = (map[key] || 0) + 1;
    } else {
        map[key] = 0;
    }
    localStorage.setItem(MASTERY_STORAGE_KEY, JSON.stringify(map));
    syncMasteryToServer(map);
}

function batchUpdateMastery(results) {
    if (!results || results.length === 0) return;
    const map = getQuestionMasteryMap();
    results.forEach(r => {
        const key = String(r.id);
        if (r.isCorrect) {
            map[key] = (map[key] || 0) + 1;
        } else {
            map[key] = 0;
        }
    });
    localStorage.setItem(MASTERY_STORAGE_KEY, JSON.stringify(map));
    syncMasteryToServer(map);
}

async function syncMasteryToServer(masteryMap) {
    try {
        await fetch('/api/mastery', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(masteryMap)
        });
    } catch (e) {
        // Chế độ file:// hoặc offline
    }
}

async function tryFetchMasteryFromServer() {
    try {
        const res = await fetch('/api/mastery');
        if (res.ok) {
            const serverMastery = await res.json();
            if (serverMastery && typeof serverMastery === 'object') {
                const local = getQuestionMasteryMap();
                const merged = Object.assign({}, serverMastery, local);
                localStorage.setItem(MASTERY_STORAGE_KEY, JSON.stringify(merged));
            }
        }
    } catch (e) {
        // Chế độ file:// hoặc offline
    }
}

/**
 * Thuật toán Bốc thăm Ngẫu nhiên có Trọng số không hoàn lại (Weighted Random Sampling Without Replacement)
 * Dựa trên thuật toán Efraimidis-Spirakis (A-Res).
 * Trọng số nghịch đảo: W_i = 1 / (streak_i + 1)
 * Trọng số càng cao (streak = 0: chưa làm hoặc vừa làm sai) thì xác suất bốc trúng càng lớn!
 */
function sampleQuestionsByMastery(pool, count) {
    if (!pool || pool.length === 0) return [];
    if (count >= pool.length) {
        const copy = [...pool];
        shuffleArray(copy);
        return copy;
    }

    const masteryMap = getQuestionMasteryMap();

    const weightedItems = pool.map(item => {
        const streak = masteryMap[String(item.id)] || 0;
        // W = 1 / (streak + 1)
        const weight = 1.0 / (streak + 1);
        const u = Math.random();
        // Efraimidis-Spirakis key: u^(1/w)
        const key = Math.pow(Math.max(0.000001, u), 1.0 / weight);
        return { item, key };
    });

    // Sắp xếp giảm dần theo key và lấy đúng `count` phần tử
    weightedItems.sort((a, b) => b.key - a.key);
    return weightedItems.slice(0, count).map(entry => entry.item);
}

window.getQuestionMasteryMap = getQuestionMasteryMap;
window.getQuestionStreak = getQuestionStreak;
window.sampleQuestionsByMastery = sampleQuestionsByMastery;

// ==========================================================================
// LOCAL STORAGE LỊCH SỬ KẾT QUẢ THI
// ==========================================================================
const STORAGE_KEY = 'GDD_MOCK_EXAM_HISTORY_v1';

function saveExamResultToHistory(record) {
    try {
        const list = getExamHistory();
        list.unshift(record); // Thêm vào đầu danh sách
        if (list.length > 30) list.pop(); // Giữ tối đa 30 lần thi gần nhất
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {
        console.error('Không thể lưu vào localStorage', e);
    }
}

function getExamHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

function openHistoryModal() {
    const list = getExamHistory();
    DOM.historyTableBody.innerHTML = '';

    if (list.length === 0) {
        DOM.historyEmpty.classList.remove('hidden');
        DOM.historyTable.classList.add('hidden');
    } else {
        DOM.historyEmpty.classList.add('hidden');
        DOM.historyTable.classList.remove('hidden');

        list.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.date}</td>
                <td><span class="mode-pill">${item.mode}</span></td>
                <td><strong>${item.score}</strong></td>
                <td style="color: var(--success); font-weight: 700;">${item.percent}</td>
                <td>${item.duration}</td>
            `;
            DOM.historyTableBody.appendChild(tr);
        });
    }

    DOM.historyModal.classList.remove('hidden');
}

function closeHistoryModal() {
    DOM.historyModal.classList.add('hidden');
}

function clearExamHistory() {
    if (confirm(`${getUserLabel()} có chắc chắn muốn xóa toàn bộ lịch sử thi đấu không?`)) {
        localStorage.removeItem(STORAGE_KEY);
        openHistoryModal();
    }
}

// ==========================================================================
// TIỆN ÍCH HỖ TRỢ (UTILITIES)
// ==========================================================================
function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

function formatSeconds(totalSeconds) {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
