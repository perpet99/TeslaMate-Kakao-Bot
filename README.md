# 테슬라메이트 카카오봇

이 프로젝트는 테슬라메이트를 이용하여 차량의 변경된 정보를 자신의 카톡에 알려주는 프로젝트 입니다.

해당 프로젝트는 아래 프로젝트를 기반으로 만들어졌습니다.

https://github.com/JakobLichterfeld/TeslaMate-Telegram-Bot

테슬라메이트 사용자 및 문의 방
https://open.kakao.com/o/glqIjMIh


## 데모동영상


## 기능

- [x] 테슬라 온라인 상태 유무
- [x] 테슬라 주행시작 종료 알람
- [x] 테슬라 주행시작 종료 알람
- [x] 테슬라 주행경로 맵
- [ ] 전비 계산
- [ ] 홈주소 및 도착 예상시간

## 요구사항

- 친구추가=>카카오톡 ID=> "pushbot" => 추가
- 1:1 대화 또는 그룹방에 초대
- 채팅방에 "/방키" 입력 하여 [방키]값 확인
  
## Installation

- 테슬라 메이트와 같은 네트워크 환경에 구축 및 테스트

### 카카오톡 방키 확인

- 친구추가=>카카오톡 ID=> "pushbot" => 추가
- 1:1 대화 또는 그룹방에 초대
- 채팅방에 "/방키" 입력 하여 [방키]값 확인

### MQTT IP 확인

- MQTT 컨테이너 생성시 기본포트 1883 포트를 외부에서 접속하도록 설정합니다

### 테스트 빌드

- teslamate_kakao_bot.py 파일 수정
   ```
   SEND_KAKAO_URL='https://perpet.synology.me:5050/kakao/[방키]'
   GET_KAKAO_URL='https://perpet.synology.me:5050/kakaoget/[방키]'
   MQTT_BROKER_HOST=[설치된 MQTT 호스트 IP 또는 내부 컨테이너 아이피]
   ```
- python -m venv myven
- linux , Mac => source myven/bin/activate
- 윈도우즈 => myven/Scripts/activate
- python -m pip install -r ./src/requirements.txt
- python .\src\teslamate_kakao_bot.py

### 도커설치

전문가가 아니면 테슬라 메이트와 같은 네트워크에 환경 구축하세요

도커 설치전 카카오톡 방키 확인

1. `docker-compose.yml` 파일을 생성하고 아래 내용을 입력합니다. 

   ```yml title="docker-compose.yml"
      services:
        teslamatekabot:
          image: perpet77/teslamate-kakao-bot:latest
          restart: unless-stopped
          environment:
            # - CAR_ID=1 # optional, defaults to 1
            - MQTT_BROKER_HOST=mosquitto # defaults to 127.0.0.1
            # - MQTT_BROKER_PORT=1883 #optional, defaults to 1883
            # - MQTT_BROKER_USERNAME=username #optional, only needed when broker has authentication enabled
            # - MQTT_BROKER_PASSWORD=password #optional, only needed when broker has authentication enabled
            # - MQTT_NAMESPACE=namespace # optional, only needed when you specified MQTT_NAMESPACE on your TeslaMate installation
            # 카톡에서 /방키를 받아서 아래 방키를 입력하세요
            - SEND_KAKAO_URL=https://perpet.synology.me:5050/kakao/[방키]
            - GET_KAKAO_URL=https://perpet.synology.me:5050/kakaoget/[방키]
          ports:
            - 1883
   ```

2. 빌드 도커 실행 `docker compose up`. 백그라운드 실행은 `-d` flag:

   ```bash
   docker compose up -d
   ```
### 도커설치 도커빌드

docker build -t perpet77/teslamate-kakao-bot:latest .

docker push perpet77/teslamate-kakao-bot:latest
## 업데이트

Pull the new images:

```bash
docker compose pull
```

and restart the stack with `docker compose up`. To run the containers in the background add the `-d` flag:

```bash
docker compose up -d
```

## 중요사항

Tesla는 Tesla API 전반, 특히 이 소프트웨어의 사용을 보증하지 않습니다. 사용에 따른 모든 책임은 사용자에게 있습니다.

