# # app/kafka_producer.py

# import json
# from kafka import KafkaProducer
# from kafka.errors import KafkaError
# import logging
# import os
# from typing import Optional

# # 로깅 설정
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Docker Compose 설정에 따라 Python 앱이 접속할 브로커 주소
# # 현재 docker-compose.yml의 advertised_listeners를 보면 localhost:9092 또는 localhost:9094를 사용할 수 있습니다.
# # 이전 로그에서 127.0.0.1:9092로 연결 실패했으므로, 다른 옵션을 시도해볼 수 있습니다.
# # 하지만 가장 기본적인 것은 docker-compose에서 호스트로 노출한 포트를 사용하는 것입니다.
# # 현재 ports: - "9092:9092" 가 있으므로, localhost:9092가 타겟입니다.

# # KAFKA_BROKERS 환경 변수를 사용하거나, 기본값으로 'localhost:9092'를 사용합니다.
# # 이전 로그에서 '127.0.0.1:9092'로 시도했으므로, 'localhost:9092'로 명시하는 것이 좋습니다.
# # (일반적으로 localhost와 127.0.0.1은 동일하게 동작하지만, 명시성을 위해)
# KAFKA_BROKERS_STRING = os.getenv("KAFKA_BROKERS", "localhost:9092")
# KAFKA_BROKERS = KAFKA_BROKERS_STRING.split(",")

# producer: Optional[KafkaProducer] = None


# def get_kafka_producer() -> Optional[KafkaProducer]:
#     global producer
#     if producer is None:
#         logger.info(
#             f"Attempting to initialize Kafka Producer with brokers: {KAFKA_BROKERS}"
#         )
#         try:
#             # 시도 1: advertised_listeners의 PLAINTEXT://localhost:9092 를 타겟으로 연결
#             producer = KafkaProducer(
#                 bootstrap_servers=['localhost:9092'],
                
#                 value_serializer=lambda x: json.dumps(x).encode('utf-8'),
#                 api_version=(2, 7, 0),  # Kafka 버전에 맞는 API 버전 설정
#                 acks="all",
#                 retries=3,
#                 request_timeout_ms=10000,  # 연결 및 요청 타임아웃 (ms)
#                 # Kafka 클라이언트가 브로커와 통신할 때 사용할 리스너 이름을 명시적으로 지정할 수 있습니다.
#                 # docker-compose.yml의 KAFKA_CFG_ADVERTISED_LISTENERS에 PLAINTEXT://localhost:9092 가 있으므로,
#                 # 기본적으로 이 주소를 사용하려고 할 것입니다.
#                 # 만약 security_protocol을 명시해야 한다면 추가합니다. (현재는 PLAINTEXT로 가정)
#                 # security_protocol='PLAINTEXT', # 기본값이 PLAINTEXT
#             )
#             logger.info(
#                 f"Kafka Producer initialized successfully (or first attempt made) with brokers: {KAFKA_BROKERS}"
#             )

#         # 만약 위에서 계속 'socket disconnected'가 발생한다면,
#         # Kafka 브로커가 클라이언트에게 다른 주소(예: 내부 Docker 네트워크 주소)를 알려주고 있을 수 있습니다.
#         # 이 경우, Kafka 브로커 설정(KAFKA_CFG_ADVERTISED_LISTENERS)이 클라이언트 환경에 맞게
#         # 정확히 설정되었는지 확인하는 것이 근본적인 해결책입니다.
#         # docker-compose.yml을 변경하지 않는 선에서는, 클라이언트에서 리스너 이름을 명시하는 방법이 있습니다.
#         # 하지만 이는 Kafka 브로KER가 해당 리스너 이름으로 올바른 외부 주소를 advertise하고 있다는 전제하에 동작합니다.
#         # 현재 설정: EXTERNAL://localhost:9094
#         # 이 리스너를 사용하려면 Docker 포트 매핑에 "9094:9094"가 있어야 합니다.
#         # 현재 docker-compose.yml의 ports에는 "9094:9094"가 없습니다.
#         # 따라서 EXTERNAL 리스너는 현재 Python 앱에서 직접 사용할 수 없습니다.

#         except KafkaError as e:
#             logger.error(f"Failed to initialize Kafka Producer with KafkaError: {e}")
#             producer = None  # 초기화 실패 시 None으로 유지
#             # raise # lifespan에서 호출될 때 예외를 다시 발생시켜 문제를 인지하게 할 수 있음
#         except Exception as e:
#             logger.error(
#                 f"An unexpected error occurred during Kafka Producer initialization: {e}"
#             )
#             producer = None  # 초기화 실패 시 None으로 유지
#             # raise

#     if producer is None:
#         logger.warning("Kafka Producer could not be initialized after attempts.")

#     return producer


# # send_kafka_message 및 close_kafka_producer 함수는 변경 없이 그대로 사용 가능합니다.
# # 해당 함수들은 get_kafka_producer()가 반환하는 producer 인스턴스를 사용하기 때문입니다.


# def send_kafka_message(topic: str, message: dict, key: Optional[str] = None):
#     kafka_producer = get_kafka_producer()
#     if not kafka_producer:  # get_kafka_producer()가 None을 반환하면 (초기화 실패)
#         logger.error(
#             f"Kafka producer is not available (failed to initialize). Cannot send message to topic {topic}."
#         )
#         return False
#     # ... (이하 동일) ...
#     try:
#         if key:
#             key_bytes = key.encode("utf-8")
#             future = kafka_producer.send(topic, value=message, key=key_bytes)
#         else:
#             future = kafka_producer.send(topic, value=message)
#         logger.info(f"Message enqueued to topic '{topic}' with key '{key}': {message}")
#         return True
#     except KafkaError as e:
#         logger.error(f"Error sending message to Kafka topic {topic}: {e}")
#     except Exception as e:
#         logger.error(
#             f"An unexpected error occurred while sending message to Kafka: {e}"
#         )
#     return False


# def close_kafka_producer():
#     global producer
#     if producer:
#         try:
#             producer.flush(timeout=10)
#             producer.close(timeout=10)
#             producer = None
#             logger.info("Kafka Producer closed successfully.")
#         except KafkaError as e:
#             logger.error(f"Error closing Kafka Producer: {e}")
#         except Exception as e:
#             logger.error(
#                 f"An unexpected error occurred while closing Kafka Producer: {e}"
#             )
