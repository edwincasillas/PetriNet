from collections import deque

class RedPetri:
    def __init__(self, pre, post, marcado_inicial):
        """
        Inicializa la Red de Petri
        
        Args:
            pre: Matriz de pre-condiciones (lugares x transiciones)
            post: Matriz de post-condiciones (lugares x transiciones)
            marcado_inicial: Lista con el marcado inicial de cada lugar
        """
        self.pre = pre
        self.post = post
        self.marcado_actual = marcado_inicial.copy()
        self.marcado_inicial = marcado_inicial.copy()
        self.n_transiciones = len(pre[0])
        self.n_lugares = len(pre)
        
        # Calcular matriz de incidencia c = post - pre
        self.c = self.calcular_matriz_incidencia()
    
    def calcular_matriz_incidencia(self):
        """Calcula la matriz de incidencia c = post - pre"""
        c = []
        for i in range(self.n_lugares):
            fila = []
            for j in range(self.n_transiciones):
                fila.append(self.post[i][j] - self.pre[i][j])
            c.append(fila)
        return c
    
    def transiciones_habilitadas(self, marcado=None):
        """
        Retorna los índices de las transiciones habilitadas en un marcado dado
        Verifica M >= Pre para cada transición
        """
        if marcado is None:
            marcado = self.marcado_actual
            
        habilitadas = []
        
        for t in range(self.n_transiciones):
            habilitada = True
            # Verificar M >= Pre para todos los lugares
            for p in range(self.n_lugares):
                if self.pre[p][t] > marcado[p]:
                    habilitada = False
                    break
            if habilitada:
                habilitadas.append(t)
        
        return habilitadas
    
    def disparar(self, transicion, marcado=None):
        """
        Dispara una transición desde un marcado dado
        
        Args:
            transicion: Índice de la transición a disparar
            marcado: Marcado desde el cual disparar (opcional)
            
        Returns:
            tuple: (éxito, nuevo_marcado)
        """
        if marcado is None:
            marcado = self.marcado_actual
            
        # Verificar si la transición está habilitada
        if transicion not in self.transiciones_habilitadas(marcado):
            return False, marcado
        
        # Calcular nuevo marcado: M' = M + c[:,t]
        nuevo_marcado = marcado.copy()
        for p in range(self.n_lugares):
            nuevo_marcado[p] = marcado[p] + self.c[p][transicion]
        
        # Actualizar marcado actual si no se proporcionó uno específico
        if marcado == self.marcado_actual:
            self.marcado_actual = nuevo_marcado
            
        return True, nuevo_marcado
    
    def busqueda_por_anchura(self, max_profundidad=10):
        """
        Realiza búsqueda por anchura en el árbol de alcance
        
        Returns:
            dict: Diccionario con todos los marcados alcanzables
        """
        # Usar tupla para poder usar como clave en diccionario
        marcado_inicial_tuple = tuple(self.marcado_inicial)
        
        visitados = {}  # marcado -> {padre: None, transicion: None}
        cola = deque()
        
        # Inicializar con el marcado inicial
        visitados[marcado_inicial_tuple] = {'padre': None, 'transicion': None}
        cola.append((marcado_inicial_tuple, 0))  # (marcado, profundidad)
        
        while cola:
            marcado_actual_tuple, profundidad = cola.popleft()
            marcado_actual = list(marcado_actual_tuple)
            
            if profundidad >= max_profundidad:
                continue
                
            # Obtener transiciones habilitadas para este marcado
            habilitadas = self.transiciones_habilitadas(marcado_actual)
            
            for transicion in habilitadas:
                # Disparar transición
                exito, nuevo_marcado = self.disparar(transicion, marcado_actual)
                
                if exito:
                    nuevo_marcado_tuple = tuple(nuevo_marcado)
                    
                    # Si es un nuevo marcado, agregar a la cola
                    if nuevo_marcado_tuple not in visitados:
                        visitados[nuevo_marcado_tuple] = {
                            'padre': marcado_actual_tuple,
                            'transicion': transicion
                        }
                        cola.append((nuevo_marcado_tuple, profundidad + 1))
        
        return visitados
    
    def mostrar_arbol_alcance(self, arbol):
        """Muestra el árbol de alcance encontrado por BFS"""
        print("ÁRBOL DE ALCANCE - BÚSQUEDA POR ANCHURA")
        
        for i, (marcado, info) in enumerate(arbol.items()):
            padre_str = f"Padre: {info['padre']}" if info['padre'] else "INICIAL"
            transicion_str = f"Transición: T{info['transicion']}" if info['transicion'] is not None else ""
            print(f"M{i}: {marcado} | {padre_str} | {transicion_str}")
    
    def mostrar_estado(self):
        """Muestra el estado actual de la red"""
        print(f"\nMarcado actual: {self.marcado_actual}")
        print(f"Transiciones habilitadas: {self.transiciones_habilitadas()}")


def simulador_red_petri():
    """
    Simulador de Red de Petri con búsqueda por anchura
    """
    
    # DATOS PREDEFINIDOS
    """pre = [
        [1, 0, 0],  # P0
        [0, 1, 0],  # P1  
        [0, 0, 1]   # P2
    ]
    
    post = [
        [0, 0, 0],  # P0
        [1, 0, 0],  # P1
        [0, 1, 1]   # P2
    ]"""

    pre = [
        [1,0,0,0,1],
        [0,1,0,0,0],
        [0,0,1,0,0],
        [0,0,0,1,0],
        [0,0,0,1,0]
    ]
    post = [
        [0,0,0,1,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [0,1,1,0,0],
        [0,0,1,0,1]
    ]
    
    #marcado_inicial = [3, 0, 0]
    marcado_inicial = [1, 0, 0, 2, 1]
    
    # Crear la red de Petri
    red = RedPetri(pre, post, marcado_inicial)
    
    print("SIMULADOR DE REDES DE PETRI COMPLETO")
    print("Datos predefinidos:")
    print(f"Matriz Pre: {pre}")
    print(f"Matriz Post: {post}")
    print(f"Matriz Incidencia (c): {red.c}")
    print(f"Marcado inicial: {marcado_inicial}")
    
    # Realizar búsqueda por anchura
    print("\nRealizando búsqueda por anchura...")
    arbol_alcance = red.busqueda_por_anchura()
    red.mostrar_arbol_alcance(arbol_alcance)
    
    # Ciclo interactivo de simulación
    print("MODO INTERACTIVO")
    
    paso = 1
    while True:
        print(f"\n--- Paso {paso} ---")
        red.mostrar_estado()
        
        # Obtener transiciones habilitadas
        habilitadas = red.transiciones_habilitadas()
        
        # Si no hay transiciones habilitadas, fin de la simulación
        if not habilitadas:
            print("\nBLOQUEO - No hay transiciones habilitadas")
            print("Fin de la simulación.")
            break
        
        # Preguntar al usuario qué transición disparar
        while True:
            try:
                opcion = int(input("¿Cuál transición desea disparar? "))
                if opcion in habilitadas:
                    break
                else:
                    print(f"Error: La transición {opcion} no está habilitada.")
                    print(f"Transiciones habilitadas: {habilitadas}")
            except ValueError:
                print("Error: Por favor ingrese un número válido.")
        
        # Disparar la transición seleccionada
        exito, nuevo_marcado = red.disparar(opcion)
        if exito:
            print(f"Transición {opcion} disparada exitosamente")
            print(f"Nuevo marcado: {nuevo_marcado}")
        else:
            print(f"Error al disparar transición {opcion}")
        
        paso += 1


# Ejemplo de uso con diferentes redes
def ejemplo_red_simple():
    """Ejemplo con una red más simple"""
    
    pre = [[1, 0], [0, 1]]
    post = [[0, 1], [1, 0]]
    marcado_inicial = [1, 0]
    
    red = RedPetri(pre, post, marcado_inicial)
    
    print("\n" + "="*50)
    print("EJEMPLO: RED SIMPLE")
    print("="*50)
    print(f"Pre: {pre}")
    print(f"Post: {post}") 
    print(f"Matriz c: {red.c}")
    print(f"Marcado inicial: {marcado_inicial}")
    
    # Búsqueda por anchura
    arbol = red.busqueda_por_anchura()
    red.mostrar_arbol_alcance(arbol)


if __name__ == "__main__":
    # Ejecutar ejemplo simple
    ejemplo_red_simple()
    
    # Ejecutar simulador principal
    simulador_red_petri()