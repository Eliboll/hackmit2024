import serial
import io

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
lat = 0
lon = 0
# ser = serial.serial_for_url('/dev/ttyUSB0', 115200, timeout=1)
# sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

def connect_murata():
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
    # ensure_send_command('AT%RATACT="NBNTN","1"') # if I want satellite
    ensure_send_command('AT%RATACT="CATM","1"') # if I want AT&T
    ensure_send_command('AT+CFUN=0') # stop radio
    ensure_send_command('AT%PDNSET=1,"DATA.MONO","IP"')
    ensure_send_command('AT%SETSYSCFG=SW_CFG.nb_band_table.band#1,ENABLE;23')
    ensure_send_command('AT%NTNCFG="POS","IGNSS","0"')
    ensure_send_command('ATZ', '%BOOTEV:0') # restart
    ensure_send_command('AT+CFUN=0') # only need to do again if I restart the module
    ensure_send_command('AT%IGNSSEV="FIX",1') # GPS coordinates subscription
    # ensure_send_command('AT%NOTIFYEV="SIB31",10') # satellite subscription
    ensure_send_command('AT+CEREG=2')
    ensure_send_command('AT%IGNSSACT=1')
    ensure_send_command('AT+CFUN=1', '+CEREG: 5') # reenable radio
    ensure_send_command('AT+COPS?')

def ensure_send_command(command, confirm = "OK"):
    ret = ""
    while(len(ret) == 0 or ret[0] != command):
        ret = send_command(command)
    while(len(ret)==0 or ret[-1][:len(confirm)] != confirm):
        ret = read_response()
        parse_gps(ret)
            
def parse_gps(ret):
    global lat,lon
    it = 0
    while(it < len(ret)-1 and (len(ret[it]) < len("%IGNSSEVU") or ret[it][:len("%IGNSSEVU")] != "%IGNSSEVU")):
        it += 1
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
    return read_response()

def read_response():
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
        read_response()

parse_gps(['', '%IGNSSEVU: "FIX",1,"04:02:56","15/09/2024","42.357978","-71.095933","39.7",1726372976000,,,"B",3'])
print(lat, lon)
connect_murata()
standby()
# while(True):
#     c = input("Enter command:")
#     send_command(c)