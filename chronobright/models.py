from dataclasses import dataclass

from chronobright.config import validate_brightness_level
from chronobright.time_utils import normalize_time_string


@dataclass(frozen=True)
class BrightnessScheduleConfig:
    morning_time: str
    morning_brightness: int
    evening_time: str
    evening_brightness: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "morning_time", normalize_time_string(self.morning_time))
        object.__setattr__(self, "evening_time", normalize_time_string(self.evening_time))
        self.validate()

    def validate(self) -> None:
        self._validate_time(self.morning_time)
        self._validate_time(self.evening_time)
        validate_brightness_level(self.morning_brightness)
        validate_brightness_level(self.evening_brightness)
        if self.morning_time == self.evening_time:
            raise ValueError(
                f"Morning and evening times must be different: {self.morning_time}"
            )

    @staticmethod
    def _validate_time(value: str) -> None:
        normalize_time_string(value)
