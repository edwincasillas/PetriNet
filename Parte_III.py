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
            if v not in self.ids:
                # Vecino no visitado
                self._tarjan(v, adyacencia)
                self.low[u] = min(self.low[u], self.low[v])
            elif self.on_stack[v]:
                # Vecino en la pila, actualiza low-link
                self.low[u] = min(self.low[u], self.ids[v])

        # Si el ID de descubrimiento es igual al low-link, se encontro un CFC.
        if self.ids[u] == self.low[u]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack[node] = False
                scc.append(node)
                if node == u:
                    break
            self.sccs.append(scc)
    
    def es_alcanzable(self, grafo_adyacencia, inicio, destino):
        """
        Verifica si el destino es alcanzable desde el inicio BFS
        """
        cola = deque([inicio])
        visitados = {inicio}

        if inicio == destino:
            return True

        while cola:
            actual = cola.popleft()
            if actual == destino:
                return True

            # Recorre los vecinos
            if actual in grafo_adyacencia:
                for vecino in grafo_adyacencia[actual]:
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
        grafo_adyacencia = {nodo: set() for nodo in nodos.keys()}

        for arco in arcos:
            grafo_adyacencia[arco['origen']].add(arco['destino'])

        # verifica el regreso a M0 desde cada nodo alcanzable
        es_reversible = True
        print(f"\nVerificando camino de regreso a M0 {M0} desde todos los {len(nodos)} nodos alcanzables...")

        for Mk in nodos.keys():
            # si Mk es M0, es alcanzable.
            if Mk == M0:
                continue

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

    def verificacion_vivacidad(self, nodos=None, arcos=None):
        """
        Verifica si la red es viva mediante tarjan.

        La RP es viva si y solo si el subgrafo del grafo de alcanzabilidad que consiste en
        la unión de todas las CFC es fuertemente conexo y cubre todas las transiciones.
        """
        n_transiciones = self.red.n_transiciones
        todas_transiciones = set(range(n_transiciones))
        grafo_adyacencia = {}

        #construccion del grafo de ady
        for nodo in nodos.keys():
            grafo_adyacencia[nodo] = set()
        for arco in arcos:
            grafo_adyacencia[arco['origen']].add(arco['destino'])
        
        # verifica que las transiciones se pueden disparar
        trans_disp = set()
        trans_no_disp = set()

        for trans in range(n_transiciones):
            disp = True
            counter = 0
            max_count = 3

            # verifica que para cada nodo hay un nodo que habilite alguna trans
            for nodo_actual in nodos.keys():
                existe_camino = False # verifica que existe un camino que habilite la transicion
                # bfs para encontrar existencia
                cola = deque([nodo_actual])
                visitados = {nodo_actual}

                while cola and not existe_camino:
                    nodo = cola.popleft()

                    # verifica que el marcado habilite la trans
                    marcado_mk = list(nodo)
                    habilitadas = self.red.transiciones_habilitadas(marcado_mk)
                    if trans in habilitadas:
                        existe_camino = True
                        break

                    # expandir vecions
                    if nodo in grafo_adyacencia:
                        for vecino in grafo_adyacencia[nodo]:
                            if vecino not in visitados:
                                visitados.add(vecino)
                                cola.append(vecino)

                if not existe_camino:
                    disp = False
                    if counter < max_count:
                        print(f" Desde el {nodo_actual} no se puede habilitar T{trans}")
                        counter += 1

            if disp:
                print(f"  ✅ T{trans} es VIVA")
                trans_disp.add(trans)
            else:
                print(f"  ❌ T{trans} NO es viva")
                trans_disp.add(trans)

        if not trans_no_disp:
            print("✅ TODAS las transiciones son VIVAS")
            print("VIVACIDAD: ✅ VIVA")
            return True
        else:
            print(f"❌ Transiciones NO vivas: {sorted(trans_disp)}")
            print(f"✅ Transiciones vivas: {sorted(trans_disp)}")
            print("VIVACIDAD: ❌ NO VIVA")
            return False

    def analysis_vivacidad(self, nodos, arcos):
        """
        Analizza las causas de no vivacidad
        
        :param self: obj
        :param nodos: nodos del grafo de cobertura
        :param arcos: arcos de disparo de transiciones
        """
         # verifica deadlocks (nodos terminales)
        nodos_terminales = [marcado for marcado, info in nodos.items() if info['tipo'] == 'terminal']

        if nodos_terminales:
            print(f"❌ Se encontraron {len(nodos_terminales)} nodos terminales (deadlocks):")
            for nodo in nodos_terminales[:3]:  # muetra solo 3
                print(f"   - {nodo}")
        
        # verifica transiciones nunca habilitadas
        trans_hab_some_nodo = set()

        for nodo in nodos.keys():
            lista_marcaje = list(nodo)
            habilitadas = self.red.transiciones_habilitadas(lista_marcaje)
            trans_hab_some_nodo.update(habilitadas)

        todas_transiciones = set(range(self.red.n_transiciones))
        transiciones_nunca_habilitadas = todas_transiciones - trans_hab_some_nodo

        if transiciones_nunca_habilitadas:
            print(f"❌ Transiciones NUNCA habilitadas: {sorted(transiciones_nunca_habilitadas)}")

        # componentes fuertemente conexas
        print("\n--- Análisis de Componentes Fuertemente Conexas ---")
        grafo_adyacencia = {}
        for nodo in nodos.keys():
            grafo_adyacencia[nodo] = set()
        for arco in arcos:
            grafo_adyacencia[arco['origen']].add(arco['destino'])

        # inicializa estructuras de Tarjan
        self.ids = {} # almacena el ID de descubrimiento de cada nodo.
        self.low = {} # almacenar el valor de enlace (low-link) de cada nodo.
        self.on_stack = {} # el nodo esta en la pila? (booleano)
        self.stack = [] # pila de nodos
        self.sccs = [] # lista de componentes fuertemente conexos
        self.time = 0 # contador de descubrimiento de ids

        # inicializa todos los nodos como no visitados
        for node in nodos.keys():
            self.on_stack[node] = False

        for node in nodos.keys():
            if node not in self.ids:
                self._tarjan(node, grafo_adyacencia)

        # verifica la vivacidad en la red
        print(f"Se encontraron {len(self.sccs)} componentes fuertemente conexas: ")

        for i, scc in enumerate(self.sccs):
            print(f"  CFC {i + 1}: {len(scc)} nodos --> {scc}")
            if len(scc) == 1:
                nodo = scc[0]
                # verificamos si es terminal
                if nodo in nodos and nodos[nodo]['tipo'] == 'terminal':
                    print(f"      CFC trivial con nodo terminal: {nodo}")
        
        # identificacion de cfc sin salidas a otras cfc
        cfc_terminal = []

        for i, scc in enumerate(self.sccs):
            es_terminal = True
            for nodo in scc:
                if nodo in grafo_adyacencia:
                    for vecino in grafo_adyacencia[nodo]:
                        if vecino not in scc:
                            es_terminal = False
                            break
                if not es_terminal:
                    break
            if es_terminal:
                cfc_terminal.append(scc)
                print(f"  CFC {i+1} es TERMINAL (sin salida a otras CFCs)")

        return {'nodos_terminales': nodos_terminales,
                'transiciones_nunca_habilitadas': transiciones_nunca_habilitadas,
                'cfc_terminales': cfc_terminal,
                'total_cfc': len(self.sccs)}
        
    def vivacidad(self, nodos=None, arcos=None):
        """
        Verificacion de vivacidad con multiples metodos
        
        :param self: Description
        :param nodos: Description
        :param arcos: Description
        """
        resultado_estructural = self.analysis_vivacidad(nodos, arcos)
        if resultado_estructural['nodos_terminales']:
            print("\n❌ VIVACIDAD: NO VIVA (la CFC final no contiene todas las transiciones/existe mas de una CFC)")
            return False
        if resultado_estructural['transiciones_nunca_habilitadas']:
            print("\n❌ VIVACIDAD: NO VIVA (hay transiciones nunca habilitadas)")
            return False
        
        # Construir mapeo de nodo a CFC
        nodo_a_cfc = {}
        for i, scc in enumerate(self.sccs):
            for nodo in scc:
                nodo_a_cfc[nodo] = i

        # Verificar que cada transicion aparece en al menos un ciclo
        transiciones_en_ciclos = set()
        for arco in arcos:
            origen = arco['origen']
            destino = arco['destino']
            transicion = arco['transicion']

            if origen in nodo_a_cfc and destino in nodo_a_cfc:
                if nodo_a_cfc[origen] == nodo_a_cfc[destino]:
                    transiciones_en_ciclos.add(transicion)

        todas_transiciones = set(range(self.red.n_transiciones))
        if transiciones_en_ciclos == todas_transiciones:
            print("✅ Todas las transiciones son parte de la misma CFC")
            print("✅ VIVACIDAD: VIVA (por analisis de CFCs)")
            return True
        else:
            transiciones_faltantes = todas_transiciones - transiciones_en_ciclos
            print(f"❌ Transiciones que no participan en las componentes: {sorted(transiciones_faltantes)}")

        return False