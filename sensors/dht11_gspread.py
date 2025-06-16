import time
import datetime
import board
import random
import numpy as np
import adafruit_dht

from googlespreadsheet import update_gspread_sheet_data, delete_gspread_sheet_data

SIMULATION = False

# DHT22 센서를 GPIO4 (Board D4)에 연결했다고 가정합니다.
# DHT11을 사용하는 경우:
try:
     dhtDevice = adafruit_dht.DHT11(board.D4) # GPIO 4번 핀에 연결된 경우
    # dht_device = adafruit_dht.DHT22(board.D4)
except Exception as e:
     print(f"센서 초기화 오류: {e}")
     dhtDevice = None


def read_dht11_sensor():
    """
    실제 DHT11 센서로부터 온도와 습도를 읽어오는 함수입니다.
    성공 시 (온도, 습도) 튜플을, 실패 시 (None, None)을 반환합니다.
    """
    if not SIMULATION:
        if dhtDevice is not None:
            try:
                temperature_c = dhtDevice.temperature
                humidity = dhtDevice.humidity
                if temperature_c is not None and humidity is not None:
                    return float(temperature_c), float(humidity)
                else:
                    return None, None
            except RuntimeError as error:
                # DHT 센서는 가끔 읽기 오류가 발생할 수 있습니다.
                print(f"센서 읽기 오류: {error.args[0]}")
                return None, None
        return None, None
    else:
        # --- 시뮬레이션 코드 시작 ---
        # 실제 센서가 없을 경우, 아래 코드가 가상의 데이터를 생성합니다.
        temp = 20 + (5 * (1 + np.sin(time.time() / 60))) + random.uniform(-0.5, 0.5)
        hum = 50 + (10 * (1 + np.cos(time.time() / 90))) + random.uniform(-1, 1)
        return round(temp, 1), round(hum, 1)
        # --- 시뮬레이션 코드 끝 ---


def main():
    
    sheet_name = 'dht11_sensor'
    # Sheet 초기화
    delete_gspread_sheet_data(sheet_name)
    
    count = 0 
    while True:
        try:
            now = datetime.datetime.now()
            t_time = now.strftime("%Y-%m-%d %H:%M:%S")
            values = read_dht11_sensor()
            if values[0]:
                update_gspread_sheet_data(sheet_name, [ count + 1, [t_time, values[0], values[1]]])
            count += 1
            time.sleep(2)        
        except Exception as e:
            print(str(e))
        
    
if __name__ == "__main__":
    
    main()


