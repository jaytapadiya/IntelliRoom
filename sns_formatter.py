import enum
import json
import datetime

class SnsFormatter:
    def __init__(self, eventType, sensorType, sensorValue):
        if type(eventType) is not self.Events:
            raise Exception("Invalid event type")
        self.eventType = eventType
        if type(sensorType) is not self.Sensors:
            raise Exception("Invalid sensor type")
        self.sensorType = sensorType
        self.sensorValue = sensorValue
    class Events(str, enum.Enum):
        INFO = 'INFO'
        WARNING = 'WARNING'
        ERROR = 'ERROR'
    class Sensors(str, enum.Enum):
        TEMPERATURE = 'TEMPERATURE'
        HUMIDITY = 'HUMIDITY'
        GAS = 'GAS'
        FLAME = 'FLAME'
        MOTION = 'MOTION'
        SOUND = 'SOUND'
