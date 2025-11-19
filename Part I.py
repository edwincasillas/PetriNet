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
        self.marcado = marcado_inicial.copy()
        self.n_transiciones = len(pre[0])
        self.n_lugares = len(pre)
    
    def transiciones_habilitadas(self):
        """Retorna los índices de las transiciones habilitadas en el marcado actual"""
        habilitadas = []
        
        for t in range(self.n_transiciones):
            habilitada = True
            for p in range(self.n_lugares):
                if self.pre[p][t] > self.marcado[p]:
                    habilitada = False
                    break
            if habilitada:
                habilitadas.append(t)
        
        return habilitadas
    
    def disparar(self, transicion):
        """
        Dispara una transición si está habilitada
        
        Args:
            transicion: Índice de la transición a disparar
            
        Returns:
            bool: True si se pudo disparar, False en caso contrario
        """
        if transicion not in self.transiciones_habilitadas():
            return False
        
        # Actualizar el marcado
        for p in range(self.n_lugares):
            self.marcado[p] = self.marcado[p] - self.pre[p][transicion] + self.post[p][transicion]
        
        return True
    
    def mostrar_estado(self):
        """Muestra el estado actual de la red"""
        print(f"\nMarcado actual: {self.marcado}")


def simulador_red_petri():
    """
    Simulador de Red de Petri con datos predefinidos
    """
    
    # DATOS PREDEFINIDOS - Ejemplo de sistema de producción
    pre = [
        [1, 0, 0],  # P0: T0 requiere 1, T1 requiere 0, T2 requiere 0
        [0, 1, 0],  # P1: T0 requiere 0, T1 requiere 1, T2 requiere 0
        [0, 0, 1]   # P2: T0 requiere 0, T1 requiere 0, T2 requiere 1
    ]
    
    post = [
        [0, 0, 0],  # P0: T0 produce 0, T1 produce 0, T2 produce 0
        [1, 0, 0],  # P1: T0 produce 1, T1 produce 0, T2 produce 0
        [0, 1, 1]   # P2: T0 produce 0, T1 produce 1, T2 produce 1
    ]
    
    marcado_inicial = [3, 0, 0]  # Marcado inicial
    
    # Crear la red de Petri
    red = RedPetri(pre, post, marcado_inicial)
    
    print("SIMULADOR DE REDES DE PETRI")
    print("=" * 40)
    print("Datos predefinidos:")
    print(f"Matriz Pre: {pre}")
    print(f"Matriz Post: {post}")
    print(f"Marcado inicial: {marcado_inicial}")
    print("=" * 40)
    
    # Ciclo principal de simulación
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
        
        # Mostrar transiciones habilitadas
        print(f"Transiciones habilitadas: {habilitadas}")
        
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
        if red.disparar(opcion):
            print(f"Transición {opcion} disparada exitosamente")
        else:
            print(f"Error al disparar transición {opcion}")
        
        paso += 1


# Ejemplo adicional con otra red predefinida
def simulador_red_mutua_exclusion():
    """
    Otro ejemplo: Red de Petri para exclusión mutua
    """
    
    # DATOS PREDEFINIDOS - Exclusión mutua entre dos procesos
    pre = [
        [1, 0, 0, 0],  # P0: Recurso disponible
        [0, 1, 0, 0],  # P1: Proceso A quiere acceder
        [0, 0, 1, 0],  # P2: Proceso B quiere acceder
        [0, 0, 0, 1],  # P3: Proceso A en sección crítica
        [0, 0, 0, 1]   # P4: Proceso B en sección crítica
    ]
    
    post = [
        [0, 0, 1, 1],  # P0
        [1, 0, 0, 0],  # P1
        [0, 1, 0, 0],  # P2
        [0, 0, 0, 0],  # P3
        [0, 0, 0, 0]   # P4
    ]
    
    marcado_inicial = [1, 1, 1, 0, 0]  # 1 recurso, ambos procesos quieren acceder
    
    red = RedPetri(pre, post, marcado_inicial)
    
    print("\n" + "=" * 50)
    print("EJEMPLO 2: EXCLUSIÓN MUTUA")
    print("=" * 50)
    print(f"Matriz Pre: {pre}")
    print(f"Matriz Post: {post}")
    print(f"Marcado inicial: {marcado_inicial}")
    print("=" * 50)
    
    paso = 1
    while True:
        print(f"\n--- Paso {paso} ---")
        red.mostrar_estado()
        
        habilitadas = red.transiciones_habilitadas()
        
        if not habilitadas:
            print("\nBLOQUEO - No hay transiciones habilitadas")
            print("Fin de la simulación.")
            break
        
        print(f"Transiciones habilitadas: {habilitadas}")
        
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
        
        if red.disparar(opcion):
            print(f"Transición {opcion} disparada exitosamente")
        else:
            print(f"Error al disparar transición {opcion}")
        
        paso += 1


if __name__ == "__main__":
    #simulador_red_petri()
    
    # Ejecutar el segundo ejemplo
    simulador_red_mutua_exclusion()