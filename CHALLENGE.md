# 🚀 Reto 2 — Evolucionar el CMS Jr.: separar Backend y Frontend

> Tu API ya funciona: tiene modelos, las 3 reglas y tests. Bien.
> Ahora toca el salto de "funciona en mi máquina" a **"una API que otra persona
> puede usar sin preguntarte nada"**. Eso es lo que separa un ejercicio de un
> producto.
>
> El reto tiene 3 fases y van en orden. No empieces la web hasta cerrar la API.

---

## 🧠 La idea de fondo: dos capas, no una

Hasta ahora todo tu proyecto es **backend**: Django sirviendo datos. En este reto
vas a añadir un **frontend**, y lo importante no es la web en sí — es que entiendas
que son **dos capas separadas con responsabilidades distintas**:

```
┌─────────────────┐      HTTP / JSON       ┌──────────────────┐
│    FRONTEND     │ ───── fetch() ──────►  │     BACKEND      │
│  (HTML/CSS/JS)  │                        │  (Django + DRF)  │
│  "la vista"     │ ◄──── respuesta ─────  │  "los datos"     │
└─────────────────┘                        └──────────────────┘
        │                                           │
   NO toca la BD                              Dueño de la BD,
   NO conoce los modelos                      la lógica y las reglas
   SOLO habla por la API                      NO sabe nada del HTML
```

**La regla mental:** el frontend **nunca** toca la base de datos ni los modelos.
Solo pide datos a la API y los pinta. El backend **nunca** sabe cómo se ven los
datos; solo los sirve y protege. Si un día cambias la web entera, el backend no se
entera. Si cambias la base de datos, la web no se entera. **Esa independencia es
todo el punto.**

> En Invelon esto es así de verdad: en proyectos como los de Aurora el backend
> (Django/DRF) y el cliente (web o app móvil) son mundos separados que solo se
> hablan por la API. Aquí lo vives en pequeño.

---

## 📏 Reglas del reto

1. Trabajas sobre **tu repo actual** (`cms-jr-intern-1`), en ramas nuevas. Un PR por fase.
2. Sigue el flujo de siempre: rama → commits limpios → PR → revisión. Aplica lo del git-kata.
3. **Puedes usar IA para entender y construir, pero no subas nada que no sepas explicar.**
   En la revisión te pediré que defiendas cada decisión.
4. Todo en **inglés**. Type hints y docstrings donde toque.

---

## 🎯 FASE 1 — Definir bien la API

Ahora mismo tu API "va", pero tiene agujeros que solo se ven cuando alguien la usa
de verdad. Tu trabajo es cerrarlos. **No te doy la solución: te doy las preguntas.**

### 1.1 Autenticación — ¿quién entra?
Tu API usa permisos por usuario, pero... ¿cómo se loguea alguien que no sea desde
el admin de Django? Ahora mismo un cliente externo (Postman, una web) **no tiene
forma clara de autenticarse**.
- Investiga cómo expone DRF la autenticación (empieza por `SessionAuthentication`
  y `TokenAuthentication`).
- Decide una y configúrala. Deja claro en el README cómo se autentica alguien.

### 1.2 Paginación — ¿y si hay 10.000 proyectos?
Prueba: crea 30 proyectos y haz `GET /api/projects/`. Te devuelve **todos** de golpe.
Eso no escala.
- Activa la paginación de DRF (`PageNumberPagination`).
- ¿Qué pasa ahora con la respuesta? ¿Qué campos nuevos aparecen?

### 1.3 Filtros y búsqueda — ¿cómo busco?
Un comercial quiere ver solo sus assets de tipo `MODEL_3D`. Ahora no puede filtrar.
- Añade filtros (mira `django-filter` y `SearchFilter` de DRF).
- Objetivo: poder hacer `GET /api/assets/?asset_type=IMAGE` y
  `GET /api/projects/?search=<nombre>`.

### 1.4 Repasa tu propia lógica (code-review a ti mismo)
Lee tu `permissions.py` con ojo crítico y responde en el PR:
- En `has_permission`, lees `request.data.get('project')` para el POST. **¿Qué pasa
  si alguien manda un `project` que no existe, o no manda ninguno?** Pruébalo.
- Tu `Project.name` es `unique=True` global. ¿Tiene sentido que **dos comerciales
  distintos** no puedan tener un proyecto con el mismo nombre? ¿Cómo lo arreglarías?
  (pista: `unique_together` / `UniqueConstraint`)
- El error de la Regla 1 dice `'allowed.'` pegado a la palabra anterior. Búscalo. 🐛

> No hace falta que resuelvas los 3 puntos de 1.4 a la perfección. Hace falta que
> los **veas** y digas qué harías. Ver el problema es media solución.

### 📦 Entrega Fase 1
PR titulado `feat: harden API (auth, pagination, filters)` con:
- Autenticación funcionando.
- Paginación activa.
- Al menos un filtro operativo.
- En la descripción del PR: tus respuestas a 1.4.

---

## 🧪 FASE 2 — Probar TODA la API con Postman

Una API no está terminada hasta que está **probada desde fuera**. Vas a montar una
colección de Postman que recorre todos los endpoints.

### 2.1 Crea una colección `CMS Jr.`
Con una **variable de entorno** `{{base_url}}` = `http://127.0.0.1:8000`. (Así no
repites la URL en cada request. Es como lo hacemos en Invelon.)

### 2.2 Cubre los 5 endpoints CRUD × 2 recursos
Para `projects` y `assets`:

| Método | Endpoint | Qué pruebas |
|---|---|---|
| `GET` | `/api/projects/` | Lista (¿paginada?) |
| `POST` | `/api/projects/` | Crear |
| `GET` | `/api/projects/{id}/` | Detalle |
| `PATCH` | `/api/projects/{id}/` | Editar |
| `DELETE` | `/api/projects/{id}/` | Borrar |

### 2.3 Prueba también lo que DEBE fallar (esto es lo importante)
Un buen tester no prueba solo el camino feliz. Captura en Postman:
- Crear un **2º `MODEL_3D`** en el mismo proyecto → debe dar **400** (Regla 1).
- Tocar el proyecto de **otro usuario** → debe dar **403/404** (Regla 3).
- Petición **sin autenticar** → debe dar **401/403**.

### 2.4 Autenticación en Postman
Configura el login (token o sesión, lo que elegiste en 1.1) para que las requests
vayan autenticadas. Documenta cómo se obtiene el token.

### 📦 Entrega Fase 2
- **Exporta la colección** (`.json`) y súbela al repo en una carpeta `/postman`.
- En el PR, pega **capturas** de: 1 caso feliz, el 400 de la Regla 1, y el 403 de la Regla 3.

> 🎤 En la revisión te preguntaré: *"enséñame en vivo un 403"*. Si lo reproduces en
> 10 segundos, es que entiendes tus permisos.

---

## 🌐 FASE 3 — El Frontend: una capa separada que consume tu API

Ahora construyes el **frontend**: HTML + CSS + JavaScript puro (sin frameworks) que
vive en el repo y consume tu API por `fetch()`. Aquí es donde las dos capas del
diagrama de arriba se vuelven reales.

**La prueba de que lo hiciste bien:** tu carpeta `/frontend` no importa **nada** de
Django. No conoce tus modelos, no toca la base de datos, no sabe qué es un
serializer. Solo hace peticiones HTTP a `http://127.0.0.1:8000/api/...` y pinta lo
que recibe. Si borraras toda la carpeta `catalog/` y levantaras otro backend
distinto que responda igual, tu web seguiría funcionando. **Eso es separar capas.**

### 3.1 Qué tiene que hacer la web
Una sola página que:
1. **Liste los proyectos** (llamando a `GET /api/projects/`).
2. Permita **crear un proyecto** nuevo desde un formulario (`POST`).
3. Al pinchar un proyecto, **muestre sus assets**.
4. Maneje el caso de **error** (si la API devuelve 400/403, enséñalo en pantalla, no
   en la consola).

No tiene que ser bonita. Tiene que **funcionar y usar la API de verdad**.

### 3.2 Dónde ponerla
Carpeta `/frontend` en el repo con `index.html`, `style.css`, `app.js`.
Arráncala simple: `python -m http.server` o la extensión Live Server de VS Code.

### 3.3 El muro con el que vas a chocar (y está bien)
Cuando tu web en `localhost:5500` llame a tu API en `localhost:8000`, el navegador
te va a **bloquear la petición**. Es el error **CORS**. No es un bug tuyo: es
seguridad del navegador.
- Investiga qué es CORS y por qué salta.
- Resuélvelo en el backend (pista: `django-cors-headers`).
- **En el PR explica con tus palabras: ¿qué es CORS y por qué el navegador lo hace?**

> Este choque es intencionado. Todo el que conecta un frontend a un backend pasa por
> aquí la primera vez. Resolverlo una vez = no volver a tenerle miedo.

### 📦 Entrega Fase 3
PR con la carpeta `/frontend` funcionando + CORS resuelto + tu explicación de CORS.

---

## 🏁 Cierre

Cuando cierres las 3 fases, tu repo pasa de "una API de ejercicio" a **"un servicio
con su cliente, documentado y probado"**. Eso ya se parece a lo que hacemos en
proyectos reales.

Marca una versión: `git tag -a v0.2.0 -m "API hardened + Postman + web client"` y
una Release en GitHub con las notas de lo que añadiste.

### ✅ Antes de dar por terminado
- [ ] La API tiene auth, paginación y al menos un filtro.
- [ ] Viste los 3 problemas de la sección 1.4 (aunque no los resolvieras todos).
- [ ] Hay una colección de Postman en `/postman` que prueba casos felices **y** de error.
- [ ] La web lista y crea proyectos consumiendo la API por `fetch`.
- [ ] CORS resuelto y sabes explicar qué es.
- [ ] Tag `v0.2.0` + Release.

### 🎤 Prepárate para defender en la revisión
- **¿Por qué separamos backend y frontend? ¿Qué responsabilidad tiene cada capa?**
- ¿Tu frontend podría funcionar con un backend distinto? ¿Por qué sí/no?
- ¿Qué autenticación elegiste y por qué?
- ¿Por qué CORS es un problema del navegador y no de tu Django?
- Enséñame un 403 en vivo desde Postman.
- Si tuvieras 10.000 proyectos, ¿qué endpoint reventaría y cómo lo evitaste?

**Bloqueado más de 30 min → paras y lo apuntas.** Llegas a la revisión con dudas
escritas, no con la pantalla en blanco.
