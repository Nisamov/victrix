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
# Opciones de configuracion (leer solo al inicio como indica funcionamiento.md)
check_interval = config.get("check_interval", 10)
purge_on_detect = config.get("purge_on_detect", False)
create_not_existing_dir = config.get("create_not_existing_dir", False)
# Permite o no detener servicios importantes del sistema (false por defecto)
allow_stop_important = config.get("allow_stop_important", False)
# Directorio de logs (puede configurarse)
log_dir = Path(config.get("log_dir", "/var/log/ssp"))

if not isinstance(check_interval, int) or check_interval <= 0:
    print(f"Invalid check_interval '{check_interval}', setting to default 10.")
    check_interval = 10 # Se establece 10 si no es un entero positivo

print("check_interval", check_interval, "purge_on_detect", purge_on_detect, "allow_stop_important", allow_stop_important)

# Fichero de servicios permitidos
# Si el directorio existe, se comprueba que en su interior existe el fichero que alberga los servicios pemritidos
lib_systemd_system_deb_services = Path("/usr/sbin/ssp_files/deb_services")
if not lib_systemd_system_deb_services.exists():
    # Si la ruta no existe, advertencia al usuario
    print("[CRITICAL ERROR] File does not exist:", lib_systemd_system_deb_services)
    sys.exit(1) # Codigo de error salida 1 - Direccion no encontrada
# Fichero ssp,service (advertencia si falta)
lib_systemd_system_ssp_service = Path("/usr/lib/systemd/system/ssp.service")
if not lib_systemd_system_ssp_service.exists():
    # Si la ruta no existe, advertencia al usuario
    print("[WARNING] File does not exist:", lib_systemd_system_ssp_service)
    #sys.exit(1) # Codigo de error salida 1 - Direccion no encontrada

# Preparar directorio de logs
var_log_deb = log_dir
if not var_log_deb.exists():
    # Si la ruta no existe, advertencia al usuario
    print("[WARNING] Log directory does not exist:", var_log_deb)
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

# Servicios criticos protegidos por defecto (no detener salvo que allow_stop_important=True)
DEFAULT_CRITICAL_SERVICES = {
    "ssp.service",
    "sshd.service",
    "systemd-journald.service",
    "systemd-logind.service",
    "dbus.service",
    "NetworkManager.service",
    "systemd-resolved.service",
    "rsyslog.service",
    "cron.service",
    "systemd-udevd.service",
    "systemd-networkd.service",
}

# Log helpers
def daily_log_path(base_dir: Path) -> Path:
    now = datetime.now()
    return base_dir / now.strftime("%Y_%m_%d.log")

alerts_log = log_dir / "alerts.log"

# Bucle de comprobacion de servicios en el sistema
while True:
    try:
        # Leer el fichero de servicios permitidos
        with open(lib_systemd_system_deb_services, "r") as f:
            allowed_services = [line.strip() for line in f if line.strip()]

        # Obtener servicios activos
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=active", "--no-legend", "--no-pager"],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print("Failed to query systemctl:", e)
            time.sleep(check_interval)
            continue

        active_services = [line.split()[0] for line in result.stdout.splitlines() if line.strip()]

        # Determinar servicios extra (activos pero no permitidos)
        extras = [s for s in active_services if s not in allowed_services]

        # Siempre generar un log diario indicando los extras detectados (aunque no se purgue)
        if extras:
            print("Services extra detected:", extras)
            logfile = daily_log_path(log_dir)
            with open(logfile, "a") as lf:
                timestamp = datetime.now().isoformat()
                lf.write(f"[{timestamp}] Detected extra services: {extras}\n")

        else:
            print("No extra services found.")

        # Manejar alertas por servicios importantes presentes en extras
        important_found = [s for s in extras if s in DEFAULT_CRITICAL_SERVICES]
        if important_found:
            # Registrar alerta
            with open(alerts_log, "a") as af:
                timestamp = datetime.now().isoformat()
                af.write(f"[{timestamp}] IMPORTANT services detected: {important_found}\n")
            print("IMPORTANT services detected (logged to alerts):", important_found)

        # Si la configuracion indica purgar, intentar detener/deshabilitar los extras
        if extras and purge_on_detect:
            print("Purging extra services...")
            logfile = daily_log_path(log_dir)
            with open(logfile, "a") as lf:
                for service in extras:
                    # Si el servicio es critico y no está permitido detenerlo, saltarlo y alertar
                    if (service in DEFAULT_CRITICAL_SERVICES) and not allow_stop_important:
                        lf.write(f"{datetime.now().isoformat()} SKIP critical/{service}\n")
                        with open(alerts_log, "a") as af:
                            af.write(f"{datetime.now().isoformat()} SKIPPED stopping critical service: {service}\n")
                        print(f"Skipping critical service {service} (allow_stop_important={allow_stop_important})")
                        continue

                    try:
                        subprocess.run(["systemctl", "stop", service], check=True)
                        subprocess.run(["systemctl", "disable", service], check=True)
                        # Obtener ruta del unit si es posible
                        try:
                            result_path = subprocess.run([
                                "systemctl", "show", service, "-p", "FragmentPath"
                            ], capture_output=True, text=True, check=True)
                            ruta_servicio = result_path.stdout.strip().split('=', 1)[1] if '=' in result_path.stdout else "Unknown"
                        except subprocess.CalledProcessError:
                            ruta_servicio = "Unknown"

                        lf.write(f"{datetime.now().isoformat()} STOPPED/{service}/{ruta_servicio}\n")
                        print(f"Service {service} stopped and disabled.")
                    except subprocess.CalledProcessError as e:
                        lf.write(f"{datetime.now().isoformat()} FAILED/{service}/{e}\n")
                        print(f"Failed to stop or disable service {service}: {e}")
        elif extras:
            print(f"Services to be stopped found but config 'purge_on_detect' = {purge_on_detect}.")

        time.sleep(check_interval)

    except Exception as e:
        print("Something went wrong:", e)
        # Registrar error crítico en alerts
        try:
            with open(alerts_log, "a") as af:
                af.write(f"{datetime.now().isoformat()} ERROR main loop: {e}\n")
        except Exception:
            pass
        sys.exit(3)