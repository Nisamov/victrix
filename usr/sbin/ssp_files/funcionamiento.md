El servicio tiene que poder:
- Leer la ruta de configuracion y aplicar los cambios en tiempo real (solo leera al inicio del servicio mismo, de esta forma evito que haya problemas)
- Detener servicios
- Deshabilitar servicios
- Generar un .log de los servicios no habilitados detectados
    - De estos detectados: Si la configuracion indica que se tumben todos los servicios forzosamente, tumbará hasta los servicios no deseados del sistema.
    - Habrá una comparacion para buscar servicios que puedan ser importantes y generará una alerta.

En la configuracion deberá haber:
-- - Ruta de output logs: /var/log/ssp/<logs.log> -- igual no
- Activar o desactivar la detención de servicios clave (importantes para el sistema) [true/false]

En el shell ssp debe contener:
- Funcion de desinstalar el programa
- Funcion de ayuda
- Funcion de version