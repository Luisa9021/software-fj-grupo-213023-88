from abc import abstractmethod  # Para declarar métodos abstractos

from modelos.entidades import Entidad  # Clase base del sistema
from excepciones import (ParametroFaltanteError, ServicioInvalidoError,
                         ServicioNoDisponibleError, ReservaInvalidaError,
                         CalculoInconsistenteError)  # Excepciones propias
from logger import registrar_evento, registrar_error  # Registro en logs

MAX_HORAS = 12  # Duración máxima de una reserva


def _fallar(error, mensaje):
    """Registra el error en el log y lo lanza."""
    registrar_error(mensaje)
    raise error(mensaje)


def _es_numero(valor):
    """True si es int o float (los booleanos no cuentan)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _texto_obligatorio(valor, mensaje):
    """Devuelve el texto sin espacios o falla si está vacío."""
    texto = str(valor or "").strip()
    if not texto:
        _fallar(ParametroFaltanteError, mensaje)
    return texto


def _exigir_bool(valor, campo):
    """Falla si el valor no es True o False."""
    if not isinstance(valor, bool):
        _fallar(ServicioInvalidoError, f"{campo} debe ser True o False.")


class Servicio(Entidad):
    """Clase abstracta: lo que todo servicio debe tener y hacer."""

    def __init__(self, nombre_servicio, tarifa_base, disponible=True):
        nombre = _texto_obligatorio(nombre_servicio, "El nombre del servicio es obligatorio.")
        if not _es_numero(tarifa_base) or tarifa_base <= 0:  # Debe ser número > 0
            _fallar(ServicioInvalidoError, f"Tarifa inválida en '{nombre}': debe ser un número mayor que cero.")
        super().__init__(nombre)  # Entidad guarda el identificador
        self._nombre_servicio = nombre  # Nombre del servicio
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

    def _validar(self, horas):
        """Revisa disponibilidad y duración antes de calcular."""
        if not self.disponible:  # Servicio desactivado
            _fallar(ServicioNoDisponibleError, f"El servicio '{self._nombre_servicio}' no está disponible.")
        if not _es_numero(horas) or not 0 < horas <= MAX_HORAS:
            _fallar(ReservaInvalidaError, f"Duración inválida en '{self._nombre_servicio}': debe estar entre 0 y {MAX_HORAS} horas.")

    def _total(self, subtotal, impuesto, descuento):
        """Aplica descuento e impuesto (fracciones: 0.10 = 10 %) y registra el costo."""
        if not 0 <= descuento <= 1 or not 0 <= impuesto <= 1:  # Deben estar entre 0 y 1
            _fallar(CalculoInconsistenteError, "Descuento e impuesto deben estar entre 0 y 1.")
        total = round(subtotal * (1 - descuento) * (1 + impuesto), 2)  # Descuento y luego impuesto
        registrar_evento(f"Costo de '{self._nombre_servicio}': {total}")
        return total

    @abstractmethod
    def validar_parametros(self, horas, **opciones):
        """Cada servicio valida sus propios parámetros (se sobrescribe)."""

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
        if not _es_numero(capacidad) or capacidad != int(capacidad) or capacidad <= 0:
            _fallar(ServicioInvalidoError, "La capacidad debe ser un entero mayor que cero.")
        self.capacidad = int(capacidad)  # Máximo de personas

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, con_proyector=False, personas=1):
        self.validar_parametros(horas, personas=personas)  # Valida antes de calcular
        tarifa = self._tarifa_base + (self.RECARGO_PROYECTOR if con_proyector else 0)
        return self._total(tarifa * horas, impuesto, descuento)

    def validar_parametros(self, horas, personas=1, **_):
        self._validar(horas)  # Disponibilidad y duración
        if personas > self.capacidad:  # No se puede superar el aforo
            _fallar(ReservaInvalidaError, f"La sala admite máximo {self.capacidad} personas.")

    def descripcion(self):
        return f"Sala para hasta {self.capacidad} personas."


class AlquilerEquipo(Servicio):
    """Servicio 2: alquiler de equipos."""

    SEGURO = 0.10  # El seguro cuesta 10 % del alquiler
    DESC_JORNADA = 0.10  # Descuento desde 8 horas (jornada completa)
    HORAS_JORNADA = 8  # Horas que cuentan como jornada completa

    def __init__(self, nombre_servicio, tarifa_base, tipo_equipo, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        self.tipo_equipo = _texto_obligatorio(tipo_equipo, "El tipo de equipo es obligatorio.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, con_seguro=False):
        self.validar_parametros(horas, con_seguro=con_seguro)  # Valida antes de calcular
        subtotal = self._tarifa_base * horas * (1 + (self.SEGURO if con_seguro else 0))
        if horas >= self.HORAS_JORNADA:  # Beneficio por jornada completa
            descuento = min(1.0, descuento + self.DESC_JORNADA)
        return self._total(subtotal, impuesto, descuento)

    def validar_parametros(self, horas, con_seguro=False, **_):
        self._validar(horas)  # Disponibilidad y duración
        _exigir_bool(con_seguro, "con_seguro")  # El seguro es sí/no

    def descripcion(self):
        return f"Alquiler de {self.tipo_equipo}."


class AsesoriaEspecializada(Servicio):
    """Servicio 3: asesoría con precio según el nivel del asesor."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # Multiplicador por nivel
    RECARGO_PRESENCIAL = 0.15  # Presencial cuesta 15 % más
    MIN_HORAS = 0.5  # Duración mínima de una asesoría

    def __init__(self, nombre_servicio, tarifa_base, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        self.especialidad = _texto_obligatorio(especialidad, "La especialidad es obligatoria.")
        self.nivel = str(nivel).strip().lower()
        if self.nivel not in self.NIVELES:  # Solo niveles definidos
            _fallar(ServicioInvalidoError, f"Nivel inválido '{self.nivel}'. Use: {', '.join(self.NIVELES)}.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, presencial=False):
        self.validar_parametros(horas, presencial=presencial)  # Valida antes de calcular
        subtotal = self._tarifa_base * self.NIVELES[self.nivel] * horas
        if presencial:  # Recargo por modalidad presencial
            subtotal *= 1 + self.RECARGO_PRESENCIAL
        return self._total(subtotal, impuesto, descuento)

    def validar_parametros(self, horas, presencial=False, **_):
        self._validar(horas)  # Disponibilidad y duración
        if horas < self.MIN_HORAS:  # Una asesoría dura mínimo media hora
            _fallar(ReservaInvalidaError, f"La asesoría debe durar al menos {self.MIN_HORAS} horas.")
        _exigir_bool(presencial, "presencial")  # La modalidad es sí/no

    def descripcion(self):
        return f"Asesoría de {self.especialidad} (nivel {self.nivel}).""""Servicios del sistema Software FJ: clase abstracta Servicio y 3 servicios especializados."""

from abc import abstractmethod  # Para declarar métodos abstractos

from modelos.entidades import Entidad  # Clase base del sistema
from excepciones import (ParametroFaltanteError, ServicioInvalidoError,
                         ServicioNoDisponibleError, ReservaInvalidaError,
                         CalculoInconsistenteError)  # Excepciones propias
from logger import registrar_evento, registrar_error  # Registro en logs

MAX_HORAS = 12  # Duración máxima de una reserva


def _fallar(error, mensaje):
    """Registra el error en el log y lo lanza."""
    registrar_error(mensaje)
    raise error(mensaje)


def _es_numero(valor):
    """True si es int o float (los booleanos no cuentan)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _texto_obligatorio(valor, mensaje):
    """Devuelve el texto sin espacios o falla si está vacío."""
    texto = str(valor or "").strip()
    if not texto:
        _fallar(ParametroFaltanteError, mensaje)
    return texto


def _exigir_bool(valor, campo):
    """Falla si el valor no es True o False."""
    if not isinstance(valor, bool):
        _fallar(ServicioInvalidoError, f"{campo} debe ser True o False.")


class Servicio(Entidad):
    """Clase abstracta: lo que todo servicio debe tener y hacer."""

    def __init__(self, nombre_servicio, tarifa_base, disponible=True):
        nombre = _texto_obligatorio(nombre_servicio, "El nombre del servicio es obligatorio.")
        if not _es_numero(tarifa_base) or tarifa_base <= 0:  # Debe ser número > 0
            _fallar(ServicioInvalidoError, f"Tarifa inválida en '{nombre}': debe ser un número mayor que cero.")
        super().__init__(nombre)  # Entidad guarda el identificador
        self._nombre_servicio = nombre  # Nombre del servicio
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

    def _validar(self, horas):
        """Revisa disponibilidad y duración antes de calcular."""
        if not self.disponible:  # Servicio desactivado
            _fallar(ServicioNoDisponibleError, f"El servicio '{self._nombre_servicio}' no está disponible.")
        if not _es_numero(horas) or not 0 < horas <= MAX_HORAS:
            _fallar(ReservaInvalidaError, f"Duración inválida en '{self._nombre_servicio}': debe estar entre 0 y {MAX_HORAS} horas.")

    def _total(self, subtotal, impuesto, descuento):
        """Aplica descuento e impuesto (fracciones: 0.10 = 10 %) y registra el costo."""
        if not 0 <= descuento <= 1 or not 0 <= impuesto <= 1:  # Deben estar entre 0 y 1
            _fallar(CalculoInconsistenteError, "Descuento e impuesto deben estar entre 0 y 1.")
        total = round(subtotal * (1 - descuento) * (1 + impuesto), 2)  # Descuento y luego impuesto
        registrar_evento(f"Costo de '{self._nombre_servicio}': {total}")
        return total

    @abstractmethod
    def validar_parametros(self, horas, **opciones):
        """Cada servicio valida sus propios parámetros (se sobrescribe)."""

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
        if not _es_numero(capacidad) or capacidad != int(capacidad) or capacidad <= 0:
            _fallar(ServicioInvalidoError, "La capacidad debe ser un entero mayor que cero.")
        self.capacidad = int(capacidad)  # Máximo de personas

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, con_proyector=False, personas=1):
        self.validar_parametros(horas, personas=personas)  # Valida antes de calcular
        tarifa = self._tarifa_base + (self.RECARGO_PROYECTOR if con_proyector else 0)
        return self._total(tarifa * horas, impuesto, descuento)

    def validar_parametros(self, horas, personas=1, **_):
        self._validar(horas)  # Disponibilidad y duración
        if personas > self.capacidad:  # No se puede superar el aforo
            _fallar(ReservaInvalidaError, f"La sala admite máximo {self.capacidad} personas.")

    def descripcion(self):
        return f"Sala para hasta {self.capacidad} personas."


class AlquilerEquipo(Servicio):
    """Servicio 2: alquiler de equipos."""

    SEGURO = 0.10  # El seguro cuesta 10 % del alquiler
    DESC_JORNADA = 0.10  # Descuento desde 8 horas (jornada completa)
    HORAS_JORNADA = 8  # Horas que cuentan como jornada completa

    def __init__(self, nombre_servicio, tarifa_base, tipo_equipo, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        self.tipo_equipo = _texto_obligatorio(tipo_equipo, "El tipo de equipo es obligatorio.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, con_seguro=False):
        self.validar_parametros(horas, con_seguro=con_seguro)  # Valida antes de calcular
        subtotal = self._tarifa_base * horas * (1 + (self.SEGURO if con_seguro else 0))
        if horas >= self.HORAS_JORNADA:  # Beneficio por jornada completa
            descuento = min(1.0, descuento + self.DESC_JORNADA)
        return self._total(subtotal, impuesto, descuento)

    def validar_parametros(self, horas, con_seguro=False, **_):
        self._validar(horas)  # Disponibilidad y duración
        _exigir_bool(con_seguro, "con_seguro")  # El seguro es sí/no

    def descripcion(self):
        return f"Alquiler de {self.tipo_equipo}."


class AsesoriaEspecializada(Servicio):
    """Servicio 3: asesoría con precio según el nivel del asesor."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # Multiplicador por nivel
    RECARGO_PRESENCIAL = 0.15  # Presencial cuesta 15 % más
    MIN_HORAS = 0.5  # Duración mínima de una asesoría

    def __init__(self, nombre_servicio, tarifa_base, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)
        self.especialidad = _texto_obligatorio(especialidad, "La especialidad es obligatoria.")
        self.nivel = str(nivel).strip().lower()
        if self.nivel not in self.NIVELES:  # Solo niveles definidos
            _fallar(ServicioInvalidoError, f"Nivel inválido '{self.nivel}'. Use: {', '.join(self.NIVELES)}.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, presencial=False):
        self.validar_parametros(horas, presencial=presencial)  # Valida antes de calcular
        subtotal = self._tarifa_base * self.NIVELES[self.nivel] * horas
        if presencial:  # Recargo por modalidad presencial
            subtotal *= 1 + self.RECARGO_PRESENCIAL
        return self._total(subtotal, impuesto, descuento)

    def validar_parametros(self, horas, presencial=False, **_):
        self._validar(horas)  # Disponibilidad y duración
        if horas < self.MIN_HORAS:  # Una asesoría dura mínimo media hora
            _fallar(ReservaInvalidaError, f"La asesoría debe durar al menos {self.MIN_HORAS} horas.")
        _exigir_bool(presencial, "presencial")  # La modalidad es sí/no

    def descripcion(self):
        return f"Asesoría de {self.especialidad} (nivel {self.nivel})."
