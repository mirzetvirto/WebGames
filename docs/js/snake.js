const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const CELL = 20;
const COLS = 30;
const ROWS = 30;
canvas.width = COLS * CELL;
canvas.height = ROWS * CELL;

let snake = [{ x: 15, y: 15 }, { x: 14, y: 15 }, { x: 13, y: 15 }];
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let food = { x: 20, y: 15 };
let speed = 100;
let lastTime = 0;
let elapsed = 0;
let score = 0;
let paused = false;
let gameOver = false;

function randomFood() {
    const positions = new Set(snake.map(cell => `${cell.x},${cell.y}`));
    while (true) {
        const x = Math.floor(Math.random() * COLS);
        const y = Math.floor(Math.random() * ROWS);
        if (!positions.has(`${x},${y}`)) {
            return { x, y };
        }
    }
}

function resetGame() {
    snake = [{ x: 15, y: 15 }, { x: 14, y: 15 }, { x: 13, y: 15 }];
    direction = { x: 1, y: 0 };
    nextDirection = { x: 1, y: 0 };
    food = randomFood();
    score = 0;
    speed = 100;
    paused = false;
    gameOver = false;
}

function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#d12';
    ctx.fillRect(food.x * CELL, food.y * CELL, CELL, CELL);

    ctx.fillStyle = '#1f8';
    snake.forEach((cell, index) => {
        ctx.fillRect(cell.x * CELL, cell.y * CELL, CELL, CELL);
        if (index === 0) {
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.strokeRect(cell.x * CELL, cell.y * CELL, CELL, CELL);
        }
    });

    ctx.fillStyle = '#eee';
    ctx.font = '18px Arial';
    ctx.fillText(`Puntaje: ${score}`, 10, 22);
    if (paused) {
        ctx.fillStyle = '#fff';
        ctx.font = '28px Arial';
        ctx.fillText('Pausado', 220, 300);
    }
    if (gameOver) {
        ctx.fillStyle = '#ff5555';
        ctx.font = '32px Arial';
        ctx.fillText('Fin del juego', 190, 300);
        ctx.font = '20px Arial';
        ctx.fillText('Pulsa R para reiniciar', 170, 340);
    }
}

function update() {
    if (paused || gameOver) {
        draw();
        requestAnimationFrame(gameLoop);
        return;
    }

    const head = { x: snake[0].x + direction.x, y: snake[0].y + direction.y };
    if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS || snake.some(cell => cell.x === head.x && cell.y === head.y)) {
        gameOver = true;
        draw();
        requestAnimationFrame(gameLoop);
        return;
    }

    snake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
        score += 1;
        food = randomFood();
        if (score % 5 === 0) {
            speed = Math.max(40, speed - 10);
        }
    } else {
        snake.pop();
    }

    draw();
    requestAnimationFrame(gameLoop);
}

function gameLoop(timestamp) {
    if (!lastTime) lastTime = timestamp;
    elapsed += timestamp - lastTime;
    lastTime = timestamp;

    if (elapsed >= speed) {
        elapsed = 0;
        direction = nextDirection;
        update();
    } else {
        draw();
        requestAnimationFrame(gameLoop);
    }
}

window.addEventListener('keydown', event => {
    if (event.key === 'ArrowUp' && direction.y !== 1) nextDirection = { x: 0, y: -1 };
    if (event.key === 'ArrowDown' && direction.y !== -1) nextDirection = { x: 0, y: 1 };
    if (event.key === 'ArrowLeft' && direction.x !== 1) nextDirection = { x: -1, y: 0 };
    if (event.key === 'ArrowRight' && direction.x !== -1) nextDirection = { x: 1, y: 0 };
    if (event.key.toLowerCase() === 'p') paused = !paused;
    if (event.key.toLowerCase() === 'r' && gameOver) resetGame();
});

resetGame();
requestAnimationFrame(gameLoop);
