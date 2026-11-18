# Avicultura Inteligente (Prototipo TRL5)

Sistema web desarrollado en **Python y Django** para la gestión administrativa y productiva de pequeños y medianos avicultores de Villa Gorgona (Proyecto de Grado UNAD - Ingeniería de Sistemas).

## Instalación y ejecución local

```bash
cd src
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations granjas
python manage.py migrate
python manage.py cargar_datos
python manage.py runserver
```

## Credenciales de prueba
- **Administrador:** `admin` / `Admin2026!`
- **Productor:** `productor` / `Productor2026!`
