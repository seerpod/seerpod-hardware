#!/bin/bash

while [ 1 ]
do
	echo "Getting disk usage."

	diskUsage=$(df -h | head -2 | tail -1)
	usediDiskPercent=$(echo $diskUsage | awk '{print $5}')
	availDisk=$(echo $diskUsage | awk '{print $4}')
	usedDisk=$(echo $diskUsage | awk '{print $3}')
	totalDisk=$(echo $diskUsage | awk '{print $2}')

	echo "Collected disk usage.\nGetting memory usage."

	memUsage=$(free -m | head -2 | tail -1)
	usedMem=$(echo $memUsage | awk '{print $3}')
	availMem=$(echo $memUsage | awk '{print $4}')
	totalMem=$(echo $memUsage | awk '{print $2}')
	usedMemPercent=$(($usedMem*100/$totalMem))
	
	echo "Collected memory usage.\nGetting CPU usage."
	
	cpuUsage=$(top -bn2 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}' | tail -1)

	echo "Collected CPU usage.\nSending the stats to Seerpod server."

	echo "{\"seerpod.id\":\"uid12345\",\"business.id\":\"cust-abcd\",\"disk.stats\":{\"total.disk\":\"$totalDisk\",\"used.disk\":\"$usedDisk\",\"available.disk\":\"$availDisk\",\"used.percent\":\"$usedDiskPercent\"},\"mem.stats\":{\"total.mem\":\"$totalMem\",\"used.mem\":\"$usedMem\",\"available.mem\":\"$availMem\",\"used.percent\":\"$usedMemPercent\"},\"cpu.stats\":{\"cpu.used\":\"$cpuUsage\"}}"
	sleep 10
done
