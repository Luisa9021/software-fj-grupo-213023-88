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
        # El nombre es obligatorio
        if not nombre_servicio or not str(nombre_servicio).strip():
            registrar_error("Servicio sin nombre")
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        # La tarifa debe ser un número mayor que cero
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            registrar_error(f"Tarifa inválida en '{nombre_servicio}': {tarifa_base}")
            raise ServicioInvalidoError("La tarifa base debe ser un número mayor que cero.")
        super().__init__(str(nombre_servicio).strip())  # Entidad guarda el identificador
        self._nombre_servicio = str(nombre_servicio).strip()  # Nombre del servicio
        self._tarifa_base = float(tarifa_base)  # Tarifa por hora
        self.disponible = bool(disponible)  # True si se puede reservar

    @property
    def nombre_servicio(self):
        """Nombre del servicio (solo lectura)."""
        return self._nombre_servicio

    @property
    def tarifa_base(self):
        """Tarifa por hora (solo lectura)."""
        return self._tarifa_base

    def verificar_disponibilidad(self):
        """Lanza error si el servicio no está disponible."""
        if not self.disponible:
            registrar_error(f"Servicio '{self._nombre_servicio}' no disponible")
            raise ServicioNoDisponibleError(f"El servicio '{self._nombre_servicio}' no está disponible.")

    def validar_duracion(self, horas):
        """Lanza error si las horas no son un número entre 0 y MAX_HORAS."""
        if not isinstance(horas, (int, float)) or horas <= 0 or horas > MAX_HORAS:
            registrar_error(f"Duración inválida en '{self._nombre_servicio}': {horas}")
            raise ReservaInvalidaError(f"La duración debe estar entre 0 y {MAX_HORAS} horas.")

    def calcular_total(self, subtotal, impuesto, descuento):
        """Aplica descuento e impuesto (0.10 = 10 %) y devuelve el total."""
        if not 0 <= descuento <= 1 or not 0 <= impuesto <= 1:
            registrar_error(f"Descuento o impuesto inválido: {descuento}, {impuesto}")
            raise CalculoInconsistenteError("Descuento e impuesto deben estar entre 0 y 1.")
        total = round(subtotal * (1 - descuento) * (1 + impuesto), 2)  # Descuento y luego impuesto
        registrar_evento(f"Costo de '{self._nombre_servicio}': {total}")
        return total

    @abstractmethod
    def validar_parametros(self, horas, **opciones):
        """Cada servicio valida sus propios parámetros."""

    @abstractmethod
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, **opciones):
        """Cada servicio calcula su costo a su manera (polimorfismo)."""

    @abstractmethod
    def descripcion(self):
        """Cada servicio se describe a sí mismo."""

    def mostrar_info(self):
        """Implementa el método abstracto de Entidad."""
        return f"Servicio: {self._nombre_servicio} | ${self._tarifa_base:,.0f}/hora | {self.descripcion()}"


class ReservaSala(Servicio):
    """Servicio 1: reserva de salas."""

    RECARGO_PROYECTOR = 20000.0  # Extra por hora si se usa proyector

    def __init__(self, nombre_servicio, tarifa_base, capacidad, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            registrar_error(f"Capacidad inválida en '{nombre_servicio}': {capacidad}")
            raise ServicioInvalidoError("La capacidad debe ser un entero mayor que cero.")
        self.capacidad = capacidad  # Máximo de personas

    def validar_parametros(self, horas, personas=1):
        self.verificar_disponibilidad()
        self.validar_duracion(horas)
        if personas > self.capacidad:  # No se puede superar el aforo
            registrar_error(f"Aforo excedido en '{self._nombre_servicio}': {personas}")
            raise ReservaInvalidaError(f"La sala admite máximo {self.capacidad} personas.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, con_proyector=False, personas=1):
        self.validar_parametros(horas, personas=personas)
        tarifa = self._tarifa_base
        if con_proyector:  # Suma el proyector si se pidió
            tarifa += self.RECARGO_PROYECTOR
        return self.calcular_total(tarifa * horas, impuesto, descuento)

    def descripcion(self):
        return f"Sala para hasta {self.capacidad} personas."


class AlquilerEquipo(Servicio):
    """Servicio 2: alquiler de equipos."""

    SEGURO = 0.10  # El seguro cuesta 10 % del alquiler
    DESC_JORNADA = 0.10  # Descuento por jornada completa
    HORAS_JORNADA = 8  # Horas que cuentan como jornada completa

    def __init__(self, nombre_servicio, tarifa_base, tipo_equipo, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        if not tipo_equipo or not str(tipo_equipo).strip():
            registrar_error(f"Equipo '{nombre_servicio}' sin tipo")
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self.tipo_equipo = str(tipo_equipo).strip()

    def validar_parametros(self, horas, con_seguro=False):
        self.verificar_disponibilidad()
        self.validar_duracion(horas)
        if not isinstance(con_seguro, bool):  # Debe ser True o False
            registrar_error(f"con_seguro inválido en '{self._nombre_servicio}': {con_seguro}")
            raise ServicioInvalidoError("con_seguro debe ser True o False.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, con_seguro=False):
        self.validar_parametros(horas, con_seguro=con_seguro)
        subtotal = self._tarifa_base * horas
        if con_seguro:  # Suma el seguro si se pidió
            subtotal += subtotal * self.SEGURO
        if horas >= self.HORAS_JORNADA:  # Descuento extra por jornada completa
            descuento = min(1.0, descuento + self.DESC_JORNADA)
        return self.calcular_total(subtotal, impuesto, descuento)

    def descripcion(self):
        return f"Alquiler de {self.tipo_equipo}."


class AsesoriaEspecializada(Servicio):
    """Servicio 3: asesoría con precio según el nivel del asesor."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # Multiplicador por nivel
    RECARGO_PRESENCIAL = 0.15  # Presencial cuesta 15 % más
    MIN_HORAS = 0.5  # Duración mínima

    def __init__(self, nombre_servicio, tarifa_base, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        if not especialidad or not str(especialidad).strip():
            registrar_error(f"Asesoría '{nombre_servicio}' sin especialidad")
            raise ParametroFaltanteError("La especialidad es obligatoria.")
        nivel = str(nivel).strip().lower()
        if nivel not in self.NIVELES:  # Solo niveles definidos
            registrar_error(f"Nivel inválido en '{nombre_servicio}': {nivel}")
            raise ServicioInvalidoError("Nivel inválido. Use: junior, senior o experto.")
        self.especialidad = str(especialidad).strip()
        self.nivel = nivel

    def validar_parametros(self, horas, presencial=False):
        self.verificar_disponibilidad()
        self.validar_duracion(horas)
        if horas < self.MIN_HORAS:  # Una asesoría dura mínimo media hora
            registrar_error(f"Asesoría muy corta en '{self._nombre_servicio}': {horas}")
            raise ReservaInvalidaError(f"La asesoría debe durar al menos {self.MIN_HORAS} horas.")
        if not isinstance(presencial, bool):  # Debe ser True o False
            registrar_error(f"presencial inválido en '{self._nombre_servicio}': {presencial}")
            raise ServicioInvalidoError("presencial debe ser True o False.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, presencial=False):
        self.validar_parametros(horas, presencial=presencial)
        subtotal = self._tarifa_base * self.NIVELES[self.nivel] * horas
        if presencial:  # Recargo por modalidad presencial
            subtotal += subtotal * self.RECARGO_PRESENCIAL
        return self.calcular_total(subtotal, impuesto, descuento)

    def descripcion(self):
        return f"Asesoría de {self.especialidad} (nivel {self.nivel})."
