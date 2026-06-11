const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const COLS = 10;
const ROWS = 20;
const CELL = 25;
const WIDTH = COLS * CELL + 160;
const HEIGHT = ROWS * CELL;
canvas.width = WIDTH;
canvas.height = HEIGHT;

const audioButton = document.getElementById('audioButton');
const backgroundMusic = new Audio('audio/musica_aliens1.mp3');
backgroundMusic.loop = true;
backgroundMusic.volume = 0.4;
backgroundMusic.load();

const tryPlayMusic = () => {
    backgroundMusic.play().then(() => {
        if (audioButton) {
            audioButton.style.display = 'none';
        }
    }).catch(() => {
        // autoplay blocked until a user gesture occurs
    });
};

backgroundMusic.play().catch(() => {
    if (audioButton) {
        audioButton.style.display = 'inline-block';
        audioButton.addEventListener('click', tryPlayMusic);
    }
    window.addEventListener('keydown', tryPlayMusic);
    window.addEventListener('click', tryPlayMusic);
});

const COLORS = [
    '#000', '#2cefff', '#0000ff', '#ff9f00', '#ffff00', '#00ff00', '#8a2be2', '#ff0000', '#ffaa00'
];

const SHAPES = [
    [[1, 1, 1, 1]],
    [[0, 2, 2], [2, 2, 0]],
    [[3, 3, 0], [0, 3, 3]],
    [[4, 4], [4, 4]],
    [[5, 0, 0], [5, 5, 5]],
    [[0, 0, 6], [6, 6, 6]],
    [[7, 7, 7], [0, 7, 0]],
    [[8]]
];

let grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
let currentPiece = null;
let nextPiece = null;
let score = 0;
let dropCounter = 0;
let dropInterval = 800;
let lastTime = 0;
let gameOver = false;

function createPiece() {
    const index = Math.floor(Math.random() * (SHAPES.length - 1));
    const shape = SHAPES[index].map(row => row.slice());
    return { x: 3, y: -2, shape, color: index + 1, isBomb: false };
}

function createBomb() {
    return { x: 4, y: -1, shape: SHAPES[7], color: 8, isBomb: true };
}

function newPiece() {
    if (!nextPiece) nextPiece = Math.random() < 0.1 ? createBomb() : createPiece();
    currentPiece = nextPiece;
    nextPiece = Math.random() < 0.1 ? createBomb() : createPiece();
}

function rotate(matrix) {
    return matrix[0].map((_, index) => matrix.map(row => row[row.length - 1 - index]));
}

function validMove(piece, offsetX = 0, offsetY = 0, shape = null) {
    const m = shape || piece.shape;
    for (let y = 0; y < m.length; y++) {
        for (let x = 0; x < m[y].length; x++) {
            if (m[y][x] !== 0) {
                const newX = piece.x + x + offsetX;
                const newY = piece.y + y + offsetY;
                if (newX < 0 || newX >= COLS || newY >= ROWS) return false;
                if (newY >= 0 && grid[newY][newX] !== 0) return false;
            }
        }
    }
    return true;
}

function mergePiece() {
    const { shape, color, x: px, y: py } = currentPiece;
    for (let y = 0; y < shape.length; y++) {
        for (let x = 0; x < shape[y].length; x++) {
            if (shape[y][x] !== 0 && py + y >= 0) {
                grid[py + y][px + x] = color;
            }
        }
    }
}

function clearLines() {
    let lines = 0;
    outer: for (let y = ROWS - 1; y >= 0; y--) {
        for (let x = 0; x < COLS; x++) {
            if (grid[y][x] === 0) continue outer;
        }
        grid.splice(y, 1);
        grid.unshift(Array(COLS).fill(0));
        lines += 1;
        y++;
    }
    if (lines > 0) {
        score += lines * 100;
        dropInterval = Math.max(150, dropInterval - lines * 30);
    }
}

function explodeBomb(px, py) {
    for (let y = py - 2; y <= py + 2; y++) {
        for (let x = px - 2; x <= px + 2; x++) {
            if (x >= 0 && x < COLS && y >= 0 && y < ROWS) {
                grid[y][x] = 0;
            }
        }
    }
}

function playerDrop() {
    if (!validMove(currentPiece, 0, 1)) {
        if (currentPiece.y < 0) {
            gameOver = true;
            return;
        }
        if (currentPiece.isBomb) {
            explodeBomb(currentPiece.x, currentPiece.y);
        } else {
            mergePiece();
        }
        clearLines();
        newPiece();
        return;
    }
    currentPiece.y += 1;
}

function update(time = 0) {
    const delta = time - lastTime;
    lastTime = time;
    dropCounter += delta;
    if (dropCounter > dropInterval) {
        playerDrop();
        dropCounter = 0;
    }
    draw();
    if (!gameOver) requestAnimationFrame(update);
}

function drawCell(x, y, colorIndex) {
    ctx.fillStyle = COLORS[colorIndex];
    ctx.fillRect(x * CELL, y * CELL, CELL - 1, CELL - 1);
}

function draw() {
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, WIDTH, HEIGHT);
    for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
            if (grid[y][x] !== 0) drawCell(x, y, grid[y][x]);
        }
    }
    if (currentPiece) {
        currentPiece.shape.forEach((row, y) => {
            row.forEach((value, x) => {
                if (value !== 0 && currentPiece.y + y >= 0) {
                    drawCell(currentPiece.x + x, currentPiece.y + y, currentPiece.color);
                }
            });
        });
    }
    ctx.fillStyle = '#eee';
    ctx.font = '18px Arial';
    ctx.fillText(`Puntaje: ${score}`, COLS * CELL + 10, 30);
    ctx.fillText('Controles:', COLS * CELL + 10, 70);
    ctx.fillText('← → desplazamiento', COLS * CELL + 10, 100);
    ctx.fillText('↑ rotar', COLS * CELL + 10, 130);
    ctx.fillText('↓ bajar rápido', COLS * CELL + 10, 160);
    if (gameOver) {
        ctx.fillStyle = '#ff5555';
        ctx.font = '24px Arial';
        ctx.fillText('Game Over', COLS * CELL + 10, 220);
    }
}

window.addEventListener('keydown', event => {
    if (event.key.toLowerCase() === 'r' && gameOver) {
        grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
        score = 0;
        dropInterval = 800;
        gameOver = false;
        newPiece();
        requestAnimationFrame(update);
        return;
    }
    if (gameOver) return;
    if (event.key === 'ArrowLeft' && validMove(currentPiece, -1, 0)) currentPiece.x -= 1;
    if (event.key === 'ArrowRight' && validMove(currentPiece, 1, 0)) currentPiece.x += 1;
    if (event.key === 'ArrowDown') playerDrop();
    if (event.key === 'ArrowUp') {
        const rotated = rotate(currentPiece.shape);
        if (validMove(currentPiece, 0, 0, rotated)) currentPiece.shape = rotated;
    }
});

newPiece();
nextPiece = createPiece();
requestAnimationFrame(update);
