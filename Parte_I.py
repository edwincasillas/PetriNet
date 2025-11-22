from collections import deque


class RedPetri:
    def __init__(self, pre, post, marcado_inicial):
        """
        Inicializa la Red de Petri
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
        self.omega = "ω"

        # Calcular matriz de incidencia c = post - pre
        self.C = self.calcular_matriz_incidencia()

    def es_omega(self, valor):
        return valor == "ω"
    
    def comparar_con_omega(self, pre_condicion, marca):
        if self.es_omega(marca):
            return True
        else:
            return marca >= pre_condicion

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
        Verifica que las transiciones tienen que ser iguales o mayores en los absolutos de C, y diferentes de 0 para
        para que se encuentren habilitadas
        """
        if marcado is None:
            marcado = self.marcado_actual
        habilitadas = []

        for t in range(self.n_transiciones):
            habilitada = True 
            arcos = False
            # Verificar M >= Pre para todos los lugares
            # Verifica que las transiciones tienen que ser iguales o mayores en los absolutos, y diferentes de 0 para
            # para que se encuentren habilitadas
            for p in range(self.n_lugares):
                # if self.pre[p][t] > marcado[p]:
                if self.pre[p][t] > 0 or self.post[p][t] > 0: # toma en cuenta el pre y post
                    arcos = True
                #if self.pre[p][t] > marcado[p]:
                if not self.comparar_con_omega(self.pre[p][t], marcado[p]):
                    habilitada = False
                    break
            if habilitada and arcos: # se habilita si existen arcos
            #if habilitada:
                habilitadas.append(t)

        return habilitadas

    def disparar(self, transicion, marcado=None):
        """
        Dispara una transición desde un marcado dado
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
            #nuevo_marcado[p] = marcado[p] + self.C[p][transicion]
            #nuevo_marcado[p] += self.C[p][transicion]
            if self.es_omega(marcado[p]):
                nuevo_marcado[p] = 'ω'
            else:
                nuevo_marcado[p] += self.C[p][transicion]
                if nuevo_marcado[p] < 0:
                    nuevo_marcado[p] = 0

        # Actualizar marcado actual si no se proporcionó uno específico
        if marcado == self.marcado_actual:
            self.marcado_actual = nuevo_marcado

        return True, nuevo_marcado



    def mostrar_estado(self):
        """Muestra el estado actual de la red"""
        print(f"\nMarcado actual: {self.marcado_actual}")
        print(f"Transiciones habilitadas: {self.transiciones_habilitadas()}")

    def mostrar_estado_primero(self, mk):
        self.marcado_actual = mk
        """Muestra el estado actual de la red en la primera iteración"""
        print(f"\nMarcado actual: {self.marcado_actual}")
        print(f"Transiciones habilitadas: {self.transiciones_habilitadas()}")


def simulador_red_petri():
    # DATOS PREDEFINIDOS
    """pre = [
        [1, 0, 0],  # P0
        [0, 1, 0],  # P1
        [0, 0, 1]   # P2
    ]
    post = [
        [0, 0, 0],  # P0
        [1, 0, 0],  # P1
        #[0, 1, 1]   # P2 <- ESTE ES EL ERROR (no se estaba cancelando la trans de entrada a t2)
        [0, 0, 1]
    ]"""
    marcado_inicial = [3, 0, 0]

    """pre = [
        [1, 0, 0, 0, 1],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0]
    ]
    post = [
        [0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 0, 1]
    ]
    marcado_inicial = [1, 0, 0, 2, 1]"""

    
    pre = [
        [1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 2, 0, 0, 0], # este marcage bloquea la red por la parte izquierda, necesitamos 2 tokens en a inicialmente para poder habilitar la trans 4
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1]
    ]
    post = [
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 2, 0]
    ]
    marcado_inicial = [1, 0, 0, 1, 0, 0, 0, 0, 1]
    

    # Crear la red de Petri
    red = RedPetri(pre, post, marcado_inicial)

    print("SIMULADOR DE REDES DE PETRI COMPLETO")
    print("Datos predefinidos:")
    print(f"Matriz Pre: {pre}")
    print(f"Matriz Post: {post}")
    print(f"Matriz Incidencia (c): {red.C}")
    print(f"Marcado inicial: {marcado_inicial}")

    # Ciclo interactivo de simulación
    print("MODO INTERACTIVO")
    red.mostrar_estado_primero(marcado_inicial)
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


if __name__ == "__main__":
    # Ejecutar simulador principal
    simulador_red_petri()
