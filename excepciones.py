"""Excepciones personalizadas del sistema Software FJ."""

# En Python, una excepción es una clase que hereda de Exception.
# Aquí se crea una jerarquía propia: una excepción base y varias hijas,
# una por cada tipo de error previsible del sistema.


class SoftwareFJError(Exception):
    """Excepción base: todas las demás heredan de esta."""
    # Al heredar de Exception, esta clase se puede lanzar con 'raise'.
    # Como todas las excepciones del sistema son hijas de esta, en main.py
    # basta un solo 'except SoftwareFJError' para capturar cualquiera de ellas.


class ClienteInvalidoError(SoftwareFJError):
    """Datos del cliente incorrectos (correo, teléfono, etc.)."""
    # Se lanza en Cliente cuando un dato existe pero no es válido
    # (por ejemplo, un correo sin arroba o un documento con letras).


class ParametroFaltanteError(SoftwareFJError):
    """Falta un dato obligatorio."""
    # Se lanza cuando un dato requerido llega vacío o en None
    # (por ejemplo, un nombre vacío o un servicio sin especialidad).


class ServicioInvalidoError(SoftwareFJError):
    """Parámetros del servicio incorrectos."""
    # Se lanza en los servicios cuando un valor no es aceptable
    # (por ejemplo, una tarifa negativa o una capacidad igual a cero).


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no está disponible."""
    # Se lanza al intentar usar o reservar un servicio
    # que está marcado como no disponible.


class ReservaInvalidaError(SoftwareFJError):
    """Datos de la reserva incorrectos (duración, etc.)."""
    # Se lanza cuando los datos de una reserva no son correctos
    # (por ejemplo, una duración en cero, no numérica o mayor al máximo).


class OperacionNoPermitidaError(SoftwareFJError):
    """Operación que no corresponde al estado actual."""
    # Se lanza cuando una acción no se puede hacer en el estado actual
    # (por ejemplo, confirmar una reserva que ya fue cancelada).


class CalculoInconsistenteError(SoftwareFJError):
    """Error en cálculo de costos, impuestos o descuentos."""
    # Se lanza cuando los valores de un cálculo no tienen sentido
    # (por ejemplo, un descuento mayor al 100 %).
