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

Otorgar permiso de ejecución al fichero `/lib/systemd/system/ssp.service` con:
```sh
sudo chmod 755 /lib/systemd/system/ssp.service
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
> /usr/local/sbin/ssp_files -> Contiene los ficheros generales del servicio.
> /etc/ssp.conf -> Contiene la configuración del servicio.
> /lib/systemd/system/ssp.service -> Servicio Secure Service Protocol

## Configuración
Para que el servicio pueda leer y aplicar la configuración establecida, es necesario reiniciar el servicio, pues este, lee durante su arranque, la configuración.
No obstante, lee activamente los ficheros de los servicios permitidos en el sistema.

## Comandos
SSP cuenta con comandos de terminal para poder administrar con mayor facilidad el servicio.

```
.
├── DEBIAN
│   ├── control
│   ├── postinst
│   └── prerm
├── _repo
│   └── _media
│       └── SecureServiceProtocol.jpg
├── etc
│   └── ssp
│       └── ssp.conf
├── lib
│   └── systemd
│       └── system
│           └── ssp.service
├── usr
│   └── sbin
│       ├── ssp
│       └── ssp_files
│           ├── deb_services
│           ├── funcionamiento.md
│           └── service.py
└── var
    └── log
        └── ssp
            └── iexist
```