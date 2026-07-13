from backend.agents.tools import (
    get_critical_inventory,
    get_network_summary,
)


containers = [
    {
        "container_id": "CONT001",
        "total_units": 5000,
    },
    {
        "container_id": "CONT002",
        "total_units": 7000,
    },
]

fulfillment_centers = [
    {"fc_code": "FC_SOCAL"},
    {"fc_code": "FC_DALLAS"},
]

inventory_coverage = [
    {
        "fc_code": "FC_SOCAL",
        "sku_id": "SKU_A123",
        "days_of_cover": 20,
    },
    {
        "fc_code": "FC_DALLAS",
        "sku_id": "SKU_A123",
        "days_of_cover": 5,
    },
]


def test_get_network_summary() -> None:
    result = get_network_summary(
        containers=containers,
        fulfillment_centers=fulfillment_centers,
        inventory_coverage=inventory_coverage,
    )

    assert result["container_count"] == 2
    assert result["total_units"] == 12000
    assert result["fulfillment_center_count"] == 2
    assert result["critical_inventory_count"] == 1


def test_get_critical_inventory() -> None:
    result = get_critical_inventory(
        inventory_coverage=inventory_coverage,
        threshold_days=7,
    )

    assert len(result) == 1
    assert result[0]["fc_code"] == "FC_DALLAS"