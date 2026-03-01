#!/usr/bin/tclsh
set conf_file "/etc/victrix/victrix.conf"
proc revisar_config {} {
    global conf_file
    # Leer el archivo de configuración
    if {[file exists $conf_file]} {
        source $conf_file
        puts "\[[clock format [clock seconds] -format %H:%M:%S]\] Revisando config... Próxima revisión en: $intervalo segundos"
    } else {
        puts "Error: No encuentro el fichero $conf_file. Usando 5 segundos por defecto."
        set intervalo 5
    }
    # Convertir segundos a milisegundos
    set ms [expr {$intervalo * 1000}]
    # Volver a ejecutar esta misma función
    after $ms revisar_config
}
# Iniciar el primer ciclo
revisar_config
# Mantener el proceso activo
vwait forever