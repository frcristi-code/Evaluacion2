"""Calcula rutas y muestra indicaciones en español con GraphHopper."""
import os
import sys
from getpass import getpass
from pathlib import Path

import requests

BASE = "https://graphhopper.com/api/1"


def pedir(texto):
    while True:
        valor = input(texto).strip()
        if valor.casefold() in {"s", "salir"}:
            raise EOFError
        if valor:
            return valor
        print("Escribe una ubicación o ingresa s para salir.")


def consultar(sesion, recurso, parametros):
    try:
        respuesta = sesion.get(BASE + recurso, params=parametros, timeout=30)
    except requests.RequestException:
        raise ValueError("No se pudo conectar con GraphHopper. Revisa tu conexión.") from None
    print(f"Estado HTTP de {'geocodificación' if recurso == '/geocode' else 'rutas'}: {respuesta.status_code}")
    if not respuesta.ok:
        mensajes = {
            400: "Revisa las ubicaciones y el perfil de transporte configurado.",
            401: "La clave de GraphHopper no es válida.",
            403: "La cuenta no tiene permiso para esta operación.",
            429: "Se alcanzó el límite de solicitudes. Intenta más tarde.",
        }
        raise ValueError(mensajes.get(respuesta.status_code, "GraphHopper no pudo completar la solicitud."))
    try:
        return respuesta.json()
    except ValueError:
        raise ValueError("El servidor no devolvió una respuesta JSON válida.") from None


def geocodificar(sesion, lugar, clave):
    datos = consultar(sesion, "/geocode", {"q": lugar, "limit": 1, "locale": "es", "key": clave})
    lugares = datos.get("hits", [])
    if not lugares:
        raise ValueError("No se encontró la ubicación. Agrega ciudad y país a la búsqueda.")
    lugar = lugares[0]
    punto = lugar["point"]
    nombre = ", ".join(str(lugar[k]) for k in ("name", "city", "country") if lugar.get(k))
    print("Ubicación encontrada: " + nombre)
    return f"{punto['lat']},{punto['lng']}", nombre


def mostrar_ruta(ruta):
    print(f"Distancia total: {ruta['distance'] / 1000:.2f} km")
    print(f"Duración estimada: {ruta['time'] / 60000:.2f} minutos")
    instrucciones = ruta.get("instructions", [])
    if not instrucciones:
        raise ValueError("La respuesta no incluyó instrucciones del viaje.")
    print("Indicaciones del viaje")
    for numero, paso in enumerate(instrucciones, 1):
        print(f"{numero}. {paso['text']} ({paso['distance'] / 1000:.2f} km; {paso['time'] / 60000:.2f} minutos)")


def main():
    print("Planificador de rutas a la Biblioteca Nacional")
    print("Ingresa s o salir en cualquier solicitud de ubicación para terminar.")
    clave = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    archivo_clave = Path.home() / ".config" / "Evaluacion2" / "graphhopper.key"
    if not clave and archivo_clave.is_file():
        clave = archivo_clave.read_text(encoding="utf-8").strip()
    if not clave:
        clave = getpass("Clave de GraphHopper (no se mostrará): ").strip()
    if not clave:
        print("Necesitas una clave de GraphHopper para consultar rutas.")
        return 1
    perfil = os.environ.get("GRAPHHOPPER_PROFILE", "car")
    with requests.Session() as sesion:
        while True:
            try:
                origen = pedir("Origen (incluye ciudad y país): ")
                destino = pedir("Destino (por ejemplo Biblioteca Nacional, Santiago, Chile): ")
                op, on = geocodificar(sesion, origen, clave)
                dp, dn = geocodificar(sesion, destino, clave)
                datos = consultar(sesion, "/route", {
                    "point": [op, dp], "profile": perfil, "locale": "es",
                    "instructions": "true", "key": clave,
                })
                if not datos.get("paths"):
                    raise ValueError("No se encontró una ruta entre las ubicaciones.")
                print(f"Ruta desde {on} hasta {dn}")
                mostrar_ruta(datos["paths"][0])
            except (EOFError, KeyboardInterrupt):
                print("\nPrograma finalizado.")
                return 0
            except ValueError as error:
                print(str(error))
            except (KeyError, TypeError):
                # No imprimir URLs de error: pueden contener la clave de API.
                print("No se pudo completar la ruta. Revisa las ubicaciones, la clave, el perfil y la respuesta HTTP.")


if __name__ == "__main__":
    sys.exit(main())
