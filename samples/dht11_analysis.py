# -*- coding: utf-8 -*-
import time
import random
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

SIMULATION = False

# --- DHT11 센서 설정 ---
import board
import adafruit_dht
try:
     dhtDevice = adafruit_dht.DHT11(board.D4)
except Exception as e:
     print(f"센서 초기화 오류: {e}")
     dhtDevice = None

def setup_korean_font():
    """
    matplotlib에서 한글을 지원하기 위한 폰트 설정 함수
    """
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf' # Linux (나눔고딕)

    try:
        font_prop = fm.FontProperties(fname=font_path, size=12)
        plt.rc('font', family=font_prop.get_name())
        plt.rc('axes', unicode_minus=False) # 마이너스 부호 깨짐 방지
        print("한글 폰트가 설정되었습니다.")
    except FileNotFoundError:
        print("지정된 경로에 폰트 파일이 없습니다. 기본 폰트로 실행됩니다.")
        print("차트의 한글이 깨질 수 있습니다. 폰트 경로를 확인해주세요.")

def read_dht11_sensor():
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
                # DHT 센서 가끔 읽기 오류 발생
                print(f"센서 읽기 오류: {error.args[0]}")
                return None, None
        return None, None
    else:
        # --- 시뮬레이션 코드 ---
        # 실제 센서가 없을 경우, 아래 코드가 가상의 데이터를 생성
        temp = 20 + (5 * (1 + np.sin(time.time() / 60))) + random.uniform(-0.5, 0.5)
        hum = 50 + (10 * (1 + np.cos(time.time() / 90))) + random.uniform(-1, 1)
        return round(temp, 1), round(hum, 1)

def update_plot(df, predicted_temp=None):
    plt.clf() # 이전 차트 지우기
    
    # 시간 경과에 따른 온도와 습도 변화
    plt.plot(df.index, df['temperature'], marker='o', linestyle='-', label='온도 (°C)')
    plt.plot(df.index, df['humidity'], marker='s', linestyle='--', label='습도 (%)')
    
    # AI 예측값 표시 (예측이 시작되었을 경우)
    if predicted_temp is not None and not df.empty:
        # 예측값은 다음 시간 단계에 대한 것이므로 마지막 인덱스 + 1 위치에 표시
        plt.plot(df.index[-1] + 1, predicted_temp, 'r*', markersize=10, label=f'AI 예측 온도 ({predicted_temp:.2f}°C)')

    plt.title('DHT11 센서 데이터 및 AI 온도 예측')
    plt.xlabel('시간 경과 (샘플 번호)')
    plt.ylabel('값')
    plt.legend() # 범례 표시
    plt.grid(True)
    plt.tight_layout() # 레이아웃 최적화
    plt.pause(0.01) # 차트를 업데이트하고 잠시 대기

def main():
    """
    메인 로직: 데이터를 수집하고 AI 모델을 훈련하여 온도를 예측하고 시각화합니다.
    """
    setup_korean_font()
    print("DHT11 센서 데이터 AI 분석 프로그램을 시작합니다.")
    print("매 2초마다 데이터를 수집하여 다음 온도를 예측하고 차트를 업데이트합니다.")
    print("-" * 50)
    
    # 데이터를 저장할 pandas DataFrame 생성
    columns = ['timestamp', 'temperature', 'humidity', 'next_temp']
    data_df = pd.DataFrame(columns=columns)
    
    # AI 모델 초기화 (선형 회귀)
    model = LinearRegression()
    # 모델 훈련에 필요한 최소 데이터 개수
    min_data_for_training = 10 
    # 실시간 차트 설정
    plt.ion() # 인터랙티브 모드 켜기
    fig = plt.figure(figsize=(10, 6))

    try:
        while True:
            # 1. 데이터 수집
            temperature, humidity = read_dht11_sensor()
            last_prediction = None
            
            if temperature is not None and humidity is not None:
                timestamp = time.time()
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 현재 상태: 온도={temperature}°C, 습도={humidity}%")
                
                if not data_df.empty:
                    data_df.loc[data_df.index[-1], 'next_temp'] = temperature

                new_row = {'timestamp': timestamp, 'temperature': temperature, 'humidity': humidity, 'next_temp': np.nan}
                data_df = pd.concat([data_df, pd.DataFrame([new_row])], ignore_index=True)

                # 2. AI 모델 훈련 및 예측
                train_data = data_df.dropna()
                
                if len(train_data) >= min_data_for_training:
                    X_train = train_data[['temperature', 'humidity']]
                    y_train = train_data['next_temp']
                    model.fit(X_train, y_train)
                    
                    current_features = np.array([[temperature, humidity]])
                    predicted_temp = model.predict(current_features)[0]
                    last_prediction = predicted_temp
                    
                    print(f">> AI 예측: 다음 온도는 약 {predicted_temp:.2f}°C 로 예상됩니다.")
                
                else:
                    print(f"데이터 수집 중... ({len(train_data)}/{min_data_for_training})")

                # 3. 실시간 차트 업데이트
                update_plot(data_df, last_prediction)

            else:
                print("센서로부터 데이터를 읽어오지 못했습니다.")
            
            print("-" * 50)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        print("수집된 데이터:")
        print(data_df)
    finally:
        plt.ioff() # 인터랙티브 모드 끄기
        if not data_df.empty:
            print("\n최종 차트를 표시합니다. 창을 닫으면 프로그램이 종료됩니다.")
            update_plot(data_df)
            plt.show() # 프로그램 종료 전 최종 차트 보여주기

if __name__ == '__main__':
    main()

