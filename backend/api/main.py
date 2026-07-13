from datetime import datetime
from typing import Literal

from fastapi import FastAPI

from backend.models import (
    Container,
    ContainerEvent,
    FulfillmentCenter,
    LaneCost,
)

# from backend.models_inventory import SKU, ContainerSKU
from backend.models_inventory import (
    SKU,
    ContainerSKU,
    FCInventory,
    InventoryCoverage,
)

from backend.optimizer.placement_optimizer import (
    optimize_container_placement,
)

skus = [
    SKU(
        sku_id="SKU_A123",
        sku_name="Wireless Mouse",
        category="Electronics",
        daily_demand_units=100,
        priority=1,
    ),
    SKU(
        sku_id="SKU_B456",
        sku_name="USB-C Hub",
        category="Electronics",
        daily_demand_units=75,
        priority=2,
    ),
    SKU(
        sku_id="SKU_C789",
        sku_name="Gaming Keyboard",
        category="Electronics",
        daily_demand_units=40,
        priority=3,
    ),
]

container_skus = [
    ContainerSKU(
        container_id="CONT001",
        sku_id="SKU_A123",
        units=500,
    ),
    ContainerSKU(
        container_id="CONT001",
        sku_id="SKU_B456",
        units=300,
    ),
    ContainerSKU(
        container_id="CONT002",
        sku_id="SKU_C789",
        units=400,
    ),
]
fc_inventory = [
    FCInventory(
        fc_code="FC_SOCAL",
        sku_id="SKU_A123",
        on_hand_units=2000,
    ),
    FCInventory(
        fc_code="FC_DALLAS",
        sku_id="SKU_A123",
        on_hand_units=500,
    ),
    FCInventory(
        fc_code="FC_PHOENIX",
        sku_id="SKU_A123",
        on_hand_units=1200,
    ),
]
app = FastAPI(
    title="PlacementIQ API",
    description="Inbound container placement and service-level optimization platform.",
    version="0.1.0",
)


containers = [
    Container(
        container_id="CONT_1001",
        origin_port="USLAX",
        current_milestone="AVAILABLE_FOR_PICKUP",
        total_units=2500,
        total_weight_kg=18000,
    ),
    Container(
        container_id="CONT_1002",
        origin_port="USOAK",
        current_milestone="DISCHARGED",
        total_units=3200,
        total_weight_kg=22100,
    ),
]


events = [
    ContainerEvent(
        container_id="CONT_1001",
        event_code="PORT_ARRIVAL",
        location="USLAX",
        event_timestamp=datetime.now(),
    ),
    ContainerEvent(
        container_id="CONT_1001",
        event_code="DISCHARGED",
        location="USLAX",
        event_timestamp=datetime.now(),
    ),
    ContainerEvent(
        container_id="CONT_1001",
        event_code="AVAILABLE_FOR_PICKUP",
        location="USLAX",
        event_timestamp=datetime.now(),
    ),
]


fulfillment_centers = [
    FulfillmentCenter(
        fc_code="FC_SOCAL",
        city="Ontario",
        state="CA",
        max_capacity_units=120000,
        current_capacity_units=85000,
    ),
    FulfillmentCenter(
        fc_code="FC_PHOENIX",
        city="Phoenix",
        state="AZ",
        max_capacity_units=95000,
        current_capacity_units=54000,
    ),
    FulfillmentCenter(
        fc_code="FC_DALLAS",
        city="Dallas",
        state="TX",
        max_capacity_units=130000,
        current_capacity_units=91000,
    ),
]


lane_costs = [
    LaneCost(
        origin_port="USLAX",
        destination_fc="FC_SOCAL",
        service_level="STANDARD",
        base_cost=1100,
        fuel_surcharge=154,
        accessorial_cost=250,
        service_level_premium=0,
        transit_days=2,
    ),
    LaneCost(
        origin_port="USLAX",
        destination_fc="FC_SOCAL",
        service_level="PREMIUM",
        base_cost=1100,
        fuel_surcharge=154,
        accessorial_cost=250,
        service_level_premium=400,
        transit_days=1,
    ),
    LaneCost(
        origin_port="USLAX",
        destination_fc="FC_PHOENIX",
        service_level="STANDARD",
        base_cost=2200,
        fuel_surcharge=308,
        accessorial_cost=300,
        service_level_premium=0,
        transit_days=3,
    ),
    LaneCost(
        origin_port="USLAX",
        destination_fc="FC_PHOENIX",
        service_level="PREMIUM",
        base_cost=2200,
        fuel_surcharge=308,
        accessorial_cost=300,
        service_level_premium=650,
        transit_days=2,
    ),
    LaneCost(
        origin_port="USLAX",
        destination_fc="FC_DALLAS",
        service_level="STANDARD",
        base_cost=4700,
        fuel_surcharge=658,
        accessorial_cost=400,
        service_level_premium=0,
        transit_days=7,
    ),
    LaneCost(
        origin_port="USLAX",
        destination_fc="FC_DALLAS",
        service_level="PREMIUM",
        base_cost=4700,
        fuel_surcharge=658,
        accessorial_cost=400,
        service_level_premium=1300,
        transit_days=4,
    ),
    LaneCost(
        origin_port="USOAK",
        destination_fc="FC_SOCAL",
        service_level="STANDARD",
        base_cost=1800,
        fuel_surcharge=252,
        accessorial_cost=275,
        service_level_premium=0,
        transit_days=3,
    ),
    LaneCost(
        origin_port="USOAK",
        destination_fc="FC_SOCAL",
        service_level="PREMIUM",
        base_cost=1800,
        fuel_surcharge=252,
        accessorial_cost=275,
        service_level_premium=500,
        transit_days=2,
    ),
    LaneCost(
        origin_port="USOAK",
        destination_fc="FC_PHOENIX",
        service_level="STANDARD",
        base_cost=2700,
        fuel_surcharge=378,
        accessorial_cost=325,
        service_level_premium=0,
        transit_days=4,
    ),
    LaneCost(
        origin_port="USOAK",
        destination_fc="FC_PHOENIX",
        service_level="PREMIUM",
        base_cost=2700,
        fuel_surcharge=378,
        accessorial_cost=325,
        service_level_premium=750,
        transit_days=2,
    ),
    LaneCost(
        origin_port="USOAK",
        destination_fc="FC_DALLAS",
        service_level="STANDARD",
        base_cost=4500,
        fuel_surcharge=630,
        accessorial_cost=425,
        service_level_premium=0,
        transit_days=7,
    ),
    LaneCost(
        origin_port="USOAK",
        destination_fc="FC_DALLAS",
        service_level="PREMIUM",
        base_cost=4500,
        fuel_surcharge=630,
        accessorial_cost=425,
        service_level_premium=1250,
        transit_days=4,
    ),
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/containers", response_model=list[Container])
def get_containers() -> list[Container]:
    return containers


@app.get("/events", response_model=list[ContainerEvent])
def get_events() -> list[ContainerEvent]:
    return events


@app.get("/containers/eligible", response_model=list[Container])
def get_eligible_containers() -> list[Container]:
    eligible_container_ids = {
        event.container_id
        for event in events
        if event.event_code == "AVAILABLE_FOR_PICKUP"
    }

    return [
        container
        for container in containers
        if container.container_id in eligible_container_ids
    ]


@app.get(
    "/fulfillment-centers",
    response_model=list[FulfillmentCenter],
)
def get_fulfillment_centers() -> list[FulfillmentCenter]:
    return fulfillment_centers


@app.get(
    "/lane-costs",
    response_model=list[LaneCost],
)
def get_lane_costs() -> list[LaneCost]:
    return lane_costs


@app.get(
    "/lane-costs/{origin_port}",
    response_model=list[LaneCost],
)
def get_lane_costs_by_port(
    origin_port: Literal["USLAX", "USOAK"],
) -> list[LaneCost]:
    return [
        lane
        for lane in lane_costs
        if lane.origin_port == origin_port
    ]


@app.get("/skus", response_model=list[SKU])
def get_skus():
    return skus

@app.get("/container-skus", response_model=list[ContainerSKU])
def get_container_skus():
    return container_skus

@app.get("/inventory", response_model=list[FCInventory])
def get_inventory():
    return fc_inventory

@app.get(
    "/inventory/coverage",
    response_model=list[InventoryCoverage],
)
def get_inventory_coverage():
    sku_demand_lookup = {
        sku.sku_id: sku.daily_demand_units
        for sku in skus
    }

    coverage = []

    for inventory_record in fc_inventory:
        daily_demand = sku_demand_lookup.get(
            inventory_record.sku_id,
            0,
        )

        days_of_cover = (
            inventory_record.on_hand_units / daily_demand
            if daily_demand > 0
            else 0
        )

        coverage.append(
            InventoryCoverage(
                fc_code=inventory_record.fc_code,
                sku_id=inventory_record.sku_id,
                on_hand_units=inventory_record.on_hand_units,
                daily_demand_units=daily_demand,
                days_of_cover=round(days_of_cover, 2),
            )
        )

    return coverage

@app.post("/optimize-placement")
def optimize_placement():
    containers_input = [
        {
            "container_id": "CONT001",
            "origin_port": "USLAX",
            "total_units": 5000,
        },
        {
            "container_id": "CONT002",
            "origin_port": "USLAX",
            "total_units": 7000,
        },
        {
            "container_id": "CONT003",
            "origin_port": "USOAK",
            "total_units": 6000,
        },
    ]

    fulfillment_centers_input = [
        {
            "fc_code": "FC_SOCAL",
            "available_capacity_units": 10000,
        },
        {
            "fc_code": "FC_PHOENIX",
            "available_capacity_units": 9000,
        },
        {
            "fc_code": "FC_DALLAS",
            "available_capacity_units": 12000,
        },
    ]

    lane_costs_input = {
        ("USLAX", "FC_SOCAL"): 1500,
        ("USLAX", "FC_PHOENIX"): 1800,
        ("USLAX", "FC_DALLAS"): 2300,
        ("USOAK", "FC_SOCAL"): 1900,
        ("USOAK", "FC_PHOENIX"): 2100,
        ("USOAK", "FC_DALLAS"): 2500,
    }

    return optimize_container_placement(
        containers=containers_input,
        fulfillment_centers=fulfillment_centers_input,
        lane_costs=lane_costs_input,
    )