import serial
import io
import time

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
lat = 42.357978
lon = -71.095933
pulse_rate = 70
# ser = serial.serial_for_url('/dev/ttyUSB0', 115200, timeout=1)
# sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

def connect_murata(satellite = False):
    global ser, sio
    while(not ser.is_open):
        ser.open()
    print("PORT OPEN")
    ensure_send_command('ATZ', '%BOOTEV:0') # restart
    ensure_send_command('AT')
    ensure_send_command('AT%PDNSET=1,"DATA.MONO","IP"')
    # ensure_send_command('AT+COPS=0')
    ensure_send_command('AT+CFUN=1')
    ensure_send_command('AT%SETACFG="manager.urcBootEv.enabled","true"',)
    ensure_send_command('AT%SETACFG="radiom.config.multi_rat_enable","true"')
    ensure_send_command('AT%SETACFG="radiom.config.preferred_rat_list","none"')
    ensure_send_command('AT%SETACFG="radiom.config.auto_preference_mode","none"')
    ensure_send_command('AT%SETACFG="locsrv.operation.locsrv_enable","true"')
    ensure_send_command('AT%SETACFG="locsrv.internal_gnss.auto_restart","enable"')
    ensure_send_command('AT%SETACFG="modem_apps.Mode.AutoConnectMode","true"')
    if(satellite):
        ensure_send_command('AT%RATACT="NBNTN","1"') # if I want satellite
    else:
        ensure_send_command('AT%RATACT="CATM","1"') # if I want AT&T
    ensure_send_command('AT+CFUN=0') # stop radio
    ensure_send_command('AT%PDNSET=1,"DATA.MONO","IP"')
    ensure_send_command('AT%SETSYSCFG=SW_CFG.nb_band_table.band#1,ENABLE;23')
    ensure_send_command('AT%NTNCFG="POS","IGNSS","0"')
    ensure_send_command('ATZ', '%BOOTEV:0') # restart
    ensure_send_command('AT+CFUN=0') # only need to do again if I restart the module
    ensure_send_command('AT%IGNSSEV="FIX",1') # GPS coordinates subscription
    if(satellite):
        ensure_send_command('AT%NOTIFYEV="SIB31",1') # satellite subscription
    ensure_send_command('AT+CEREG=2')
    if(satellite):
        ensure_send_command('AT%IGNSSACT=1', '%IGNSSEVU')
    if (ensure_send_command('AT+CFUN=1', '+CEREG: 5')): # reenable radio
        return False
    return True
    # ensure_send_command('AT+COPS?')

def ensure_send_command(command, confirm = "OK"):
    start = time.time()
    counter_send = 0
    counter_recieve = 0
    ret = ""
    while((len(ret) == 0 or ("ERROR" in ret)) and counter_send < 5):
        if len(ret) > 0:
            counter_send +=1
        ret = send_command(command)
        # if(check_gps):
        #     parse_gps(ret)
    while((len(ret)==0 or ret[-1][:len(confirm)] != confirm) and counter_recieve < 5):
        if len(ret) > 0:
            counter_recieve +=1
        ret = pull_responses()
        now = time.time()
        if (now -start > 180):
            counter_recieve =5
            break
        # if(check_gps):
        #     parse_gps(ret)
    return counter_send==5 or counter_recieve ==5
    
            
def parse_gps(ret):
    global lat,lon
    it = 0
    while(it < len(ret)-1 and (len(ret[it]) < len("%IGNSSEVU") or ret[it][:len("%IGNSSEVU")] != "%IGNSSEVU")):
        it += 1
    if(len(ret) == 0):
        return
    if ret[it][:len("%IGNSSEVU")] == "%IGNSSEVU":
        chopped = ret[it].split(",")
        lat = float(chopped[4].replace('"',''))
        lon = float(chopped[5].replace('"',''))

def send_command(command):
    global ser, sio
    # sio.write(str(command+"\n"))
    # sio.flush()
    ser.write(bytes(command + '\r\n','utf-8'))
    ser.flush()
    return pull_responses()

def get_gps_send_packet(packet):
    parse_gps(pull_responses())
    ensure_send_command('AT%SOCKETCMD="ALLOCATE",1,"UDP","OPEN","172.104.219.246",5000,0')
    ensure_send_command('AT%SOCKETCMD="SETOPT",1,36000,1')
    ensure_send_command('AT%SOCKETCMD="ACTIVATE",1')
    if (ensure_send_command('AT%SOCKETDATA="SEND",1,'+str(len(packet))+',"'+packet.encode().hex()+'"')):
        ensure_send_command('AT%SOCKETCMD="DELETE",1')
        return False
    ensure_send_command('AT%SOCKETCMD="DELETE",1')
    return True

def pull_responses():
    global ser, sio
    # print(sio.readline())
    ret = [r.decode().rstrip() for r in ser.readlines()]
    print(ret)
    return ret

def disconnect_murata():
    global ser, sio
    ser.close()

def standby():
    while True:
        pull_responses()

    
def main():
    toggle = True
    if not connect_murata(satellite=False):
        toggle = False
        connect_murata(satellite=True)
        
    while(True):
        # Record Arduino pulse rate data via Serial

        if not (get_gps_send_packet('{"lat": '+str(lat)+', "lon": '+str(lon)+', "rate": '+str(pulse_rate)+', "id": 5}')):
            connect_murata(satellite=toggle)
            toggle = not toggle
        time.sleep(5)
    
    
if __name__ == "__main__":
    main()