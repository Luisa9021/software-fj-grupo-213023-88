from abc import ABC, abstractmethod
from excepciones import (ParametroFaltanteError, ClienteInvalidoError)
from logger import registrar_error


class Entidad(ABC):
    """
    Clase abstracta base para las entidades
    generales del sistema.
    """

    def __init__(self, identificador):
        self.identificador = identificador

    # ==========================
    # IDENTIFICADOR
    # ==========================

    @property
    def identificador(self):
        return self._identificador

    @identificador.setter
    def identificador(self, valor):

        if valor is None:
            mensaje = ("El identificador es obligatorio.")
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        if not isinstance(valor, (str, int)):
            mensaje = ("El identificador debe ser " "texto o número.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        valor = str(valor).strip()

        if not valor:
            mensaje = ("El identificador no puede " "estar vacío.")
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        self._identificador = valor

    # ==========================
    # MÉTODO ABSTRACTO
    # ==========================

    @abstractmethod
    def mostrar_info(self):
        """
        Cada entidad debe implementar
        su propia presentación.
        """
        pass

    # ==========================
    # REPRESENTACIÓN
    # ==========================

    def __str__(self):
        return self.mostrar_info()
