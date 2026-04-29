# Pagina de privacidad - Recetario MX (Skill Alexa)

Contenido: politica de privacidad para la skill de Alexa Recetario MX.

## Opcion 1: GitHub Pages

1. Crea un repositorio en GitHub (ej. `recetario-mx-privacy`).
2. Sube solo la carpeta `privacy/` con su contenido (o solo `index.html` en la raiz del repo).
3. En el repo: Settings > Pages > Source: Deploy from a branch > Branch: main, folder: / (root) o la carpeta donde este index.html.
4. La URL sera: `https://TU_USUARIO.github.io/recetario-mx-privacy/` (o la ruta donde este index.html).

Usa esa URL en **Privacy Policy URL** de la skill en Alexa Developer Console.

## Opcion 2: Desde recetario-mx (Next.js)

Si despliegas la app Next.js (recetario-mx), los archivos en `public/privacy/` se sirven en la ruta `/privacy/`. Mueve el contenido de esta carpeta a `recetario-mx/public/privacy/` (index.html dentro de public/privacy/). La URL sera: `https://tu-dominio.com/privacy/`.

## Opcion 3: Cualquier hosting

Sube `index.html` a cualquier servidor o CDN y usa la URL publica en Privacy Policy URL.
