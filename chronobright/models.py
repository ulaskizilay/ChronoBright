from dataclasses import dataclass
from datetime import datetime

from chronobright.config import validate_brightness_level


@dataclass(frozen=True)
class BrightnessScheduleConfig:
    morning_time: str
    morning_brightness: int
    evening_time: str
    evening_brightness: int

    def validate(self) -> None:
        self._validate_time(self.morning_time)
        self._validate_time(self.evening_time)
        validate_brightness_level(self.morning_brightness)
        validate_brightness_level(self.evening_brightness)

    @staticmethod
    def _validate_time(value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Invalid time format: {value}. Use HH:MM.")
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError(f"Invalid time format: {value}. Use HH:MM.") from exc
