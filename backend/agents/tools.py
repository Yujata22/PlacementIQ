from __future__ import annotations

from typing import Any


def get_network_summary(
    containers: list[dict[str, Any]],
    fulfillment_centers: list[dict[str, Any]],
    inventory_coverage: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return high-level statistics for the fulfillment network."""

    total_units = sum(
        int(container.get("total_units", 0))
        for container in containers
    )

    critical_inventory = [
        record
        for record in inventory_coverage
        if float(record.get("days_of_cover", 0)) < 7
    ]

    return {
        "container_count": len(containers),
        "total_units": total_units,
        "fulfillment_center_count": len(fulfillment_centers),
        "critical_inventory_count": len(critical_inventory),
    }


def get_critical_inventory(
    inventory_coverage: list[dict[str, Any]],
    threshold_days: float = 7,
) -> list[dict[str, Any]]:
    """Return FC-SKU records below the coverage threshold."""

    critical_records = [
        record
        for record in inventory_coverage
        if float(record.get("days_of_cover", 0)) < threshold_days
    ]

    return sorted(
        critical_records,
        key=lambda record: float(record.get("days_of_cover", 0)),
    )


def get_container_details(
    container_id: str,
    containers: list[dict[str, Any]],
    container_skus: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return container attributes and the SKUs packed inside it."""

    container = next(
        (
            record
            for record in containers
            if record.get("container_id") == container_id
        ),
        None,
    )

    if container is None:
        return {
            "error": f"Container {container_id} was not found."
        }

    sku_contents = [
        record
        for record in container_skus
        if record.get("container_id") == container_id
    ]

    return {
        "container": container,
        "sku_contents": sku_contents,
    }


def get_assignment_explanation(
    container_id: str,
    optimization_result: dict[str, Any],
) -> dict[str, Any]:
    """Return the optimizer evidence for a container assignment."""

    assignments = optimization_result.get("assignments", [])

    assignment = next(
        (
            record
            for record in assignments
            if record.get("container_id") == container_id
        ),
        None,
    )

    if assignment is None:
        return {
            "error": (
                f"No optimization assignment was found for "
                f"{container_id}."
            )
        }

    return {
        "container_id": assignment.get("container_id"),
        "recommended_fc": assignment.get("recommended_fc"),
        "service_level": assignment.get("service_level"),
        "transportation_cost": assignment.get(
            "transportation_cost"
        ),
        "inventory_risk_reward": assignment.get(
            "inventory_risk_reward"
        ),
        "effective_cost": assignment.get("effective_cost"),
        "coverage_details": assignment.get(
            "coverage_details",
            [],
        ),
    }