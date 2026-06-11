import os
import sys
import subprocess
from flask import Flask, render_template, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GAMES = {
    'tetris': {
        'title': 'Tetris',
        'file': 'tetris.py',
        'description': 'Juego de Tetris con piezas y bomba especial.',
        'instructions': 'Flechas izquierda/derecha para mover, arriba para rotar y abajo para bajar rápido.'
    },
    'invaders': {
        'title': 'Space Invaders',
        'file': 'juego_invaders.py',
        'description': 'Aliens clásicos con disparos y oleadas crecientes.',
        'instructions': 'Flechas izquierda/derecha para mover, espacio para disparar.'
    },
    'snake': {
        'title': 'Snake / Juego nuevo',
        'file': 'juego_nuevo.py',
        'description': 'Snake básico con pausa y velocidad creciente.',
        'instructions': 'Flechas para mover, P para pausar, R para reiniciar.'
    },
}

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


def launch_game(game_key):
    game = GAMES.get(game_key)
    if not game:
        return None

    script_path = os.path.join(BASE_DIR, game['file'])
    if not os.path.exists(script_path):
        return None

    try:
        subprocess.Popen(
            [sys.executable, script_path],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return game
    except OSError:
        return None


@app.route('/')
def index():
    return render_template('index.html', games=GAMES)


@app.route('/play/<game_key>')
def play(game_key):
    game = GAMES.get(game_key)
    if not game:
        return redirect(url_for('index'))
    return render_template('game.html', game=game, game_key=game_key)


@app.route('/launch/<game_key>')
def launch(game_key):
    game = launch_game(game_key)
    if not game:
        return render_template('launch.html', success=False, game_key=game_key)
    return render_template('launch.html', success=True, game=game)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
