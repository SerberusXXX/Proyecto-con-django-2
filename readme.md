# Reserva ECCI

Sistema de reservas tipo catalogo para consultar salones, auditorios, laboratorios y equipos disponibles. El proyecto esta separado en 1 modulo publico y 2 modulos privados protegidos por inicio de sesion.

## Funcionalidades

- Catalogo publico de recursos activos.
- Consulta de disponibilidad por fecha.
- Detalle publico de cada recurso con horarios ocupados.
- Registro e inicio de sesion de usuarios.
- Modulo privado 1: panel para consultar y cancelar reservas propias.
- Modulo privado 2: agenda interna para revisar la ocupacion activa de todos los recursos.
- Creacion de reservas solo para usuarios autenticados.
- Cancelacion de reservas propias.
- Validacion de cruces de horario para evitar dobles reservas.
- Base de datos PostgreSQL con Docker.
- Panel de administracion de Django.

## Flujo principal

1. El visitante entra a `http://localhost:9000/myapp/`.
2. Revisa salones o equipos disponibles.
3. Si quiere reservar, el sistema lo envia a iniciar sesion o crear cuenta.
4. El usuario crea la reserva.
5. Desde `Privado 1: reservas`, consulta o cancela sus reservas.
6. Desde `Privado 2: agenda`, consulta la ocupacion interna por fecha.

## Modulos del proyecto

`Modulo publico`

- Ruta principal: `/myapp/`
- Permite ver recursos activos y disponibilidad por fecha.
- No requiere iniciar sesion.

`Modulo privado 1: reservas`

- Ruta principal: `/myapp/panel/`
- Permite crear, consultar y cancelar reservas propias.
- Requiere usuario autenticado.

`Modulo privado 2: agenda`

- Ruta principal: `/myapp/agenda/`
- Permite consultar la agenda interna de todos los recursos por fecha.
- Requiere usuario autenticado.

## Estructura principal

```txt
django-main/
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- .env.example
|-- manage.py
|-- mi_proyecto/
|   |-- settings.py
|   `-- urls.py
`-- myapp/
    |-- admin.py
    |-- forms.py
    |-- models.py
    |-- tests.py
    |-- urls.py
    |-- views.py
    |-- migrations/
    `-- templates/
```

## Modelos

`Recurso`: representa lo que se puede reservar.

- Nombre
- Tipo
- Ubicacion
- Capacidad
- Descripcion
- Estado activo/inactivo

`Reserva`: representa la solicitud de un usuario.

- Recurso
- Usuario
- Responsable
- Correo
- Fecha
- Hora de inicio
- Hora de fin
- Estado activa/cancelada
- Motivo de cancelacion

## Ejecutar con Docker y PostgreSQL

1. Copiar variables de entorno:

```bash
cp .env.example .env
```

2. Construir y levantar servicios:

```bash
docker compose up --build
```

3. Ejecutar migraciones en otra terminal:

```bash
docker compose exec web python manage.py migrate
```

4. Abrir:

```txt
http://localhost:9000/myapp/
```

## Crear superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

Luego entrar a:

```txt
http://localhost:9000/admin/
```

## Ejecutar localmente con SQLite

Para pruebas locales sin Docker:

```powershell
.\.venv\Scripts\Activate.ps1
$env:DB_ENGINE="sqlite"
python manage.py migrate
python manage.py runserver 127.0.0.1:9001
```

Tambien puedes usar:

```powershell
.\run_local_sqlite.cmd
```

## Pruebas

```powershell
$env:DB_ENGINE="sqlite"
python manage.py test
```

## Subir a GitHub

```bash
git init
git add .
git commit -m "Sistema de reservas con login y PostgreSQL"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```
