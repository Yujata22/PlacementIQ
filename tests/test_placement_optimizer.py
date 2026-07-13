from backend.optimizer.placement_optimizer import (
    optimize_container_placement,
)


containers = [
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


lane_costs = {
    ("USLAX", "FC_SOCAL"): 1500,
    ("USLAX", "FC_PHOENIX"): 1800,
    ("USLAX", "FC_DALLAS"): 2300,
    ("USOAK", "FC_SOCAL"): 1900,
    ("USOAK", "FC_PHOENIX"): 2100,
    ("USOAK", "FC_DALLAS"): 2500,
}


result = optimize_container_placement(
    containers=containers,
    fulfillment_centers=fulfillment_centers,
    lane_costs=lane_costs,
)

print(result)