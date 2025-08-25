import logging
import os
import json
import socket

import logstash
from logging import Formatter


class LogstashJsonFormatter(Formatter):
    """로그스태시용 JSON 포맷터"""

    def __init__(self, logger_name):
        super().__init__()
        self.logger_name = logger_name

    def format(self, record):
        # 원본 메시지 가져오기
        message = record.getMessage()

        # JSON 형식으로 변환
        try:
            # 이미 JSON 문자열인 경우 파싱
            if isinstance(message, str) and (
                message.startswith("{") and message.endswith("}")
            ):
                try:
                    data = json.loads(message)
                    if isinstance(data, dict):
                        return json.dumps(data)
                except (json.JSONDecodeError, TypeError):
                    pass  # JSON이 아니면 다음 단계로 진행

            # 일반 문자열인 경우 JSON 객체로 변환
            log_data = {
                "message": message,
                "logger_name": self.logger_name,
                "host": socket.gethostname(),
                "level": record.levelname,
                "pathname": record.pathname,
                "lineno": record.lineno,
                "type": "python-log",  # 로그 타입 지정
                "app": "tricorn_app_server",  # 애플리케이션 이름
                "@timestamp": record.created,  # 타임스탬프 필드 추가
            }
            return json.dumps(log_data)
        except Exception as e:
            # 포맷팅 중 오류 발생 시 대체 메시지 반환
            return f'{{"message": "{message}", "format_error": "{str(e)}"}}'


class Logger(object):
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

        # 기본 로그 레벨 설정
        log_level = logging.DEBUG
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s][%(levelname)s|%(name)s|%(filename)s:%(lineno)s] %(message)s",
        )

        # 로그스태시 핸들러 설정
        logstash_host = os.getenv("LOGSTASH_URL")
        print(f"LOGSTASH_URL: {logstash_host}")
        if logstash_host:
            # 로그스태시 핸들러 생성 및 설정
            logstash_handler = logstash.TCPLogstashHandler(
                host=logstash_host,
                port=50000,
                version=1,
                message_type="logstash",  # 메시지 타입 지정
                fqdn=False,  # FQDN 대신 hostname 사용
                tags=["python", "tricorn_app_server"],  # 태그 추가
            )

            # 로그스태시용 JSON 포맷터 적용
            logstash_handler.setFormatter(LogstashJsonFormatter(name))
            logstash_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(logstash_handler)

    def d(self, msg: str):
        self.logger.debug(msg)

    def i(self, msg: str):
        self.logger.info(msg)

    def w(self, msg: str):
        self.logger.warning(msg)

    def e(self, msg: str):
        self.logger.error(msg)


logger = Logger("tricorn_app_server")
