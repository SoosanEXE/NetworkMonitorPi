#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import sys
import pandas as pd
host = ""
cmd = ""
DEFAULT_LOG_FILE_NAME = 'log'
LOG_EXTENSION = '.csv'
SLEEP_DURATION = 1
HEADER = 'Time,IP,Status,Ping\n'

def ping_network(log_file):
    ip_df = pd.read_csv('ips.txt', sep='\t')
    
    for ip in ip_df['IP']:
        host_reachable = False
        ping_time = 0.0
        timestamp = time.asctime()

        # get network details from `ping`
        try:
            cmd = "ping -c 1 " + ip
            response = subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip().split('\n')[1]
            host_reachable = True
            # Split the line
            res_split = response.split()
            # Extract the details
            ping_time = float(res_split[7].split('=')[1])
        except:
            pass
        online= "Online" if host_reachable else "Offline"
        log_file.write('{},{},{},{}\n'.format(timestamp, ip, online, ping_time))
        log_file.flush()
        # sleep to avoid using unnessary resources
        time.sleep(SLEEP_DURATION)
        
def print_help():
    print('This program logs out network health.')
    print('The default log name is', str(DEFAULT_LOG_FILE_NAME + LOG_EXTENSION))
    print('Add your name as an argument to change the log name (####.csv where #### is the name given)')
    
    
if __name__ == '__main__':
    # Get the log path
    log_path = DEFAULT_LOG_FILE_NAME
    args = sys.argv[1:]
    t = time.asctime()
    print("Running health checks at " + t)
    if len(args) > 0:
        if args[0] == '-h':
            print_help()
            quit()
        log_path = args[0]
    log_path += LOG_EXTENSION
    # Try to open the file - if it doesn't open it is empty and needs a header
    try:
        log_file = open(log_path, 'r')
    except:
        log_file = open(log_path, 'w')
        log_file.write(HEADER)
    log_file = open(log_path, 'a')
    try:
        ping_network(log_file)
    except KeyboardInterrupt:
        pass
    print("Over!")
    log_df = pd.read_csv(log_path)
    print(log_df.to_markdown())
    pd.set_option('colheader_justify', 'center')
    html_string = '''
    <html>
    <head>
        <title>Network Status</title>
        <meta http-equiv="refresh" content="5">
    </head>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <body>
        <center>
        <h1>NETWORK STATUS</h1>
        {} <br>
        {}
        {} <br>
        {}
        {}
        <center>
    </body>
    </html>
    '''

    prev_df = pd.read_csv('prev_log.csv')
    number_of_cuurent_devices = log_df.shape[0]
    number_of_prev_devices  = prev_df.shape[0]
    changed_devices = number_of_cuurent_devices - number_of_prev_devices
    changed = ""
    changed_IP = pd.DataFrame()
    if changed_devices < 0:
        # some existing device has gone offline
        # prev_log > log
        off = prev_df[prev_df['IP'].isin(log_df['IP']) == False]
        changed = "These devices have gone offline"
        print(changed)
        print(off['IP'].to_markdown(index=False))
        changed_IP = off

    elif changed_devices > 0:
        #some new device has entered
        on = log_df[log_df['IP'].isin(prev_df['IP']) == False]
        changed = "These devices are new"
        print(changed)
        print(on['IP'].to_markdown(index=False))
        print("These devices are new")
        print(on['IP'].to_markdown(index=False))
        changed_IP=on
    else:
        changed = "No new devices"
        print(changed)
        

    offline_devices = log_df[log_df['Status'] == 'Offline']
    offline_Message = "These Devices are Offline"
    print(offline_Message)
    print(offline_devices['IP'].to_markdown(index=False))

    
    with open('log.html', 'w') as f:
        f.write(html_string.format(log_df.to_html(classes='mystyle', index=False),
        changed, changed_IP.to_html(classes='mystyle', index=False) ,
        offline_Message, offline_devices.to_html(classes='mystyle', index=False)))

    
    log_file.close()