from pydantic import BaseModel


class SKU(BaseModel):
    sku_id: str
    sku_name: str
    category: str
    daily_demand_units: int
    priority: int


class ContainerSKU(BaseModel):
    container_id: str
    sku_id: str
    units: int


class FCInventory(BaseModel):
    fc_code: str
    sku_id: str
    on_hand_units: int


class InventoryCoverage(BaseModel):
    fc_code: str
    sku_id: str
    on_hand_units: int
    daily_demand_units: int
    days_of_cover: float