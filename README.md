# Secure Service Protocol
Este software permite controlar el estado de los servicios en tu equipo Debian.
Puede ser peligroso si se configura de una mala manera.

## Instalación

Para descargar el software, ve a [releases](https://github.com/Nisamov/ssp/releases) y descárgate el paquete en el equipo, o ejecuta el siguiente comando desde la terminal:
```sh
sudo apt install git -y && git clone https://github.com/Nisamov/ssp
```

Con el repositorio descargado, ejecuta el siguiente comando (ruta relativa):
```sh
sudo chmod 0755 ssp/DEBIAN/*
```
Los permisos deberian ser 0755 [0 usuario permisos rxw, 5 de grupos y 5 para otros]

Ahora monta el paquete `.deb`con:
```sh
dpkg-deb --build mi-paquete nombre-del-paquete.deb
```

Para instalarlo asegúrate de haberte descargado el fichero `.deb`del repositorio.
Tras descargarlo, ubicate en la ruta del fichero y ejecuta el siguiente comando:
```sh
sudo dpkg -i fichero.deb
```

Finalmente iniciamos el servicio con:
```sh
sudo systemctl start ssp.service
```
Y revisamos su estado con:
```
sudo systemctl status ssp.service
```

Si se realiza algún cambio durante su ejecución, se recomienda reiniciar el servicio:
```sh
sudo systemctl restart ssp.service
```

## Rutas
Las rutas usadas del software son:
- `/usr/local/sbin/ssp_files` Contiene los ficheros generales del servicio.
- `/etc/ssp.conf` Contiene la configuración del servicio.
- `/lib/systemd/system/ssp.service` Servicio Secure Service Protocol

## Configuración
Para que el servicio pueda leer y aplicar la configuración establecida, es necesario reiniciar el servicio, pues este, lee durante su arranque, la configuración.
No obstante, lee activamente los ficheros de los servicios permitidos en el sistema.

**Fichero /etc/ssp.conf**
```sh
## Seconds to wait before analyzing the services again
check_interval=15
## If enabled, the SSP will stop and unable the services
purge_on_detect=false
## If dir not found, create it
create_not_existing_dir=false
```

## Configurción Seguridad del Servicio
```sh
ProtectSystem=full
ProtectHome=yes
NoNewPrivileges=yes
PrivateTmp=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictRealtime=yes
CapabilityBoundingSet=CAP_SYS_ADMIN CAP_NET_ADMIN CAP_SYS_RESOURCE CAP_KILL
AmbientCapabilities=CAP_SYS_ADMIN CAP_NET_ADMIN CAP_SYS_RESOURCE CAP_KILL
```

## Estructura
```
.
├── DEBIAN
│   ├── control
│   ├── postinst
│   └── prerm
├── etc
│   └── ssp
│       └── ssp.conf
├── lib
│   └── systemd
│       └── system
│           └── ssp.service
├── usr
│   ├── sbin
│   │   ├── ssp
│   │   └── ssp_files
│   │       ├── deb_services
│   │       ├── funcionamiento.md
│   │       └── service.py
│   └── share
│       └── man
│           └── man8
│               └── ssp.8
└── var
    └── log
        └── ssp
            └── iexist
```