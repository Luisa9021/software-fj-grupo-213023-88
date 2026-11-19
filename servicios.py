from abc import abstractmethod  # Sirve para marcar los métodos que cada hijo está obligado a escribir

from modelos.entidades import Entidad  # Clase base del sistema: de ella heredan clientes, servicios y reservas
from excepciones import (ParametroFaltanteError, ServicioInvalidoError,
                         ServicioNoDisponibleError, ReservaInvalidaError,
                         CalculoInconsistenteError)  # Excepciones propias del proyecto
from logger import registrar_evento, registrar_error  # Para dejar todo registrado en el archivo de logs

MAX_HORAS = 12  # Una sola reserva no puede pasar de 12 horas


class Servicio(Entidad):
    """Clase abstracta: define lo que todo servicio debe tener y hacer.

    No se puede crear un Servicio directamente; solo sus hijos (sala, equipo y asesoría).
    """

    def __init__(self, nombre_servicio, tarifa_base, disponible=True):
      
        # Primero revisamos el nombre: sin nombre no podemos identificar el servicio,
        # así que lo registramos en el log y detenemos la creación con un error claro.
        if not nombre_servicio or not str(nombre_servicio).strip():
            registrar_error("Servicio sin nombre")
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
          
        # Luego revisamos la tarifa: tiene que ser un número mayor que cero.
        # En Python True y False también cuentan como números, por eso los rechazamos aparte.
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            registrar_error(f"Tarifa inválida en '{nombre_servicio}': {tarifa_base}")
            raise ServicioInvalidoError("La tarifa base debe ser un número mayor que cero.")
          
        # Con los datos ya validados, Entidad guarda el identificador (usamos el nombre)
        # y aquí guardamos los atributos propios. El guion bajo indica que son protegidos:
        # solo se leen desde afuera mediante las propiedades de abajo.
      
        super().__init__(str(nombre_servicio).strip())
        self._nombre_servicio = str(nombre_servicio).strip()  # Nombre del servicio, sin espacios sobrantes
        self._tarifa_base = float(tarifa_base)  # Lo que cuesta cada hora del servicio
        self.disponible = disponible  # Pasa por el setter de abajo, que valida que sea True o False

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
        # Solo aceptamos True o False; así nadie puede dejar el servicio en un estado raro
        # (por ejemplo "si" o 5) que luego cause errores difíciles de encontrar.
      
        if not isinstance(valor, bool):
            registrar_error(f"Disponibilidad inválida en '{self._nombre_servicio}': {valor}")
            raise ServicioInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = valor
        registrar_evento(f"Servicio '{self._nombre_servicio}' disponible={valor}")  # Queda el cambio en el log

    def verificar_disponibilidad(self):
        """Lanza error si el servicio no está disponible."""
        # Si el servicio está desactivado no se puede reservar ni calcular su costo.
        if not self._disponible:
            registrar_error(f"Servicio '{self._nombre_servicio}' no disponible")
            raise ServicioNoDisponibleError(f"El servicio '{self._nombre_servicio}' no está disponible.")

    def validar_duracion(self, horas):
        """Lanza error si las horas no son un número entre 0 y MAX_HORAS."""
        # Las horas deben ser un número real (no True/False), mayor que cero y sin pasar
        # el máximo permitido. Si algo falla, avisamos con un error de reserva inválida.
      
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or horas <= 0 or horas > MAX_HORAS:
            registrar_error(f"Duración inválida en '{self._nombre_servicio}': {horas}")
            raise ReservaInvalidaError(f"La duración debe estar entre 0 y {MAX_HORAS} horas.")

    def calcular_total(self, subtotal, impuesto, descuento):
        """Aplica descuento e impuesto (0.10 = 10 %) y devuelve el total."""
        try:
            # El descuento y el impuesto se manejan como fracciones: 0.10 significa 10 %.
            # Si vienen fuera del rango de 0 a 1, el cálculo no tendría sentido.
          
            if not 0 <= descuento <= 1 or not 0 <= impuesto <= 1:
                registrar_error(f"Descuento o impuesto inválido: {descuento}, {impuesto}")
                raise CalculoInconsistenteError("Descuento e impuesto deben estar entre 0 y 1.")
            # Primero se resta el descuento al subtotal y sobre ese resultado se suma el impuesto.
            total = round(subtotal * (1 - descuento) * (1 + impuesto), 2)
        except TypeError as error:
            # Si alguno de los datos no es un número (por ejemplo un texto), Python lanza TypeError.
            # Lo convertimos en nuestro error propio y usamos "from error" para encadenarlos:
            # así no se pierde la causa original y se puede ver en el seguimiento del error.
          
            registrar_error(f"Datos no numéricos en el cálculo de '{self._nombre_servicio}': {error}")
            raise CalculoInconsistenteError("Subtotal, descuento e impuesto deben ser números.") from error
        registrar_evento(f"Costo de '{self._nombre_servicio}': {total}")  # Dejamos constancia del cálculo
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
        # Arma un resumen en una línea: nombre, tarifa y la descripción propia de cada servicio.
        return f"Servicio: {self._nombre_servicio} | ${self._tarifa_base:,.0f}/hora | {self.descripcion()}"


class ReservaSala(Servicio):
    """Servicio 1: reserva de salas."""

    def __init__(self, nombre_servicio, tarifa_base, capacidad, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)  # Los datos comunes los valida Servicio
        self.capacidad = capacidad  # Pasa por el setter, que valida que sea un entero positivo

    @property
    def capacidad(self):
        """Máximo de personas de la sala."""
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        # La capacidad debe ser un número entero mayor que cero (y no True/False).
        # Validarla aquí protege tanto al crear la sala como si luego se quiere cambiar.
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            registrar_error(f"Capacidad inválida en '{self._nombre_servicio}': {valor}")
            raise ServicioInvalidoError("La capacidad debe ser un entero mayor que cero.")
        self._capacidad = valor

    def validar_parametros(self, horas, personas=1):
        self.verificar_disponibilidad()  # Que la sala esté disponible
        self.validar_duracion(horas)  # Que la duración sea razonable
        # Lo propio de la sala: no pueden entrar más personas de las que caben.
        if personas > self._capacidad:
            registrar_error(f"Capacidad excedida en '{self._nombre_servicio}': {personas}")
            raise ReservaInvalidaError(f"La sala admite máximo {self._capacidad} personas.")

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, personas=1):
        # Primero validamos todo; si algo está mal, se lanza el error y no se calcula nada.
        self.validar_parametros(horas, personas=personas)
        # Costo base = tarifa por hora x horas; el impuesto y el descuento son opcionales.
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Sala para hasta {self._capacidad} personas."


class AlquilerEquipo(Servicio):
    """Servicio 2: alquiler de equipos."""

    def __init__(self, nombre_servicio, tarifa_base, tipo_equipo, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)  # Los datos comunes los valida Servicio
        self.tipo_equipo = tipo_equipo  # Pasa por el setter, que valida que no esté vacío

    @property
    def tipo_equipo(self):
        """Tipo de equipo que se alquila."""
        return self._tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor):
        # Sin tipo de equipo no sabríamos qué se está alquilando, por eso es obligatorio.
        if not valor or not str(valor).strip():
            registrar_error(f"Equipo '{self._nombre_servicio}' sin tipo")
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = str(valor).strip()

    def validar_parametros(self, horas):
        self.verificar_disponibilidad()  # Que el equipo esté disponible
        self.validar_duracion(horas)  # Que la duración sea razonable

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        # Validamos antes de calcular para no devolver un costo de una reserva inválida.
        self.validar_parametros(horas)
        # Costo base = tarifa por hora x horas; el impuesto y el descuento son opcionales.
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Alquiler de {self._tipo_equipo}."


class AsesoriaEspecializada(Servicio):
    """Servicio 3: asesoría especializada."""

    def __init__(self, nombre_servicio, tarifa_base, especialidad, disponible=True):
        super().__init__(nombre_servicio, tarifa_base, disponible)  # Los datos comunes los valida Servicio
        self.especialidad = especialidad  # Pasa por el setter, que valida que no esté vacía

    @property
    def especialidad(self):
        """Especialidad de la asesoría."""
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor):
        # Una asesoría necesita saber de qué tema es, por eso la especialidad es obligatoria.
        if not valor or not str(valor).strip():
            registrar_error(f"Asesoría '{self._nombre_servicio}' sin especialidad")
            raise ParametroFaltanteError("La especialidad es obligatoria.")
        self._especialidad = str(valor).strip()

    def validar_parametros(self, horas):
        self.verificar_disponibilidad()  # Que la asesoría esté disponible
        self.validar_duracion(horas)  # Que la duración sea razonable

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        # Validamos antes de calcular para no devolver un costo de una reserva inválida.
        self.validar_parametros(horas)
        # Costo base = tarifa por hora x horas; el impuesto y el descuento son opcionales.
        return self.calcular_total(self._tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return f"Asesoría de {self._especialidad}."
