"""Genera 50 libros, los incorpora a DEVASC y verifica su presencia."""
# Permite elegir opciones al ejecutar el programa en la terminal.
import argparse
# Permite leer y guardar los datos en formato JSON.
import json
# Permite leer la configuración guardada en variables del sistema.
import os
# Se usa para elegir datos al azar para los libros.
import random
# Permite dejar una pausa entre solicitudes.
import time
# Sirve para pedir una clave sin mostrarla en pantalla.
from getpass import getpass
# Ayuda a trabajar con las rutas de los archivos.
from pathlib import Path

# Esta biblioteca permite hacer las consultas HTTP a la API.
import requests


# Guarda los datos con acentos y un formato fácil de leer.
def guardar(nombre, datos):
    # Convierte los datos a JSON y los escribe en el archivo indicado.
    Path(nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


# Prepara los cincuenta libros a partir del ID inicial elegido.
def generar(inicio):
    # Lista de nombres disponibles para formar autores al azar.
    nombres = ["Ana", "Luis", "Camila", "Diego", "Elena", "Tomás", "Paula", "Javier"]
    # Lista de apellidos para combinar con los nombres.
    apellidos = ["Soto", "Rojas", "Pérez", "Díaz", "Silva", "Muñoz", "Vera", "Torres"]
    # Temas que se pueden usar en los títulos.
    temas = ["Redes", "Python", "Colaboración", "Seguridad", "Sistemas", "Automatización", "APIs"]
    # Palabras que permiten variar los títulos de los libros.
    enfoques = ["prácticos", "modernos", "distribuidos", "avanzados", "esenciales", "aplicados"]
    # Recuerda los números generados para evitar ISBN repetidos.
    usados = set()
    # Crea la lista donde se guardarán los libros.
    libros = []
    # Repite la creación exactamente cincuenta veces.
    for indice in range(50):
        # Forma los primeros doce dígitos del ISBN con números al azar.
        base = "978" + "".join(str(random.randrange(10)) for _ in range(9))
        # Si ese número ya salió, genera otro antes de continuar.
        while base in usados:
            # Forma los primeros doce dígitos del ISBN con números al azar.
            base = "978" + "".join(str(random.randrange(10)) for _ in range(9))
        # Registra el número para no volver a utilizarlo.
        usados.add(base)
        # Calcula el último dígito del ISBN-13 alternando pesos uno y tres.
        control = (-sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))) % 10
        # Agrega un libro con ID, título, autor e ISBN a la lista.
        libros.append({
            "id": inicio + indice,
            "title": f"{random.choice(temas)} {random.choice(enfoques)} {random.randrange(1000, 10000)}",
            "author": f"{random.choice(nombres)} {random.choice(apellidos)}",
            "isbn": base + str(control),
        })
    # Entrega los cincuenta libros preparados.
    return libros


# Consulta todas las páginas del catálogo para obtener los libros.
def listar(sesion, base):
    # El simulador puede paginar. Recorrer hasta una página vacía y detectar repeticiones.
    # Guarda cada libro por su ID para evitar duplicados en el listado.
    resultado = {}
    # Permite comparar la página actual con la anterior.
    anterior = None
    # Empieza en la página cero y establece un límite de seguridad.
    for pagina in range(0, 1000):
        # Permite hasta cuatro consultas por página si hay límite de solicitudes.
        for intento in range(4):
            # Solicita una página de libros incluyendo el ISBN.
            respuesta = sesion.get(base + "/books", params={"includeISBN": "true", "page": pagina}, timeout=30)
            # Continúa si el servidor no está limitando las solicitudes.
            if respuesta.status_code != 429:
                break
            # Espera un poco más antes de volver a intentar la consulta.
            time.sleep(2 * (intento + 1))
        # Detiene la operación si la respuesta HTTP informa un error.
        respuesta.raise_for_status()
        # Convierte la respuesta recibida a una estructura de Python.
        datos = respuesta.json()
        # Revisa que el catálogo tenga el formato de lista esperado.
        if not isinstance(datos, list):
            raise ValueError("El catálogo no es una lista JSON; revisa la documentación de tu VM.")
        # Una página vacía indica que ya se llegó al final del catálogo.
        if not datos:
            # Entrega todos los libros reunidos hasta ese momento.
            return list(resultado.values())
        # Forma una secuencia de IDs para identificar la página recibida.
        firma = tuple(str(libro["id"]) for libro in datos)
        # Detecta si la API está devolviendo la misma página otra vez.
        if firma == anterior:
            raise ValueError("La API repite la página. Revisa la paginación antes de afirmar que el listado está completo.")
        # Recuerda esta página para compararla con la siguiente.
        anterior = firma
        # Recorre los libros de la página actual.
        for libro in datos:
            # Incorpora el libro al catálogo usando su ID como referencia.
            resultado[str(libro["id"])] = libro
    raise ValueError("Se alcanzó el límite de páginas; no se puede asegurar un listado completo.")


# Reúne los pasos principales del programa.
def main():
    # Prepara la lectura de las opciones de la terminal.
    parser = argparse.ArgumentParser(description=__doc__)
    # Permite cambiar la dirección de la API del laboratorio.
    parser.add_argument("--base-url", default="http://library.demo.local/api/v1")
    # Solo envía los libros cuando se indica expresamente --crear.
    parser.add_argument("--crear", action="store_true", help="Enviar los 50 libros a la API")
    # Permite elegir el primer ID; normalmente se usa el ocho.
    parser.add_argument("--inicio", type=int, default=8)
    # Lee las opciones que se escribieron al ejecutar el archivo.
    args = parser.parse_args()
    # Protege los IDs reservados para los libros de la evaluación.
    if args.inicio < 8:
        parser.error("Usa un ID inicial de 8 o superior para no ocupar los IDs de la evaluación.")
    # Sin --crear, solo prepara un archivo local de prueba.
    if not args.crear:
        # Genera los libros y los guarda sin enviarlos a la API.
        guardar("libros_generados.json", generar(args.inicio))
        print("Se generaron 50 libros en libros_generados.json. No se enviaron a la API.")
        return
    # Obtiene el token del sistema o lo solicita sin mostrarlo.
    clave = os.environ.get("BIBLIOTECA_API_KEY") or getpass("Token de biblioteca (no se mostrará): ")
    # Reutiliza la conexión y la cierra al terminar este bloque.
    with requests.Session() as sesion:
        # Incluye el token y el formato esperado en las solicitudes.
        sesion.headers.update({"X-API-KEY": clave, "Accept": "application/json"})
        # Quita la barra final para construir correctamente las direcciones.
        base = args.base_url.rstrip("/")
        # Consulta el catálogo antes de intentar crear libros.
        existentes = listar(sesion, base)
        # Reúne los IDs que ya están utilizados.
        ocupados = {int(libro["id"]) for libro in existentes}
        # Impide crear libros sobre IDs que ya existen.
        if ocupados.intersection(range(args.inicio, args.inicio + 50)):
            raise ValueError("Hay IDs ocupados. Elige otro --inicio; no se sobrescribió ningún libro.")
        # Prepara los cincuenta libros que se van a enviar.
        libros = generar(args.inicio)
        # Conserva una copia de los datos enviados para verificarlos después.
        guardar("libros_generados.json", libros)
        # Procesa cada uno de los cincuenta libros.
        for libro in libros:
            # Envía el libro actual a la biblioteca en formato JSON.
            respuesta = sesion.post(base + "/books", json=libro, timeout=30)
            # Muestra el ID y el estado HTTP de cada creación.
            print(f"Libro {libro['id']}: HTTP {respuesta.status_code}")
            # Detiene la operación si la respuesta HTTP informa un error.
            respuesta.raise_for_status()
            # Deja una pequeña pausa para no enviar todo de golpe.
            time.sleep(0.25)
        # Vuelve a consultar el catálogo completo después de la carga.
        catalogo = listar(sesion, base)
        # Organiza los libros recibidos por ID para encontrarlos fácilmente.
        por_id = {int(libro["id"]): libro for libro in catalogo}
        # Procesa cada uno de los cincuenta libros.
        for libro in libros:
            # Busca en el catálogo el libro que se acaba de enviar.
            recibido = por_id.get(libro["id"], {})
            # Compara título, autor e ISBN para comprobar que se guardaron bien.
            if any(recibido.get(campo) != libro[campo] for campo in ("title", "author", "isbn")):
                raise ValueError(f"No se pudo verificar el libro {libro['id']}.")
        # Guarda el catálogo completo como respaldo de la revisión.
        guardar("catalogo_final.json", catalogo)
        # Muestra el catálogo completo con acentos y sangría.
        print(json.dumps(catalogo, ensure_ascii=False, indent=2))
        # Informa que se verificaron los cincuenta libros y muestra el total.
        print(f"50 libros verificados. Catálogo completo guardado: {len(catalogo)} libros.")


# Ejecuta el programa solamente cuando este archivo se abre directamente.
if __name__ == "__main__":
    try:
        main()
    # Atiende los problemas de conexión o de la solicitud HTTP.
    except requests.RequestException:
        raise SystemExit("Error HTTP o de conexión. Revisa el último estado y el servicio. Puede haber creaciones parciales; consulta el catálogo antes de repetir.")
    # Muestra el problema explicado por el programa.
    except ValueError as error:
        raise SystemExit(str(error))

