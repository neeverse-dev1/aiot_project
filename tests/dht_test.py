import time
import board
import adafruit_dht

# DHT22 센서를 GPIO4 (Board D4)에 연결했다고 가정합니다.
# DHT11을 사용하는 경우:
dht_device = adafruit_dht.DHT11(board.D4)
# dht_device = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        if temperature_c is not None and humidity is not None:
            temperature_f = temperature_c * (9 / 5) + 32
            print(f"온도: {temperature_c:.1f}°C / {temperature_f:.1f}°F")
            print(f"습도: {humidity:.1f}%")
        else:
            print("센서에서 데이터를 읽을 수 없습니다. 다시 시도합니다.")

    except RuntimeError as error:
        # DHT 센서가 데이터를 읽지 못하는 것은 흔한 일입니다.
        # 계속해서 다시 시도하세요.
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dht_device.exit()
        raise error

    time.sleep(2) # 2초마다 측정
