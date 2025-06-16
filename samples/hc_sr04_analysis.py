import RPi.GPIO as GPIO
import time
import numpy as np
from sklearn.ensemble import IsolationForest
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.font_manager as fm # 폰트 관리 모듈

# --- 시뮬레이션 모드 설정 ---
# True로 설정하면 실제 HC-SR04 센서 없이 거리 데이터를 시뮬레이션합니다.
# False로 설정하면 실제 HC-SR04 센서에서 데이터를 읽습니다.
SIMULATION_MODE = False

# 시뮬레이션 모드에서 거리 변화를 위한 변수
sim_current_distance = 150.0 # 초기 시뮬레이션 거리 (cm)
sim_distance_change_step = 5.0 # 시뮬레이션에서 거리가 변하는 정도
sim_anomaly_trigger_counter = 0
SIM_ANOMALY_INTERVAL = 50 # 50번의 시뮬레이션마다 이상치 발생 (조절 가능)


# --- Matplotlib 한글 폰트 설정 ---
# 시스템에 설치된 나눔고딕 폰트 경로를 찾습니다.
# 만약 'fonts-nanum' 패키지를 설치했다면 보통 이 경로에 있습니다.
# 시스템마다 경로가 다를 수 있으니, 직접 확인하여 수정해야 할 수도 있습니다.
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if fm.findfont(fm.FontProperties(fname=font_path)) is None:
    print("경고: NanumGothic 폰트를 찾을 수 없습니다. 시스템에 'fonts-nanum' 패키지가 설치되어 있는지 확인하거나, 폰트 경로를 수정해 주세요.")
    # 대체 폰트 설정 (기본 폰트로 폴백)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
else:
    plt.rcParams['font.family'] = 'NanumGothic' # 폰트 패밀리 설정
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지


# --- HC-SR04 센서 설정 ---
# TRIG 핀과 ECHO 핀의 GPIO 번호를 설정합니다 (BCM 모드).
# 이 값들은 여러분의 배선에 따라 다를 수 있습니다.
GPIO_TRIGGER = 27  # TRIG 핀을 GPIO 27 (물리적 핀 13)에 연결
GPIO_ECHO = 17     # ECHO 핀을 GPIO 17 (물리적 핀 11)에 전압 분배 후 연결

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

# --- AI 분석: IsolationForest를 이용한 이상 감지 ---

# 1. '정상' 데이터 수집을 위한 설정
#    모델 훈련을 위해 수집할 정상 데이터 포인트의 수입니다.
#    이 데이터가 모델이 '정상'이라고 판단할 기준이 됩니다.
NUM_TRAINING_SAMPLES = 100 
# 데이터를 수집할 때 각 측정 사이의 시간 간격 (초)
TRAINING_COLLECTION_INTERVAL = 0.5 

# 2. Isolation Forest 모델 설정
#    contamination: 데이터셋에서 이상치(anomaly)의 비율을 추정하는 값입니다 (0과 0.5 사이).
#                   이 값을 조절하여 이상 감지의 민감도를 조절할 수 있습니다.
#    random_state: 재현 가능한 결과를 위해 설정합니다.
model = IsolationForest(contamination=0.05, random_state=42)

# --- 차트 설정 ---
# 시계열 데이터를 저장할 deque (최근 50개 데이터 포인트)
PLOT_BUFFER_SIZE = 50
time_data = collections.deque(maxlen=PLOT_BUFFER_SIZE)
distance_plot_data = collections.deque(maxlen=PLOT_BUFFER_SIZE)
anomaly_points_x = collections.deque(maxlen=PLOT_BUFFER_SIZE)
anomaly_points_y = collections.deque(maxlen=PLOT_BUFFER_SIZE)

# matplotlib 인터랙티브 모드 켜기
plt.ion()
fig, ax = plt.subplots(figsize=(10, 6)) # 차트 크기 설정
line, = ax.plot([], [], 'b-', label='거리 (cm)') # 거리 그래프 라인 (한글화)
# 이상치 표시를 위한 설정: 빨간색, 삼각형 마커, 큰 크기, 검은색 테두리
anomaly_scatter = ax.scatter([], [], color='red', marker='^', s=100, edgecolor='black', label='이상 감지') # 이상치 표시 (한글화)

ax.set_title('HC-SR04 거리 측정 및 이상 감지', fontsize=16) # 제목 한글화 및 크기
ax.set_xlabel('시간 (초)', fontsize=12) # X축 레이블 한글화 및 크기
ax.set_ylabel('거리 (cm)', fontsize=12) # Y축 레이블 한글화 및 크기
ax.legend(fontsize=10) # 범례 한글화 및 크기
ax.grid(True) # 그리드 표시
plt.show(block=False) # 차트를 블록하지 않고 표시

# 시작 시간 기록 (차트의 X축 시간 계산용)
start_overall_time = time.time()

def update_plot(frame):
    """
    matplotlib 차트를 업데이트하는 함수입니다.
    이 함수는 FuncAnimation에 의해 주기적으로 호출됩니다.
    """
    # X축 시간 데이터를 업데이트합니다.
    if time_data:
        ax.set_xlim(min(time_data), max(time_data) + 1)
    
    # Y축 범위는 센서 측정 범위에 따라 동적으로 설정합니다.
    if distance_plot_data:
        min_dist = min(distance_plot_data)
        max_dist = max(distance_plot_data)
        # 센서 유효 범위(2~400cm)를 고려하여 y축 범위 설정
        ax.set_ylim(max(0, min_dist - 10), min(400, max_dist + 10)) 

    line.set_data(list(time_data), list(distance_plot_data))
    anomaly_scatter.set_offsets(np.c_[list(anomaly_points_x), list(anomaly_points_y)])

    fig.canvas.draw_idle() # 차트 업데이트 요청
    fig.canvas.flush_events() # 이벤트 처리 (차트 반응성 향상)

    return line, anomaly_scatter

print("-------------------------------------------------")
print("AI 분석을 위한 '정상' 데이터 수집을 시작합니다.")
print(f"총 {NUM_TRAINING_SAMPLES}개의 샘플을 수집합니다.")

if SIMULATION_MODE:
    print("현재 시뮬레이션 모드입니다. 코드 내 SIMULATION_MODE 변수를 False로 변경하면 실제 센서 데이터를 사용합니다.")
else:
    print("주변에 움직이는 물체가 없는 '정상' 상태를 유지해 주세요.")
print("-------------------------------------------------")

normal_data = []
try:
    while len(normal_data) < NUM_TRAINING_SAMPLES:
        distance = get_distance()
        if distance is not None:
            normal_data.append([distance]) # scikit-learn은 2D 배열을 기대합니다.
            
            # 차트 업데이트를 위한 데이터 추가
            current_time = time.time() - start_overall_time
            time_data.append(current_time)
            distance_plot_data.append(distance)
            
            print(f"수집 중: {len(normal_data)}/{NUM_TRAINING_SAMPLES} - 거리: {distance:.2f} cm")
        else:
            print("데이터 수집 실패. 재시도합니다.")
        
        update_plot(None) # 수집 중에도 차트 업데이트
        time.sleep(TRAINING_COLLECTION_INTERVAL)

    # 수집된 정상 데이터를 사용하여 Isolation Forest 모델을 훈련합니다.
    print("\n-------------------------------------------------")
    print("Isolation Forest 모델 훈련 중...")
    model.fit(normal_data)
    print("모델 훈련 완료.")
    print("-------------------------------------------------")

    # 훈련이 끝나면 차트 데이터 초기화 (이상 감지 데이터만 보기 위함)
    time_data.clear()
    distance_plot_data.clear()
    anomaly_points_x.clear()
    anomaly_points_y.clear()


    print("\n-------------------------------------------------")
    print("실시간 이상 감지 시작!")
    print("-------------------------------------------------")

    # matplotlib 애니메이션 설정 (차트가 주기적으로 업데이트되도록)
    # interval은 밀리초 단위입니다. (예: 500ms마다 업데이트)
    ani = animation.FuncAnimation(fig, update_plot, interval=500, blit=True, cache_frame_data=False)


    # 3. 실시간 이상 감지 루프
    while True:
        current_distance = get_distance()

        if current_distance is not None:
            # 현재 측정값을 모델에 입력할 수 있는 형태로 변환 (2D 배열)
            current_sample = np.array([[current_distance]])
            
            # 모델을 사용하여 현재 샘플이 이상치인지 예측합니다.
            # predict() 메서드는 1 (정상) 또는 -1 (이상치)를 반환합니다.
            prediction = model.predict(current_sample)
            
            # 차트 업데이트를 위한 데이터 추가
            current_time = time.time() - start_overall_time
            time_data.append(current_time)
            distance_plot_data.append(current_distance)
            
            if prediction == -1:
                # 이상치로 감지된 경우
                print(f"[!] 이상 감지: 현재 거리 {current_distance:.2f} cm. 비정상적인 움직임이 감지되었습니다!")
                # 이상치 포인트를 차트에 추가: 빨간색 삼각형으로 명확하게 표시
                anomaly_points_x.append(current_time)
                anomaly_points_y.append(current_distance)
                # 여기에 알림 (예: LED 점등, 경고음 재생 등) 기능을 추가할 수 있습니다.
                # import os; os.system("aplay /path/to/alarm.wav")
            else:
                # 정상으로 감지된 경우
                print(f"정상: 현재 거리 {current_distance:.2f} cm")
        else:
            print("거리 측정 실패 또는 유효하지 않은 값. 재시도합니다.")

        # 애니메이션이 차트 업데이트를 담당하므로 여기서는 짧게 기다립니다.
        time.sleep(0.1) 

except KeyboardInterrupt:
    print("\n프로그램 종료. GPIO 핀 초기화 중...")
    if not SIMULATION_MODE: # 실제 GPIO를 사용했을 경우만 초기화
        GPIO.cleanup()
except Exception as e:
    print(f"오류 발생: {e}")
    if not SIMULATION_MODE: # 실제 GPIO를 사용했을 경우만 초기화
        GPIO.cleanup()


