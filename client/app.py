import time

CLIENT_ID = 8542
ENDPOINT = "http://172.104.219.246:5000/log"


def main():
    while True:
        time.sleep(1)
        # Grab heart rate from arduino
        # 
        # 
        # 
        heart_rate = 100
        
        # Grab GPS heart rate from dev board
        #
        #
        
        lat = "182.194837"
        lon = "-49.23597"
        
        payload = {
            "lat":lat,
            "lon":lon,
            "rate":heart_rate,
            "id":CLIENT_ID
        }      
    

if __name__ == "__main__":
    main()