import RPi.GPIO as GPIO
import time

# GPIO 핀 설정 (BCM 모드)
# TRIG 핀은 센서에 초음파를 발생시키기 위해 사용
# ECHO 핀은 초음파가 반사되어 돌아오는 시간을 측정
#GPIO_TRIGGER = 23  # TRIG 핀을 GPIO 23 (물리적 핀 16)에 연결
#GPIO_ECHO = 24     # ECHO 핀을 GPIO 24 (물리적 핀 18)에 전압 분배 후 연결
GPIO_TRIGGER = 27  # TRIG 핀을 GPIO 23 (물리적 핀 16)에 연결
GPIO_ECHO = 17     # ECHO 핀을 GPIO 24 (물리적 핀 18)에 전압 분배 후 연결

# GPIO 설정
GPIO.setmode(GPIO.BCM) # BCM 핀 번호 체계 사용
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def get_distance():
    # TRIG 핀을 LOW로 설정하여 센서 초기화
    GPIO.output(GPIO_TRIGGER, False)
    # print("센서 초기화 중...")
    time.sleep(0.000002) # 2 마이크로초 대기

    # TRIG 핀에 10us(마이크로초)의 펄스 발생
    # 펄스를 발생시키면 센서가 초음파를 방출
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001) # 10 마이크로초 동안 HIGH 유지
    GPIO.output(GPIO_TRIGGER, False)

    start_time = time.time()
    end_time = time.time()

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

    # 거리 계산
    # 소리의 속도: 343m/s (0.0343 cm/us)
    # 거리는 왕복 시간의 절반이므로 2로 나눔
    distance = (pulse_duration * 34300) / 2
    
    return distance

try:
    while True:
        distance = get_distance()
        if distance is not None:
            print(f"거리: {distance:.2f} cm")
        else:
            print("거리 측정 실패 (센서 오류 또는 타임아웃)")
        time.sleep(1) # 1초마다 측정

except KeyboardInterrupt:
    print("프로그램 종료")
    GPIO.cleanup() # GPIO 핀 초기화
