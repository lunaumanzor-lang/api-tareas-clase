# Cómo se despliega hoy la API de tareas (proceso manual)

> Documento interno del equipo de plataforma de **Comercial Delta** (empresa ficticia). Así se
> publica cada versión nueva de la API desde hace un año. Lo escribió la única persona que hacía
> los despliegues, antes de cambiar de equipo.

## Antes de empezar

- Pedir por chat a alguien de desarrollo que confirme que "las pruebas pasaron".
- Avisar en el canal general que la API va a estar caída unos minutos.
- Tener a mano la clave del servidor (está en el correo de bienvenida de quien despliega).

## Pasos

1. Entrar al servidor por SSH como `root`.
2. Ir a la carpeta de la aplicación y traer lo último:

   ```bash
   cd /opt/api-tareas
   git pull
   ```

   Si `git pull` da conflicto, borrar la carpeta y volver a clonar.
3. Instalar las dependencias:

   ```bash
   pip install flask gunicorn
   ```

4. Configurar el token de la API:

   ```bash
   export API_TOKEN=tok_prod_7f3a9c21
   ```

5. Detener la versión anterior. Buscar el proceso con `ps aux | grep gunicorn` y terminarlo con
   `kill -9`.
6. Arrancar la versión nueva:

   ```bash
   nohup gunicorn -b 0.0.0.0:8000 "app:create_app()" &
   ```

7. Abrir `http://<servidor>:8000/tareas` en el navegador. Si carga, el despliegue salió bien.
8. Avisar en el canal general que la API volvió.

## Si algo sale mal

Volver a la versión anterior con `git checkout` al commit de la semana pasada (preguntar cuál era) y
repetir los pasos 3 a 7.

## Historial reciente

| Fecha | Qué pasó |
|---|---|
| Hace 3 semanas | La API no arrancó: `pip` instaló una versión nueva de Flask que cambió un comportamiento. Se resolvió a las dos horas fijando la versión a mano en el servidor. |
| Hace 2 semanas | El despliegue "salió bien" (la página `/tareas` cargaba) pero `POST /tareas` respondía 401 a todos: el token quedó vacío porque la sesión SSH se cerró antes del paso 6. |
| La semana pasada | Nadie sabía qué commit estaba corriendo en el servidor. Se revisó a mano comparando archivos. |
