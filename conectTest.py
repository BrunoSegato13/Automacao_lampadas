import RPi.GPIO as gpio
import time
from datetime import datetime
import threading
# Specific Librarys
import sqlite3
import requests

TOKEN = "BBFF-WLBvoPc3VK6bgkI5haAR4R4VvBOapc"  
DEVICE_LABEL = "RaspBerry"  
VARIABLE_LABEL_1 = "Ligth"  
VARIABLE_LABEL_2 = "TESTE"  
VARIABLE_LABEL_3 = "Time_ON"  


def post_request(payload):
    #  headers  HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    #  HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    #  results
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True

# Data Base start
conn = sqlite3.connect('lightlogs.db')
c = conn.cursor()

# Create Tables 
def create_tables():
   c.execute('''CREATE TABLE IF NOT EXISTS logs (date TEXT, sensor INTEGER)''')
   c.execute('''CREATE TABLE IF NOT EXISTS timeon (datemonth TEXT, timepass REAL)''')
   c.execute('''INSERT INTO timeon (datemonth, timepass) VAlUES (?, ?)''',
                                       ("06", 0))
   conn.commit()

def data_entry_logs():
   date = str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
   sensor = 24
   c.execute('''INSERT INTO logs (date, sensor) VAlUES (?, ?)''',
                                       (date, sensor))
   conn.commit()

def data_entry_timeon():
   datemonth = str(datetime.fromtimestamp(time.time()).strftime('%m'))
   c.execute('''SELECT datemonth FROM timeon''')
   curmonth = c.fetchone()[0]
   print(curmonth)
   print(datemonth)
   c.execute('''SELECT timepass FROM timeon''')
   timep = c.fetchone()[0]
   print(timep)
   if(datemonth == curmonth):
      timep += 10.0
      c.execute('''UPDATE timeon SET timepass = (?)''',
                                          (timep,))
      conn.commit()
   else:
      timep = 0
      timep += 10
      c.execute('''INSERT INTO timeon (datemonth, timepass) VAlUES (?, ?)''',
                                       (datemonth, timep))
      conn.commit()

# Variables 

liga = 0


create_tables()

def main():
    
    # GPIOs Setup
    pir_sensor = 24;
    ligth = 23;
    gpio.setmode(gpio.BCM);
    gpio.setup(ligth, gpio.OUT);
    gpio.setup(pir_sensor, gpio.IN);
    
   
    
    
    try:
        
         if gpio.input(pir_sensor) == gpio.LOW:
            gpio.output(ligth, gpio.LOW)
            print('Off')
            global liga
            liga = 0
            payload = build_payload(
                VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3)
            post_request(payload)
            
         if gpio.input(pir_sensor) == gpio.HIGH:
             liga = 1
             
             payload = build_payload(
                  VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3)
             post_request(payload)
             t1 = threading.Thread(target = light_on())

        

    except KeyboardInterrupt:
        pass
    

def light_on():
    gpio.output(23, gpio.HIGH)
    print('On')
    time.sleep(10)
    data_entry_logs()
    data_entry_timeon()
    c.execute("SELECT * FROM logs")
    print(c.fetchall())
    c.execute("SELECT * FROM timeon")
    print(c.fetchall())


def build_payload(variable_1, variable_2, variable_3):
     
    c.execute('''SELECT timepass FROM timeon''')
    timep = c.fetchone()[0]
    global liga
    li = liga
    if li == 1:
        #print("Pi")
        value_1 = 1
    else:
        #print("MyBAD")
        value_1 = 0
    
    value_2 = 2
    value_3 = timep
    
    payload = {variable_1: value_1,
               variable_2: value_2,
               variable_3: value_3}

    return payload

if __name__ == '__main__':
    while (True):
        main()
        time.sleep(1)