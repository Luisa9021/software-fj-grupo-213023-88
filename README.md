# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto colaborativo del curso **Programación (213023)** - UNAD. Fase 4: manejo de excepciones en aplicaciones orientadas a objetos.

**Grupo:** 213023_88

## Descripción
Sistema en Python con Programación Orientada a Objetos, sin base de datos. Gestiona clientes, servicios y reservas mediante objetos y listas, y registra eventos y errores en un archivo de logs.

## Reparto del trabajo

| Integrante | Archivo | Estado |
|---|---|---|
| Luisa Viviana Rueda Ayala (Luisa9021) | `excepciones.py` y `logger.py` | Listo |
| Jorge Castaño (jorgecaasta17-rgb) | `modelos/entidades.py`: clase abstracta `Entidad` y `modelos/cliente.py`: clase `Cliente` | En revisión |
| (pendiente) | `servicios.py`: clase abstracta `Servicio` y 3 servicios especializados | Pendiente |
| Valeria Daniel Sisa (valeriadaniel17) | `reserva.py`: clase `Reserva` con estados | Asignado |
| (pendiente) | `main.py`: simulación de 10 operaciones o más | Pendiente |

## Estructura del proyecto

```
software-fj-grupo-213023-88/
├── main.py            # Simulación de 10 operaciones o más (pendiente)
├── excepciones.py     # Excepciones personalizadas
├── logger.py          # Registro de eventos y errores
├── servicios.py       # Servicio y 3 servicios especializados (pendiente)
├── reserva.py         # Reserva con estados (asignado)
├── logs/
│   └── software_fj.log   # Se genera al ejecutar el programa
└── modelos/
    ├── __init__.py    # Convierte la carpeta en paquete de Python
    ├── entidades.py   # Clase abstracta Entidad
    └── cliente.py     # Clase Cliente
```

## Cómo participar
1. Aceptar la invitación de colaborador que llega al correo de GitHub.
2. Crear el archivo que le corresponde con **Add file → Create new file**.
3. Documentar cada línea del código con comentarios.
4. Guardar con un commit de mensaje claro, por ejemplo: `Agregar clase Cliente`.
5. Actualizar su nombre en la tabla de arriba.

## Cómo ejecutarlo
1. Instalar Python 3.
2. Descargar el proyecto y abrir una terminal en la carpeta.
3. Ejecutar: `python main.py`
4. Revisar el archivo `logs/software_fj.log`.
