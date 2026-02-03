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
    let team1Score = 0;
    
    // حساب الأكلات
    team1Score -= round.tricks * POINTS.trick;
    
    // حساب الديناري
    team1Score -= round.diamonds * POINTS.diamond;
    
    // حساب البنات
    round.queens.forEach(suit => {
        const doubled = round.opponentDoubled[suit];
        team1Score -= POINTS.queen * (doubled ? 2 : 1);
    });
    
    // حساب شيخ القبة
    if (round.hasKing) {
        const doubled = round.opponentDoubled['king'];
        team1Score -= POINTS.kingHeart * (doubled ? 2 : 1);
    }
    
    // حساب التدبيل على الخصم
    Object.entries(round.myDoubled).forEach(([card, isDoubled]) => {
        if (isDoubled) {
            if (card === 'king') {
                team1Score += POINTS.kingHeart; // استرداد المضاعفة
            } else {
                team1Score += POINTS.queen;
            }
        }
    });
    
    // حساب نقاط الفريق الثاني
    const team2Score = POINTS.roundTotal - team1Score;
    
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
