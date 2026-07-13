from datetime import datetime
from typing import Literal

from pydantic import BaseModel, computed_field


class Container(BaseModel):
    container_id: str
    origin_port: str
    current_milestone: str
    total_units: int
    total_weight_kg: float


class ContainerEvent(BaseModel):
    container_id: str
    event_code: str
    location: str
    event_timestamp: datetime


class FulfillmentCenter(BaseModel):
    fc_code: str
    city: str
    state: str
    max_capacity_units: int
    current_capacity_units: int

    @computed_field
    @property
    def available_capacity_units(self) -> int:
        return self.max_capacity_units - self.current_capacity_units

    @computed_field
    @property
    def capacity_utilization_pct(self) -> float:
        return round(
            self.current_capacity_units
            / self.max_capacity_units
            * 100,
            2,
        )


class LaneCost(BaseModel):
    origin_port: Literal["USLAX", "USOAK"]
    destination_fc: str
    service_level: Literal["STANDARD", "PREMIUM"]

    base_cost: float
    fuel_surcharge: float
    accessorial_cost: float
    service_level_premium: float
    transit_days: int

    @computed_field
    @property
    def total_transportation_cost(self) -> float:
        return round(
            self.base_cost
            + self.fuel_surcharge
            + self.accessorial_cost
            + self.service_level_premium,
            2,
        )