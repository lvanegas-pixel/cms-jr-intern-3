# 🚀 Reto de la semana: **CMS Jr.**

> Bienvenid@ a Invelon. Esta semana no vas a tocar código de clientes todavía.
> Vas a construir, desde cero y en tu propio repo, una versión en miniatura de un
> tipo de sistema **real** que tenemos en producción: un **CMS** (gestor de
> contenido) multi-usuario con roles y permisos.
>
> Cuando acabes, vas a reconocer la arquitectura de nuestros proyectos reales
> porque la habrás vivido en pequeño. Ese es el objetivo: no "hacer una práctica",
> sino **entrar al código real sin perderte**.

---

## 🎯 El contexto

Un CMS tiene un catálogo de contenido que gestionan varias personas con **roles
distintos**: administradores y comerciales. No todos ven lo mismo, y nadie puede
tocar lo que no es suyo.

Tu misión: construir una API REST que gestione eso, en versión mínima.
La llamamos **CMS Jr.**

## 🧱 Qué vas a construir

Una API en **Django + Django REST Framework** con dos entidades:

### `Project` (un proyecto del catálogo)
- `name` — texto, obligatorio, mínimo 3 caracteres.
- `owner` — el usuario (comercial) dueño del proyecto.
- `created_at` — fecha automática.

### `Asset` (un elemento de contenido dentro de un proyecto)
- `project` — a qué proyecto pertenece.
- `name` — texto, obligatorio.
- `asset_type` — uno de: `MODEL_3D`, `IMAGE`, `VIDEO`.
- `is_public` — booleano, por defecto `False`.

## 📐 Las 3 reglas que lo hacen interesante

Esto NO es un CRUD normal. Hay 3 reglas que te van a hacer pensar *dónde* va cada
cosa. En Invelon, **el sitio importa tanto como que funcione.**

### Regla 1 — Validación de negocio (va en el Serializer)
> Un `Project` solo puede tener **un** `Asset` de tipo `MODEL_3D`.
> (En un CMS real, un proyecto tiene un único modelo 3D principal.)

Si alguien intenta crear un segundo `MODEL_3D` en el mismo proyecto, la API lo
rechaza con un error claro. **Esta lógica vive en el Serializer, nunca en la vista.**

### Regla 2 — Scoping por rol (quién ve qué)
> - Un usuario con rol `commercial` solo ve **sus** proyectos (los que tiene como `owner`).
> - Un usuario con rol `admin` ve **todos** los proyectos.

### Regla 3 — Anti-trampa (va en una Permission Class)
> Nadie puede crear un `Asset` dentro de un proyecto que **no es suyo**.
> Si lo intentas, la API responde con **403** (o 404, pregúntale a tu mentor por qué
> a veces es mejor 404).

**Las reglas 2 y 3 viven en una Permission Class, NUNCA dentro de la vista.**

## ✅ Qué significa "terminado" en Invelon

Un endpoint NO está terminado solo porque "funciona". Está terminado cuando:
- [ ] La validación de negocio está **en el serializer**.
- [ ] Los permisos están **en una Permission Class**, no en la vista.
- [ ] La vista (ViewSet) está **delgada**: sin lógica de negocio dentro.
- [ ] Tiene **al menos un test** con pytest que lo prueba.
- [ ] Todo el código y comentarios están **en inglés**.
- [ ] Hay **type hints y docstrings** donde toca.
- [ ] Pasó por un **Pull Request** en GitHub (ver sección Git abajo).

---

## 🌿 Git & GitHub — el flujo profesional (OBLIGATORIO)

Trabajas en **GitHub**. Cada vez que tocas algo, lo haces en una rama y lo integras
con un **Pull Request (PR)**. En algunos proyectos de Invelon verás que a esto le
llaman *Merge Request (MR)*: es exactamente lo mismo, solo cambia el nombre entre
GitHub (PR) y GitLab (MR).

**No se evalúa solo que el código funcione: se evalúa cómo usas Git.**

### Lo mínimo que tienes que dominar esta semana

**1. Clonar y configurar**
```bash
git clone https://github.com/<tu-repo>.git
cd <tu-repo>
```

**2. Crear una rama por cada tarea** (nunca trabajes directo en `main`)
```bash
git checkout -b feature/3-project-serializer-validation
```
Convención: `feature/<numero-issue>-descripcion-corta`.

**3. Guardar tu trabajo: add → commit → push**
```bash
git add .
git commit -m "Add MODEL_3D uniqueness validation in serializer"
git push -u origin feature/3-project-serializer-validation
```

**4. Traer cambios del remoto: fetch vs pull** (tienes que saber la diferencia)
- `git fetch` → **descarga** los cambios del remoto pero NO los aplica a tu rama.
  Sirve para "mirar antes de tocar".
- `git pull` → `fetch` + `merge`: descarga **y** fusiona en tu rama actual.
```bash
git fetch origin
git pull origin main
```

**5. Rebase: reescribir tu historia sobre la última base**
Cuando `main` avanzó mientras tú trabajabas, pon tus commits *encima* de lo nuevo:
```bash
git fetch origin
git rebase origin/main
# si hay conflictos: los resuelves, luego:
git add .
git rebase --continue
```
> Diferencia clave que te van a preguntar: **merge** conserva la historia tal cual
> (crea un commit de merge); **rebase** la reescribe en línea recta (más limpia).
> Regla de la casa: **rebase para actualizar tu rama; merge (vía PR) para integrar a `main`.**

**6. Squash: juntar varios commits en uno limpio**
Si hiciste 5 commits tipo "wip", "fix", "otra vez", únelos en uno solo antes del PR:
```bash
git rebase -i origin/main
# en el editor: deja 'pick' en el primero y 'squash' (o 's') en los demás
```
Un PR con un historial limpio (1-2 commits con mensaje claro) vale más que 10 commits "asdf".

**7. Abrir el Pull Request**
- Push de tu rama → ve a GitHub → botón **"Compare & pull request"**.
- Base: `main` ← Compare: tu rama.
- **Título claro** + **descripción**: qué hace y cómo probarlo.
- Asigna a tu mentor como revisor.

**8. El PR se revisa, no se auto-mergea**
Tu mentor deja comentarios. Corriges **en la misma rama** (nuevo commit o amend +
push) y el PR se actualiza solo. Cuando está aprobado → merge.

**9. Release + tag (el viernes): marcar una versión**
Cuando `main` tiene tu trabajo terminado, marcas una **versión** con un *tag*. Así
se sabe qué commit exacto es la release `0.1.0` (igual que el doc 3 de Invelon).
```bash
git checkout main
git pull origin main
git tag -a v0.1.0 -m "First working release: CMS Jr. API"
git push origin v0.1.0
```
Después, en GitHub → pestaña **Releases** → **Draft a new release** → eliges el tag
`v0.1.0`, pones título y pegas tus **Release Notes** (qué hiciste en esta versión).
> Versionado semántico (SemVer): `MAJOR.MINOR.PATCH` → `v0.1.0`.
> - `PATCH` (0.0.**X**) = un bugfix. `MINOR` (0.**X**.0) = nueva funcionalidad.
> - `MAJOR` (**X**.0.0) = cambio que rompe compatibilidad.

### Glosario rápido Git

| Término | Qué es |
|---|---|
| `clone` | Copiar el repo remoto a tu máquina. |
| `branch` | Línea de trabajo paralela. Una por tarea. |
| `commit` | Guardar un cambio en la historia, con mensaje. |
| `push` | Subir tus commits al remoto. |
| `fetch` | Descargar cambios remotos SIN fusionarlos. |
| `pull` | `fetch` + `merge` en tu rama actual. |
| `merge` | Fusionar una rama en otra (conserva historia). |
| `rebase` | Reaplicar tus commits sobre otra base (historia lineal). |
| `squash` | Combinar varios commits en uno. |
| `PR` (Pull Request) | Petición de integrar tu rama a `main`, con revisión. En GitLab = `MR`. |
| `tag` | Etiqueta fija sobre un commit para marcar una versión (`v0.1.0`). |
| `release` | Versión publicada en GitHub a partir de un tag, con sus notas. |

---

## 🔍 Revisión de código y lógica (cómo te vamos a evaluar)

Cada PR pasa por **dos revisiones**, no una:

1. **Revisión de código** — ¿está en el sitio correcto? ¿validación en el serializer?
   ¿permisos en Permission Class? ¿vista delgada? ¿inglés, type hints, docstrings?
   ¿historial Git limpio?
2. **Revisión de lógica** — ¿la regla de negocio es *correcta*, no solo que corre?
   ¿cubre los casos límite? ¿el 403/404 salta cuando debe? ¿el test prueba de verdad
   lo que dice que prueba, o pasa por casualidad?

> Un PR puede "funcionar" y **no** pasar la revisión. Si la lógica está en el lugar
> equivocado o el test no prueba nada real, se rebota con feedback para que lo
> corrijas tú. Así se trabaja aquí.

### 🎤 Defiende tu Git (revisión oral)

En la revisión, el mentor te va a pedir que **expliques con tus palabras** lo que
hiciste. No vale "lo hice porque lo decía el enunciado". Prepárate para responder:

- ¿Qué hace **rebase** y en qué se diferencia de **merge**? ¿Por qué usaste uno u otro?
- ¿Para qué hiciste **squash** y qué pasó con tus commits "wip"?
- Diferencia entre **fetch** y **pull**. ¿Cuándo usas cada uno?
- ¿Qué es un **tag** y por qué no basta con el nombre de la rama para marcar una release?
- ¿Por qué la validación va en el **serializer** y no en la vista?
- ¿Por qué los permisos van en una **Permission Class** y no con un `if` en la vista?

> Saber ejecutar el comando es la mitad. La otra mitad es **entender por qué**. Si
> puedes explicárselo a otra persona, lo sabes de verdad. Eso es lo que evaluamos.

### 🤖 Sobre usar IA (ChatGPT, Copilot, etc.)

**Puedes usar IA. No está prohibido y no es hacer trampa.** En Invelon usamos estas
herramientas todos los días. Pero el objetivo de este reto NO es entregar código:
es que **tú domines lo que entregas.**

La regla es simple:

> **No subas ni una línea que no sepas explicar.**

Si la IA te da una solución, tu trabajo no termina ahí — empieza ahí:
- Entiéndela línea por línea. ¿Por qué esto y no otra cosa?
- ¿Dónde la colocarías tú? (¿serializer? ¿permiso? ¿vista?) La IA no conoce *nuestras*
  reglas de arquitectura; tú sí tienes que conocerlas.
- Reescríbela con tus palabras / a tu manera. Si no puedes, es que no la entiendes aún.

En la revisión oral se nota al instante quién entendió y quién copió y pegó. Un
código perfecto que no sabes defender vale **menos** que un código con un fallo que
sabes explicar y arreglar. Aquí preferimos lo segundo.

**Úsala como un tutor que te explica, no como una máquina que te hace el trabajo.**

---

## 🗺️ El recorrido de la semana

| Día | Qué consigues |
|---|---|
| **Lun** | Entorno montado, server arrancando. Primer `clone` + rama. |
| **Mar** | Modelos `Project` + `Asset`, el admin, la Regla 1, y tu primer **PR**. |
| **Mié** | La API viva: ViewSets + Reglas 2 y 3. Probada en Postman. |
| **Jue** | Tests con pytest + pruebas el repo de tu compañer@ (rebase/squash en práctica). |
| **Vie** | Cierras el ciclo: **tag `v0.1.0` + release en GitHub** + Release Notes. Revisión oral. 🏅 |

## 🧭 Pistas (no soluciones)

- Antes de escribir una línea, abre la **pre-flight checklist** del doc 4 ("La Pausa").
  ¿DRF ya tiene algo nativo para esto? Casi siempre sí.
- Para la Regla 1: busca el método `validate()` de los serializers de DRF.
- Para las Reglas 2 y 3: busca "DRF custom permission classes" y `get_queryset`.
- El `403` de la Regla 3 lo pruebas creando 2 usuarios en el admin: logueas con uno
  e intentas tocar el proyecto del otro desde Postman.

## 🆘 Si te bloqueas

Regla de la casa: **bloqueado más de 30 minutos → paras y lo apuntas.** No pierdas
media mañana atascado en silencio. Llega a las revisiones con dudas escritas, no
con la pantalla en blanco.

**Nunca** commitees tu archivo `.env` ni la carpeta `venv/`. (Ya hay un `.gitignore`
en el repo base que te protege — míralo el primer día y entiende por qué.)

¡A por ello! 🔥
