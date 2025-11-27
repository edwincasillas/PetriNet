from __init__ import *
import  dibuja_red

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

    print("=" * 50)
    print("SIMULADOR DE REDES DE PETRI")
    print("=" * 50)
    print(f"Matriz Pre: {pre}")
    print(f"Matriz Post: {post}")
    print(f"Matriz de incidencia: {red.C}")
    print(f"Marcado inicial: {marcado_inicial}")

    print("\nRealizando búsqueda por anchura...")
    arbol_alcance = red.busqueda_por_anchura()
    red.mostrar_arbol_alcance(arbol_alcance)

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

    print("=" * 50)
    print("GRAFO DE COBERTURA")
    print("=" * 50)
    print("GENERANDO GRAFO DE COBERTURA...")

    # Expandir grafo de cobertura
    nodos, arcos = grafo.expandir_grafo_cobertura()

    grafo.imprimir_grafo(nodos, arcos)
    dibuja_red.dibuja_GC(nodos, arcos)

    # Mostrar estadísticas
    stats = grafo.obtener_estadisticas(nodos, arcos)
    print("\nESTADÍSTICAS DEL GRAFO:")
    """for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")"""
    print(f"Total de nodos: {stats['total_nodos']}")
    print(f"Total de arcos: {stats['total_arcos']}")
    print(f"Nodos con ω: {stats['nodos_con_omega']}")
    print(f"Nodos expandidos: {stats['nodos_expandidos']}")
    print(f"Nodos frontera: {stats['nodos_frontera']}")
    print(f"Nodos terminales: {stats['nodos_terminales']}")
    print(f"Nodos duplicados: {stats['nodos_duplicados']}")
    print(f"Nodos con profundidad máxima: {stats['nodos_profundidad_maxima']}")

    """PARTE 3, ANALISIS"""
    print("\n")
    print("=" * 50)
    print("ANALISIS DEL GRAFO")
    print("=" * 50)

    # Propiedad de acotamiento
    es_acotada = stats['nodos_con_omega'] == 0
    if not es_acotada:
        print('ACOTAMIENTO: ❌ (hay presencia de ω)')
    else:
        print('ACOTAMIENTO: ✅')
        cota_max = 0
        for marcado in nodos.keys():
            cota_max = max(cota_max, * [m for m in marcado if isinstance(m, int)])
        print(f"La cota maxima es {cota_max}")
    analiza_grafo(nodos, arcos, es_acotada)


def analiza_grafo(nodos, arcos, acotamiento):
    """
    Realiza el analisis del grafo
    """
    red = RedPetri(pre, post, marcado_inicial)
    analisis = Analysis(red)

    es_reversible = analisis.reversibilidad(nodos, arcos)
    es_viva = analisis.vivacidad(nodos, arcos)

    print("\n" + "="*50)
    print("RESUMEN FINAL DE PROPIEDADES")
    print("="*50)
    print(f"Acotamiento: {'✅ ACOTADA' if acotamiento else '❌ NO ACOTADA'}")
    print(f"Reversibilidad: {'✅ REVERSIBLE' if es_reversible else '❌ NO REVERSIBLE'}")
    print(f"Vivacidad: {'✅ VIVA' if es_viva else '❌ NO VIVA'}")


def main():
    dibuja_red.dibuja_RP(pre, post, marcado_inicial)
    while True:
        print("\n")
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
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()