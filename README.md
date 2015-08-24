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
	sudo service counter (start|stop|status|restart)

Command to run counter.py standalone
------------------------------------
1. To run on a sample video:
	python counter.py -vt "file" -vs "images/Video2-short.mp4"
2. To run on live camera feed:
	python counter.py
	(uses -vt=stream and -vt=0)
3. To adjust log levels:
	python counter.py -vt "file" -vs "images/Video2-short.mp4" -ll "warn"
	(log levels can be info/debug/warn/error/critical)