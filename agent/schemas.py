from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SHANGHAI = ZoneInfo('Asia/Shanghai')


class ReservationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    num_people: int = Field(ge=1, le=20, description='总人数，包含儿童，1-20')
    num_children: int = Field(ge=0, le=20, description='0-5岁儿童人数，必须询问')
    arrival_time: datetime = Field(description='到店时间，上海时区，YYYY-MM-DD HH:MM')
    seat_preference: str = Field(min_length=1, max_length=100, description='座位偏好；明确无要求填不限')
    main_dish_preference: str = Field(min_length=1, max_length=100, description='主菜偏好；明确无要求填不限')
    other_comments: str = Field(min_length=1, max_length=1000, description='其他备注；明确无要求填无')

    @field_validator('seat_preference', 'main_dish_preference', 'other_comments', mode='before')
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator('arrival_time', mode='before')
    @classmethod
    def parse_hour(cls, value):
        if isinstance(value, str) and len(value.strip()) == 13:
            return value.strip() + ':00'
        return value

    @model_validator(mode='after')
    def validate_business_rules(self):
        if self.num_children > self.num_people:
            raise ValueError('儿童人数不能超过总人数')
        arrival = self.arrival_time
        arrival = arrival.replace(tzinfo=SHANGHAI) if arrival.tzinfo is None else arrival.astimezone(SHANGHAI)
        if arrival <= datetime.now(SHANGHAI):
            raise ValueError('到店时间必须晚于当前上海时间')
        close_hour = 23 if arrival.weekday() in (4, 5) else 21
        if arrival.hour < 10 or arrival.hour >= close_hour:
            raise ValueError(f'到店时间不在营业时间内，当日营业时间10:00-{close_hour}:00')
        self.arrival_time = arrival
        return self


class SearchMenuInput(BaseModel):
    is_featured: bool | None = None
    max_spice_level: int | None = Field(default=None, ge=0, le=3)
    is_vegetarian: bool | None = None
    category: str | None = Field(default=None, max_length=50)
    keyword: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=5, ge=1, le=20)
