# Guía para completar la evaluación 2

## Orden de trabajo

1. Conseguir e iniciar la VM DEVASC institucional.
2. Abrir `http://library.demo.local` y consultar su documentación de API.
3. Importar la colección Postman y configurar nombre, apellido y RUT localmente.
4. Obtener token, crear los tres libros y guardar las capturas de cada creación.
5. Consultar un libro y actualizar el título del ID 5. Consultarlo nuevamente.
6. Listar por autor incluyendo ISBN y capturar la respuesta.
7. Ejecutar el script de 50 libros y revisar el catálogo completo.
8. Obtener la clave personal de GraphHopper y ejecutar el programa de rutas.
9. Probar una ruta real, la salida con `s` y la salida con `salir`.
10. Crear y publicar el repositorio público `Evaluacion2`.
11. Completar el informe Word o PDF con evidencias, introducción y conclusión.

## Capturas necesarias

| Evidencia | Qué debe mostrar |
| --- | --- |
| 01 Creación del libro 5 | Postman, POST, URL, cuerpo con título exacto, autor e ISBN y estado HTTP satisfactorio |
| 02 Creación del libro 6 | Los mismos elementos para el ID 6 |
| 03 Creación del libro 7 | Los mismos elementos para el ID 7 |
| 04 Consulta | GET de un libro creado, respuesta con sus datos y HTTP satisfactorio |
| 05 Actualización | Solicitud de actualización del ID 5, título Guía de Estudio para la Certificación CCNA Security V2.0 y HTTP satisfactorio |
| 06 Verificación de actualización | GET del ID 5 con el nuevo título persistido |
| 07 Orden e ISBN | GET con includeISBN=true y sortBy=author; respuesta ordenada con los ISBN visibles |
| 08 Carga de 50 libros | Terminal con ejecución, estados HTTP y verificación de los 50 registros |
| 09 Listado completo | Archivo catalogo_final.json con todos los registros y total; si hacen falta varias capturas, que sean legibles |
| 10 Código de rutas | VS Code mostrando locale=es, formato de dos decimales y condición de salida |
| 11 Ruta real | Terminal con origen, destino, HTTP 200, distancia, tiempo e instrucciones en español |
| 12 Salida s | Ejecución que termina al ingresar s |
| 13 Salida salir | Otra ejecución que termina al ingresar salir |
| 14 Git | Commit, subida correcta y git status |
| 15 GitHub | Repositorio público Evaluacion2 con código y README; URL visible |

No muestres claves de API en las capturas. En Postman puedes encuadrar el cuerpo y estado de respuesta sin la sección de autorización. Conserva los datos personales exigidos por la pauta en el informe destinado al docente, pero no publiques el RUT en GitHub.

## Estructura sugerida del informe

### Portada

Evaluación parcial 2 de Telepresencia y Entornos Innovadores de Colaboración Humana. Nombre del estudiante, sección, docente y fecha real de ejecución.

### Introducción

Explica el escenario de la Biblioteca Nacional y los objetivos: administrar su catálogo mediante API REST, consultar rutas y mantener el código en GitHub.

### Desarrollo de la biblioteca

Describe el entorno y la autenticación sin incluir el token. Para cada operación incorpora método, endpoint, datos enviados, estado HTTP observado y explicación del resultado real. Incluye las evidencias 01 a 09. Para la carga aleatoria explica el bucle, las listas utilizadas, la generación del ISBN y la comprobación final.

### Desarrollo de geolocalización

Explica cómo las entradas y mensajes se presentan en español; cómo `locale=es` solicita instrucciones traducidas; cómo se convierten metros y milisegundos; y cómo `:.2f` limita la precisión mostrada. Explica la salida con ambas palabras. Incorpora las evidencias 10 a 13.

### Control de versiones

Describe el repositorio local y remoto, el commit y la publicación del script y README. Incorpora las evidencias 14 y 15 y pega el enlace real al repositorio.

### Conclusión

Resume únicamente los resultados comprobados durante tu ejecución. Si hubo un error, indica cómo lo resolviste o qué quedó pendiente. No afirmes que una operación funcionó si no tienes su respuesta real.

## Aclaraciones de la pauta

El documento docente menciona tanto trabajo individual como en parejas, y tanto 120 minutos como cuatro horas académicas. Confirma modalidad y plazo con el docente. No cambia los archivos técnicos que puedes preparar desde ahora.
