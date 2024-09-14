from flask import Flask, jsonify, request, Response

import datetime

app = Flask(__name__)

@app.route("/log", methods=['GET'])
def log_heartbeat():
    if request.is_json:
        data = request.get_json()
        lat  = data.get("lat")
        lon  = data.get("lon")
        id   = data.get("id")
        rate = data.get("rate")
        if None in (lat, lon, rate, id):
            return Response("{'error': 'no given parameters'}", status=400)
        try:
            lat  = float(lat)
            lon  = float(lon)
            id   = int(id)
            rate = int(rate)
        except ValueError:
            return Response("{'error': 'parameters crafed invalid'}", status=400)
        
        ######################################################################
        #   Made it past data validation
        ######################################################################
        
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | id={id:05d} |lat={lat:3.8f}, lon={lon:3.8f}, rate={rate:03d}")
        
        if rate < 30:
            print("\tCRITICAL HEART RATE DETECTED")
            return Response("{'success': 'CRITICAL CONDITION DETECTED, SENDING HELP'}", status=200)
        return Response("{'success': 'logged'}", status=200)         
        
    else:
        return Response("{'error': 'request not as json'}", status=400)
    
@app.route("/", methods=['GET'])
def home():
    return "Hello world!"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
    
