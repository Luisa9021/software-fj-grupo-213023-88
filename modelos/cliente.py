from modelos.entidades import Entidad
from excepciones import (ClienteInvalidoError, ParametroFaltanteError)
from logger import registrar_error


class Cliente(Entidad):
    def __init__(self,documento,nombre,correo,telefono):
        super().__init__(documento)

        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    # ==========================
    # DOCUMENTO
    # ==========================

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, identidad):

        if identidad is None:
            mensaje = "El documento es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)
            
        identidad = str(identidad).strip()

        if not identidad:
            mensaje = "El documento es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        if not identidad.isdigit():
            mensaje = ("El documento debe contener " "solo números.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        self.__documento = identidad

    # ==========================
    # NOMBRE
    # ==========================

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, nomb):

        if nomb is None:
            mensaje = "El nombre es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        if not isinstance(nomb, str):
            mensaje = ("El nombre debe ser texto.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        nomb = nomb.strip()

        if len(nomb) < 3:
            mensaje = ("El nombre debe tener " "mínimo 3 caracteres.")
            registrar_error(mensaje)

            raise ClienteInvalidoError(mensaje)

        self.__nombre = nomb.title()

    # ==========================
    # CORREO
    # ==========================

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, email):

        if email is None:
            mensaje = "El correo es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        if not isinstance(email, str):
            mensaje = ("El correo debe ser texto.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        email = email.strip().lower()

        if not email:
            mensaje = "El correo es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        if "@" not in email or "." not in email:
            mensaje = ("Correo electrónico inválido.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        self.__correo = email

    # ==========================
    # TELÉFONO
    # ==========================

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, tel):

        if tel is None:
            mensaje = "El teléfono es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        tel = str(tel).strip()

        if not tel:
            mensaje = "El teléfono es obligatorio."
            registrar_error(mensaje)
            raise ParametroFaltanteError(mensaje)

        if not tel.isdigit():
            mensaje = ("El teléfono debe contener " "solo números.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        if len(tel) < 7:
            mensaje = ("El teléfono debe tener " "al menos 7 dígitos.")
            registrar_error(mensaje)
            raise ClienteInvalidoError(mensaje)

        self.__telefono = tel

    # ==========================
    # INFORMACIÓN
    # ==========================

    def mostrar_info(self):

        return (
            f"Cliente: {self.nombre}\n"
            f"Documento: {self.documento}\n"
            f"Teléfono: {self.telefono}\n"
            f"Correo: {self.correo}"
        )

    def __str__(self):

        return (f"{self.nombre} " f"({self.documento})")
