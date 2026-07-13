from typing import Any

from ortools.sat.python import cp_model


def optimize_container_placement(
    containers: list[dict[str, Any]],
    fulfillment_centers: list[dict[str, Any]],
    lane_costs: dict[tuple[str, str], int],
) -> dict[str, Any]:
    """
    Assign multiple containers to fulfillment centers while:

    1. Assigning each container to exactly one FC.
    2. Respecting available FC capacity.
    3. Minimizing total transportation cost.
    """

    model = cp_model.CpModel()

    # x[container_id, fc_code] equals 1 when the container
    # is assigned to that fulfillment center.
    assignment_variables = {}

    for container in containers:
        container_id = container["container_id"]
        origin_port = container["origin_port"]

        for fc in fulfillment_centers:
            fc_code = fc["fc_code"]
            lane_key = (origin_port, fc_code)

            # Create a decision variable only when a valid lane exists.
            if lane_key in lane_costs:
                assignment_variables[(container_id, fc_code)] = (
                    model.NewBoolVar(
                        f"assign_{container_id}_to_{fc_code}"
                    )
                )

    # Constraint 1:
    # Every container must be assigned to exactly one FC.
    for container in containers:
        container_id = container["container_id"]

        eligible_variables = [
            variable
            for (current_container_id, _), variable
            in assignment_variables.items()
            if current_container_id == container_id
        ]

        if not eligible_variables:
            raise ValueError(
                f"No valid transportation lane found for {container_id}"
            )

        model.Add(sum(eligible_variables) == 1)

    # Constraint 2:
    # Total units routed to an FC cannot exceed its available capacity.
    for fc in fulfillment_centers:
        fc_code = fc["fc_code"]
        available_capacity = fc["available_capacity_units"]

        assigned_units = []

        for container in containers:
            container_id = container["container_id"]
            variable_key = (container_id, fc_code)

            if variable_key in assignment_variables:
                assigned_units.append(
                    container["total_units"]
                    * assignment_variables[variable_key]
                )

        model.Add(sum(assigned_units) <= available_capacity)

    # Objective:
    # Minimize total transportation cost across the network.
    total_cost = []

    for container in containers:
        container_id = container["container_id"]
        origin_port = container["origin_port"]

        for fc in fulfillment_centers:
            fc_code = fc["fc_code"]
            variable_key = (container_id, fc_code)
            lane_key = (origin_port, fc_code)

            if variable_key in assignment_variables:
                total_cost.append(
                    lane_costs[lane_key]
                    * assignment_variables[variable_key]
                )

    model.Minimize(sum(total_cost))

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
            "total_cost": None,
        }

    assignments = []

    for (container_id, fc_code), variable in assignment_variables.items():
        if solver.Value(variable) == 1:
            assignments.append(
                {
                    "container_id": container_id,
                    "recommended_fc": fc_code,
                }
            )

    return {
        "status": solver.StatusName(status),
        "assignments": assignments,
        "total_cost": int(solver.ObjectiveValue()),
    }
