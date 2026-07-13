from typing import Any

from ortools.sat.python import cp_model


TARGET_DAYS_OF_COVER = 10
SHORTAGE_REWARD_PER_DAY = 500


def optimize_container_placement(
    containers: list[dict[str, Any]],
    fulfillment_centers: list[dict[str, Any]],
    lane_costs: list[dict[str, Any]],
    inventory_coverage: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Assign containers to fulfillment centers and service levels while:

    1. Assigning each container exactly once.
    2. Respecting available fulfillment-center capacity.
    3. Minimizing transportation cost.
    4. Rewarding placement into fulfillment centers with low SKU coverage.

    Expected container structure:
    {
        "container_id": "CONT001",
        "origin_port": "USLAX",
        "total_units": 5000,
        "sku_units": {
            "SKU_A123": 3000,
            "SKU_B456": 2000,
        },
    }
    """

    model = cp_model.CpModel()

    lane_cost_lookup = {
        (
            lane["origin_port"],
            lane["destination_fc"],
            lane["service_level"],
        ): int(
            lane["base_cost"]
            + lane["fuel_surcharge"]
            + lane["accessorial_cost"]
            + lane["service_level_premium"]
        )
        for lane in lane_costs
    }

    coverage_lookup = {
        (
            record["fc_code"],
            record["sku_id"],
        ): float(record["days_of_cover"])
        for record in inventory_coverage
    }

    container_lookup = {
        container["container_id"]: container
        for container in containers
    }

    container_origin_lookup = {
        container["container_id"]: container["origin_port"]
        for container in containers
    }

    assignment_variables: dict[
        tuple[str, str, str],
        cp_model.IntVar,
    ] = {}

    # Create one binary variable for each valid:
    # container -> FC -> service-level combination.
    for container in containers:
        container_id = container["container_id"]
        origin_port = container["origin_port"]

        if not container.get("sku_units"):
            raise ValueError(
                f"{container_id} must include a non-empty sku_units mapping"
            )

        for fc in fulfillment_centers:
            fc_code = fc["fc_code"]

            for service_level in ("STANDARD", "PREMIUM"):
                lane_key = (
                    origin_port,
                    fc_code,
                    service_level,
                )

                if lane_key in lane_cost_lookup:
                    variable_key = (
                        container_id,
                        fc_code,
                        service_level,
                    )

                    assignment_variables[variable_key] = (
                        model.NewBoolVar(
                            f"assign_{container_id}_to_"
                            f"{fc_code}_{service_level}"
                        )
                    )

    # Constraint 1:
    # Every container must be assigned to exactly one FC/service-level pair.
    for container in containers:
        container_id = container["container_id"]

        eligible_variables = [
            variable
            for (
                current_container_id,
                _,
                _,
            ), variable in assignment_variables.items()
            if current_container_id == container_id
        ]

        if not eligible_variables:
            raise ValueError(
                f"No valid transportation lane found for {container_id}"
            )

        model.Add(sum(eligible_variables) == 1)

    # Constraint 2:
    # Total units assigned to an FC cannot exceed available capacity.
    for fc in fulfillment_centers:
        fc_code = fc["fc_code"]
        available_capacity = int(
            fc["available_capacity_units"]
        )

        assigned_unit_terms = []

        for container in containers:
            container_id = container["container_id"]
            total_units = int(container["total_units"])

            for service_level in ("STANDARD", "PREMIUM"):
                variable_key = (
                    container_id,
                    fc_code,
                    service_level,
                )

                if variable_key in assignment_variables:
                    assigned_unit_terms.append(
                        total_units
                        * assignment_variables[variable_key]
                    )

        model.Add(
            sum(assigned_unit_terms) <= available_capacity
        )

    # Objective:
    # effective cost =
    # transportation cost - low-coverage placement reward
    objective_terms = []

    for (
        container_id,
        fc_code,
        service_level,
    ), variable in assignment_variables.items():
        container = container_lookup[container_id]
        origin_port = container_origin_lookup[container_id]

        lane_key = (
            origin_port,
            fc_code,
            service_level,
        )

        transportation_cost = lane_cost_lookup[lane_key]

        inventory_risk_reward = 0

        for sku_id in container["sku_units"]:
            days_of_cover = coverage_lookup.get(
                (fc_code, sku_id),
                0.0,
            )

            shortage_days = max(
                0.0,
                TARGET_DAYS_OF_COVER - days_of_cover,
            )

            inventory_risk_reward += int(
                round(
                    shortage_days
                    * SHORTAGE_REWARD_PER_DAY
                )
            )

        effective_cost = (
            transportation_cost
            - inventory_risk_reward
        )

        objective_terms.append(
            effective_cost * variable
        )

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10

    status = solver.Solve(model)

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE,
    ):
        return {
            "status": solver.StatusName(status),
            "assignments": [],
            "total_transportation_cost": None,
            "total_inventory_risk_reward": None,
            "objective_value": None,
        }

    assignments = []
    total_transportation_cost = 0
    total_inventory_risk_reward = 0

    for (
        container_id,
        fc_code,
        service_level,
    ), variable in assignment_variables.items():
        if solver.Value(variable) != 1:
            continue

        container = container_lookup[container_id]
        origin_port = container_origin_lookup[container_id]

        lane_key = (
            origin_port,
            fc_code,
            service_level,
        )

        transportation_cost = lane_cost_lookup[lane_key]
        coverage_details = []
        assignment_inventory_reward = 0

        for sku_id, sku_units in container["sku_units"].items():
            days_of_cover = coverage_lookup.get(
                (fc_code, sku_id),
                0.0,
            )

            shortage_days = max(
                0.0,
                TARGET_DAYS_OF_COVER - days_of_cover,
            )

            sku_reward = int(
                round(
                    shortage_days
                    * SHORTAGE_REWARD_PER_DAY
                )
            )

            assignment_inventory_reward += sku_reward

            coverage_details.append(
                {
                    "sku_id": sku_id,
                    "units_in_container": int(sku_units),
                    "days_of_cover_before_placement": (
                        days_of_cover
                    ),
                    "shortage_days_below_target": round(
                        shortage_days,
                        2,
                    ),
                    "inventory_risk_reward": sku_reward,
                }
            )

        effective_cost = (
            transportation_cost
            - assignment_inventory_reward
        )

        total_transportation_cost += transportation_cost
        total_inventory_risk_reward += (
            assignment_inventory_reward
        )

        assignments.append(
            {
                "container_id": container_id,
                "recommended_fc": fc_code,
                "service_level": service_level,
                "transportation_cost": transportation_cost,
                "inventory_risk_reward": (
                    assignment_inventory_reward
                ),
                "effective_cost": effective_cost,
                "coverage_details": coverage_details,
            }
        )

    return {
        "status": solver.StatusName(status),
        "assignments": assignments,
        "total_transportation_cost": (
            total_transportation_cost
        ),
        "total_inventory_risk_reward": (
            total_inventory_risk_reward
        ),
        "objective_value": int(
            solver.ObjectiveValue()
        ),
    }