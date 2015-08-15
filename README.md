# Hardware related code which will be deployed in Rasp Pi or any other compatible Hardware.

Instructions to build debian package
------------------------------------
1. Clone the repository.
2. Run "dpkg-deb --build seerpod_1.0-1" from outside the "seerpod_1.0-1" directory and "seerpod_1.0-1.deb" package will be created.

Installation
------------
Run "sudo apt-get install seepod".

Installation Directory
---------------------
/opt/seerpod
	init.d - contains all seerpod services
	scripts - contains all seerpod system and service scripts
	logs - contains all logs from seerpod services and scripts
	run - comtains pid files for all seerpod services
	conf - contains seerpod configuration files

Services
--------
1. HealthCheck service
	sudo service health (start|stop|status|restart)
2. Counter service
	sudo service health (start|stop|status|restart)
