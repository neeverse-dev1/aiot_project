import RPi.GPIO as GPIO
import time

GPIO_TRIGGER = 17
GPIO_ECHO = 27

def get_distance():
    # TRIG 핀을 LOW로 설정하여 센서 초기화
    GPIO.output(GPIO_TRIGGER, False)
    time.sleep(0.000002) # 2us 대기

    # TRIG 핀에 10us(마이크로초)의 펄스 발생
    # 펄스를 발생시키면 센서가 초음파를 방출
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001) # 10us Pulse delay
    GPIO.output(GPIO_TRIGGER, False)

    # ECHO 핀이 HIGH가 될 때까지 대기 (초음파 발사 시작)
    # timeout을 추가하여 무한 루프 방지
    timeout_start = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
        if time.time() - timeout_start > 1: # 1초 이상 대기하면 타임아웃
            return None # 오류 처리 또는 무한 루프 방지
            
    # ECHO 핀이 LOW가 될 때까지 대기 (초음파 수신 완료)
    timeout_end = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        end_time = time.time()
        if time.time() - timeout_end > 1: # 1초 이상 대기하면 타임아웃
            return None # 오류 처리 또는 무한 루프 방지

    # 펄스 지속 시간 계산 (초음파가 왕복한 시간)
    pulse_duration = end_time - start_time
    distance = (pulse_duration * 34300) / 2
    
    return distance

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    
    while True:
        distance = get_distance()
        if distance:
            print(f"거리: {distance:.2f} cm")
        else:
            print("거리 측정 실패 (센서 오류 또는 타임아웃)")
        time.sleep(0.5) # 0.5초마다 측정

except KeyboardInterrupt:
    print("\nEnd program")
finally:
    GPIO.cleanup() # GPIO 핀 초기화

