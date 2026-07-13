from backend.optimizer.placement_optimizer import (
    optimize_container_placement,
)


containers = [
    {
        "container_id": "CONT001",
        "origin_port": "USLAX",
        "total_units": 5000,
        "sku_units": {
            "SKU_A123": 3000,
            "SKU_B456": 2000,
        },
    },
    {
        "container_id": "CONT002",
        "origin_port": "USLAX",
        "total_units": 7000,
        "sku_units": {
            "SKU_A123": 4000,
            "SKU_C789": 3000,
        },
    },
    {
        "container_id": "CONT003",
        "origin_port": "USOAK",
        "total_units": 6000,
        "sku_units": {
            "SKU_B456": 2500,
            "SKU_C789": 3500,
        },
    },
]


fulfillment_centers = [
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


lane_costs = [
    {
        "origin_port": "USLAX",
        "destination_fc": "FC_SOCAL",
        "service_level": "STANDARD",
        "base_cost": 1200,
        "fuel_surcharge": 150,
        "accessorial_cost": 50,
        "service_level_premium": 0,
    },
    {
        "origin_port": "USLAX",
        "destination_fc": "FC_SOCAL",
        "service_level": "PREMIUM",
        "base_cost": 1200,
        "fuel_surcharge": 150,
        "accessorial_cost": 50,
        "service_level_premium": 300,
    },
    {
        "origin_port": "USLAX",
        "destination_fc": "FC_PHOENIX",
        "service_level": "STANDARD",
        "base_cost": 1450,
        "fuel_surcharge": 180,
        "accessorial_cost": 70,
        "service_level_premium": 0,
    },
    {
        "origin_port": "USLAX",
        "destination_fc": "FC_PHOENIX",
        "service_level": "PREMIUM",
        "base_cost": 1450,
        "fuel_surcharge": 180,
        "accessorial_cost": 70,
        "service_level_premium": 350,
    },
    {
        "origin_port": "USLAX",
        "destination_fc": "FC_DALLAS",
        "service_level": "STANDARD",
        "base_cost": 1900,
        "fuel_surcharge": 220,
        "accessorial_cost": 80,
        "service_level_premium": 0,
    },
    {
        "origin_port": "USLAX",
        "destination_fc": "FC_DALLAS",
        "service_level": "PREMIUM",
        "base_cost": 1900,
        "fuel_surcharge": 220,
        "accessorial_cost": 80,
        "service_level_premium": 400,
    },
    {
        "origin_port": "USOAK",
        "destination_fc": "FC_SOCAL",
        "service_level": "STANDARD",
        "base_cost": 1600,
        "fuel_surcharge": 180,
        "accessorial_cost": 70,
        "service_level_premium": 0,
    },
    {
        "origin_port": "USOAK",
        "destination_fc": "FC_SOCAL",
        "service_level": "PREMIUM",
        "base_cost": 1600,
        "fuel_surcharge": 180,
        "accessorial_cost": 70,
        "service_level_premium": 350,
    },
    {
        "origin_port": "USOAK",
        "destination_fc": "FC_PHOENIX",
        "service_level": "STANDARD",
        "base_cost": 1750,
        "fuel_surcharge": 200,
        "accessorial_cost": 80,
        "service_level_premium": 0,
    },
    {
        "origin_port": "USOAK",
        "destination_fc": "FC_PHOENIX",
        "service_level": "PREMIUM",
        "base_cost": 1750,
        "fuel_surcharge": 200,
        "accessorial_cost": 80,
        "service_level_premium": 350,
    },
    {
        "origin_port": "USOAK",
        "destination_fc": "FC_DALLAS",
        "service_level": "STANDARD",
        "base_cost": 2050,
        "fuel_surcharge": 230,
        "accessorial_cost": 90,
        "service_level_premium": 0,
    },
    {
        "origin_port": "USOAK",
        "destination_fc": "FC_DALLAS",
        "service_level": "PREMIUM",
        "base_cost": 2050,
        "fuel_surcharge": 230,
        "accessorial_cost": 90,
        "service_level_premium": 400,
    },
]


inventory_coverage = [
    {
        "fc_code": "FC_SOCAL",
        "sku_id": "SKU_A123",
        "days_of_cover": 20,
    },
    {
        "fc_code": "FC_SOCAL",
        "sku_id": "SKU_B456",
        "days_of_cover": 18,
    },
    {
        "fc_code": "FC_SOCAL",
        "sku_id": "SKU_C789",
        "days_of_cover": 16,
    },
    {
        "fc_code": "FC_PHOENIX",
        "sku_id": "SKU_A123",
        "days_of_cover": 8,
    },
    {
        "fc_code": "FC_PHOENIX",
        "sku_id": "SKU_B456",
        "days_of_cover": 7,
    },
    {
        "fc_code": "FC_PHOENIX",
        "sku_id": "SKU_C789",
        "days_of_cover": 6,
    },
    {
        "fc_code": "FC_DALLAS",
        "sku_id": "SKU_A123",
        "days_of_cover": 3,
    },
    {
        "fc_code": "FC_DALLAS",
        "sku_id": "SKU_B456",
        "days_of_cover": 4,
    },
    {
        "fc_code": "FC_DALLAS",
        "sku_id": "SKU_C789",
        "days_of_cover": 5,
    },
]


result = optimize_container_placement(
    containers=containers,
    fulfillment_centers=fulfillment_centers,
    lane_costs=lane_costs,
    inventory_coverage=inventory_coverage,
)

print(result)