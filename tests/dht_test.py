import time
import board
import adafruit_dht

dht_device = adafruit_dht.DHT11(board.D4)

try:
    while True:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        if temperature_c is not None and humidity is not None:
            temperature_f = temperature_c * (9 / 5) + 32
            print(f"온도: {temperature_c:.1f}°C / {temperature_f:.1f}°F")
            print(f"습도: {humidity:.1f}%")
        else:
            print("센서에서 데이터를 읽을 수 없습니다. 다시 시도합니다.")

        time.sleep(1)
    
except KeyboardInterrupt:
    print("\nEnd program")
finally:
    dht_device.exit()
