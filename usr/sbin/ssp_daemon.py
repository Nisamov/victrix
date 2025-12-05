#!/usr/bin/env python3
import subprocess
import time
import logging

CONFIG_FILE = "/etc/ssp/ssp.conf"
CHECK_INTERVAL = 5  # segundos

# Configuración de logging
logging.basicConfig(
    filename="/var/log/ssp/ssp.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_config():
    """Carga el fichero ssp.conf en un diccionario {servicio: 'yes'|'no'}"""
    config = {}
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    config[parts[0]] = parts[1].lower()
    except Exception as e:
        logging.error(f"Error leyendo {CONFIG_FILE}: {e}")
    return config

def list_active_services():
    """Lista todos los servicios activos usando systemctl"""
    try:
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--no-legend", "--no-pager"],
            capture_output=True, text=True, check=True
        )
        services = []
        for line in result.stdout.splitlines():
            fields = line.split()
            if fields:
                services.append(fields[0])
        return services
    except Exception as e:
        logging.error(f"Error listando servicios: {e}")
        return []

def stop_service(service):
    """Intenta detener un servicio usando systemctl (Polkit gestiona permisos)"""
    try:
        subprocess.run(["systemctl", "stop", service], check=True)
        logging.info(f"Servicio detenido: {service}")
    except subprocess.CalledProcessError as e:
        logging.warning(f"No se pudo detener {service}: {e}")
    except Exception as e:
        logging.error(f"Error al detener {service}: {e}")

def main_loop():
    logging.info("SSP daemon iniciado")
    while True:
        config = load_config()
        services = list_active_services()
        for srv in services:
            # Consultar configuración: solo detener si config indica 'yes'
            if config.get(srv) == "yes":
                stop_service(srv)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
