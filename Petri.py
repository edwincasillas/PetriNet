import re
import numpy as np
import os
import time


class Petri:
    def __init__(self, pre: np.ndarray, post: np.ndarray, M: list):
        self.pre = pre
        self.post = post
        self.M = M
        self.C = self.pre - self.post

    def data(self):
        print("_" * 50)
        print("Los datos de la red son:")
        print(f"Marcaje: {self.M}")
        print(f"Pre ({self.pre.shape}): \n{self.pre}")
        print(f"post ({self.post.shape}): \n{self.post}")
        print(f"Matriz de incidencia: \n{self.C}")
        print("_" * 50)

    def get_marcaje(self):
        return self.M

    def set_new_mark(self, new):
        self.M = new

    def trans_habilitadas(self):
        """
        Revisa cuales transiciones estan habilitadas
        """
        self.habilitadas = []
        num_trans = self.pre.shape[1]

        for j in range(num_trans):
            print(f"Transicion T{j}: ")
            enable = True
            req = []

            for i in range(len(self.M)):
                if self.pre[i, j] > 0:  # muestra lo que requiere tokens
                    cumple_req = self.M[i] >= self.pre[i, j]
                    estado = "✓ Habilitada" if cumple_req else "✗ Bloqueada"
                    req.append(f"P{i}: {self.M[i]} >= {self.pre[i, j]} ({estado})")

                    if not cumple_req:
                        enable = False
            if not req:
                req.append("Sin requizitos de lugares de entrada")

            # Mostrar requisitos
            for req_item in req:
                print(f"  {req_item}")

            # Mostrar estado final
            if enable:
                print(f"  → TRANSICION T{j} HABILITADA ✓")
                self.habilitadas.append(j)
            else:
                print(f"  → TRANSICION T{j} BLOQUEADA ✗")

        # Resumen final
        print("\n" + "=" * 60)
        if self.habilitadas:
            print(f"TRANSICIONES HABILITADAS: {self.habilitadas}")
            print(f"Total: {len(self.habilitadas)} de {num_trans} transiciones están habilitadas")
        else:
            print("NINGUNA TRANSICIÓN ESTA HABILITADA")
        return self.habilitadas

    def dispara(self, trans):
        """
        Dispara transiciones
        """
        if trans not in self.habilitadas:
            print(f"Error: La transición T{trans} no esta habilitada")
            return False

        # Actualiza marcaje: M = M + C
        new_M = []
        for i in range(len(self.M)):
            new_value = self.M[i] + self.C[i, trans]
            new_M.append(new_value)

        print(f"Disparando transición T{trans}")
        print(f"Marcaje anterior: {self.M}")
        self.M = new_M
        print(f"Nuevo marcaje: {self.M}")

        return True


def limpia():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == "__main__":
    # Exec = True
    r_mark = r'0-9|,|-|.| |'
    # mark = input("Ingresa el marcaje inicial: ")
    mark = "1, 2, 1, 1"  # temporal para pruebas
    trans = int(input("Ingrese la cantidad de transiciones: "))

    # limpieza del marcaje para admitirlo
    if re.search(r_mark, mark):
        mark = mark.replace(' ', '')
    mark = mark.split(',')
    mark = [int(i) for i in mark]

    print(f"Las matrices tienen un tamaño de {len(mark)} x {trans}")
    pre = np.zeros((len(mark), trans))
    post = np.zeros((len(mark), trans))

    print("Ingrese los datos para el pre:\n")
    for i in range(len(mark)):
        for j in range(trans):
            pre[i, j] = int(input(f"Ingrese el dato [{i+1},{j+1}]: "))
            time.sleep(0.5)

    print("Ingrese los datos para el post:\n")
    for i in range(len(mark)):
        for j in range(trans):
            post[i, j] = int(input(f"Ingrese el dato [{i+1},{j+1}]: "))
            time.sleep(0.5)

    limpia()  # limpia pantalla
    petri = Petri(pre, post, mark)

    petri.data()

    print("Transiciones habilitadas: ")
    petri.trans_habilitadas()

    """while Exec:
        trans = int(input("Ingrese transicion a disparar: "))"""
