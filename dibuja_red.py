import graphviz
import os

output_directory = "grafos_generados"

def directorio():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)


def dibuja_RP(pre, post, Mk, imagen="RP"):
    """
    dibuja red de petri inicial
    """
    directorio()
    n_lugares = len(pre)
    n_trans = len(pre[0])

    dot = graphviz.Digraph('PetriNet',
                           comment='Red de Petri',
                           graph_attr={'rankdir': 'TB', 'splines': 'false'})
    
    for i in range(n_lugares):
        # agrega nodos
        place_id = f"P{i}"
        label = f"{place_id}\n({Mk[i]})"

        # forma de circulos, borde verde si es inicial
        dot.node(place_id,
                 label=label,
                 shape='circle',
                 color='green' if Mk[i] > 0 else 'black',)
                # fontcolor='green' if Mk[i] > 0 else 'black')

    # agrega las transiciones
    for i in range(n_trans):
        trans_id = f"T{i}"
        # ls transiciones son cajas delgadas
        dot.node(trans_id,
                 label=trans_id,
                 shape='box',
                 width='0.1',
                 height='0.5')

    # agrega arcos
    # pre, lugar->trans
    for i in range(n_lugares):
        for j in range(n_trans):
            weigth = pre[i][j]
            if weigth > 0:
                place_id = f"P{i}"
                trans_id = f"T{j}"
                dot.edge(place_id, trans_id, label=str(weigth) if weigth > 1 else "")

    # post trans->lugar
    for i in range(n_lugares):
        for j in range(n_trans):
            weigth = post[i][j]
            if weigth > 0:
                place_id = f"P{i}"
                trans_id = f"T{j}"
                dot.edge(trans_id, place_id, label=str(weigth) if weigth > 1 else "")
                
    dot.render(imagen, view=True, format='png', directory=output_directory)
    print(f"Red de Petri guardada en '{output_directory}'!")


def dibuja_GC(nodos, arcos, imagen="GC"):
    """
    dibuja grafo de cobertura
    """
    directorio()
    dot = graphviz.Digraph('CoverageGraph',
                           comment='Grafo de Cobertura',
                           graph_attr={'rankdir': 'LR',
                                       'splines': 'false'})

    marcado_inicial_tuple = next(iter(nodos.keys()))
    
    # Agregar Nodos (Marcados)
    for marcado, info in nodos.items():
        # Formatear el marcado para incluir 'ω' y el tipo de nodo
        marcado_str = [str(x) for x in marcado]

        # Etiqueta del nodo: El marcado
        label_marcado = f"[{', '.join(marcado_str)}]"

        # Color y forma para identificar nodos especiales
        color = 'black'
        shape = 'oval'

        if marcado == marcado_inicial_tuple:
            color = 'green'
        elif 'ω' in marcado:
            color = 'red'
        elif info['tipo'] == 'terminal':
            color = 'blue'
            shape = 'doublecircle'
        elif info['tipo'] == 'duplicado':
            shape = 'box'

        dot.node(str(marcado), # El ID del nodo es la tupla como string
                 label=label_marcado,
                 shape=shape,
                 color=color,
                 style='filled' if info['tipo'] == 'terminal' else '')

    # Agregar Arcos
    for arco in arcos:
        origen_str = str(arco['origen'])
        destino_str = str(arco['destino'])
        transicion_label = f"T{arco['transicion']}"
        dot.edge(origen_str, destino_str, label=transicion_label)

    dot.render(imagen, view=True, format='png', directory=output_directory)
    print(f"¡Grafo de Cobertura guardado en '{output_directory}!")