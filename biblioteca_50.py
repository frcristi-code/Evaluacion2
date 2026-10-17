"""Genera 50 libros, los incorpora a DEVASC y verifica su presencia."""
import argparse
import json
import os
import random
import time
from getpass import getpass
from pathlib import Path

import requests


def guardar(nombre, datos):
    Path(nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def generar(inicio):
    nombres = ["Ana", "Luis", "Camila", "Diego", "Elena", "Tomás", "Paula", "Javier"]
    apellidos = ["Soto", "Rojas", "Pérez", "Díaz", "Silva", "Muñoz", "Vera", "Torres"]
    temas = ["Redes", "Python", "Colaboración", "Seguridad", "Sistemas", "Automatización", "APIs"]
    enfoques = ["prácticos", "modernos", "distribuidos", "avanzados", "esenciales", "aplicados"]
    usados = set()
    libros = []
    for indice in range(50):
        base = "978" + "".join(str(random.randrange(10)) for _ in range(9))
        while base in usados:
            base = "978" + "".join(str(random.randrange(10)) for _ in range(9))
        usados.add(base)
        control = (-sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))) % 10
        libros.append({
            "id": inicio + indice,
            "title": f"{random.choice(temas)} {random.choice(enfoques)} {random.randrange(1000, 10000)}",
            "author": f"{random.choice(nombres)} {random.choice(apellidos)}",
            "isbn": base + str(control),
        })
    return libros


def listar(sesion, base):
    # El simulador puede paginar. Recorrer hasta una página vacía y detectar repeticiones.
    resultado = {}
    anterior = None
    for pagina in range(0, 1000):
        for intento in range(4):
            respuesta = sesion.get(base + "/books", params={"includeISBN": "true", "page": pagina}, timeout=30)
            if respuesta.status_code != 429:
                break
            time.sleep(2 * (intento + 1))
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not isinstance(datos, list):
            raise ValueError("El catálogo no es una lista JSON; revisa la documentación de tu VM.")
        if not datos:
            return list(resultado.values())
        firma = tuple(str(libro["id"]) for libro in datos)
        if firma == anterior:
            raise ValueError("La API repite la página. Revisa la paginación antes de afirmar que el listado está completo.")
        anterior = firma
        for libro in datos:
            resultado[str(libro["id"])] = libro
    raise ValueError("Se alcanzó el límite de páginas; no se puede asegurar un listado completo.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://library.demo.local/api/v1")
    parser.add_argument("--crear", action="store_true", help="Enviar los 50 libros a la API")
    parser.add_argument("--inicio", type=int, default=8)
    args = parser.parse_args()
    if args.inicio < 8:
        parser.error("Usa un ID inicial de 8 o superior para no ocupar los IDs de la evaluación.")
    if not args.crear:
        guardar("libros_generados.json", generar(args.inicio))
        print("Se generaron 50 libros en libros_generados.json. No se enviaron a la API.")
        return
    clave = os.environ.get("BIBLIOTECA_API_KEY") or getpass("Token de biblioteca (no se mostrará): ")
    with requests.Session() as sesion:
        sesion.headers.update({"X-API-KEY": clave, "Accept": "application/json"})
        base = args.base_url.rstrip("/")
        existentes = listar(sesion, base)
        ocupados = {int(libro["id"]) for libro in existentes}
        if ocupados.intersection(range(args.inicio, args.inicio + 50)):
            raise ValueError("Hay IDs ocupados. Elige otro --inicio; no se sobrescribió ningún libro.")
        libros = generar(args.inicio)
        guardar("libros_generados.json", libros)
        for libro in libros:
            respuesta = sesion.post(base + "/books", json=libro, timeout=30)
            print(f"Libro {libro['id']}: HTTP {respuesta.status_code}")
            respuesta.raise_for_status()
            time.sleep(0.25)
        catalogo = listar(sesion, base)
        por_id = {int(libro["id"]): libro for libro in catalogo}
        for libro in libros:
            recibido = por_id.get(libro["id"], {})
            if any(recibido.get(campo) != libro[campo] for campo in ("title", "author", "isbn")):
                raise ValueError(f"No se pudo verificar el libro {libro['id']}.")
        guardar("catalogo_final.json", catalogo)
        print(json.dumps(catalogo, ensure_ascii=False, indent=2))
        print(f"50 libros verificados. Catálogo completo guardado: {len(catalogo)} libros.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException:
        raise SystemExit("Error HTTP o de conexión. Revisa el último estado y el servicio. Puede haber creaciones parciales; consulta el catálogo antes de repetir.")
    except ValueError as error:
        raise SystemExit(str(error))

