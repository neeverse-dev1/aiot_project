import RPi.GPIO as GPIO
import numpy as np
import time
import datetime

from googlespreadsheet import update_gspread_sheet_data, delete_gspread_sheet_data


# GPIO 핀 설정 (BCM 모드)
# TRIG 핀은 센서에 초음파를 발생시키기 위해 사용
# ECHO 핀은 초음파가 반사되어 돌아오는 시간을 측정
GPIO_TRIGGER = 27  # TRIG 핀을 GPIO 27 (물리적 핀 13)에 연결
GPIO_ECHO = 17     # ECHO 핀을 GPIO 17 (물리적 핀 11)에 전압 분배 후 연결

# --- 시뮬레이션 모드 설정 ---
# True로 설정하면 실제 HC-SR04 센서 없이 거리 데이터를 시뮬레이션합니다.
# False로 설정하면 실제 HC-SR04 센서에서 데이터를 읽습니다.
SIMULATION_MODE = False

# 시뮬레이션 모드에서 거리 변화를 위한 변수
sim_current_distance = 150.0 # 초기 시뮬레이션 거리 (cm)
sim_distance_change_step = 5.0 # 시뮬레이션에서 거리가 변하는 정도
sim_anomaly_trigger_counter = 0
SIM_ANOMALY_INTERVAL = 50 # 50번의 시뮬레이션마다 이상치 발생 (조절 가능)


# GPIO 모드를 BCM으로 설정합니다. 이는 GPIO 핀 번호 체계를 의미합니다.
if not SIMULATION_MODE: # 시뮬레이션 모드가 아닐 때만 GPIO 설정
    GPIO.setmode(GPIO.BCM)
    # TRIG 핀을 출력으로 설정하여 초음파 펄스를 보냅니다.
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    # ECHO 핀을 입력으로 설정하여 반사된 초음파를 받습니다.
    GPIO.setup(GPIO_ECHO, GPIO.IN)

def get_distance():
    """
    HC-SR04 센서를 사용하여 거리를 측정하는 함수입니다.
    SIMULATION_MODE가 True이면 시뮬레이션 데이터를 반환하고,
    False이면 실제 센서에서 데이터를 읽습니다.
    """
    if SIMULATION_MODE:
        return simulate_distance()
    else:
        # TRIG 핀을 잠시 LOW로 설정하여 센서를 초기화합니다.
        GPIO.output(GPIO_TRIGGER, False)
        time.sleep(0.000002) # 2 마이크로초 대기

        # TRIG 핀에 10us(마이크로초)의 HIGH 펄스를 발생시킵니다.
        # 이 펄스가 센서가 초음파를 방출하도록 트리거합니다.
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001) # 10 마이크로초 동안 HIGH 유지
        GPIO.output(GPIO_TRIGGER, False)

        start_time = time.time()
        end_time = time.time()

        # ECHO 핀이 HIGH가 될 때까지 대기합니다 (초음파 발사 시작).
        # 타임아웃을 추가하여 센서가 반응하지 않을 때 무한 루프에 빠지는 것을 방지합니다.
        timeout_start = time.time()
        while GPIO.input(GPIO_ECHO) == 0:
            start_time = time.time()
            if time.time() - timeout_start > 0.1: # 0.1초 이상 대기하면 타임아웃
                return None # 오류 처리 또는 무한 루프 방지
                
        # ECHO 핀이 LOW가 될 때까지 대기합니다 (초음파 수신 완료).
        timeout_end = time.time()
        while GPIO.input(GPIO_ECHO) == 1:
            end_time = time.time()
            if time.time() - timeout_end > 0.1: # 0.1초 이상 대기하면 타임아웃
                return None # 오류 처리 또는 무한 루프 방지

        # 펄스 지속 시간 (초음파가 왕복하는 데 걸린 시간)을 계산합니다.
        pulse_duration = end_time - start_time

        # 거리 계산: (시간 * 소리의 속도) / 2
        # 소리의 속도는 약 34300 cm/s (20°C 기준)
        # 왕복 거리이므로 2로 나눕니다.
        distance = (pulse_duration * 34300) / 2
        
        # HC-SR04의 유효 측정 범위(2cm ~ 400cm)를 벗어나는 값은 필터링합니다.
        if 2 <= distance <= 400:
            return distance
        else:
            return None

def simulate_distance():
    """
    HC-SR04 센서 데이터를 시뮬레이션하는 함수입니다.
    특정 간격마다 이상치(급격한 거리 변화)를 발생시킵니다.
    """
    global sim_current_distance, sim_anomaly_trigger_counter

    sim_anomaly_trigger_counter += 1

    # 일정 간격마다 큰 변화 (이상치) 발생
    if sim_anomaly_trigger_counter % SIM_ANOMALY_INTERVAL == 0:
        # 현재 거리에 큰 변화를 줘서 이상치 발생 유도
        change_amount = np.random.uniform(50, 150) # 50~150cm 변화
        if np.random.rand() > 0.5:
            sim_current_distance += change_amount
        else:
            sim_current_distance -= change_amount
        print(f"--- 시뮬레이션: 큰 거리 변화 발생 (이상치 유도) ---")

    # 작은 노이즈 추가 (정상적인 센서 노이즈 시뮬레이션)
    noise = np.random.normal(0, 2) # 평균 0, 표준편차 2cm의 노이즈
    sim_current_distance += noise

    # 거리가 유효 범위(2cm ~ 400cm)를 벗어나지 않도록 클리핑
    sim_current_distance = np.clip(sim_current_distance, 2, 400)
    
    return sim_current_distance


try:
    sheet_name = 'hc_sr0_sensor'
    # Sheet 초기화
    delete_gspread_sheet_data(sheet_name)
    count = 0 
    
    while True:
        distance = get_distance()
        if distance is not None:
            now = datetime.datetime.now()
            t_time = now.strftime("%Y-%m-%d %H:%M:%S")
            update_gspread_sheet_data(sheet_name, [ count + 1, [t_time, distance]])
            count += 1
            print(f"거리: {distance:.2f} cm")

        else:
            print("거리 측정 실패 (센서 오류 또는 타임아웃)")
        time.sleep(1) # 1초마다 측정

except KeyboardInterrupt:
    print("프로그램 종료")
    if not SIMULATION_MODE:
        GPIO.cleanup() # GPIO 핀 초기화
