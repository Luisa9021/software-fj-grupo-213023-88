"""Clase Reserva con estados del sistema Software FJ."""

from excepciones import (SoftwareFJError, ReservaInvalidaError,
                         OperacionNoPermitidaError)  # Excepciones propias
from logger import registrar_evento, registrar_advertencia, registrar_error  # Logs

ESTADOS_VALIDOS = ("Creada", "Confirmada", "Cancelada")  # Estados permitidos


class Reserva:
    """Reserva de un servicio por parte de un cliente."""
# Contador de clase para que cada reserva nueva tenga su ID consecutivo automáticamente
    _contador_id = 1  

    def __init__(self, cliente, servicio, duracion_horas, id_reserva=None):
        # Cliente y servicio son obligatorios
        if cliente is None or servicio is None:
            registrar_error("Reserva sin cliente o sin servicio")
            raise ReservaInvalidaError("La reserva requiere un cliente y un servicio.")
        # Si no llega un ID, se genera uno consecutivo (RES-001, RES-002...)
        if id_reserva is None:
            self.id_reserva = f"RES-{Reserva._contador_id:03d}"
            Reserva._contador_id += 1
        else:
            self.id_reserva = id_reserva
          # Guardo cliente y servicio como atributos protegidos
        self._cliente = cliente  # Atributo protegido
        self._servicio = servicio  # Atributo protegido
        self.duracion_horas = duracion_horas  # Pasa por el setter (valida)
        self.estado = "Creada"  # Estado inicial
        registrar_evento(f"Reserva {self.id_reserva} creada ({self.duracion_horas} h)")

    @property
    def cliente(self):
        """Cliente de la reserva (solo lectura)."""
        return self._cliente

    @property
    def servicio(self):
        """Servicio reservado (solo lectura)."""
        return self._servicio

    @property
    def id_reserva(self):
        """Identificador de la reserva."""
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor):
        # Debe ser un texto no vacío
        if not isinstance(valor, str) or not valor.strip():
            raise ReservaInvalidaError("El ID de la reserva no puede estar vacío o ser inválido.")
        self._id_reserva = valor.strip()

    @property
    def duracion_horas(self):
        """Duración en horas."""
        return self._duracion_horas

    @duracion_horas.setter
    def duracion_horas(self, valor):
        try:
            # Compara con cero; falla con TypeError si no es numérico
            if valor <= 0:
                raise ReservaInvalidaError("La duración en horas debe ser mayor a cero.")
        except TypeError as error:
            # Encadenamiento: se conserva el TypeError original como causa
            raise ReservaInvalidaError(f"Duración no numérica: {valor!r}") from error
        # Solo se aceptan horas enteras: 2.7 no se convierte en 2 en silencio
        if valor != int(valor):
            raise ReservaInvalidaError(f"La duración debe ser un número entero de horas: {valor!r}")
        self._duracion_horas = int(valor)

    @property
    def estado(self):
        """Estado actual de la reserva."""
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado):
        # Solo se aceptan los estados definidos
        if nuevo_estado not in ESTADOS_VALIDOS:
            raise ReservaInvalidaError(
                f"Estado no permitido: '{nuevo_estado}'. Use: {list(ESTADOS_VALIDOS)}")
        self._estado = nuevo_estado

    def calcular_costo_total(self, impuesto=0.0, descuento=0.0):
        """Calcula el costo delegando en el servicio (polimorfismo).

        Impuesto y descuento son fracciones entre 0 y 1 (0.19 = 19 %),
        igual que en servicios.py.
        """
        try:
            # El servicio valida disponibilidad, duración y calcula el total
            return self._servicio.calcular_costo(self._duracion_horas, impuesto, descuento)
        except SoftwareFJError:
            # Los errores propios ya vienen registrados: se propagan igual
            raise
        except Exception as error:
            # Error no previsto: se registra y se encadena con 'from'
            registrar_error(f"Fallo inesperado al calcular costo de {self._id_reserva}")
            raise ReservaInvalidaError(
                f"No se pudo calcular el costo de {self._id_reserva}.") from error

    def confirmar_reserva(self):
        """Confirma la reserva si su estado lo permite."""
        try:
            # No se puede confirmar dos veces ni una reserva cancelada
            if self._estado == "Confirmada":
                raise OperacionNoPermitidaError(f"La reserva {self._id_reserva} ya está confirmada.")
            if self._estado == "Cancelada":
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar {self._id_reserva}: está cancelada.")
            self._servicio.verificar_disponibilidad()  # El servicio debe seguir disponible
            self.estado = "Confirmada"
        except OperacionNoPermitidaError as error:
            registrar_advertencia(f"Confirmación rechazada: {error}")
            raise
        except SoftwareFJError:
            raise  # Ya registrado por el servicio
        except Exception as error:
            registrar_error(f"Fallo inesperado al confirmar {self._id_reserva}")
            raise ReservaInvalidaError(
                f"Falla no prevista al confirmar {self._id_reserva}.") from error
        else:
            # Solo si no hubo error
            registrar_evento(f"Reserva {self._id_reserva} confirmada ({self._cliente.nombre})")
        finally:
            # Siempre se deja constancia de que la operación terminó
            registrar_evento(f"Fin de confirmación de {self._id_reserva}")

    def cancelar_reserva(self):
        """Cancela la reserva si aún no está cancelada."""
        # Cancelar dos veces no está permitido
        if self._estado == "Cancelada":
            registrar_advertencia(f"Cancelación repetida en {self._id_reserva}")
            raise OperacionNoPermitidaError(f"La reserva {self._id_reserva} ya está cancelada.")
        self.estado = "Cancelada"
        registrar_evento(f"Reserva {self._id_reserva} cancelada")

    def obtener_detalles_reserva(self):
        """Resumen en texto de la reserva."""
        return (f"Reserva [ID: {self._id_reserva}] | Estado: {self._estado} | "
                f"Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre_servicio} | "
                f"Duración: {self._duracion_horas} horas")
