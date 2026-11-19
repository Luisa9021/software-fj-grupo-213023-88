Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto colaborativo del curso Programación (213023) - UNAD. Fase 4: manejo de excepciones en aplicaciones orientadas a objetos.

Grupo: 213023_88

Descripción

Sistema en Python con Programación Orientada a Objetos, sin base de datos. Gestiona clientes, servicios y reservas mediante objetos y listas, y registra eventos y errores en un archivo de logs.

Reparto del trabajo
Integrante	Archivo	Estado
Luisa Viviana Rueda Ayala (Luisa9021)	excepciones.py y logger.py	Listo
Jorge Castaño (jorgecaasta17-rgb)	modelos/entidades.py: clase abstracta Entidad y modelos/cliente.py: clase Cliente	Listo
Mauricio Ramírez (Mmaupp)	servicios.py: clase abstracta Servicio y 3 servicios especializados	Listo
Valeria Daniel Sisa (valeriadaniel17)	reserva.py: clase Reserva con estados	Listo
Dayan de Jesus Wilches Lozano (SrJungler)	main.py: simulación de 16 operaciones (válidas e inválidas).	Asignado
Estructura del proyecto
software-fj-grupo-213023-88/
├── main.py            # Simulación de 16 operaciones
├── excepciones.py     # Excepciones personalizadas
├── logger.py          # Registro de eventos y errores
├── servicios.py       # Servicio y 3 servicios especializados
├── reserva.py         # Reserva con estados
├── logs/
│   └── software_fj.log   # Se genera al ejecutar el programa
└── modelos/
    ├── entidades.py   # Clase abstracta Entidad
    └── cliente.py     # Clase Cliente
Conceptos aplicados
Abstracción: clases abstractas Entidad y Servicio.
Herencia y polimorfismo: Cliente y los servicios heredan de Entidad; cada servicio calcula su costo a su manera.
Encapsulación: atributos protegidos o privados con validación en propiedades.
Excepciones personalizadas: jerarquía que parte de SoftwareFJError.
Bloques de control: try/except, try/except/else y try/except/finally.
Encadenamiento: raise ... from ... para conservar la causa original.
Logs: eventos y errores registrados en logs/software_fj.log sin detener la ejecución.
Cómo ejecutarlo
Instalar Python 3.
Descargar el proyecto y abrir una terminal en la carpeta raíz.
Ejecutar: python main.py
Revisar el archivo logs/software_fj.log.
Resultado de la simulación

main.py ejecuta 16 operaciones seguidas. Las 7 operaciones con datos válidos terminan con éxito y las 9 con datos inválidos (correo sin arroba, documento con letras, tarifa negativa, duración abc o cero, sala con exceso de personas, servicio no disponible, descuento del 150 % y confirmar una reserva cancelada) se controlan con excepciones personalizadas. El programa no se detiene y todo queda registrado en logs/software_fj.log.
