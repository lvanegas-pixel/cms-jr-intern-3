# Genesal Jr. — repo base

Tu punto de partida para el reto de la semana. Lee `02_ENUNCIADO_SANDBOX.md`
(te lo pasa tu mentor) para saber **qué** construir. Esto explica **cómo arrancar**.

## 1. Entorno (día 1)

```bash
# 1. Crea y activa el entorno virtual
python -m venv venv
source venv/bin/activate        # macOS/Linux
# .\venv\Scripts\activate       # Windows

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Copia el archivo de entorno (el .env real NUNCA se commitea)
cp .env.example .env

# 4. Crea el proyecto Django (si aún no existe)
django-admin startproject config .

# 5. Primeras migraciones + superusuario (para el admin)
python manage.py migrate
python manage.py createsuperuser

# 6. Arranca
python manage.py runserver
```

Abre http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/ — si ves ambas, +10 pts 🎉

## 2. Checklist antes de tu primer commit

- [ ] `git status` NO muestra `.env` ni `venv/` (el `.gitignore` ya los protege).
- [ ] Trabajas en una **rama**, no en `main` (créala desde GitLab, no desde PyCharm).
- [ ] El código está en **inglés**.

## 3. Correr los tests

```bash
pytest
```

## 4. Convención de ramas

```
feature/<numero-issue>-descripcion-corta
# ej: feature/3-project-serializer-validation
```

## 5. Estructura que acabarás teniendo (orientativa)

```
config/              # settings, urls raíz
catalogue/           # tu app principal
├── models.py        # Project, Asset
├── serializers.py   # validación de negocio (Regla 1)
├── permissions.py   # scoping + anti-trampa (Reglas 2 y 3)
├── views.py         # ViewSets DELGADOS
├── urls.py          # router
└── tests/           # pytest
```

> Fíjate: `permissions.py` y `serializers.py` son archivos **separados**. Así está
> montado el Aurora real. Mantén cada cosa en su sitio.
