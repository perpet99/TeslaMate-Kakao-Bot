""" A simple Telegram bot that listens to MQTT messages from Teslamate
and sends them to a Telegram chat."""
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import asyncio
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from teslaLib import TeslaLib

# from telegram import Bot
# from telegram.constants import ParseMode

##############################################################################

# Default values
CAR_ID_DEFAULT = 1
MQTT_BROKER_HOST_DEFAULT = '127.0.0.1'
MQTT_BROKER_PORT_DEFAULT = 1883
MQTT_BROKER_KEEPALIVE = 60
MQTT_BROKER_USERNAME_DEFAULT = ''
MQTT_BROKER_PASSWORD_DEFAULT = ''
MQTT_NAMESPACE_DEFAULT = ''
TESLA_EVENTS_DEFAULT = [{'event':'전체알람', 'alarm': True,"eventValue":""},
                        {'event':'드라이브', 'alarm': True,"eventValue":""},
                        {'event':'state', 'alarm': True,"eventValue":""},
                        {'event':'sentry_mode', 'alarm': True,"eventValue":""}]

# Environment variables
SEND_KAKAO_URL = 'SEND_KAKAO_URL'
GET_KAKAO_URL = 'GET_KAKAO_URL'
TESLA_EVENTS = 'TESLA_EVENTS'
# TELEGRAM_BOT_CHAT_ID = 'TELEGRAM_BOT_CHAT_ID'
MQTT_BROKER_USERNAME = 'MQTT_BROKER_USERNAME'
MQTT_BROKER_PASSWORD = 'MQTT_BROKER_PASSWORD'
MQTT_BROKER_HOST = 'MQTT_BROKER_HOST'
MQTT_BROKER_PORT = 'MQTT_BROKER_PORT'
MQTT_NAMESPACE = 'MQTT_NAMESPACE'
CAR_ID = 'CAR_ID'

##############################################################################
load_dotenv()

# Logging
# Configure the logging module to output info level logs and above
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 로그 폴더 경로 설정
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # 폴더 없으면 자동 생성

# 로그 파일 경로 (기본 파일명)
# log_file = os.path.join(log_dir, "app.log")

# 오늘 날짜를 파일명으로 지정
today = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(log_dir, f"{today}.log")

# 핸들러 설정: 자정마다 로그 분할, 최대 7일 보관
handler = TimedRotatingFileHandler(
    filename=log_file,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
handler.suffix = "%Y-%m-%d"  # 날짜 형식 지정

# 포맷 설정
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


# 콘솔 출력 핸들러
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# 로거 설정
logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(console)

# Global state
class State:
    """ A class to hold the global state of the application."""
    def __init__(self):
        self.update_available = False               # Flag to indicate if an update is available
        self.update_available_message_sent = False  # Flag to indicate if the message has been sent
        self.update_version = "unknown"             # The version of the update
        self.events = []
        self.getKakao_url = ""
        self.sendKakao_url = ""
        
# Global state
state = State()
teslaLib = TeslaLib()

def get_env_variable(var_name, default_value=None):
    """ Get the environment variable or return a default value"""
def get_env_variable(var_name, default_value=None):
    """ Get the environment variable or return a default value"""
    logger.debug("Getting environment variable %s", var_name)
    var_value = os.getenv(var_name, default_value)
    logger.debug("Environment variable %s: %s", var_name, var_value)
    if var_value is None and var_name in [SEND_KAKAO_URL,GET_KAKAO_URL]:
        error_message_get_env_variable = f"Error: Please set the environment variable {var_name} and try again."
        raise EnvironmentError(error_message_get_env_variable)
    return var_value


# MQTT topics
try:
    car_id = int(get_env_variable(CAR_ID, CAR_ID_DEFAULT))
except ValueError as value_error_car_id:
    ERROR_MESSAGE_CAR_ID = (f"Error: Please set the environment variable {CAR_ID} "
                            f"to a valid number and try again.")
    raise EnvironmentError(ERROR_MESSAGE_CAR_ID) from value_error_car_id

namespace = get_env_variable(MQTT_NAMESPACE, MQTT_NAMESPACE_DEFAULT)
if namespace:
    logger.info("Using MQTT namespace: %s", namespace)
    TESLAMATE_MQTT_TOPIC_BASE = f"teslamate/{namespace}/cars/{car_id}/"
else:
    TESLAMATE_MQTT_TOPIC_BASE = f"teslamate/cars/{car_id}/"

TESLAMATE_MQTT_TOPIC_UPDATE_AVAILABLE = TESLAMATE_MQTT_TOPIC_BASE + "update_available"
TESLAMATE_MQTT_TOPIC_UPDATE_VERSION = TESLAMATE_MQTT_TOPIC_BASE + "update_version"


def on_connect(client, userdata, flags, reason_code, properties=None):  # pylint: disable=unused-argument
    """ The callback for when the client receives a CONNACK response from the server."""
    logger.debug("Connected with result code: %s", reason_code)
    if reason_code == "Unsupported protocol version":
        logger.error("Unsupported protocol version")
        client_status = "Unsupported protocol version"
        send_kakao_message(state.sendKakao_url, f"테슬라 메이트 접속실패(Unsupported protocol version)")
        sys.exit(1)
    if reason_code == "Client identifier not valid":
        logger.error("Client identifier not valid")
        client_status = "Client identifier not valid"
        send_kakao_message(state.sendKakao_url, f"테슬라 메이트 접속실패(Client identifier not valid)")
        sys.exit(1)
    if reason_code == 0:
        client_status = "접속완료"
        send_kakao_message(state.sendKakao_url, f"테슬라 메이트 접속성공")
        logger.info("Connected successfully to MQTT broker")
    else:
        send_kakao_message(state.sendKakao_url, f"테슬라 메이트 접속실패(Connection failed)")
        client_status = "Connection failed"
        logger.error("Connection failed")
        sys.exit(1)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    logger.info("Subscribing to MQTT topics:")

    # client.subscribe(TESLAMATE_MQTT_TOPIC_UPDATE_AVAILABLE)
    # logging.info("Subscribed to MQTT topic: %s", TESLAMATE_MQTT_TOPIC_UPDATE_AVAILABLE)

    # client.subscribe(TESLAMATE_MQTT_TOPIC_UPDATE_VERSION)
    # logging.info("Subscribed to MQTT topic: %s", TESLAMATE_MQTT_TOPIC_UPDATE_VERSION)

    # Subscribe to all MQTT topics (wildcard)
    client.subscribe("#")
    logger.info("Subscribed to all MQTT topics with wildcard '#'.")

    logger.info("Waiting for MQTT messages...")


def on_message(client, userdata, msg):  # pylint: disable=unused-argument
    """ The callback for when a PUBLISH message is received from the server."""
    global state  # pylint: disable=global-variable-not-assigned, # noqa: F824
    logger.info("Received message: %s %s", msg.topic, msg.payload.decode())

    try:
        
        
        oldState = teslaLib.isDriving
        
        teslaLib.update()

        
        if teslaLib.isDriving != oldState:
            if teslaLib.isDriving:
                send_kakao_message(state.sendKakao_url, f"드라이브 : 주행정지 => 주행시작")
            else :
                send_kakao_message(state.sendKakao_url, f"드라이브 : 주행시작 => 주행정지")
                pathUrl = teslaLib.getPathUrlNClear()
                send_kakao_message(state.sendKakao_url, f"드라이브경로 : {pathUrl}")

        
        for i, item in  enumerate(state.events):
            event = item["event"]
            
            
            if event == "전체알람" and item["alarm"] == False:
                break
            if event == "드라이브":
                if teslaLib.isDriving:
                    item["eventValue"] = "주행중"
                else:
                    item["eventValue"] = "주차중"
            
            eventValue = msg.payload.decode()
            
            if msg.topic == TESLAMATE_MQTT_TOPIC_BASE+ "speed":
                
                teslaLib.updatePower(int(eventValue))
                
            
            
                    
            if msg.topic == TESLAMATE_MQTT_TOPIC_BASE+ "location":
                teslaLib.updateLocation(eventValue)
                return
            
            if item["alarm"] == True and msg.topic == TESLAMATE_MQTT_TOPIC_BASE + event and item["eventValue"] != eventValue:
                oldEventValue = item["eventValue"]
                item["eventValue"] = eventValue
                logger.info("값변경 : %s %s", msg.topic, msg.payload.decode())
                saveData(state.events)
                send_kakao_message(state.sendKakao_url, f"{event} : {oldEventValue} => {eventValue}")
                
                
    except Exception as e :
        logger.info(f"Received error : {e}")
    # if msg.topic == TESLAMATE_MQTT_TOPIC_UPDATE_VERSION:
    #     state.update_version = msg.payload.decode()
    #     logging.info("Update to version %s available.", state.update_version)

    # if msg.topic == TESLAMATE_MQTT_TOPIC_UPDATE_AVAILABLE:
    #     state.update_available = msg.payload.decode() == "true"
    #     if msg.payload.decode() == "true":
    #         logging.info("A new SW update to version: %s for your Tesla is available!", state.update_version)
    #     if msg.payload.decode() == "false":
    #         logging.debug("No SW update available.")
    #         state.update_available_message_sent = False  # Reset the message sent flag


# 전역 상태 변수 추가
client_status = "접속중"

# def on_connect(client, userdata, flags, reason_code, properties=None):
#     global client_status
#     if reason_code == 0:
#         client_status = "접속완료"
#     else:
#         client_status = "접속실패"
    # ...existing code...

def on_disconnect(client, userdata, reason_code, properties=None):
    global client_status
    client_status = "접속실패"
    send_kakao_message(state.sendKakao_url, f"테슬라 메이트 접속실패")
    logger.info("MQTT disconnected. Reason: %s", reason_code)

def get_mqtt_status():
    """Return the current MQTT client status."""
    return client_status

def setup_mqtt_client():
    """ Setup the MQTT client """
    logger.info("Setting up the MQTT client...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    username = get_env_variable(MQTT_BROKER_USERNAME, MQTT_BROKER_USERNAME_DEFAULT)
    password = get_env_variable(MQTT_BROKER_PASSWORD, MQTT_BROKER_PASSWORD_DEFAULT)
    client.username_pw_set(username, password)

    host = get_env_variable(MQTT_BROKER_HOST, MQTT_BROKER_HOST_DEFAULT)
    try:
        port = int(get_env_variable(MQTT_BROKER_PORT, MQTT_BROKER_PORT_DEFAULT))
    except ValueError as value_error_mqtt_broker_port:
        error_message_mqtt_broker_port = (f"Error: Please set the environment variable {MQTT_BROKER_PORT} "
                                          f"to a valid number and try again."
                                          )
        raise EnvironmentError(error_message_mqtt_broker_port) from value_error_mqtt_broker_port
    logger.info("Connect to MQTT broker at %s:%s", host, port)
    send_kakao_message(state.sendKakao_url, f"테슬라메이트 접속시도({host}:{port})")
    

    client.connect(host, port, MQTT_BROKER_KEEPALIVE)

    return client


# def setup_telegram_bot():
#     """ Setup the Telegram bot """
#     logging.info("Setting up the Telegram bot...")
#     bot = Bot(get_env_variable(TELEGRAM_BOT_API_KEY))
#     try:
#         chat_id = int(get_env_variable(TELEGRAM_BOT_CHAT_ID))
#     except ValueError as value_error_chat_id:
#         error_message_chat_id = (f"Error: Please set the environment variable {TELEGRAM_BOT_CHAT_ID} "
#                                  f"to a valid number and try again."
#                                  )
#         raise EnvironmentError(error_message_chat_id) from value_error_chat_id

#     logging.info("Connected to Telegram bot successfully.")
#     return bot, chat_id

def sendEventList():
    sendMessage = "알람리스트\n"
    sendMessage += f"[이벤트] : [상태] : [알람]\n"
    for item in state.events:
        event = item["event"]
        eventValue = item["eventValue"]
        alarm = item["alarm"]
        
        sendMessage += f"[{event}] [{eventValue}] [{str(alarm)}]\n"
    send_kakao_message( state.sendKakao_url,sendMessage)
    

# def saveNSendEventList():
#     saveData(state.events)
#     sandEventList()

async def check_state_and_send_messages(url):
    
    
    try:
        messageList = send_kakao_message(state.getKakao_url,"")
        
        if  len(messageList) == 0:
            return
        
        for msg in messageList:
            try:
                parts = msg.split(",", 1)
                alarm = True
                if parts[0] == '/알람켜기':
                    alarm = True
                elif parts[0] == '/알람끄기':
                    alarm = False
                elif parts[0] == '/알람리스트':
                    sendHowTouse()
                    continue
                else:
                    sendHowTouse()
                    continue
                 
                for item in state.events:
                    if item["event"] == parts[1]:
                        item["alarm"] = alarm
                        parts[1] = ""
                        sendEventList()
                        saveData(state.events)
                if parts[1] == "":
                    continue
                state.events.append({"event":parts[1],"alarm":alarm,"eventValue":""})
                sendEventList()
                saveData(state.events)
                
            except Exception  as e:
                logger.info(f"파싱 실패 : {e}")    
        
    except Exception  as e:
        sendHowTouse()
        # await asyncio.sleep(1)
        # saveNSendEventList()
        logger.info(f"메시지 받기 실패 : {e}")
    
    
    # """ Check the state and send messages if necessary """
    # logging.info("Checking state and sending messages...")
    # global state  # pylint: disable=global-variable-not-assigned, # noqa: F824

    # if state.update_available and not state.update_available_message_sent:
    #     logging.info("Update available and message not sent.")
    #     if state.update_version not in ("unknown", ""):
    #         logging.info("A new SW update to version: %s for your Tesla is available!", state.update_version)
    #         message_text = "<b>" \
    #             "SW Update 🎁" \
    #             "</b>\n" \
    #             "A new SW update to version: " \
    #             + state.update_version \
    #             + " for your Tesla is available!"
    #         await send_kakao_message(url, message_text)

    #         # Mark the message as sent
    #         state.update_available_message_sent = True
    #         logging.debug("Message sent flag set.")



def send_kakao_message(webhook_url, message):
    try:
        # state_message = ""
        # if get_mqtt_status() != "접속중":
        #     state_message = "테슬라 메이트 " + get_mqtt_status()
            
        data = {
            "content": message  # 디스코드 채널에 표시될 메시지
        }
        # logger.info(f"쿼리시작{webhook_url}")
        response = requests.post(webhook_url, json=data,timeout=5)
        if response.status_code != 201:
            logger.info(f"쿼리에러{response.status_code}")  
            return []
        
        # logger.info(f"쿼리종료{response.status_code}")
        # logging.debug(f"응답 코드: {response.status_code}")
        
        return response.json()
    except Exception as e:
        logger.info(f"서버응답실패{webhook_url}")
        logger.info(f"{e}")
    return []
# async def send_telegram_message_to_chat_id(bot, chat_id, message_text_to_send):
#     """ Send a message to a chat ID """
#     logging.debug("Sending message.")
#     await bot.send_message(
#             chat_id,
#             text=message_text_to_send,
#             parse_mode=ParseMode.HTML,
#         )
#     logging.debug("Message sent.")

configFileName = 'data.json'

def loadData():
    if os.path.exists(configFileName) == False:
        return None
    with open(configFileName, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data
    return None

def saveData(data):
    with open(configFileName, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    
def sendHowTouse():
    start_message = "테슬라메이트 연동 카카오봇 시작\n" \
            "명령어\n" \
            "/알람리스트\n" \
            "/알람끄기,[이벤트이름]\n" \
            "/알람켜기,[이벤트이름]\n" \
            "/알람끄기,state <= 차량상태 이벤트 끄기 \n" \
            "/알람끄기,전체알람 <= 모든 이벤트 끄기"
                        
                
    send_kakao_message(state.sendKakao_url, start_message)
    sendEventList()
# Main function
async def main():
    """ Main function"""
    logger.info("카카오봇 시작.")
    
    try:
        
        state.sendKakao_url = get_env_variable(SEND_KAKAO_URL)
        state.getKakao_url= get_env_variable(GET_KAKAO_URL)
        
        state.events = loadData()
        if state.events == None:
            # state.events = TESLA_EVENTS_DEFAULT
            state.events = get_env_variable(TESLA_EVENTS,TESLA_EVENTS_DEFAULT)
        
        logger.info (state.events)
        
        sendHowTouse()
    
        client = setup_mqtt_client()
        client.loop_start()
    
        try:
            count = 0
            while True:
                
                await check_state_and_send_messages(state.sendKakao_url)

                logging.debug("Sleeping for 5 second.")
                await asyncio.sleep(5)
        except KeyboardInterrupt:
            logger.info("Exiting after receiving SIGINT (Ctrl+C) signal.")
    except EnvironmentError as e:
        logger.error(e)
        send_kakao_message(state.sendKakao_url, f"카톡봇 에러  {e}")
        send_kakao_message(state.sendKakao_url, f"테슬라 접속상태({get_mqtt_status()})")
        logger.info("Sleeping for 30 seconds before exiting or restarting, depending on your restart policy.")
        await asyncio.sleep(30)

    # clean exit
    logger.info("Disconnecting from MQTT broker.")
    client.disconnect()
    logger.info("Disconnected from MQTT broker.")
    client.loop_stop()
    logger.info("Exiting the Teslamate Telegram bot.")
    stop_message = "테슬라메이트 카톡봇 정지"
    send_kakao_message(state.sendKakao_url, stop_message)
    # await bot.close()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
