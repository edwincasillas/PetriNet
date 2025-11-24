from collections import deque
from __init__ import *


class Analysis:
    def __init__(self, red_petri):
        self.red = red_petri
        self.grafo_cobertura = GrafoCobertura(red_petri)
    
    def _tarjan(self, u, adyacencia):
        self.ids[u] = self.low[u] = self.time  # almacena el id de descubrimiento de cada nodo/ valor de enlace
        self.time += 1  # contador de descubrimiento
        self.stack.append(u)  # pila de nodos
        self.on_stack[u] = True  # esta el nodo en la pila?

        for v in adyacencia.get(u, set()):
            if v not in self.ids or self.ids[v] == -1:
                # Vecino no visitado
                self._tarjan(v, adyacencia)
                self.low[u] = min(self.low[u], self.low[v])
            elif self.on_stack[v]:
                # Vecino en la pila, actualiza low-link
                self.low[u] = min(self.low[u], self.ids[v])

        # Si el ID de descubrimiento es igual al low-link, se encontro un CFC.
        if self.ids[u] == self.low[u]:
            scc = []
            while self.stack:
                node = self.stack.pop()
                self.on_stack[node] = False
                scc.append(node)
                if node == u:
                    break
            self.sccs.append(scc)
    
    def es_alcanzable(self, grafo_arcos_inverso, inicio, destino):
        """
        Verifica si el destino es alcanzable desde el inicio BFS
        """
        cola = deque([inicio])
        visitados = {inicio}

        while cola:
            actual = cola.popleft()
            if actual == destino:
                return True

            # Recorre los vecinos (los arcos del grafo invertido)
            if actual in grafo_arcos_inverso:
                for vecino in grafo_arcos_inverso[actual]:
                    if vecino not in visitados:
                        visitados.add(vecino)
                        cola.append(vecino)
        return False

    def reversibilidad(self, nodos=None, arcos=None):
        """
        Verifica si la Red de Petri es reversible.
        """
        if nodos is None or arcos is None:
            nodos, arcos = self.grafo_cobertura.expandir_grafo_cobertura()
        
        # Verifica Acotamiento
        """
        # aunque visualmente podemos ver que hay finitos lugares en el GC, realmente hay infinitos,
        # por lo que no puede ir desde el destino al inicio
        # Se tendria que cambiar la logica para ignorar el ω y que tome los nodos visuales en lugar
        # de los reales
        # """
        if any('ω' in marcado for marcado in nodos.keys()):
            print("\nREVERSIBILIDAD: ❌ NO REVERSIBLE (La red es NO ACOTADA)")
            return False

        # un nodo (marcado) es una tupla
        M0 = tuple(self.red.marcado_inicial)

        # diccionario para almacenar el grafo invertido (destino -> lista de origenes)
        grafo_inverso = {nodo: set() for nodo in nodos.keys()}

        for arco in arcos:
            origen = arco['origen']
            destino = arco['destino']
            # el destino del arco original (arco['destino']) es el inicio del arco inverso
            grafo_inverso[destino].add(origen)

        # verifica el regreso a M0 desde cada nodo alcanzable
        es_reversible = True
        print(f"\nVerificando camino de regreso a M0 {M0} desde todos los {len(nodos)} nodos alcanzables...")

        for Mk in nodos.keys():
            # si Mk es M0, es alcanzable.
            if Mk == M0:
                continue

            grafo_adyacencia = {nodo: set() for nodo in nodos.keys()}
            for arco in arcos:
                grafo_adyacencia[arco['origen']].add(arco['destino'])

            if not self.es_alcanzable(grafo_adyacencia, Mk, M0):
                print(f"Fallo la reversibilidad: No se puede regresar a M0 desde {list(Mk)}")
                es_reversible = False
                break

        if es_reversible:
            print(f"El marcado inicial M0 es alcanzable desde todos los nodos.")
            print("\nREVERSIBILIDAD: ✅ REVERSIBLE")
        else:
            print("\nREVERSIBILIDAD: ❌ NO REVERSIBLE")
        
        return es_reversible

    def vivacidad(self, nodos=None, arcos=None):
        """
        Verifica si la red es viva mediante tarjan.

        La RP es viva si y solo si el subgrafo del grafo de alcanzabilidad que consiste en
        la unión de todas las CFC es fuertemente conexo y cubre todas las transiciones.
        """
        if nodos is None or arcos is None:
            nodos, arcos = self.grafo_cobertura.expandir_grafo_cobertura()

        # Verifica nodos terminales (deadlocks)
        for _ , info in nodos.items():
            if info['tipo'] == 'terminal':
                print("\nVIVACIDAD: ❌ NO VIVA (Existe nodo terminal/deadlock).")
                return False

        # construye grafo de adyacencia
        graph_adj = {nodo: set() for nodo in nodos.keys()}
        for arco in arcos:
            graph_adj[arco['origen']].add(arco['destino'])

        # inicializa estructuras de Tarjan
        self.ids = {} # almacena el ID de descubrimiento de cada nodo.
        self.low = {} # almacenar el valor de enlace (low-link) de cada nodo.
        self.on_stack = {} # el nodo esta en la pila? (booleano)
        self.stack = [] # pila de nodos
        self.sccs = [] # lista de componentes fuertemente conexos
        self.time = 0 # contador de descubrimiento de ids

        # inicializa todos los nodos como no visitados
        for node in nodos.keys():
            self.ids[node] = -1
            self.low[node] = -1
            self.on_stack[node] = False

        for node in nodos.keys():
            if self.ids[node] == -1:
                self._tarjan(node, graph_adj)

        # verifica la vivacidad en la red
        node_to_scc = {}
        for scc in self.sccs:
            # Convertimos la lista de CFC a una tupla de tuplas, o simplemente la usamos como identificador.
            # Aquí, usaremos la primera tupla de la CFC como identificador para simplificar.
            scc_identifier = tuple(sorted(scc))
            for node in scc:
                node_to_scc[node] = scc_identifier
        
        # 3. VERIFICACIÓN DE CICLOS Y COBERTURA DE TRANSICIONES
        
        n_transiciones = self.red.n_transiciones
        todas_las_transiciones = set(range(n_transiciones))
        transiciones_cfc = set()

        # recorre los arcos verificando si el origen y destino estan en el SCC
        for arco in arcos:
            origen = arco['origen']
            destino = arco['destino']
            transicion = arco['transicion']
            scc_origen_id = node_to_scc.get(origen)
            scc_destino_id = node_to_scc.get(destino)
            if scc_origen_id is not None and scc_origen_id == scc_destino_id:
                transiciones_cfc.add(transicion)

        # todas las transiciones pueden participar en un ciclo?
        if transiciones_cfc == todas_las_transiciones:
            print(f"\nVIVACIDAD: ✅ VIVA (Todas las transiciones T{list(todas_las_transiciones)} estan en un ciclo/CFC).")
            return True
        else:
            transiciones_faltantes = todas_las_transiciones - transiciones_cfc
            print(f"\nVIVACIDAD: ❌ NO VIVA (Faltan transiciones {list(transiciones_faltantes)} en los ciclos).")
            return False
