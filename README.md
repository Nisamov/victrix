![Presetación Servicio](_repo/_media/SecureServiceProtocol.jpg)

# Secure Service Protocol
Este software permite controlar el estado de los servicios en tu equipo Debian.
Puede ser peligroso si se configura de una mala manera.

## Instalación

Para descargar el software, ve a [releases](https://github.com/Nisamov/ssp/releases) y descárgate el paquete en el equipo, o ejecuta el siguiente comando desde la terminal:
```sh
sudo apt install git -y && git clone https://github.com/Nisamov/ssp
```

![Instalacion de Repositorio](_repo/_media/paso_sub1.png)

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

![Instalacion completada](_repo/_media/paso_sub2.gif)

Finalmente iniciamos el servicio con:
```sh
sudo systemctl start ssp.service
```
Y revisamos su estado con:
```
sudo systemctl status ssp.service
```

![Revisión de estado](_repo/_media/paso_sub3.png)

Si se realiza algún cambio durante su ejecución, se recomienda reiniciar el servicio:
```sh
sudo systemctl restart ssp.service
```

## Rutas
Las rutas usadas del software son:
- `/etc/ssp.conf` Contiene la configuración del servicio.
- `/lib/systemd/system/ssp.service` Servicio Secure Service Protocol

## Configuración
Para que el servicio pueda leer y aplicar la configuración establecida, es necesario reiniciar el servicio, pues este, lee durante su arranque, la configuración.
No obstante, lee activamente los ficheros de los servicios permitidos en el sistema.

**Fichero /etc/ssp.conf**
```sh
apache2.service yes
nginx.service yes
mysql.service no
sshd.service no
```

## Configurción Seguridad del Servicio
```sh
ExecStart=/usr/sbin/ssp_daemon.py
WorkingDirectory=/usr/sbin
User=ssp
Group=ssp

ProtectSystem=full
ReadWritePaths=/var/log/ssp
ProtectHome=read-only
PrivateTmp=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictRealtime=yes
```

## Estructura
```
ssp
├── DEBIAN
│   ├── control
│   ├── postinst
│   ├── preinst
│   └── prerm
├── LICENSE
├── README.md
├── _repo
│   └── _media
│       ├── SecureServiceProtocol.jpg
│       ├── paso_sub1.png
│       ├── paso_sub2.gif
│       └── paso_sub3.png
├── etc
│   ├── polkit-1
│   │   └── rules
│   │       └── 10-ssp.rules
│   └── ssp
│       └── ssp.conf
├── lib
│   └── systemd
│       └── system
│           └── ssp.service
└── usr
    ├── sbin
    │   ├── ssp
    │   └── ssp_daemon.py
    └── share
        └── man
            └── man8
                └── ssp.8
```