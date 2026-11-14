import logging
class ReservaError(Exception):
    pass

class Reserva:
    def __init__(self, id_reserva: str, cliente, servicio, duracion_horas: int):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = duracion_horas
        self.estado = "Creada"  # Estados permitidos: Creada, Confirmada, Cancelada

    @property
    def id_reserva(self) -> str:
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) == 0:
            raise ReservaError("El ID de la reserva no puede estar vacío o ser inválido.")
        self._id_reserva = valor.strip()

    @property
    def duracion_horas(self) -> int:
        return self._duracion_horas

    @duracion_horas.setter
    def duracion_horas(self, valor: int):
        if valor <= 0:
            raise ReservaError("La duración en horas de la reserva debe ser mayor estrictamente a cero.")
        self._duracion_horas = int(valor)

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado: str):
        estados_validos = ["Creada", "Confirmada", "Cancelada"]
        if nuevo_estado not in estados_validos:
            raise ReservaError(f"Estado de reserva no permitido: '{nuevo_estado}'. Use: {estados_validos}")
        self._estado = nuevo_estado

    def confirmar_reserva(self):
      #Confirmación 
        try:
            # Validaciones lógicas del estado actual
            if self.estado == "Confirmada":
                raise ReservaError(f"La reserva {self.id_reserva} ya se encuentra confirmada previamente.")
            if self.estado == "Cancelada":
                raise ReservaError(f"No es posible confirmar la reserva {self.id_reserva} porque está cancelada.")
            # Procesamiento exitoso del cambio de estado
            self.estado = "Confirmada"
            logging.info(f"Éxito: Reserva {self.id_reserva} confirmada para el cliente {self.cliente.nombre}.")
          
        except ReservaError as re:
            # Excepción controlada personalizada
            logging.warning(f"Advertencia al confirmar reserva {self.id_reserva}: {re}")
            raise  # Propaga la excepción controlada
        except Exception as e:
            # Manejo de error crítico inesperado
            logging.error(f"Error crítico inesperado al procesar la confirmación de la reserva {self.id_reserva}.")
            raise ReservaError(f"Falla grave y no prevista al confirmar la reserva {self.id_reserva}.") from e
        else:
            # Se ejecuta si el bloque 'try' no lanzó ninguna excepción
            print(f"-> [ESTADO EXITOSO] La reserva {self.id_reserva} se procesó y confirmó correctamente.")
        finally:
            # Se ejecuta siempre (haya error o éxito)
            print(f"-> [LOG DE SISTEMA] Operación de confirmación finalizada para la reserva {self.id_reserva}.\n")

    def cancelar_reserva(self):
       #Cancelación de reserva
        try:
            if self.estado == "Cancelada":
                raise ReservaError(f"La reserva {self.id_reserva} ya estaba previamente cancelada.")
            
            self.estado = "Cancelada"
            logging.info(f"Evento: Reserva {self.id_reserva} cancelada exitosamente.")
            print(f"-> [ESTADO CANCELADO] La reserva {self.id_reserva} ha sido cancelada con éxito.")

        except ReservaError as re:
            logging.warning(f"Intento fallido de cancelación en reserva {self.id_reserva}: {re}")
            raise

    def obtener_detalles_reserva(self) -> str:
      
        return (f"Reserva [ID: {self.id_reserva}] | Estado: {self.estado} | "

                f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
                f"Duración: {self.duracion_horas} horas")

      
