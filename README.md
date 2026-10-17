# Evaluacion2

Repositorio pÃºblico de esta entrega: https://github.com/frcristi-code/Evaluacion2

Proyecto de Telepresencia y Entornos Innovadores de ColaboraciÃ³n Humana CUY6142. Integra la API REST de la biblioteca de DEVASC y GraphHopper mediante Python. La aplicaciÃ³n de rutas solicita origen y destino, presenta las indicaciones en espaÃ±ol y muestra distancias y tiempos con dos decimales. Permite terminar escribiendo `s` o `salir` en cualquiera de las dos solicitudes de ubicaciÃ³n.

## PreparaciÃ³n en DEVASC

1. Inicia la mÃ¡quina virtual DEVASC proporcionada por tu instituciÃ³n. Si todavÃ­a no la tienes, solicita la imagen y las instrucciones de importaciÃ³n al docente. Esta carpeta no contiene la VM.
2. Copia la carpeta `Evaluacion2` a la VM y Ã¡brela en Visual Studio Code.
3. Desde una terminal ubicada dentro de esa carpeta, ejecuta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecutar el programa de rutas

ObtÃ©n tu propia clave en https://www.graphhopper.com/ y habilita el acceso a las APIs de geocodificaciÃ³n y rutas. Ejecuta:

```bash
python graphhopper_es.py
```

El programa pide la clave sin mostrarla. TambiÃ©n admite la variable de entorno `GRAPHHOPPER_API_KEY` o el archivo local `~/.config/Evaluacion2/graphhopper.key`. No la escribas dentro del cÃ³digo. El perfil predeterminado es `car`; si tu cuenta requiere otro perfil, configura `GRAPHHOPPER_PROFILE` con un identificador habilitado.

Escribe direcciones que incluyan ciudad y paÃ­s. Revisa las ubicaciones encontradas antes de interpretar la ruta. Ejemplo de destino: Biblioteca Nacional, Santiago, Chile. La geocodificaciÃ³n usa la primera coincidencia, que puede ser ambigua.

La narrativa se obtiene solicitando `locale=es` a GraphHopper; los nombres propios de calles o lugares pueden conservar su idioma original. El tiempo recibido en milisegundos se convierte a minutos y la distancia en metros a kilÃ³metros. Las salidas usan `:.2f`.

## Biblioteca con Postman

Importa `Evaluacion2.postman_collection.json`. En las variables de la colecciÃ³n configura `autor` con tu nombre y apellido, e `isbn` con tu RUT sin puntos ni guion. Son valores personales que deben configurarse localmente antes de enviar las solicitudes.

Comprueba desde la VM que abre `http://library.demo.local`. En su documentaciÃ³n de API confirma los nombres de parÃ¡metros, la paginaciÃ³n y el mÃ©todo de actualizaciÃ³n de tu versiÃ³n.

Ejecuta las solicitudes de la colecciÃ³n una por una, en orden. La primera usa Basic Auth con las credenciales de laboratorio indicadas en el recurso 2.3.2: usuario `cisco` y contraseÃ±a `Cisco123!`. Introduce esos datos en la pestaÃ±a Authorization de la solicitud. El token devuelto se guarda en la variable local `token` de la colecciÃ³n.

Las siguientes solicitudes usan el encabezado `X-API-KEY`. La colecciÃ³n prepara las altas de los IDs 5, 6 y 7, consulta del ID 5, actualizaciÃ³n del tÃ­tulo y listado por autor con ISBN. La documentaciÃ³n Swagger de DEVASC fue consultada y confirma `PUT /books/{id}` para actualizar libros. La colecciÃ³n usa `PUT /books/5`.

Si alguno de los IDs estÃ¡ ocupado, consulta al docente antes de modificar registros existentes. No ejecutes toda la colecciÃ³n automÃ¡ticamente: revisa cada respuesta y captura la evidencia correspondiente. Las pruebas de Postman verifican HTTP satisfactorio y contenido, pero debes revisar tambiÃ©n el cuerpo recibido.

## Agregar 50 libros con Python

Primero puedes generar un archivo local sin modificar el servidor:

```bash
python biblioteca_50.py
```

DespuÃ©s de completar las operaciones de Postman, ejecuta:

```bash
python biblioteca_50.py --crear
```

Pega el token de biblioteca cuando se solicite. El script consulta el catÃ¡logo, comprueba que los IDs 8 a 57 estÃ©n libres, genera tÃ­tulos y autores al azar, y crea ISBN de 13 dÃ­gitos con dÃ­gito de control. EnvÃ­a 50 POST, consulta las pÃ¡ginas del catÃ¡logo y verifica los datos creados. Guarda `libros_generados.json` y `catalogo_final.json` y muestra el listado completo en terminal. Estos archivos se excluyen de Git.

Si hay IDs ocupados, elige un bloque libre con `--inicio 100`, por ejemplo. No hay transacciÃ³n: si falla un POST, algunos libros pueden haberse creado. Revisa el catÃ¡logo antes de repetir. En esta VM las pÃ¡ginas comienzan en 0, comprobado con consultas reales. El script recorre desde la pÃ¡gina 0 hasta recibir una lista vacÃ­a.

## Revisar los libros sin volver a crearlos

Se integrÃ³ el aporte de Rodrigo Velasquez como un programa separado de consulta:

```bash
python listar_todos_libros.py --total-esperado 57
```

ReÃºne todas las pÃ¡ginas con la funciÃ³n de `biblioteca_50.py`, ordena el catÃ¡logo
completo por autor, muestra ISBN y comprueba los IDs 8 a 57. No crea ni modifica
libros. `--total-esperado 57` comprueba el escenario de la evaluaciÃ³n; se puede
omitir para aceptar otro total. `--inicio` y `--cantidad` permiten revisar otro
bloque. La revisiÃ³n de IDs no sustituye la comparaciÃ³n de tÃ­tulo, autor e ISBN
que realiza el creador al terminar una carga. El creador original de Rodrigo
no se ejecuta sobre este catÃ¡logo porque esos IDs ya estÃ¡n ocupados.

## Git y GitHub

Ejecuta dentro de `Evaluacion2` en DEVASC:

```bash
git init
git add README.md graphhopper_es.py biblioteca_50.py requirements.txt .gitignore Evaluacion2.postman_collection.json
git commit -m "Agrega rutas en espaÃ±ol y gestiÃ³n de biblioteca"
git branch -M main
```

Antes de aÃ±adir la colecciÃ³n, revisa que las variables `token`, `autor` e `isbn` estÃ©n vacÃ­as o con marcadores. No publiques una exportaciÃ³n con tus datos. Las capturas tambiÃ©n deben ocultar los tokens.

Crea en GitHub un repositorio pÃºblico llamado exactamente `Evaluacion2`, sin README inicial. Copia su URL y ejecuta, reemplazando `TU_USUARIO` por tu cuenta:

```bash
git remote add origin https://github.com/TU_USUARIO/Evaluacion2.git
git push -u origin main
git status
```

Comprueba en el navegador que el repositorio sea pÃºblico y que aparezcan el cÃ³digo y el README. AÃ±ade la URL real al informe. La pauta usa nombres inconsistentes; estas instrucciones siguen el nombre explÃ­cito `Evaluacion2` de los requerimientos.

## Evidencias y entrega

Sigue `GUIA_DE_EVIDENCIAS.md`. El informe final debe incluir introducciÃ³n, desarrollo, conclusiÃ³n, capturas autÃ©nticas y URL real de GitHub. No reemplaces evidencia de Postman por salidas de Python para las operaciones que se solicitan expresamente en Postman.

## Referencias

- Pauta de evaluaciÃ³n parcial 2 y recursos 2.3.2 y 2.4.2 proporcionados por el curso.
- DocumentaciÃ³n oficial de GraphHopper: https://docs.graphhopper.com/

## ValidaciÃ³n realizada

El 17 de octubre de 2026 se ejecutÃ³ el proyecto en DEVASC. Se crearon los tres libros con Postman, se actualizÃ³ el ID 5 y se consultÃ³ el catÃ¡logo por autor incluyendo ISBN, con HTTP 200. Se aÃ±adieron y verificaron 50 libros con Python; el catÃ¡logo resultante contiene 57 registros. El script espera y reintenta las consultas cuando recibe HTTP 429 por lÃ­mite de velocidad.

La prueba real de GraphHopper entre Plaza de Armas y Biblioteca Nacional de Chile, en Santiago, devolviÃ³ HTTP 200: 3,17 km, 6,22 minutos y 15 indicaciones en espaÃ±ol para el perfil car. TambiÃ©n se verificaron las salidas con s y salir. Los resultados corresponden a esa consulta y pueden variar cuando se vuelva a ejecutar.

Las evidencias se conservan localmente fuera del contenido publicado, porque incluyen datos personales exigidos por la evaluaciÃ³n. La clave de GraphHopper se mantiene fuera del repositorio.


