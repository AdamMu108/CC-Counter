/**
 * عداد الكومبلكس شراكة - CC Counter
 * تطبيق ويب لحساب نقاط لعبة الورق
 */

// ========== الثوابت ==========
const POINTS = {
    trick: 15,        // -15 لكل أكلة
    diamond: 10,      // -10 لكل ديناري
    queen: 25,        // -25 لكل بنت
    kingHeart: 75,    // -75 لشيخ القبة
    roundTotal: -500  // مجموع الجولة
};

// ========== حالة اللعبة ==========
let gameState = {
    team1Name: 'فريقنا',
    team2Name: 'الخصم',
    team1Total: 0,
    team2Total: 0,
    roundNumber: 0,
    history: [],
    currentRound: {
        tricks: 0,
        diamonds: 0,
        queens: [],
        hasKing: false,
        opponentDoubled: {},
        myDoubled: {}
    }
};

// ========== التهيئة ==========
document.addEventListener('DOMContentLoaded', () => {
    loadGameState();
    updateUI();
});

// ========== التنقل بين الشاشات ==========
function goToScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

// ========== شاشة الترحيب ==========
function startNewGame() {
    const team1 = document.getElementById('team1-name').value.trim() || 'فريقنا';
    const team2 = document.getElementById('team2-name').value.trim() || 'الخصم';
    
    gameState = {
        team1Name: team1,
        team2Name: team2,
        team1Total: 0,
        team2Total: 0,
        roundNumber: 0,
        history: [],
        currentRound: resetCurrentRound()
    };
    
    saveGameState();
    updateUI();
    goToScreen('game-screen');
}

function continueGame() {
    loadGameState();
    updateUI();
    goToScreen('game-screen');
}

// ========== شاشة اللعبة ==========
function updateUI() {
    // تحديث الأسماء
    document.getElementById('game-team1-name').textContent = gameState.team1Name;
    document.getElementById('game-team2-name').textContent = gameState.team2Name;
    
    // تحديث النقاط
    document.getElementById('team1-score').textContent = gameState.team1Total;
    document.getElementById('team2-score').textContent = gameState.team2Total;
    
    // تحديث رقم الجولة
    document.getElementById('round-number').textContent = gameState.roundNumber;
}

function startRound() {
    gameState.roundNumber++;
    gameState.currentRound = resetCurrentRound();
    updateCountingScreen();
    goToScreen('counting-screen');
}

function confirmNewGame() {
    if (confirm('هل أنت متأكد من بدء لعبة جديدة؟')) {
        goToScreen('welcome-screen');
    }
}

// ========== شاشة العد ==========
function resetCurrentRound() {
    return {
        selectedTeam: 1, // 1 = الفريق الأول، 2 = الفريق الثاني
        tricks: 0,
        diamonds: 0,
        queens: [],
        hasKing: false,
        opponentDoubled: {},
        myDoubled: {}
    };
}

function updateCountingScreen() {
    document.getElementById('tricks-value').textContent = gameState.currentRound.tricks;
    document.getElementById('diamonds-value').textContent = gameState.currentRound.diamonds;
    
    // إعادة تعيين البطاقات
    document.querySelectorAll('#counting-screen .card-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    gameState.currentRound.queens = [];
    gameState.currentRound.hasKing = false;
    
    // تحديث أسماء الفرق في الاختيار
    document.getElementById('select-team1-name').textContent = gameState.team1Name;
    document.getElementById('select-team2-name').textContent = gameState.team2Name;
    
    // تحديد الفريق الأول افتراضياً
    selectTeam(1);
}

function selectTeam(teamNum) {
    gameState.currentRound.selectedTeam = teamNum;
    
    // تحديث الأزرار
    document.getElementById('select-team1').classList.toggle('active', teamNum === 1);
    document.getElementById('select-team2').classList.toggle('active', teamNum === 2);
    
    // تحديث العنوان
    const teamName = teamNum === 1 ? gameState.team1Name : gameState.team2Name;
    document.getElementById('selected-team-name').textContent = teamName;
    
    if ('vibrate' in navigator) {
        navigator.vibrate(15);
    }
}

function changeValue(type, delta) {
    const maxValues = { tricks: 13, diamonds: 13 };
    const current = gameState.currentRound[type];
    const newValue = Math.max(0, Math.min(maxValues[type], current + delta));
    
    gameState.currentRound[type] = newValue;
    document.getElementById(`${type}-value`).textContent = newValue;
    
    // اهتزاز خفيف
    if ('vibrate' in navigator) {
        navigator.vibrate(10);
    }
}

function toggleCard(btn) {
    const card = btn.dataset.card;
    btn.classList.toggle('selected');
    
    if (card === 'king-heart') {
        gameState.currentRound.hasKing = btn.classList.contains('selected');
    } else if (card.startsWith('queen-')) {
        const suit = card.replace('queen-', '');
        if (btn.classList.contains('selected')) {
            if (!gameState.currentRound.queens.includes(suit)) {
                gameState.currentRound.queens.push(suit);
            }
        } else {
            gameState.currentRound.queens = gameState.currentRound.queens.filter(s => s !== suit);
        }
    }
    
    // اهتزاز خفيف
    if ('vibrate' in navigator) {
        navigator.vibrate(15);
    }
}

// ========== شاشة التدبيل ==========
function goToDoubling() {
    setupDoublingScreen();
    goToScreen('doubling-screen');
}

function setupDoublingScreen() {
    const opponentSection = document.getElementById('opponent-doubled-cards');
    const mySection = document.getElementById('my-doubled-cards');
    
    opponentSection.innerHTML = '';
    mySection.innerHTML = '';
    
    gameState.currentRound.opponentDoubled = {};
    gameState.currentRound.myDoubled = {};
    
    // البطاقات التي أخذتها (للتدبيل عليّ)
    const myCards = [...gameState.currentRound.queens];
    if (gameState.currentRound.hasKing) {
        myCards.push('king');
    }
    
    // البطاقات التي أخذها الخصم (للتدبيل مني)
    const allQueens = ['spade', 'heart', 'diamond', 'club'];
    const opponentQueens = allQueens.filter(s => !gameState.currentRound.queens.includes(s));
    const opponentHasKing = !gameState.currentRound.hasKing;
    
    // إنشاء أزرار التدبيل عليّ
    myCards.forEach(card => {
        const btn = createDoublingCard(card, 'opponent');
        opponentSection.appendChild(btn);
    });
    
    // إنشاء أزرار التدبيل مني
    opponentQueens.forEach(suit => {
        const btn = createDoublingCard(suit, 'my');
        mySection.appendChild(btn);
    });
    
    if (opponentHasKing) {
        const btn = createDoublingCard('king', 'my');
        mySection.appendChild(btn);
    }
    
    // إخفاء الأقسام الفارغة
    document.getElementById('opponent-doubled-section').style.display = 
        myCards.length > 0 ? 'block' : 'none';
    document.getElementById('my-doubled-section').style.display = 
        (opponentQueens.length > 0 || opponentHasKing) ? 'block' : 'none';
}

function createDoublingCard(card, type) {
    const btn = document.createElement('button');
    btn.className = 'card-btn';
    btn.dataset.card = card;
    btn.dataset.type = type;
    
    const isKing = card === 'king';
    const rank = isKing ? 'K' : 'Q';
    const suit = isKing ? 'heart' : card;
    const suitSymbol = { spade: '♠', heart: '♥', diamond: '♦', club: '♣' }[suit];
    const suitClass = suit;
    
    btn.innerHTML = `
        <span class="card-rank">${rank}</span>
        <span class="suit ${suitClass}">${suitSymbol}</span>
    `;
    
    btn.onclick = () => toggleDoublingCard(btn);
    
    return btn;
}

function toggleDoublingCard(btn) {
    const card = btn.dataset.card;
    const type = btn.dataset.type;
    btn.classList.toggle('selected');
    
    const doubled = type === 'opponent' ? 
        gameState.currentRound.opponentDoubled : 
        gameState.currentRound.myDoubled;
    
    doubled[card] = btn.classList.contains('selected');
    
    if ('vibrate' in navigator) {
        navigator.vibrate(15);
    }
}

// ========== حساب النتيجة ==========
function calculateAndFinish() {
    const round = gameState.currentRound;
    let selectedTeamScore = 0;
    
    // حساب الأكلات
    selectedTeamScore -= round.tricks * POINTS.trick;
    
    // حساب الديناري
    selectedTeamScore -= round.diamonds * POINTS.diamond;
    
    // حساب البنات
    round.queens.forEach(suit => {
        const doubled = round.opponentDoubled[suit];
        selectedTeamScore -= POINTS.queen * (doubled ? 2 : 1);
    });
    
    // حساب شيخ القبة
    if (round.hasKing) {
        const doubled = round.opponentDoubled['king'];
        selectedTeamScore -= POINTS.kingHeart * (doubled ? 2 : 1);
    }
    
    // حساب التدبيل على الخصم
    Object.entries(round.myDoubled).forEach(([card, isDoubled]) => {
        if (isDoubled) {
            if (card === 'king') {
                selectedTeamScore += POINTS.kingHeart; // استرداد المضاعفة
            } else {
                selectedTeamScore += POINTS.queen;
            }
        }
    });
    
    // حساب نقاط الفريق الآخر
    const otherTeamScore = POINTS.roundTotal - selectedTeamScore;
    
    // تحديد نقاط كل فريق حسب الاختيار
    let team1Score, team2Score;
    if (round.selectedTeam === 1) {
        team1Score = selectedTeamScore;
        team2Score = otherTeamScore;
    } else {
        team1Score = otherTeamScore;
        team2Score = selectedTeamScore;
    }
    
    // تحديث المجاميع
    gameState.team1Total += team1Score;
    gameState.team2Total += team2Score;
    
    // إضافة للسجل
    gameState.history.push({
        round: gameState.roundNumber,
        team1: team1Score,
        team2: team2Score
    });
    
    saveGameState();
    updateUI();
    
    // عرض النتيجة
    showResult(team1Score, team2Score);
}

function showResult(team1Score, team2Score) {
    const winner = team1Score > team2Score ? gameState.team1Name : gameState.team2Name;
    const message = `
        ${gameState.team1Name}: ${team1Score}
        ${gameState.team2Name}: ${team2Score}
        
        الفائز بالجولة: ${winner}
    `;
    
    alert(message);
    goToScreen('game-screen');
}

// ========== شاشة السجل ==========
function showHistory() {
    const table = document.getElementById('history-table');
    table.innerHTML = '';
    
    // العنوان
    const header = document.createElement('div');
    header.className = 'history-row header';
    header.innerHTML = `
        <span class="round-num">#</span>
        <span>${gameState.team1Name}</span>
        <span>${gameState.team2Name}</span>
    `;
    table.appendChild(header);
    
    // الجولات
    if (gameState.history.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'history-row';
        empty.innerHTML = '<span style="flex:1; text-align:center; color: var(--text-secondary);">لا توجد جولات</span>';
        table.appendChild(empty);
    } else {
        gameState.history.forEach(entry => {
            const row = document.createElement('div');
            row.className = 'history-row';
            
            const t1Class = entry.team1 > entry.team2 ? 'winner' : '';
            const t2Class = entry.team2 > entry.team1 ? 'winner' : '';
            
            row.innerHTML = `
                <span class="round-num">${entry.round}</span>
                <span class="${t1Class}">${entry.team1}</span>
                <span class="${t2Class}">${entry.team2}</span>
            `;
            table.appendChild(row);
        });
    }
    
    // المجموع
    const summary = document.getElementById('total-summary');
    const total = gameState.team1Total + gameState.team2Total;
    const expected = gameState.roundNumber * POINTS.roundTotal;
    summary.innerHTML = `
        المجموع: ${gameState.team1Total} + ${gameState.team2Total} = ${total}<br>
        <small style="color: var(--text-secondary)">المتوقع: ${expected}</small>
    `;
    
    goToScreen('history-screen');
}

// ========== الحفظ والتحميل ==========
function saveGameState() {
    try {
        localStorage.setItem('ccCounter', JSON.stringify(gameState));
    } catch (e) {
        console.warn('Could not save game state');
    }
}

function loadGameState() {
    try {
        const saved = localStorage.getItem('ccCounter');
        if (saved) {
            const loaded = JSON.parse(saved);
            gameState = { ...gameState, ...loaded };
        }
    } catch (e) {
        console.warn('Could not load game state');
    }
}

// ========== PWA Service Worker ==========
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js').catch(() => {});
    });
}

// ========== الإعدادات و API ==========
let apiKey = localStorage.getItem('roboflowApiKey') || '';
let cameraStream = null;
let detectedResults = null;

function showSettings() {
    document.getElementById('api-key-input').value = apiKey;
    goToScreen('settings-screen');
}

function saveApiKey() {
    const key = document.getElementById('api-key-input').value.trim();
    apiKey = key;
    localStorage.setItem('roboflowApiKey', key);
    alert('تم حفظ المفتاح بنجاح ✓');
    goToScreen('game-screen');
}

// ========== شاشة الكاميرا ==========
async function startCameraRound() {
    if (!apiKey) {
        if (confirm('لم تقم بإدخال مفتاح API بعد. هل تريد إدخاله الآن؟')) {
            showSettings();
        }
        return;
    }
    
    gameState.roundNumber++;
    gameState.currentRound = resetCurrentRound();
    detectedResults = null;
    
    // إعادة تعيين الواجهة
    document.getElementById('capture-btn').style.display = 'block';
    document.getElementById('analyze-btn').style.display = 'none';
    document.getElementById('retake-btn').style.display = 'none';
    document.getElementById('use-results-btn').style.display = 'none';
    document.getElementById('detection-results').style.display = 'none';
    document.getElementById('captured-image').style.display = 'none';
    
    goToScreen('camera-screen');
    await startCamera();
}

async function startCamera() {
    const video = document.getElementById('camera-preview');
    
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        video.srcObject = cameraStream;
        video.style.display = 'block';
    } catch (err) {
        alert('تعذر الوصول للكاميرا. تأكد من إعطاء الإذن للتطبيق.');
        goToScreen('game-screen');
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
}

function capturePhoto() {
    const video = document.getElementById('camera-preview');
    const canvas = document.getElementById('camera-canvas');
    const img = document.getElementById('captured-image');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    img.src = canvas.toDataURL('image/jpeg', 0.9);
    img.style.display = 'block';
    video.style.display = 'none';
    
    stopCamera();
    
    // تغيير الأزرار
    document.getElementById('capture-btn').style.display = 'none';
    document.getElementById('analyze-btn').style.display = 'block';
    document.getElementById('retake-btn').style.display = 'block';
    
    if ('vibrate' in navigator) {
        navigator.vibrate(50);
    }
}

async function retakePhoto() {
    document.getElementById('captured-image').style.display = 'none';
    document.getElementById('detection-results').style.display = 'none';
    document.getElementById('use-results-btn').style.display = 'none';
    
    document.getElementById('capture-btn').style.display = 'block';
    document.getElementById('analyze-btn').style.display = 'none';
    document.getElementById('retake-btn').style.display = 'none';
    
    await startCamera();
}

function closeCameraAndReturn() {
    stopCamera();
    gameState.roundNumber--; // إلغاء الجولة
    goToScreen('game-screen');
}

// ========== تحليل الصورة بـ Roboflow ==========
async function analyzeImage() {
    const canvas = document.getElementById('camera-canvas');
    const imageBase64 = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
    
    showLoading('جاري تحليل البطاقات...');
    
    try {
        const response = await fetch(
            `https://detect.roboflow.com/playing-cards-ow27d/4?api_key=${apiKey}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: imageBase64
            }
        );
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        hideLoading();
        
        if (data.predictions && data.predictions.length > 0) {
            processDetections(data.predictions);
        } else {
            alert('لم يتم اكتشاف أي بطاقات. حاول التقاط صورة أوضح.');
        }
        
    } catch (err) {
        hideLoading();
        console.error('API Error:', err);
        alert('حدث خطأ أثناء التحليل. تأكد من صحة مفتاح API والاتصال بالإنترنت.');
    }
}

function processDetections(predictions) {
    // تصفية النتائج بالثقة
    const minConfidence = 0.5;
    const filtered = predictions.filter(p => p.confidence >= minConfidence);
    
    // تحليل البطاقات
    const cards = {
        diamonds: 0,
        queens: [],
        kingOfHearts: false,
        allCards: []
    };
    
    filtered.forEach(pred => {
        const cardClass = pred.class.toUpperCase();
        cards.allCards.push({
            name: cardClass,
            confidence: pred.confidence
        });
        
        // عد الديناري
        if (cardClass.endsWith('D') || cardClass.includes('DIAMOND')) {
            cards.diamonds++;
        }
        
        // اكتشاف البنات
        if (cardClass.startsWith('Q')) {
            if (cardClass.includes('S') || cardClass.includes('SPADE')) {
                if (!cards.queens.includes('spade')) cards.queens.push('spade');
            } else if (cardClass.includes('H') || cardClass.includes('HEART')) {
                if (!cards.queens.includes('heart')) cards.queens.push('heart');
            } else if (cardClass.includes('D') || cardClass.includes('DIAMOND')) {
                if (!cards.queens.includes('diamond')) cards.queens.push('diamond');
            } else if (cardClass.includes('C') || cardClass.includes('CLUB')) {
                if (!cards.queens.includes('club')) cards.queens.push('club');
            }
        }
        
        // اكتشاف شيخ القبة (ملك القلب)
        if (cardClass.startsWith('K') && (cardClass.includes('H') || cardClass.includes('HEART'))) {
            cards.kingOfHearts = true;
        }
    });
    
    // حساب عدد الأكلات (تقريبي: كل 4 بطاقات = أكلة)
    cards.tricks = Math.floor(filtered.length / 4);
    
    detectedResults = cards;
    displayDetectionResults(cards);
}

function displayDetectionResults(cards) {
    const container = document.getElementById('detected-cards-list');
    container.innerHTML = '';
    
    // عرض كل البطاقات المكتشفة
    cards.allCards.forEach(card => {
        const item = document.createElement('div');
        item.className = 'detected-card-item';
        
        // تحديد اللون حسب نوع البطاقة
        if (card.name.includes('H')) item.classList.add('heart');
        else if (card.name.includes('D')) item.classList.add('diamond');
        else if (card.name.includes('S')) item.classList.add('spade');
        else if (card.name.includes('C')) item.classList.add('club');
        
        item.innerHTML = `
            ${card.name}
            <span class="confidence">${Math.round(card.confidence * 100)}%</span>
        `;
        container.appendChild(item);
    });
    
    // إضافة ملخص
    const summary = document.createElement('div');
    summary.style.cssText = 'width:100%; margin-top:10px; padding-top:10px; border-top:1px solid var(--bg-secondary); font-size:13px; color:var(--text-secondary);';
    summary.innerHTML = `
        <strong>الملخص:</strong><br>
        الأكلات: ~${cards.tricks} | الديناري: ${cards.diamonds} | البنات: ${cards.queens.length}
        ${cards.kingOfHearts ? ' | شيخ القبة ♥' : ''}
    `;
    container.appendChild(summary);
    
    document.getElementById('detection-results').style.display = 'block';
    document.getElementById('use-results-btn').style.display = 'block';
}

function useDetectionResults() {
    if (!detectedResults) return;
    
    // تطبيق النتائج على الجولة الحالية
    gameState.currentRound.tricks = detectedResults.tricks;
    gameState.currentRound.diamonds = Math.min(13, detectedResults.diamonds);
    gameState.currentRound.queens = detectedResults.queens;
    gameState.currentRound.hasKing = detectedResults.kingOfHearts;
    
    // الانتقال لشاشة العد للتعديل إذا لزم
    updateCountingScreen();
    
    // تحديث الواجهة
    document.getElementById('tricks-value').textContent = gameState.currentRound.tricks;
    document.getElementById('diamonds-value').textContent = gameState.currentRound.diamonds;
    
    // تحديد البطاقات
    document.querySelectorAll('#counting-screen .card-btn').forEach(btn => {
        const card = btn.dataset.card;
        if (card === 'king-heart' && gameState.currentRound.hasKing) {
            btn.classList.add('selected');
        } else if (card.startsWith('queen-')) {
            const suit = card.replace('queen-', '');
            if (gameState.currentRound.queens.includes(suit)) {
                btn.classList.add('selected');
            }
        }
    });
    
    goToScreen('counting-screen');
}

// ========== Loading Overlay ==========
function showLoading(text = 'جاري التحميل...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner"></div>
            <div class="loading-text">${text}</div>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.loading-text').textContent = text;
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}
