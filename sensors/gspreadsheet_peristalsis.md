# Google SpreadSheet 데이터 연동

## 구글 드라이브 설정


## 연동 테스트

#### 환경 설정

1. google spreadsheert oauth 인증키 다운로드

- 구글 드라이브 api 인증키 다운로드
```
    # wget https://175.198.234.166/media/thermal-shuttle-462907-n3-67e56bbfe64c.json
```

2. 구글 드라이드 스프레드시트 URL

    url : https://docs.google.com/spreadsheets/d/1e5729Xo60oVCM6nnpcjSVp3KTZp8UeVy2UosJTZ0C8s/edit?usp=sharing

3. 실행

- 예시
```python
    cd aiot_project
    cd sensors
    wget https://175.198.234.166/media/thermal-shuttle-462907-n3-67e56bbfe64c.json
    python dht11_gspread.py
```

4. 확인 
-
![Alt text](https://raw.githubusercontent.com/neeverse-dev1/aiot_project/refs/heads/main/sensors/capture_gspread_1.png)
