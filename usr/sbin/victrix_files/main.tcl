#!/usr/bin/tclsh
set conf_file "/etc/victrix/victrix.conf"
proc revisar_config {} {
    global conf_file
    set intervalo 5;
    if {[file exists $conf_file]} {
        # Uso de catch para la salida de errores
        if {[catch {source $conf_file} err]} {
            puts "Error al leer el archivo: $err"
        }     
        # Verficiacion de existencia 'intervalo'
        if {![info exists intervalo]} {
            puts "Aviso: 'intervalo' no definido en $conf_file. Usando 5s."
            set intervalo 5
        }
        puts "\[[clock format [clock seconds] -format %H:%M:%S]\] Revisando config... Próxima en: $intervalo s"
    } else {
        puts "Error: Fichero $conf_file inexistente. Usando 5s por defecto."
        set intervalo 5
    }
    flush stdout
    set ms [expr {$intervalo * 1000}]
    after $ms revisar_config
}
puts "Iniciando monitor de configuración..."
flush stdout
revisar_config
vwait forever