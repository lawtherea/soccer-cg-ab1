"""Classe para criar a bola"""
from OpenGL.GLU import gluNewQuadric, gluQuadricTexture, GLU_SMOOTH, gluQuadricNormals, gluSphere, gluDeleteQuadric
from OpenGL.GL import (
       glEnable,
       glBindTexture,
       glTexEnvi,
       glDisable,
       glColor3f,
       glMatrixMode,
       glPushMatrix,
       glTranslatef,
       glRotatef,
       GL_TEXTURE_ENV_MODE,
       GL_REPLACE,
       GL_TRUE,
       GL_MODELVIEW, GL_TEXTURE_2D, GL_TEXTURE_ENV, glPopMatrix, glMultMatrixf, GL_MODULATE, GL_BLEND, glIsEnabled
)
import math

from abc import ABC, abstractmethod
from typing import override

def transpor_matriz(m: list[float]) -> list[float]:
    """Retorna a transposta de uma matriz 4x4 em row-major (lista 16)"""

    return [
        m[0], m[4], m[8], m[12],
        m[1], m[5], m[9], m[13],
        m[2], m[6], m[10], m[14],
        m[3], m[7], m[11], m[15]
    ]

class GameObject(ABC):
    """Classe base para todos os objetos do jogo"""

    def __init__(self, name: str, 
                 position: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        self.name: str = name
        self.position: list[float] = list(position)
        self.rotation_axis: list[float] = [0.0, 0.0, 0.0]
        self.scale: list[float] = [1.0, 1.0, 1.0]

    def set_position(self, x: float, y: float, z: float) -> None:
        self.position = [x, y, z]

    def get_position(self) -> tuple[float, ...]:
        return tuple(self.position)

    def translate(self, dx: float, dy: float, dz: float) -> None:
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz

    @abstractmethod
    def draw(self) -> None:
        """Metodo a ser sobrescrito pelas subclasses"""

    @abstractmethod
    def get_info(self) -> dict[str, str | int | float | list | tuple]:
        """Metodo a ser sobrescrito pelas subclasses"""

class Bola(GameObject):
    """Classe para criar, manter e atualizar a bola"""

    def __init__(self, name: str, raio: float = 0.8, 
                 position: tuple[float, float, float] = (0.0, 0.0, 0.0),
                 texture_id = None):
        super().__init__(name, position)
        self.raio: float = raio
        self.texture_id = texture_id

        self.rot_matriz = [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
                ]

        self.angulo_rotacao: float = 0.0
        self.direcao_de_rotacao: float = 0.0
        self.eixo_rotacao_x: float = 0.0
        self.eixo_rotacao_z: float = 0.0

    def _aplicar_rotacao(self, dx: float, dz: float) -> None:
        """Atualiza a matriz de rotacao com base na movimentacao"""
        distancia = math.hypot(dx, dz)
        if distancia == 0:
            return None

        # angulo de rotacao
        angulo: float = distancia / self.raio

        # direcao de rotacao
        dir_x: float = dx / distancia
        dir_z: float = dz / distancia

        # eixo de rotacao
        e_x: float = dir_z
        e_z: float = -dir_x

        c: float = math.cos(angulo)
        s: float = math.sin(angulo)

        # matriz de rotacao 3x3
        m11: float = c + e_x * e_x * (1 - c)
        m12: float = -e_z * s
        m13: float = e_x * e_z * (1 - c)

        m21: float = e_z * s
        m22: float = c
        m23: float = -e_x * s

        m31: float = e_x * e_z * (1 - c)
        m32: float = e_x * s
        m33: float = c + e_z * e_z * (1 - c)

        rotacao = [
                m11, m12, m13, 0.0,
                m21, m22, m23, 0.0,
                m31, m32, m33, 0.0,
                0.0, 0.0, 0.0, 1.0
                ]

        # rotacao = [
        #         m11, m21, m31, 0.0,
        #         m12, m22, m32, 0.0,
        #         m13, m23, m33, 0.0,
        #         0.0, 0.0, 0.0, 1.0
        #         ]

        # multiplicar matriz atual pela matriz de rotacao
        nova = [0.0] * 16
        for i in range(4): # linhas na matriz de rotacao e nova matriz
            for j in range (4): # colunas na matriz atual
                soma: float = 0.0

                for k in range(4): # colunas na matriz de rotacao e linhas na matriz atual
                    soma += rotacao[i*4 + k] * self.rot_matriz[k*4 + j]

                nova [i*4 + j] = soma

        self.rot_matriz = nova

    def set_rotacao_movimento(self, dx: float, dz: float) -> float:
        """Rotaciona a bola de acordo com sua movimentacao"""
        distancia = math.hypot(dx, dz)
        if distancia > 0:
            delta_angulo: float = (distancia / self.raio) * (180.0 * math.pi) * 0.2
            self.angulo_rotacao += delta_angulo
            return delta_angulo

        return 0.0

    def set_rotacao(self, direcao: int, rotacao_x: int, rotacao_z: int) -> None:
        self.direcao_de_rotacao = direcao
        self.eixo_rotacao_x = rotacao_x
        self.eixo_rotacao_z = rotacao_z

    @override
    def translate(self, dx: float, dy: float, dz: float) -> None:
        super().translate(dx, dy, dz)
        self._aplicar_rotacao(dx, dz)

    def _draw_textured(self) -> None:
        """Desenha a bola com a textura armazenada na classe"""

        # desativa o blend para eliminar transparencia da bola
        blend_enabled = glIsEnabled(GL_BLEND)
        if blend_enabled:
            glDisable(GL_BLEND)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluQuadricNormals(quadric, GLU_SMOOTH)

        gluSphere(quadric, self.raio, 100, 100)

        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)

    def _draw_solid(self) -> None:
        """Desenha a bola solida (sem textura)"""
        glColor3f(1.0, 1.0, 1.0)
        gluSphere(self.raio, 100, 100)

    @override
    def draw(self) -> None:
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glTranslatef(self.position[0], self.position[1], self.position[2])
        # glRotatef(self.angulo_rotacao * self.direcao_de_rotacao,
        #           self.eixo_rotacao_x, 0.0, self.eixo_rotacao_z)
        glMultMatrixf(transpor_matriz(self.rot_matriz))

        if self.texture_id is not None:
            self._draw_textured()
        else:
            self._draw_solid()

        glPopMatrix()

    @override
    def get_info(self) -> dict[str, str | int | float | list | tuple]:
        """Retorna informações da bola para debug"""
        return {
            "nome": self.name,
            "posicao": self.get_position(),
            "angulo_rotacao": self.angulo_rotacao,
            "raio": self.raio
        }
