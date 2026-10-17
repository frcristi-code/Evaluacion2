"""Calcula rutas y muestra indicaciones en español con GraphHopper."""
# Permite leer la configuración guardada en variables del sistema.
import os
# Permite devolver el resultado del programa al terminar.
import sys
# Sirve para pedir una clave sin mostrarla en pantalla.
from getpass import getpass
# Ayuda a trabajar con las rutas de los archivos.
from pathlib import Path

# Esta biblioteca permite hacer las consultas HTTP a la API.
import requests

# Dirección de la API que se usará para buscar lugares y rutas.
BASE = "https://graphhopper.com/api/1"


# Pide una ubicación y revisa si la persona quiere salir.
def pedir(texto):
    # Repite este bloque hasta recibir un dato válido o terminar el programa.
    while True:
        # Lee lo escrito y quita los espacios que sobren al principio y al final.
        valor = input(texto).strip()
        # Acepta s o salir, incluso si se escriben con mayúsculas.
        if valor.casefold() in {"s", "salir"}:
            # Avisa al programa principal que debe finalizar.
            raise EOFError
        # Comprueba que se haya escrito algo.
        if valor:
            # Entrega el texto válido a la parte que lo solicitó.
            return valor
        print("Escribe una ubicación o ingresa s para salir.")


# Hace una consulta a GraphHopper y revisa la respuesta recibida.
def consultar(sesion, recurso, parametros):
    try:
        # Envía los parámetros y espera como máximo 30 segundos.
        respuesta = sesion.get(BASE + recurso, params=parametros, timeout=30)
    # Atiende los problemas de conexión o de la solicitud HTTP.
    except requests.RequestException:
        raise ValueError("No se pudo conectar con GraphHopper. Revisa tu conexión.") from None
    # Muestra el estado HTTP para comprobar el resultado de la consulta.
    print(f"Estado HTTP de {'geocodificación' if recurso == '/geocode' else 'rutas'}: {respuesta.status_code}")
    # Si el servidor informa un error, prepara una explicación en español.
    if not respuesta.ok:
        # Relaciona los errores más comunes con un mensaje que se entienda.
        mensajes = {
            400: "Revisa las ubicaciones y el perfil de transporte configurado.",
            401: "La clave de GraphHopper no es válida.",
            403: "La cuenta no tiene permiso para esta operación.",
            429: "Se alcanzó el límite de solicitudes. Intenta más tarde.",
        }
        raise ValueError(mensajes.get(respuesta.status_code, "GraphHopper no pudo completar la solicitud."))
    try:
        # Convierte la respuesta JSON en datos que Python pueda usar.
        return respuesta.json()
    # Atiende una respuesta que no se pudo interpretar como JSON.
    except ValueError:
        raise ValueError("El servidor no devolvió una respuesta JSON válida.") from None


# Busca las coordenadas de un lugar a partir de su nombre.
def geocodificar(sesion, lugar, clave):
    # Busca una coincidencia y solicita los resultados en español.
    datos = consultar(sesion, "/geocode", {"q": lugar, "limit": 1, "locale": "es", "key": clave})
    # Obtiene la lista de coincidencias; si falta, usa una lista vacía.
    lugares = datos.get("hits", [])
    # Comprueba si la búsqueda no encontró ningún lugar.
    if not lugares:
        raise ValueError("No se encontró la ubicación. Agrega ciudad y país a la búsqueda.")
    # Usa la primera coincidencia devuelta por el servicio.
    lugar = lugares[0]
    # Separa la latitud y la longitud del lugar encontrado.
    punto = lugar["point"]
    # Arma un nombre con el lugar, la ciudad y el país disponibles.
    nombre = ", ".join(str(lugar[k]) for k in ("name", "city", "country") if lugar.get(k))
    print("Ubicación encontrada: " + nombre)
    # Devuelve las coordenadas y el nombre para calcular la ruta.
    return f"{punto['lat']},{punto['lng']}", nombre


# Muestra la distancia, el tiempo y los pasos del recorrido.
def mostrar_ruta(ruta):
    # Convierte metros a kilómetros y muestra dos decimales.
    print(f"Distancia total: {ruta['distance'] / 1000:.2f} km")
    # Convierte milisegundos a minutos y muestra dos decimales.
    print(f"Duración estimada: {ruta['time'] / 60000:.2f} minutos")
    # Recupera los pasos del viaje que llegaron desde GraphHopper.
    instrucciones = ruta.get("instructions", [])
    # Comprueba que la respuesta incluya las indicaciones solicitadas.
    if not instrucciones:
        raise ValueError("La respuesta no incluyó instrucciones del viaje.")
    print("Indicaciones del viaje")
    # Recorre las indicaciones y las numera desde el uno.
    for numero, paso in enumerate(instrucciones, 1):
        # Muestra cada paso con su distancia y su tiempo usando dos decimales.
        print(f"{numero}. {paso['text']} ({paso['distance'] / 1000:.2f} km; {paso['time'] / 60000:.2f} minutos)")


# Reúne los pasos principales del programa.
def main():
    print("Planificador de rutas a la Biblioteca Nacional")
    print("Ingresa s o salir en cualquier solicitud de ubicación para terminar.")
    # Primero busca la clave en una variable del sistema.
    clave = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    # Define dónde se guarda la clave local, fuera del repositorio.
    archivo_clave = Path.home() / ".config" / "Evaluacion2" / "graphhopper.key"
    # Si no hay una clave en el sistema, revisa el archivo local.
    if not clave and archivo_clave.is_file():
        # Lee la clave sin imprimirla en la terminal.
        clave = archivo_clave.read_text(encoding="utf-8").strip()
    if not clave:
        # Si aún falta la clave, la pide de forma oculta.
        clave = getpass("Clave de GraphHopper (no se mostrará): ").strip()
    if not clave:
        print("Necesitas una clave de GraphHopper para consultar rutas.")
        # Termina indicando que falta un dato necesario.
        return 1
    # Usa automóvil por defecto, salvo que se configure otro perfil.
    perfil = os.environ.get("GRAPHHOPPER_PROFILE", "car")
    # Reutiliza la conexión y la cierra al terminar este bloque.
    with requests.Session() as sesion:
        # Repite este bloque hasta recibir un dato válido o terminar el programa.
        while True:
            try:
                # Solicita el punto de partida.
                origen = pedir("Origen (incluye ciudad y país): ")
                # Solicita el lugar al que se quiere llegar.
                destino = pedir("Destino (por ejemplo Biblioteca Nacional, Santiago, Chile): ")
                # Obtiene las coordenadas y el nombre del origen.
                op, on = geocodificar(sesion, origen, clave)
                # Obtiene las coordenadas y el nombre del destino.
                dp, dn = geocodificar(sesion, destino, clave)
                # Pide una ruta entre ambos puntos, con indicaciones en español.
                datos = consultar(sesion, "/route", {
                    "point": [op, dp], "profile": perfil, "locale": "es",
                    "instructions": "true", "key": clave,
                })
                # Comprueba que el servicio haya devuelto una ruta.
                if not datos.get("paths"):
                    raise ValueError("No se encontró una ruta entre las ubicaciones.")
                print(f"Ruta desde {on} hasta {dn}")
                # Presenta la primera ruta encontrada.
                mostrar_ruta(datos["paths"][0])
            # Permite terminar con s, salir, fin de entrada o Ctrl+C.
            except (EOFError, KeyboardInterrupt):
                print("\nPrograma finalizado.")
                # Termina normalmente, sin indicar un error.
                return 0
            # Muestra el problema explicado por el programa.
            except ValueError as error:
                print(str(error))
            # Atiende datos incompletos o con un formato inesperado.
            except (KeyError, TypeError):
                # No imprimir URLs de error: pueden contener la clave de API.
                print("No se pudo completar la ruta. Revisa las ubicaciones, la clave, el perfil y la respuesta HTTP.")


# Ejecuta el programa solamente cuando este archivo se abre directamente.
if __name__ == "__main__":
    # Devuelve al sistema el resultado de la ejecución.
    sys.exit(main())
