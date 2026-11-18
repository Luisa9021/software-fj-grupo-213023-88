from abc import abstractmethod  # Para declarar métodos abstractos

from modelos.entidades import Entidad  # Clase base del sistema
from excepciones import (ParametroFaltanteError, ServicioInvalidoError,
                         ServicioNoDisponibleError, ReservaInvalidaError,
                         CalculoInconsistenteError)  # Excepciones propias
from logger import registrar_evento, registrar_error  # Registro en logs

MAX_HORAS = 12  # Duración máxima de una reserva


class Servicio(Entidad):
    """Clase abstracta: define lo que todo servicio debe tener y hacer."""

    def __init__(self, nombre_servicio, tarifa_base, disponible=True):
      
        # Validación del nombre: es obligatorio
        if not nombre_servicio or not str(nombre_servicio).strip():
            registrar_error("Servicio sin nombre")
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        # Validación de la tarifa: número mayor que cero (True/False no cuentan como número)
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            registrar_error(f"Tarifa inválida en '{nombre_servicio}': {tarifa_base}")
            raise ServicioInvalidoError("La tarifa base debe ser un número mayor que cero.")
          
        # Guardado de datos: Entidad guarda el identificador y aquí quedan los atributos protegidos
        super().__init__(str(nombre_servicio).strip())
        self._nombre_servicio = str(nombre_servicio).strip()  # Nombre del servicio
        self._tarifa_base = float(tarifa_base)  # Tarifa por hora
        self.disponible = disponible  # Pasa por el setter, que lo valida



    @property
    def nombre_servicio(self):
        """Nombre del servicio (solo lectura)."""
        return self._nombre_servicio

    @property
    def tarifa_base(self):
        """Tarifa por hora (solo lectura)."""
        return self._tarifa_base

    @property
    def disponible(self):
        """Indica si el servicio se puede reservar."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
      
        # Solo se acepta True o False
        if not isinstance(valor, bool):
            registrar_error(f"Disponibilidad inválida en '{self._nombre_servicio}': {valor}")
            raise ServicioInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = valor
        registrar_evento(f"Servicio '{self._nombre_servicio}' disponible={valor}")

   

    def verificar_disponibilidad(self):
        """Lanza error si el servicio no está disponible."""
        if not self._disponible:
            registrar_error(f"Servicio '{self._nombre_servicio}' no disponible")
            raise ServicioNoDisponibleError(f"El servicio '{self._nombre_servicio}' no está disponible.")

    def validar_duracion(self, horas):
      
        """Lanza error si las horas no son un número entre 0 y MAX_HORAS."""
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or horas <= 0 or horas > MAX_HORAS:
            registrar_error(f"Duración inválida en '{self._nombre_servicio}': {horas}")
            raise ReservaInvalidaError(f"La duración debe estar entre 0 y {MAX_HORAS} horas.")

    def calcular_total(self, subtotal, impuesto, descuento):
      
        """Aplica descuento e impuesto (0.10 = 10 %) y devuelve el total."""
        try:
            # Descuento e impuesto son fracciones entre 0 y 1
            if not 0 <= descuento <= 1 or not 0 <= impuesto <= 1:
                registrar_error(f"Descuento o impuesto inválido: {descuento}, {impuesto}")
                raise CalculoInconsistenteError("Descuento e impuesto deben estar entre 0 y 1.")
            # Cálculo: primero el descuento y luego el impuesto
            total = round(subtotal * (1 - descuento) * (1 + impuesto), 2)
        except TypeError as error:
            # Si llega un dato que no es número, se encadena el error original (raise ... from)
            registrar_error(f"Datos no numéricos en el cálculo de '{self._nombre_servicio}': {error}")
            raise CalculoInconsistenteError("Subtotal, descuento e impuesto deben ser números.") from error
        registrar_evento(f"Costo de '{self._nombre_servicio}': {total}")  # Se deja constancia en el log
        return total


    @abstractmethod
    def validar_parametros(self, horas, **opciones):
        """Cada servicio valida sus propios parámetros."""

    @abstractmethod
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        """Cada servicio calcula su costo (polimorfismo)."""

    @abstractmethod
    def descripcion(self):
        """Cada servicio se describe a sí mismo."""

    def mostrar_info(self):
        """Implementa el método abstracto de Entidad."""
        return f"Servicio: {self._nombre_servicio} | ${self._tarifa_base:,.0f}/hora | {self.descripcion()}"


class ReservaSala(Servicio):
    """Servicio 1: reserva de salas."""

    def __init__(self, nombre_servicio, tarifa_base, capacidad, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)  # Datos comunes
        self.capacidad = capacidad  # Pasa por el setter, que lo valida

    @property
    def capacidad(self):
        """Máximo de personas de la sala."""
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        # Debe ser un entero mayor que cero (True/False no cuentan como número)
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            registrar_error(f"Capacidad inválida en '{self._nombre_servicio}': {valor}")
            raise ServicioInvalidoError("La capacidad debe ser un entero mayor que cero.")
        self._capacidad = valor

    def validar_parametros(self, horas, personas=1):
        self.verificar_disponibilidad()  # Servicio disponible
        self.validar_duracion(horas)  # Duración válida
        # No se puede superar la capacidad de la sala
        if personas > self._capacidad:
            registrar_error(f"Capacidad excedida en '{self._nombre_servicio}': {personas}")
            raise ReservaInvalidaError(f"La sala admite máximo {self._capacidad} personas.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, personas=1):
        self.validar_parametros(horas, personas=personas)  # Valida antes de calcular
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Sala para hasta {self._capacidad} personas."


class AlquilerEquipo(Servicio):
    """Servicio 2: alquiler de equipos."""

    def __init__(self, nombre_servicio, tarifa_base, tipo_equipo, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)  # Datos comunes
        self.tipo_equipo = tipo_equipo  # Pasa por el setter, que lo valida

    @property
    def tipo_equipo(self):
        """Tipo de equipo que se alquila."""
        return self._tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor):
        # El tipo de equipo es obligatorio
        if not valor or not str(valor).strip():
            registrar_error(f"Equipo '{self._nombre_servicio}' sin tipo")
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = str(valor).strip()

    def validar_parametros(self, horas):
        self.verificar_disponibilidad()  # Servicio disponible
        self.validar_duracion(horas)  # Duración válida

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        self.validar_parametros(horas)  # Valida antes de calcular
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Alquiler de {self._tipo_equipo}."


class AsesoriaEspecializada(Servicio):
    """Servicio 3: asesoría especializada."""

    def __init__(self, nombre_servicio, tarifa_base, especialidad, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)  # Datos comunes
        self.especialidad = especialidad  # Pasa por el setter, que lo valida

    @property
    def especialidad(self):
        """Especialidad de la asesoría."""
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor):
        # La especialidad es obligatoria
        if not valor or not str(valor).strip():
            registrar_error(f"Asesoría '{self._nombre_servicio}' sin especialidad")
            raise ParametroFaltanteError("La especialidad es obligatoria.")
        self._especialidad = str(valor).strip()

    def validar_parametros(self, horas):
        self.verificar_disponibilidad()  # Servicio disponible
        self.validar_duracion(horas)  # Duración válida

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        self.validar_parametros(horas)  # Valida antes de calcular
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Asesoría de {self._especialidad}."
        self.validar_parametros(horas)
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Asesoría de {self.especialidad}."
