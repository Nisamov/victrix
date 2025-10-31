#!/usr/bin/python3

from pathlib import Path
from datetime import datetime
import sys
import subprocess
import time

# Fichero de configuracion
etc_ssp_conf = Path("/etc/ssp/ssp.conf")
if not etc_ssp_conf.exists():
    # Si la ruta no existe, advertencia al usuario
    print("Config file does not exist:", etc_ssp_conf)
    sys.exit(1) # Codigo de error salida 1 - Direccion no encontrada

# Pre carga de configuracion
def load_config(etc_ssp_conf):
    config = {}
    try:
        with open(etc_ssp_conf, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Detectar booleanos
                    if value.lower() == "true":
                        config[key] = True
                    elif value.lower() == "false":
                        config[key] = False
                    else:
                        # Intentar parsear como entero
                        try:
                            config[key] = int(value)
                        except ValueError:
                            # Si no es int, dejar como string
                            config[key] = value
    except Exception as e:
        print("Error reading config file:", e)
        sys.exit(2)
    return config

config = load_config(etc_ssp_conf)

check_interval = config.get("check_interval", 10)
purge_on_detect = config.get("purge_on_detect", False)
create_not_existing_dir = config.get("create_not_existing_dir", False)

check_interval = config.get("check_interval", 10) # Revisar el tiempo de espera
if not isinstance(check_interval, int) or check_interval <= 0:
    print(f"Invalid check_interval '{check_interval}', setting to default 10.")
    check_interval = 10 # Se establece 10 si no es un entero positivo
print("check_interval", check_interval, "purge_on_detect" , purge_on_detect)

# Fichero de servicios permitidos
# Si el directorio existe, se comprueba que en su interior existe el fichero que alberga los servicios pemritidos
lib_systemd_system_deb_services = Path("/usr/sbin/ssp_files/deb_services")
if not lib_systemd_system_deb_services.exists():
    # Si la ruta no existe, advertencia al usuario
    print("[CRITICAL ERROR] File does not exist:", lib_systemd_system_deb_services)
    sys.exit(1) # Codigo de error salida 1 - Direccion no encontrada

# Fichero ssp,service
lib_systemd_system_ssp_service = Path("/usr/lib/systemd/system/ssp.service")
if not lib_systemd_system_ssp_service.exists():
    # Si la ruta no existe, advertencia al usuario
    print("[WARNING] File does not exist:", lib_systemd_system_ssp_service)
    #sys.exit(1) # Codigo de error salida 1 - Direccion no encontrada

# Directorio de logs del sistema
var_log_deb = Path("/var/log/ssp")
if not var_log_deb.exists():
    # Si la ruta no existe, advertencia al usuario
    print("[WARNING] File does not exist:", var_log_deb)
    if create_not_existing_dir: # Si la configuracion lo permite, crea directorio
        try:
            var_log_deb.mkdir(parents=True, exist_ok=True)
            print(f"Directory created: {var_log_deb}")
        except PermissionError:
            print(f"Permission denied: Cannot create directory {var_log_deb}. Run as root?")
            sys.exit(1)
    else:
        print("create_not_existing_dir is False, exiting.")
        sys.exit(1)

# Bucle de comprobacion de servicios en el sistema
while True:
    try:
        # Leer el fichero de servicios
        with open(lib_systemd_system_deb_services, "r") as f:
            allowed_services = [line.strip() for line in f if line.strip()]
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--state=active", "--no-legend", "--no-pager"],
            capture_output=True, text=True
        )
        active_services = [line.split()[0] for line in result.stdout.splitlines()]
        # Comprobar qué servicios activos no están en el fichero
        extras = [s for s in active_services if s not in allowed_services]

        if extras:
            print("Services extra detected:", extras)
            if purge_on_detect == True:
                print("Purging extra services...")
                # Crear nombre del archivo log

            ##########################################
            # Generar log por dia, al terminar el dia, se genera un nuevo log (solo si se han detectado servicios que eliminar)

                now = datetime.now()
                log_filename = var_log_deb / now.strftime("%Y_%m_%d_%H_%M.log")
                with open(log_filename, "a") as log_file:
                    for service in extras:
                        try:
                            subprocess.run(["systemctl", "stop", service], check=True)
                            subprocess.run(["systemctl", "disable", service], check=True)
                            print(f"Service {service} stopped and disabled.")
                            result_path = subprocess.run(
                                ["systemctl", "show", service, "-p", "FragmentPath"],
                                capture_output=True, text=True, check=True
                            )
                            ruta_servicio = result_path.stdout.strip().split('=', 1)[1] if '=' in result_path.stdout else "Unknown"
                            log_file.write(f"stopped/{service}/{ruta_servicio}\n")
                        except subprocess.CalledProcessError as e:
                            print(f"Failed to stop or disable service {service}: {e}")

            ##########################################

            else:
                print(f"Services to be stopped found but config 'purge_on_detect' = {purge_on_detect}.")
        else:
            print("No extra services found.")
        time.sleep(check_interval) # Tiempo de espera predefinido por la configuracion
    except Exception as e:
        print("Something went wrong:", e)
        sys.exit(3)  # Codigo de error salida 3 - Error en la ejecucion