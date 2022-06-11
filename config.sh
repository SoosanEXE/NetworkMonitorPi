echo -e "IP\tMAC\tNAME" > ips.txt
sudo arp-scan -l | grep -P '^[\d.]+' | head -n -1 >> ips.txt