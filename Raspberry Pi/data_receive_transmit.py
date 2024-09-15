import serial
import io

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
# ser = serial.serial_for_url('/dev/ttyUSB0', 115200, timeout=1)
# sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

def connect_murata():
    global ser, sio
    while(not ser.is_open):
        ser.open()
    print("PORT OPEN")
    ensure_send_command('AT')
    ensure_send_command('AT%PDNSET=1,"DATA.MONO","IP"')
    ensure_send_command('AT+COPS=0')
    ensure_send_command('AT+CFUN=1')
    ensure_send_command('AT%SETACFG="manager.urcBootEv.enabled","true"')
    ensure_send_command('AT%SETACFG="radiom.config.multi_rat_enable","true"')
    ensure_send_command('AT%SETACFG="radiom.config.preferred_rat_list","none"')
    ensure_send_command('AT%SETACFG="radiom.config.auto_preference_mode","none"')
    ensure_send_command('AT%SETACFG="locsrv.operation.locsrv_enable","true"')
    ensure_send_command('AT%SETACFG="locsrv.internal_gnss.auto_restart","enable"')
    ensure_send_command('AT%SETACFG="modem_apps.Mode.AutoConnectMode","true"')
    ensure_send_command('AT%RATACT="NBNTN","1"') # if I want satellite
    # ensure_send_command('AT%RATACT="CATM","1"') # if I want AT&T
    ensure_send_command('AT+CFUN=0') # stop radio
    ensure_send_command('AT%PDNSET=1,"DATA.MONO","IP"')
    ensure_send_command('AT%SETSYSCFG=SW_CFG.nb_band_table.band#1,ENABLE;23')
    ensure_send_command('AT%NTNCFG="POS","IGNSS","0"')
    ensure_send_command('ATZ') # restart
    ensure_send_command('AT+CFUN=0') # only need to do again if I restart the module
    ensure_send_command('AT%IGNSSEV="FIX",1') # GPS coordinates subscription
    ensure_send_command('AT%NOTIFYEV="SIB31",1') # satellite subscription
    ensure_send_command('AT+CEREG=2')
    ensure_send_command('AT%IGNSSACT=1')
    ensure_send_command('AT+CFUN=1') # reenable radio
    ensure_send_command('AT+COPS?')

def ensure_send_command(command):
    while(True):
        ret = send_command(command)
        try:
            if(ret[-1] == "OK"):
                break
        except IndexError:
            pass

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

connect_murata()
standby()
# while(True):
#     c = input("Enter command:")
#     send_command(c)