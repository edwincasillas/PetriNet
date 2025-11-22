from __init__ import *


def salir(ans):
    """
    Da la posibilidad de salir de la primer parte sin tener que parar el script
    """
    ans = input("¿Desea salir? [y/n]: ")
    if ans in ['y', 'Y']:
        return True
    return False


def simulador_interactivo():
    """Simulador interactivo de Red de Petri"""
    # Crear la red de Petri
    red = RedPetri(pre, post, marcado_inicial)

    print("SIMULADOR DE REDES DE PETRI")
    print("=" * 50)
    print(f"Matriz Pre: {pre}")
    print(f"Matriz Post: {post}")
    print(f"Marcado inicial: {marcado_inicial}")

    # Ciclo interactivo
    red.mostrar_estado_primero(marcado_inicial)
    paso = 1

    while True:
        print(f"\n--- Paso {paso} ---")
        red.mostrar_estado()

        habilitadas = red.transiciones_habilitadas()

        if not habilitadas:
            print("\n¡BLOQUEO! - No hay transiciones habilitadas")
            break

        try:
            opcion = int(input("¿Cuál transición desea disparar? "))
            if opcion in habilitadas:
                exito, nuevo_marcado = red.disparar(opcion)
                if exito:
                    print(f"Transición {opcion} disparada exitosamente")
                    print(f"Nuevo marcado: {nuevo_marcado}")
                else:
                    print(f"Error al disparar transición {opcion}")
            else:
                print(f"Transición {opcion} no está habilitada. Habilitadas: {habilitadas}")
                no_run = salir(opcion)
                if no_run:
                    break
                continue
        except ValueError:
            print("Error: Ingrese un número válido")
            continue

        paso += 1


def generar_grafo_cobertura():
    """Genera y muestra el grafo de cobertura"""
    # Crear red y grafo de cobertura
    red = RedPetri(pre, post, marcado_inicial)
    grafo = GrafoCobertura(red)

    print("GENERANDO GRAFO DE COBERTURA...")

    # Expandir grafo de cobertura
    nodos, arcos = grafo.expandir_grafo_cobertura()

    grafo.imprimir_grafo(nodos, arcos)

    # Mostrar estadísticas
    stats = grafo.obtener_estadisticas(nodos, arcos)
    print("\nESTADÍSTICAS DEL GRAFO:")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

def main():
    while True:
        print("REDES DE PETRI")
        print("1. Mostrar RP y Transiciones Habilitadas")
        print("2. Generar Grafo de Cobertura")
        print("3. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            simulador_interactivo()
        elif opcion == '2':
            generar_grafo_cobertura()
        elif opcion == '3':
            print("Exit...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()