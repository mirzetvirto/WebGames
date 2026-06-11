# Flask Game Launcher

Esta aplicación ahora incluye versiones web jugables de los tres juegos, además de mantener el lanzador local de Pygame.

## Archivos principales

- `app.py` - servidor Flask que muestra la página web y lanza los juegos.
- `requirements.txt` - dependencias para ejecutar la app.
- `Procfile` - configuración de ejecución para servicios como Heroku/Render.
- `runtime.txt` - versión de Python recomendada.
- `templates/` - plantillas HTML del launcher.

## Cómo ejecutar localmente

1. Activa tu entorno virtual.
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la app:
   ```bash
   python app.py
   ```
4. Abre `http://127.0.0.1:5000`.

## Despliegue en la nube

### Render / Railway / Heroku

1. Sube el proyecto a un repositorio Git.
2. Crea una nueva app en el servicio.
3. Configura el repositorio y usa `Python` como runtime.
4. El servicio detectará `requirements.txt` y `Procfile`.

> Importante: este proyecto solo despliega el launcher web. Los juegos en `tetris.py`, `juego_invaders.py` y `juego_nuevo.py` se ejecutan como aplicaciones de escritorio en el servidor.

## Juegos web

La app ahora sirve versiones web de los juegos directamente en el navegador desde `http://127.0.0.1:5000`.

## Nota importante sobre Pygame local

El botón "Lanzar local" sigue disponible para ejecutar el juego original con Pygame en el servidor local. Esta opción abre una ventana local en la máquina que ejecuta el servidor y no transmite esa ventana al navegador remoto.

Si deseas que los juegos funcionen completamente desde cualquier navegador remoto sin depender de Pygame local, debes usar las versiones web implementadas en `static/js/`.
