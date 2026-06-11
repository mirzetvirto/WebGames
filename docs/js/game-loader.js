const GAMES = {
    tetris: {
        title: 'Tetris',
        description: 'Un Tetris con piezas, bombas especiales y puntaje.',
    },
    invaders: {
        title: 'Space Invaders',
        description: 'Dispara a los invasores mientras esquivas sus proyectiles.',
    },
    snake: {
        title: 'Snake',
        description: 'Juega la serpiente con velocidad creciente y pausa.',
    },
};

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function showInvalidGame(message) {
    const invalidMessage = document.getElementById('invalidMessage');
    const gameContainer = document.getElementById('gameContainer');
    invalidMessage.textContent = message;
    invalidMessage.style.display = 'block';
    gameContainer.style.display = 'none';
    document.getElementById('gameTitle').textContent = 'Juego no encontrado';
    document.getElementById('gameDescription').textContent = '';
}

function loadGame(gameKey) {
    const game = GAMES[gameKey];
    if (!game) {
        showInvalidGame('El juego no existe o el enlace está dañado. Vuelve al menú e intenta otro juego.');
        return;
    }

    document.title = `${game.title} - Juegos Web`;
    document.getElementById('gameTitle').textContent = game.title;
    document.getElementById('gameDescription').textContent = game.description;

    const script = document.createElement('script');
    script.src = `js/${gameKey}.js`;
    script.onload = () => {
        console.log(`${gameKey} cargado correctamente.`);
    };
    script.onerror = () => {
        showInvalidGame('No se pudo cargar el juego. Comprueba que el archivo js exista en el directorio.');
    };
    document.body.appendChild(script);
}

window.addEventListener('DOMContentLoaded', () => {
    const gameKey = getQueryParam('game');
    if (!gameKey) {
        showInvalidGame('No se ha especificado un juego. Usa el menú principal para iniciar un juego.');
        return;
    }
    loadGame(gameKey);
});
