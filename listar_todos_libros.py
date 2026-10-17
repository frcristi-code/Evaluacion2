"""Lista y verifica la biblioteca sin crear libros.

Integra el aporte de Rodrigo Velasquez: listado separado, orden por autor,
ISBN visible y comprobación de IDs. Reutiliza la paginación completa del
proyecto para no depender de una cantidad fija de páginas o de registros.
"""
import argparse
import os

import requests

from biblioteca_50 import listar


def main():
    # Permite adaptar la dirección y el grupo de IDs que se quiere revisar.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://library.demo.local/api/v1')
    parser.add_argument('--inicio', type=int, default=8)
    parser.add_argument('--cantidad', type=int, default=50)
    parser.add_argument('--total-esperado', type=int)
    args = parser.parse_args()
    if args.inicio < 0 or args.cantidad < 1:
        parser.error('El inicio no puede ser negativo y la cantidad debe ser positiva.')
    if args.total_esperado is not None and args.total_esperado < 0:
        parser.error('El total esperado no puede ser negativo.')

    # GET permite consultar el catálogo de este laboratorio sin crear registros.
    with requests.Session() as sesion:
        # Si el servidor requiere token para leer, puede configurarse localmente.
        token = os.environ.get('BIBLIOTECA_API_KEY', '').strip()
        if token:
            sesion.headers.update({'X-API-KEY': token})
        catalogo = listar(sesion, args.base_url.rstrip('/'))

    # Ordena todo el catálogo después de reunir las páginas, no cada página sola.
    catalogo.sort(key=lambda libro: str(libro.get('author', '')).casefold())
    print('CATÁLOGO COMPLETO ORDENADO POR AUTOR')
    for libro in catalogo:
        print(f"ID: {libro['id']} | Título: {libro['title']} | "
              f"Autor: {libro['author']} | ISBN: {libro.get('isbn', 'No disponible')}")
    print(f'\nTotal de libros: {len(catalogo)}')

    # Comprueba el bloque de IDs indicado y que todos tengan ISBN visible.
    presentes = {int(libro['id']) for libro in catalogo}
    esperados = set(range(args.inicio, args.inicio + args.cantidad))
    faltantes = sorted(esperados - presentes)
    sin_isbn = [libro['id'] for libro in catalogo if not libro.get('isbn')]
    total_correcto = args.total_esperado is None or len(catalogo) == args.total_esperado
    if faltantes or sin_isbn or not total_correcto:
        print(f'IDs esperados que faltan: {faltantes}')
        print(f'Libros sin ISBN: {sin_isbn}')
        if not total_correcto:
            print(f'Total esperado: {args.total_esperado}; recibido: {len(catalogo)}')
        return 1
    print(f'VERIFICACIÓN CORRECTA: {args.cantidad} IDs esperados presentes e ISBN visibles.')
    print('Esta revisión no crea ni modifica libros.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except requests.RequestException:
        raise SystemExit('No se pudo consultar la biblioteca. Revisa la conexión y el servicio.')
    except (ValueError, KeyError, TypeError):
        raise SystemExit('No se pudo verificar el catálogo. Revisa el formato de la respuesta.')
