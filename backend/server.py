import logging
import datetime
import socketserver
import json

class logger_class:
    def __init__(self, filename):
        self.filename = filename
    def print_log(self,message):
        print(message)
        with open(self.filename, "a") as fp:
            fp.write(message+"\n")

logger = logger_class("output.log")

def udp_handler(self):
    try:
        msgRecvd = self.rfile.readline().strip()
        data = json.loads(msgRecvd)
    except json.decoder.JSONDecodeError:
        logger.print_log(f"{datetime.datetime.now().strftime('%H:%M:%S')}| ERROR; Packet from {self.client_address[0]} unreadable")

    lat  = data.get("lat")
    lon  = data.get("lon")
    id   = data.get("id")
    rate = data.get("rate")
    if None in (lat, lon, rate, id):
        logger.print_log(f"{datetime.datetime.now().strftime('%H:%M:%S')}| ERROR; Packet from {self.client_address[0]} does not contain all params")
    try:
        lat  = float(lat)
        lon  = float(lon)
        id   = int(id)
        rate = int(rate)
    except ValueError:
        logger.print_log(f"{datetime.datetime.now().strftime('%H:%M:%S')}| ERROR; Packet from {self.client_address[0]} was not formatted properly")
        
    ######################################################################
    #   Made it past data validation
    ######################################################################
    temp_string = f"{datetime.datetime.now().strftime('%H:%M:%S')} | id={id:05d} |lat={lat:3.8f}, lon={lon:3.8f}, rate={rate:03d}"
    logger.print_log(temp_string)
    if rate < 30:
        temp_string = "\tCRITICAL HEART RATE DETECTED"
        logger.print_log(temp_string)    
    

if __name__ == '__main__':
    listen_addr = ('0.0.0.0', 5000)

    # with allowing to reuse the address we dont get into problems running it consecutively sometimes
    socketserver.UDPServer.allow_reuse_address = True 

    # register our class
    serverUDP = socketserver.UDPServer(listen_addr, udp_handler)
    serverUDP.serve_forever()
