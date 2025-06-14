# 라즈베리파이 센서 설치 및 사용방법

> 주의사항:
> - **64비트 호환성**: Adafruit CircuitPython DHT 라이브러리 문서에 따르면, "The library may or may not work in Linux 64-bit platforms." (라이브러리가 리눅스 64비트 플랫폼에서 작동할 수도 있고 안 할 수도 있습니다.) 라고 명시되어 있습니다. 대부분의 경우 잘 작동하지만, 문제가 발생할 수 있음을 인지해야 한다.
> - Wormbook: "Wormbook"은 일반적인 라즈베리파이 운영체제 이름이 아니므로, 아마도 사용자 정의 OS나 특정 배포판을 의미하는 것으로 보입니다. 일반적인 Debian 기반의 Raspberry Pi OS (예: Bookworm)를 사용한다고 가정하고 설명합니다. 다른 OS라면 일부 명령어가 다를 수 있습니다.


- 라즈베리파이 4 핀 맵

![Alt text](https://www.raspberrypi.com/documentation/computers/images/GPIO-Pinout-Diagram-2.png?hash=df7d7847c57a1ca6d5b2617695de6d46)

## DHT11 센서 

### 설치 단계:

#### 1. 시스템 업데이트:
가장 먼저 시스템 패키지 목록을 업데이트하고 기존 패키지를 업그레이드하여 최신 상태를 유지합니다.

```
sudo apt update
sudo apt upgrade -y
```

#### 2. 필수 패키지 설치:
Python 개발에 필요한 python3, python3-pip, python3-venv 패키지를 설치합니다. pip는 Python 패키지 관리자이고, venv는 가상 환경을 만드는 데 사용됩니다.

```
sudo apt install python3 python3-pip python3-venv -y
```

#### 3. GPIO 그룹에 사용자 추가 (권장):
DHT 센서와 같이 GPIO (General Purpose Input/Output) 핀에 접근해야 하는 경우, 현재 사용자를 gpio 그룹에 추가해야 할 수 있습니다. 이렇게 하면 sudo 없이도 GPIO 핀에 접근할 수 있습니다.

```
sudo usermod -a -G gpio $USER
```
이 변경 사항을 적용하려면 재부팅하거나 로그아웃 후 다시 로그인해야 합니다.

#### 4. 가상 환경 생성 (권장):
Python 프로젝트를 위한 가상 환경을 사용하는 것은 좋은 습관입니다. 이렇게 하면 시스템 전체의 Python 설치와 라이브러리 충돌을 피할 수 있습니다.

```
mkdir ~/aiot_project  # 프로젝트 폴더 생성 (원하는 이름으로 변경 가능)
cd ~/aiot_project
python3 -m venv .venv # .venv라는 이름으로 가상 환경 생성
```

#### 5. 가상 환경 활성화:
가상 환경을 생성한 후에는 이를 활성화해야 합니다. 프롬프트가 (.venv)와 같이 변경되어 가상 환경이 활성화되었음을 나타냅니다.

```
source .venv/bin/activate
```
팁: 터미널을 닫았다가 다시 열면 가상 환경이 비활성화됩니다. 스크립트를 실행할 때마다 이 명령을 다시 실행해야 합니다.

#### 6. Adafruit CircuitPython DHT 라이브러리 설치:
가상 환경이 활성화된 상태에서 pip를 사용하여 adafruit-circuitpython-dht 패키지를 설치합니다. 이 패키지는 Adafruit_DHT의 최신 버전이자 권장되는 대안입니다.

```
pip install adafruit-circuitpython-dht
```

또는, sudo와 함께 시스템 전체에 설치하려면 (가상 환경을 사용하지 않는 경우):

```
sudo pip3 install adafruit-circuitpython-dht
```
참고: 이전 Adafruit_Python_DHT 라이브러리는 더 이상 활발하게 개발되지 않습니다. adafruit-
