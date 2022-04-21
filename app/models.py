from enum import Enum

from pydantic import BaseModel, Field


class Measurement():
    """
    Класс для представления последнего измерения снятого с узла
    """

    def __init__(self, node_id, display_name=None, value_type=None, last_value=None, health_is_good: bool = False):
        """
        :param node_id: Строкове предствление node id узла
        :param display_name: Имя узла, отображаемое в OPC-сервере
        :param value_type: Тип данных (enum)
        :param last_value: Последнее значение
        :param health_is_good: Здоровье узла
        """
        self.node_id = node_id
        self.display_name = display_name
        self.value_type = value_type
        self.last_value = last_value
        self.health_is_good = health_is_good


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerSettings(BaseModel):
    log_level: LogLevel = Field(...)
