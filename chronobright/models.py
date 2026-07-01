from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BrightnessScheduleConfig:
    morning_time: str
    morning_brightness: int
    evening_time: str
    evening_brightness: int

    def validate(self) -> None:
        self._validate_time(self.morning_time)
        self._validate_time(self.evening_time)
        self._validate_level(self.morning_brightness)
        self._validate_level(self.evening_brightness)

    @staticmethod
    def _validate_time(value: str) -> None:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError(f"Invalid time format: {value}. Use HH:MM.") from exc

    @staticmethod
    def _validate_level(value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError(f"Brightness must be between 0 and 100: {value}")
