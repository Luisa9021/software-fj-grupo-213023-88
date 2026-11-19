"""Simulación principal de Software FJ (Grupo 213023_88 - Fase 4).

Ejecuta 16 operaciones secuenciales (válidas e inválidas) para demostrar que
el sistema maneja errores sin detenerse y deja todo registrado en
logs/software_fj.log.
"""

# ---------------------------------------------------------------------------
# Importaciones
# ---------------------------------------------------------------------------
# Excepciones personalizadas (excepciones.py)
from excepciones import SoftwareFJError, ReservaInvalidaError

# Registro de eventos (logger.py); se importa primero para configurar el log
from logger import (
    registrar_evento,        # Operación exitosa (INFO)
    registrar_advertencia,   # Situación no crítica (WARNING)
    registrar_error,         # Error controlado (ERROR)
    registrar_excepcion,     # Error inesperado con traceback completo
)

from modelos.cliente import Cliente                 # Clase Cliente
from servicios import (                             # Servicios especializados
    ReservaSala,
    AlquilerEquipo,
    AsesoriaEspecializada,
)
try:
    from reserva import Reserva                     # Clase Reserva (si está en la raíz)
except ImportError:
    from modelos.reserva import Reserva             # Clase Reserva (si está en modelos/)


# ---------------------------------------------------------------------------
# Funciones de apoyo
# ---------------------------------------------------------------------------
def convertir_duracion(texto):
    """Convierte un texto a horas enteras; encadena el error original."""
    try:
        # Intenta convertir el texto recibido a número entero
        return int(texto)
    except ValueError as error:
        # Encadenamiento: 'from error' conserva la causa original
        raise ReservaInvalidaError(
            f"La duración '{texto}' no es un número válido"
        ) from error


def ejecutar_operacion(numero, descripcion, funcion):
    """Ejecuta una operación con try/except/else/finally.

    Nunca deja escapar una excepción, así la simulación continúa siempre.
    Devuelve el resultado de la operación, o None si falló.
    """
    # Encabezado visible en consola para seguir la simulación
    print(f"\n[{numero:02d}] {descripcion}")
    resultado = None
    try:
        # Intenta ejecutar la operación recibida
        resultado = funcion()
    except SoftwareFJError as error:
        # Error propio del sistema: controlado, se registra y se continúa
        registrar_error(f"Operación {numero} ({descripcion}) falló: {error}")
        # Si el error trae una causa encadenada, se deja constancia
        if error.__cause__ is not None:
            registrar_advertencia(f"Causa original: {error.__cause__!r}")
        print(f"     ERROR CONTROLADO: {error}")
    except Exception as error:  # Error no previsto por el sistema
        # Se guarda el traceback completo para depurar después
        registrar_excepcion(error)
        print(f"     ERROR INESPERADO ({type(error).__name__}): {error}")
    else:
        # Solo se ejecuta si NO hubo excepción
        registrar_evento(f"Operación {numero} ({descripcion}) exitosa")
        print("     OK")
    finally:
        # Se ejecuta siempre, haya o no error
        registrar_evento(f"Operación {numero} finalizada")
    return resultado


# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------
def main():
    """Ejecuta las 16 operaciones de la simulación."""
    registrar_evento("===== INICIO DE LA SIMULACIÓN =====")
    print("=== Simulación Software FJ ===")

    # Listas donde se guardan los objetos creados con éxito
    clientes, servicios, reservas = [], [], []

    # --- 1: cliente válido (documento, nombre, correo, teléfono) ----------
    c1 = ejecutar_operacion(
        1, "Crear cliente válido",
        lambda: Cliente("1001234567", "Ana Torres", "ana@correo.com", "3001234567"))
    if c1:
        clientes.append(c1)

    # --- 2: correo sin arroba ---------------------------------------------
    ejecutar_operacion(
        2, "Crear cliente con correo inválido",
        lambda: Cliente("1002345678", "Luis Pérez", "correo-sin-arroba", "3009876543"))

    # --- 3: documento con letras ------------------------------------------
    ejecutar_operacion(
        3, "Crear cliente con documento no numérico",
        lambda: Cliente("ABC123", "Pedro Ruiz", "pedro@correo.com", "3005550000"))

    # --- 4: segundo cliente válido ----------------------------------------
    c2 = ejecutar_operacion(
        4, "Crear segundo cliente válido",
        lambda: Cliente("1003456789", "Marta Gómez", "marta@correo.com", "3112223344"))
    if c2:
        clientes.append(c2)

    # --- 5: sala válida (nombre, tarifa, capacidad) -----------------------
    s1 = ejecutar_operacion(
        5, "Crear servicio ReservaSala válido",
        lambda: ReservaSala("Sala A", 50000, 10))
    if s1:
        servicios.append(s1)

    # --- 6: equipo con tarifa negativa ------------------------------------
    ejecutar_operacion(
        6, "Crear AlquilerEquipo con tarifa negativa",
        lambda: AlquilerEquipo("Proyector", -1000, "Video"))

    # --- 7: asesoría válida (nombre, tarifa, especialidad) ----------------
    s2 = ejecutar_operacion(
        7, "Crear AsesoriaEspecializada válida",
        lambda: AsesoriaEspecializada("Asesoría Python", 80000, "Programación"))
    if s2:
        servicios.append(s2)

    # --- 8: reserva válida y cálculo polimórfico del costo ----------------
    if clientes and servicios:
        r1 = ejecutar_operacion(
            8, "Crear reserva válida (cliente 1, sala A, 2 horas)",
            lambda: Reserva(clientes[0], servicios[0], 2))
        if r1:
            reservas.append(r1)
            # El servicio calcula su costo: 19 % de impuesto y 10 % de descuento
            ejecutar_operacion(
                9, "Calcular costo de la reserva (impuesto 19 %, descuento 10 %)",
                lambda: servicios[0].calcular_costo(2, impuesto=0.19, descuento=0.10))

    # --- 10: duración no numérica (excepción encadenada) ------------------
    if clientes and servicios:
        ejecutar_operacion(
            10, "Reserva con duración 'abc' (encadenamiento)",
            lambda: Reserva(clientes[0], servicios[0], convertir_duracion("abc")))

    # --- 11: duración cero -------------------------------------------------
    if clientes and servicios:
        ejecutar_operacion(
            11, "Reserva con duración 0",
            lambda: Reserva(clientes[-1], servicios[-1], 0))

    # --- 12: sala con más personas que su capacidad -----------------------
    if servicios:
        ejecutar_operacion(
            12, "Sala con 50 personas (capacidad 10)",
            lambda: servicios[0].calcular_costo(2, personas=50))

    # --- 13: servicio no disponible ---------------------------------------
    if len(servicios) > 1:
        def usar_no_disponible():
            """Marca la asesoría como no disponible y trata de cotizarla."""
            servicios[1].disponible = False
            try:
                return servicios[1].calcular_costo(1)
            finally:
                # Se restablece siempre, falle o no la cotización
                servicios[1].disponible = True

        ejecutar_operacion(13, "Cotizar servicio no disponible", usar_no_disponible)

    # --- 14: descuento fuera de rango -------------------------------------
    if servicios:
        ejecutar_operacion(
            14, "Cotizar con descuento del 150 %",
            lambda: servicios[0].calcular_costo(2, descuento=1.5))

    # --- 15: confirmar reserva válida (camino de éxito) -------------------
    if reservas:
        ejecutar_operacion(
            15, "Confirmar reserva válida", reservas[0].confirmar_reserva)

    # --- 16: cancelar y luego confirmar (operación no permitida) ----------
    if reservas:
        def cancelar_y_confirmar():
            """Cancela la reserva y luego intenta confirmarla (debe fallar)."""
            reservas[0].cancelar_reserva()
            reservas[0].confirmar_reserva()

        ejecutar_operacion(
            16, "Confirmar una reserva ya cancelada", cancelar_y_confirmar)

    # --- Resumen final ----------------------------------------------------
    registrar_evento(
        f"Resumen: {len(clientes)} clientes, {len(servicios)} servicios, "
        f"{len(reservas)} reservas creadas")
    registrar_evento("===== FIN DE LA SIMULACIÓN =====")
    print("\n=== Fin. Revise logs/software_fj.log ===")


# Punto de entrada: solo se ejecuta al correr 'python main.py'
if __name__ == "__main__":
    main()
