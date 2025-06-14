# -*- coding: utf-8 -*-
import time
import random
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# --- 가상 DHT11 센서 설정 ---
# 실제 라즈베리파이와 DHT11 센서가 있다면 이 부분을 주석 해제하고 사용하세요.
import board
import adafruit_dht
try:
     dhtDevice = adafruit_dht.DHT11(board.D4) # GPIO 4번 핀에 연결된 경우
except Exception as e:
     print(f"센서 초기화 오류: {e}")
     dhtDevice = None

def read_dht11_sensor():
    """
    실제 DHT11 센서로부터 온도와 습도를 읽어오는 함수입니다.
    성공 시 (온도, 습도) 튜플을, 실패 시 (None, None)을 반환합니다.
    """
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
    
    # --- 시뮬레이션 코드 시작 ---
    # 실제 센서가 없을 경우, 아래 코드가 가상의 데이터를 생성합니다.
    # 현실적인 데이터처럼 보이도록 약간의 노이즈를 추가합니다.
    # temp = 20 + (5 * (1 + np.sin(time.time() / 60))) + random.uniform(-0.5, 0.5)
    # hum = 50 + (10 * (1 + np.cos(time.time() / 90))) + random.uniform(-1, 1)
    #return round(temp, 1), round(hum, 1)
    # --- 시뮬레이션 코드 끝 ---


def main():
    """
    메인 로직: 데이터를 수집하고 AI 모델을 훈련하여 온도를 예측합니다.
    """
    print("DHT11 센서 데이터 AI 분석 프로그램을 시작합니다.")
    print("매 2초마다 데이터를 수집하여 다음 온도를 예측합니다.")
    print("-" * 50)
    
    # 데이터를 저장할 pandas DataFrame 생성
    columns = ['timestamp', 'temperature', 'humidity', 'next_temp']
    data_df = pd.DataFrame(columns=columns)
    
    # AI 모델 초기화 (선형 회귀)
    model = LinearRegression()
    
    min_data_for_training = 10 # 모델 훈련에 필요한 최소 데이터 개수

    try:
        while True:
            # 1. 데이터 수집
            temperature, humidity = read_dht11_sensor()
            
            if temperature is not None and humidity is not None:
                timestamp = time.time()
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 현재 상태: 온도={temperature}°C, 습도={humidity}%")
                
                # 이전 데이터의 'next_temp'를 현재 온도로 업데이트
                if not data_df.empty:
                    data_df.loc[data_df.index[-1], 'next_temp'] = temperature

                # 새 데이터 추가
                new_row = {'timestamp': timestamp, 'temperature': temperature, 'humidity': humidity, 'next_temp': np.nan}
                data_df = pd.concat([data_df, pd.DataFrame([new_row])], ignore_index=True)

                # 2. AI 모델 훈련 및 예측
                # 훈련용 데이터가 충분히 쌓였는지 확인
                # (마지막 행은 target(next_temp)이 없으므로 제외)
                train_data = data_df.dropna()
                
                if len(train_data) >= min_data_for_training:
                    # 입력(X)과 목표(y) 데이터 분리
                    X_train = train_data[['temperature', 'humidity']] # 훈련용 입력: 현재 온도, 습도
                    y_train = train_data['next_temp'] # 훈련용 목표: 다음 시점의 온도

                    # 모델 훈련
                    model.fit(X_train, y_train)
                    
                    # 현재 데이터로 다음 온도 예측
                    current_features = np.array([[temperature, humidity]])
                    predicted_temp = model.predict(current_features)
                    
                    print(f"✨ AI 예측: 다음 온도는 약 {predicted_temp[0]:.2f}°C 로 예상됩니다.")
                
                else:
                    print(f"데이터 수집 중... ({len(train_data)}/{min_data_for_training})")

            else:
                print("센서로부터 데이터를 읽어오지 못했습니다.")
            
            print("-" * 50)
            # 2초 대기
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        print("수집된 데이터:")
        print(data_df)

if __name__ == '__main__':
    main()

