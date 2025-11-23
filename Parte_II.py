from collections import deque

class GrafoCobertura:
    def __init__(self, red_petri):
        """
        Inicializa el Grafo de Cobertura con una Red de Petri
        red_petri: Instancia de la clase RedPetri
        """
        self.red = red_petri
        self.omega = 'ω'  # Representación simbólica de omega
        self.red.cobertura = True
    
    def es_omega(self, valor):
        """Verifica si un valor representa omega"""
        return valor == self.omega
    
    def comparar_marcas(self, marca1, marca2):
        """
        Compara dos marcas considerando omega.
        Devuelve: -1 si marca1 < marca2, 0 si iguales, 1 si marca1 > marca2
        """
        if marca1 == marca2:
            return 0
        
        # Si ambos son omega, son iguales
        if self.es_omega(marca1) and self.es_omega(marca2):
            return 0
        
        # Omega es mayor que cualquier número finito
        if self.es_omega(marca1) and not self.es_omega(marca2):
            return 1
        if not self.es_omega(marca1) and self.es_omega(marca2):
            return -1
        
        # Comparación numérica normal
        return -1 if marca1 < marca2 else 1
    
    def expandir_grafo_cobertura(self, max_profundidad=100):
        """
        Expande el grafo de cobertura completo
        """
        marcado_inicial_tuple = tuple(self.red.marcado_inicial)
        
        # Estructuras para almacenar información del grafo
        nodos = {}  # marcado_tuple -> información del nodo
        arcos = []  # lista de arcos (origen, destino, transicion)
        
        # Inicializar con el nodo raíz
        nodos[marcado_inicial_tuple] = {
            'tipo': 'frontera',
            'marcado': marcado_inicial_tuple,
            'profundidad': 0,
            'camino_desde_raiz': [marcado_inicial_tuple]
        }
        
        cola_frontera = deque([marcado_inicial_tuple])
        
        while cola_frontera:
            marcado_actual_tuple = cola_frontera.popleft()
            
            # Verificar profundidad máxima
            if nodos[marcado_actual_tuple]['profundidad'] >= max_profundidad:
                nodos[marcado_actual_tuple]['tipo'] = 'profundidad_maxima'
                continue
                
            nodo_actual = nodos[marcado_actual_tuple]
            marcado_actual = list(marcado_actual_tuple)
            
            # Verificar si es nodo duplicado (existe nodo no-frontera con mismo marcado)
            es_duplicado = False
            for marcado_tuple, info_nodo in nodos.items():
                if (marcado_tuple == marcado_actual_tuple and 
                    info_nodo['tipo'] != 'frontera' and 
                    marcado_tuple != marcado_actual_tuple):
                    es_duplicado = True
                    break
            
            if es_duplicado:
                nodos[marcado_actual_tuple]['tipo'] = 'duplicado'
                continue
            
            # Obtener transiciones habilitadas usando la Red de Petri
            habilitadas = self.red.transiciones_habilitadas(marcado_actual)
            
            # Si ninguna transición está habilitada, es nodo terminal
            if not habilitadas:
                nodos[marcado_actual_tuple]['tipo'] = 'terminal'
                continue
            
            # Expandir para cada transición habilitada
            for transicion in habilitadas:
                # Disparar transición (obtener marcado base)
                exito, nuevo_marcado_base = self.red.disparar(transicion, marcado_actual)
                
                if not exito:
                    continue
                
                # Aplicar reglas del grafo de cobertura
                nuevo_marcado = self._aplicar_reglas_cobertura(
                    marcado_actual, nuevo_marcado_base, nodo_actual['camino_desde_raiz']
                )
                
                nuevo_marcado_tuple = tuple(nuevo_marcado)
                
                # Crear nuevo nodo si no existe
                if nuevo_marcado_tuple not in nodos:
                    nuevo_camino = nodo_actual['camino_desde_raiz'] + [nuevo_marcado_tuple]
                    
                    nodos[nuevo_marcado_tuple] = {
                        'tipo': 'frontera',
                        'marcado': nuevo_marcado_tuple,
                        'profundidad': nodo_actual['profundidad'] + 1,
                        'camino_desde_raiz': nuevo_camino
                    }
                    cola_frontera.append(nuevo_marcado_tuple)
                
                # Agregar arco
                arcos.append({
                    'origen': marcado_actual_tuple,
                    'destino': nuevo_marcado_tuple,
                    'transicion': transicion
                })
            
            # Marcar nodo actual como expandido
            nodos[marcado_actual_tuple]['tipo'] = 'expandido'
        
        return nodos, arcos
    
    def _aplicar_reglas_cobertura(self, marcado_k, marcado_z_base, camino_n0_a_nk):
        """
        Aplica las reglas del grafo de cobertura para determinar el marcado final
        """
        nuevo_marcado = marcado_z_base.copy()
        
        for i in range(len(marcado_k)):
            pi = i  # índice del lugar
            
            # Regla 1: Si μ_k(pi) = ω, entonces μ_z(pi) = ω
            if self.es_omega(marcado_k[pi]):
                nuevo_marcado[pi] = self.omega
                continue
            
            # Regla 2: Si existe n_r en el camino de n_0 a n_k con μ_r(pi) < μ_k(pi)
            # y μ_k(pi) < μ_z_base(pi), entonces μ_z(pi) = ω

            # verifica crecimiento μ_k(pi) < μ_z_base(pi) solo si μ_z_base(pi) es finito
            crecimiento = (not self.es_omega(marcado_z_base[pi]) and
                           self.comparar_marcas(marcado_k[pi], nuevo_marcado[pi]) == -1)
            if crecimiento:
                existe_nr_con_condicion = False
            
                #itera sobre los predecesores, excluye el ultimo elemento μ_k
                for marcado_r_tuple in camino_n0_a_nk[:-1]:
                    marcado_r = list(marcado_r_tuple)

                    if (not self.es_omega(marcado_r[pi]) and
                        self.comparar_marcas(marcado_r[pi], marcado_k[pi]) <= 0):
                        existe_nr_con_condicion = True
                        break
                if existe_nr_con_condicion:
                    nuevo_marcado[pi] = self.omega
            """
            for marcado_r_tuple in camino_n0_a_nk:
                marcado_r = list(marcado_r_tuple)

                if (not self.es_omega(marcado_r[pi]) and 
                    not self.es_omega(marcado_k[pi]) and 
                    not self.es_omega(marcado_z_base[pi])):

                    # Verificar si μ_r(pi) < μ_k(pi) y μ_k(pi) < μ_z_base(pi)
                    condicion1 = self.comparar_marcas(marcado_r[pi], marcado_k[pi]) == -1
                    condicion2 = self.comparar_marcas(marcado_k[pi], marcado_z_base[pi]) == -1
                
                if condicion1 and condicion2:
                    existe_nr_con_condicion = True
                    break
            
            if existe_nr_con_condicion:
                nuevo_marcado[pi] = self.omega
            """
        
        return nuevo_marcado
    
    def imprimir_grafo(self, nodos, arcos):
        """Método auxiliar para imprimir el grafo de cobertura"""
        print("GRAFO DE COBERTURA COMPLETO")
        
        print("\nNODOS DEL GRAFO:")
        for marcado, info in nodos.items():
            # Convertir tupla a lista para mostrar omega claramente
            marcado_str = [f"'{x}'" if self.es_omega(x) else str(x) for x in marcado]
            print(f"Nodo: [{', '.join(marcado_str)}]")
            print(f"  Tipo: {info['tipo']}")
            print(f"  Profundidad: {info['profundidad']}")
            print()
        
        print("\nARCOS DEL GRAFO:")
        for arco in arcos:
            origen_str = [f"'{x}'" if self.es_omega(x) else str(x) for x in arco['origen']]
            destino_str = [f"'{x}'" if self.es_omega(x) else str(x) for x in arco['destino']]
            print(f"[{', '.join(origen_str)}] --[t{arco['transicion']}]--> [{', '.join(destino_str)}]")

    def obtener_estadisticas(self, nodos, arcos):
        """Obtiene estadísticas del grafo de cobertura"""
        estadisticas = {
            'total_nodos': len(nodos),
            'nodos_expandidos': 0,
            'nodos_frontera': 0,
            'nodos_terminales': 0,
            'nodos_duplicados': 0,
            'nodos_profundidad_maxima': 0,
            'total_arcos': len(arcos),
            'nodos_con_omega': 0
        }
        
        for marcado, info in nodos.items():
            tipo = info['tipo']
            if tipo in estadisticas:
                estadisticas[f'nodos_{tipo}'] += 1
            
            # Contar nodos que contienen al menos un omega
            if any(self.es_omega(x) for x in marcado):
                estadisticas['nodos_con_omega'] += 1
        
        return estadisticas