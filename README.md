# Evaluacion2

Proyecto de Telepresencia y Entornos Innovadores de Colaboración Humana CUY6142. Integra la API REST de la biblioteca de DEVASC y GraphHopper mediante Python. La aplicación de rutas solicita origen y destino, presenta las indicaciones en español y muestra distancias y tiempos con dos decimales. Permite terminar escribiendo `s` o `salir` en cualquiera de las dos solicitudes de ubicación.

## Preparación en DEVASC

1. Inicia la máquina virtual DEVASC proporcionada por tu institución. Si todavía no la tienes, solicita la imagen y las instrucciones de importación al docente. Esta carpeta no contiene la VM.
2. Copia la carpeta `Evaluacion2` a la VM y ábrela en Visual Studio Code.
3. Desde una terminal ubicada dentro de esa carpeta, ejecuta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecutar el programa de rutas

Obtén tu propia clave en https://www.graphhopper.com/ y habilita el acceso a las APIs de geocodificación y rutas. Ejecuta:

```bash
python graphhopper_es.py
```

El programa pide la clave sin mostrarla. También admite la variable de entorno `GRAPHHOPPER_API_KEY` o el archivo local `~/.config/Evaluacion2/graphhopper.key`. No la escribas dentro del código. El perfil predeterminado es `car`; si tu cuenta requiere otro perfil, configura `GRAPHHOPPER_PROFILE` con un identificador habilitado.

Escribe direcciones que incluyan ciudad y país. Revisa las ubicaciones encontradas antes de interpretar la ruta. Ejemplo de destino: Biblioteca Nacional, Santiago, Chile. La geocodificación usa la primera coincidencia, que puede ser ambigua.

La narrativa se obtiene solicitando `locale=es` a GraphHopper; los nombres propios de calles o lugares pueden conservar su idioma original. El tiempo recibido en milisegundos se convierte a minutos y la distancia en metros a kilómetros. Las salidas usan `:.2f`.

## Biblioteca con Postman

Importa `Evaluacion2.postman_collection.json`. En las variables de la colección configura `autor` con tu nombre y apellido, e `isbn` con tu RUT sin puntos ni guion. Son valores personales que deben configurarse localmente antes de enviar las solicitudes.

Comprueba desde la VM que abre `http://library.demo.local`. En su documentación de API confirma los nombres de parámetros, la paginación y el método de actualización de tu versión.

Ejecuta las solicitudes de la colección una por una, en orden. La primera usa Basic Auth con las credenciales de laboratorio indicadas en el recurso 2.3.2: usuario `cisco` y contraseña `Cisco123!`. Introduce esos datos en la pestaña Authorization de la solicitud. El token devuelto se guarda en la variable local `token` de la colección.

Las siguientes solicitudes usan el encabezado `X-API-KEY`. La colección prepara las altas de los IDs 5, 6 y 7, consulta del ID 5, actualización del título y listado por autor con ISBN. La documentación Swagger de DEVASC fue consultada y confirma `PUT /books/{id}` para actualizar libros. La colección usa `PUT /books/5`.

Si alguno de los IDs está ocupado, consulta al docente antes de modificar registros existentes. No ejecutes toda la colección automáticamente: revisa cada respuesta y captura la evidencia correspondiente. Las pruebas de Postman verifican HTTP satisfactorio y contenido, pero debes revisar también el cuerpo recibido.

## Agregar 50 libros con Python

Primero puedes generar un archivo local sin modificar el servidor:

```bash
python biblioteca_50.py
```

Después de completar las operaciones de Postman, ejecuta:

```bash
python biblioteca_50.py --crear
```

Pega el token de biblioteca cuando se solicite. El script consulta el catálogo, comprueba que los IDs 8 a 57 estén libres, genera títulos y autores al azar, y crea ISBN de 13 dígitos con dígito de control. Envía 50 POST, consulta las páginas del catálogo y verifica los datos creados. Guarda `libros_generados.json` y `catalogo_final.json` y muestra el listado completo en terminal. Estos archivos se excluyen de Git.

Si hay IDs ocupados, elige un bloque libre con `--inicio 100`, por ejemplo. No hay transacción: si falla un POST, algunos libros pueden haberse creado. Revisa el catálogo antes de repetir. En esta VM las páginas comienzan en 0, comprobado con consultas reales. El script recorre desde la página 0 hasta recibir una lista vacía.

## Git y GitHub

Ejecuta dentro de `Evaluacion2` en DEVASC:

```bash
git init
git add README.md graphhopper_es.py biblioteca_50.py requirements.txt .gitignore Evaluacion2.postman_collection.json
git commit -m "Agrega rutas en español y gestión de biblioteca"
git branch -M main
```

Antes de añadir la colección, revisa que las variables `token`, `autor` e `isbn` estén vacías o con marcadores. No publiques una exportación con tus datos. Las capturas también deben ocultar los tokens.

Crea en GitHub un repositorio público llamado exactamente `Evaluacion2`, sin README inicial. Copia su URL y ejecuta, reemplazando `TU_USUARIO` por tu cuenta:

```bash
git remote add origin https://github.com/TU_USUARIO/Evaluacion2.git
git push -u origin main
git status
```

Comprueba en el navegador que el repositorio sea público y que aparezcan el código y el README. Añade la URL real al informe. La pauta usa nombres inconsistentes; estas instrucciones siguen el nombre explícito `Evaluacion2` de los requerimientos.

## Evidencias y entrega

Sigue `GUIA_DE_EVIDENCIAS.md`. El informe final debe incluir introducción, desarrollo, conclusión, capturas auténticas y URL real de GitHub. No reemplaces evidencia de Postman por salidas de Python para las operaciones que se solicitan expresamente en Postman.

## Referencias

- Pauta de evaluación parcial 2 y recursos 2.3.2 y 2.4.2 proporcionados por el curso.
- Documentación oficial de GraphHopper: https://docs.graphhopper.com/

## Validación realizada

El 17 de octubre de 2026 se ejecutó el proyecto en DEVASC. Se crearon los tres libros con Postman, se actualizó el ID 5 y se consultó el catálogo por autor incluyendo ISBN, con HTTP 200. Se añadieron y verificaron 50 libros con Python; el catálogo resultante contiene 57 registros. El script espera y reintenta las consultas cuando recibe HTTP 429 por límite de velocidad.

La prueba real de GraphHopper entre Plaza de Armas y Biblioteca Nacional de Chile, en Santiago, devolvió HTTP 200: 3,17 km, 6,22 minutos y 15 indicaciones en español para el perfil car. También se verificaron las salidas con s y salir. Los resultados corresponden a esa consulta y pueden variar cuando se vuelva a ejecutar.

Las evidencias se conservan localmente fuera del contenido publicado, porque incluyen datos personales exigidos por la evaluación. La clave de GraphHopper se mantiene fuera del repositorio.


