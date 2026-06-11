const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 640;
canvas.height = 700;

const PLAYER_WIDTH = 50;
const PLAYER_HEIGHT = 18;
const PLAYER_SPEED = 6;
const BULLET_SPEED = 7;
const ALIEN_SIZE = 40;
const ALIEN_ROWS = 4;
const ALIEN_COLS = 8;

const player = { x: canvas.width / 2 - PLAYER_WIDTH / 2, y: canvas.height - 80, lives: 5 };
const bullets = [];
const enemyBullets = [];
const aliens = [];
let alienDirection = 1;
let alienSpeed = 0.8;
let score = 0;
let gameOver = false;
let lastTime = 0;
const keys = {};

const backgroundMusic = new Audio('audio/musica_aliens1.mp3');
backgroundMusic.loop = true;
backgroundMusic.volume = 0.4;
backgroundMusic.play().catch(() => {
    // Autoplay may be blocked. Play on first interaction.
    const tryPlay = () => {
        backgroundMusic.play().catch(() => {});
        window.removeEventListener('keydown', tryPlay);
        window.removeEventListener('click', tryPlay);
    };
    window.addEventListener('keydown', tryPlay);
    window.addEventListener('click', tryPlay);
});

function setupAliens() {
    aliens.length = 0;
    const offsetX = 60;
    const offsetY = 80;
    const gapX = 70;
    const gapY = 60;
    for (let row = 0; row < ALIEN_ROWS; row++) {
        for (let col = 0; col < ALIEN_COLS; col++) {
            aliens.push({ x: offsetX + col * gapX, y: offsetY + row * gapY, alive: true });
        }
    }
}

function reset() {
    player.x = canvas.width / 2 - PLAYER_WIDTH / 2;
    player.lives = 5;
    bullets.length = 0;
    enemyBullets.length = 0;
    alienDirection = 1;
    alienSpeed = 0.8;
    score = 0;
    gameOver = false;
    setupAliens();
}

function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#00b';
    ctx.fillRect(player.x, player.y, PLAYER_WIDTH, PLAYER_HEIGHT);
    ctx.fillStyle = '#1af';
    ctx.beginPath();
    ctx.moveTo(player.x, player.y);
    ctx.lineTo(player.x + PLAYER_WIDTH / 2, player.y - 20);
    ctx.lineTo(player.x + PLAYER_WIDTH, player.y);
    ctx.closePath();
    ctx.fill();

    bullets.forEach(b => {
        ctx.fillStyle = '#ff0';
        ctx.fillRect(b.x, b.y, 6, 18);
    });
    enemyBullets.forEach(b => {
        ctx.fillStyle = '#f33';
        ctx.fillRect(b.x, b.y, 6, 18);
    });

    aliens.forEach(alien => {
        if (!alien.alive) return;
        ctx.fillStyle = '#0f0';
        ctx.fillRect(alien.x, alien.y, ALIEN_SIZE, ALIEN_SIZE);
        ctx.fillStyle = '#000';
        ctx.fillRect(alien.x + 8, alien.y + 10, 8, 8);
        ctx.fillRect(alien.x + 24, alien.y + 10, 8, 8);
        ctx.fillRect(alien.x + 14, alien.y + 24, 12, 8);
    });

    ctx.fillStyle = '#eee';
    ctx.font = '18px Arial';
    ctx.fillText(`Puntos: ${score}`, 16, 28);
    ctx.fillText(`Vidas: ${player.lives}`, 16, 52);
    ctx.fillText('Flechas: mover, Espaço: disparar', 16, 76);

    if (gameOver) {
        ctx.fillStyle = '#ff5555';
        ctx.font = '32px Arial';
        ctx.fillText('GAME OVER', 220, 300);
        ctx.font = '20px Arial';
        ctx.fillText('Presiona R para reiniciar', 190, 340);
    }
}

function collideRect(a, b) {
    return a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
}

function update(delta) {
    if (gameOver) return;

    if (keys.ArrowLeft) player.x = Math.max(0, player.x - PLAYER_SPEED);
    if (keys.ArrowRight) player.x = Math.min(canvas.width - PLAYER_WIDTH, player.x + PLAYER_SPEED);

    if (Math.random() < Math.min(0.005 + score * 0.0002, 0.02)) {
        const aliveAliens = aliens.filter(alien => alien.alive);
        if (aliveAliens.length > 0) {
            const shooter = aliveAliens[Math.floor(Math.random() * aliveAliens.length)];
            enemyBullets.push({ x: shooter.x + ALIEN_SIZE / 2 - 3, y: shooter.y + ALIEN_SIZE, width: 6, height: 18 });
        }
    }

    aliens.forEach(alien => {
        if (!alien.alive) return;
        alien.x += alienDirection * alienSpeed;
    });
    const aliveAliens = aliens.filter(a => a.alive);
    const leftMost = Math.min(...aliveAliens.map(a => a.x));
    const rightMost = Math.max(...aliveAliens.map(a => a.x + ALIEN_SIZE));
    if (rightMost >= canvas.width - 20 && alienDirection === 1) {
        alienDirection = -1;
        aliens.forEach(alien => alien.y += 20);
    } else if (leftMost <= 20 && alienDirection === -1) {
        alienDirection = 1;
        aliens.forEach(alien => alien.y += 20);
    }

    bullets.forEach((bullet, index) => {
        bullet.y -= BULLET_SPEED;
        if (bullet.y < 0) bullets.splice(index, 1);
    });
    enemyBullets.forEach((bullet, index) => {
        bullet.y += BULLET_SPEED;
        if (bullet.y > canvas.height) enemyBullets.splice(index, 1);
    });

    bullets.forEach((bullet, bIndex) => {
        aliens.forEach(alien => {
            if (!alien.alive) return;
            if (bullet.x >= alien.x && bullet.x <= alien.x + ALIEN_SIZE && bullet.y >= alien.y && bullet.y <= alien.y + ALIEN_SIZE) {
                alien.alive = false;
                bullets.splice(bIndex, 1);
                score += 10;
            }
        });
    });

    enemyBullets.forEach((bullet, index) => {
        if (bullet.x >= player.x && bullet.x <= player.x + PLAYER_WIDTH && bullet.y >= player.y && bullet.y <= player.y + PLAYER_HEIGHT) {
            enemyBullets.splice(index, 1);
            player.lives -= 1;
            if (player.lives <= 0) gameOver = true;
        }
    });

    aliens.forEach(alien => {
        if (!alien.alive) return;
        if (alien.y + ALIEN_SIZE >= player.y) gameOver = true;
    });

    if (aliens.every(a => !a.alive)) {
        setupAliens();
        alienSpeed = Math.min(2.5, alienSpeed + 0.2);
    }
}

function gameLoop(timestamp) {
    if (!lastTime) lastTime = timestamp;
    const delta = timestamp - lastTime;
    lastTime = timestamp;
    update(delta);
    draw();
    requestAnimationFrame(gameLoop);
}

window.addEventListener('keydown', event => {
    keys[event.key] = true;
    if (event.key === ' ' && !gameOver) {
        bullets.push({ x: player.x + PLAYER_WIDTH / 2 - 3, y: player.y, width: 6, height: 18 });
    }
    if (event.key.toLowerCase() === 'r' && gameOver) reset();
});
window.addEventListener('keyup', event => {
    keys[event.key] = false;
});

reset();
requestAnimationFrame(gameLoop);
