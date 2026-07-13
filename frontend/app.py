from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 10


st.set_page_config(
    page_title="PlacementIQ",
    page_icon="📦",
    layout="wide",
)


def fetch_api(endpoint: str) -> Any:
    """Retrieve JSON data from the PlacementIQ FastAPI backend."""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "PlacementIQ API is unavailable. "
            "Start FastAPI with: "
            "`uvicorn backend.api.main:app --reload`"
        )
        return []

    except requests.exceptions.Timeout:
        st.error(f"The request to `{endpoint}` timed out.")
        return []

    except requests.exceptions.HTTPError as exc:
        st.error(f"API request failed for `{endpoint}`: {exc}")
        return []

    except ValueError:
        st.error(f"The API returned invalid JSON for `{endpoint}`.")
        return []


def normalize_records(payload: Any) -> list[dict[str, Any]]:
    """
    Convert common API response structures into a list of records.

    Supports:
    - Direct lists
    - {"data": [...]}
    - {"results": [...]}
    - {"containers": [...]}
    """
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    possible_keys = [
        "data",
        "results",
        "containers",
        "events",
        "fulfillment_centers",
        "lane_costs",
        "inventory",
        "coverage",
        "recommendations",
        "assignments",
    ]

    for key in possible_keys:
        value = payload.get(key)

        if isinstance(value, list):
            return value

    return [payload] if payload else []


def make_dataframe(payload: Any) -> pd.DataFrame:
    """Create a dataframe safely from an API payload."""
    records = normalize_records(payload)

    if not records:
        return pd.DataFrame()

    return pd.json_normalize(records)


def first_existing_column(
    dataframe: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    """Return the first candidate column found in the dataframe."""
    for candidate in candidates:
        if candidate in dataframe.columns:
            return candidate

    return None


def calculate_total_units(containers: pd.DataFrame) -> int:
    """Calculate total units using the available units column."""
    units_column = first_existing_column(
        containers,
        ["total_units", "units", "container_units"],
    )

    if units_column is None:
        return 0

    return int(
        pd.to_numeric(
            containers[units_column],
            errors="coerce",
        )
        .fillna(0)
        .sum()
    )


def calculate_critical_inventory(
    coverage: pd.DataFrame,
    threshold: float = 7,
) -> int:
    """Count FC-SKU records below the critical coverage threshold."""
    coverage_column = first_existing_column(
        coverage,
        ["days_of_cover", "inventory_coverage", "coverage_days"],
    )

    if coverage_column is None:
        return 0

    coverage_values = pd.to_numeric(
        coverage[coverage_column],
        errors="coerce",
    )

    return int((coverage_values < threshold).sum())


def add_risk_status(coverage: pd.DataFrame) -> pd.DataFrame:
    """Add a readable inventory-risk category."""
    output = coverage.copy()

    coverage_column = first_existing_column(
        output,
        ["days_of_cover", "inventory_coverage", "coverage_days"],
    )

    if coverage_column is None:
        output["risk_status"] = "Unknown"
        return output

    coverage_values = pd.to_numeric(
        output[coverage_column],
        errors="coerce",
    )

    output["risk_status"] = pd.cut(
        coverage_values,
        bins=[-float("inf"), 7, 14, float("inf")],
        labels=["Critical", "Watch", "Healthy"],
        right=False,
    )

    return output


def display_empty_state(message: str) -> None:
    """Display a consistent empty-state message."""
    st.info(message)


st.title("PlacementIQ")
st.caption(
    "Inventory-aware container placement optimization and "
    "agentic supply chain planning"
)

with st.sidebar:
    st.header("Planning Controls")

    critical_threshold = st.slider(
        "Critical coverage threshold",
        min_value=1,
        max_value=20,
        value=7,
        step=1,
        help="FC-SKU combinations below this value are considered critical.",
    )

    st.divider()

    if st.button("Refresh Network Data", use_container_width=True):
        st.rerun()

    st.caption(f"Backend: `{API_BASE_URL}`")


containers_payload = fetch_api("/containers")
fulfillment_centers_payload = fetch_api("/fulfillment-centers")
inventory_coverage_payload = fetch_api("/inventory/coverage")

containers_df = make_dataframe(containers_payload)
fulfillment_centers_df = make_dataframe(
    fulfillment_centers_payload
)
coverage_df = make_dataframe(inventory_coverage_payload)


overview_tab, recommendations_tab, inventory_tab, copilot_tab = st.tabs(
    [
        "Network Overview",
        "Placement Recommendations",
        "Inventory Risk",
        "AI Planning Copilot",
    ]
)


with overview_tab:
    st.subheader("Network Overview")

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    container_count = len(containers_df)
    total_units = calculate_total_units(containers_df)
    fc_count = len(fulfillment_centers_df)
    critical_inventory_count = calculate_critical_inventory(
        coverage_df,
        threshold=critical_threshold,
    )

    metric_1.metric(
        label="Containers",
        value=f"{container_count:,}",
    )

    metric_2.metric(
        label="Total Units",
        value=f"{total_units:,}",
    )

    metric_3.metric(
        label="Fulfillment Centers",
        value=f"{fc_count:,}",
    )

    metric_4.metric(
        label="Critical FC-SKU Records",
        value=f"{critical_inventory_count:,}",
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown("#### Containers in Network")

        if containers_df.empty:
            display_empty_state(
                "No container records were returned by the API."
            )
        else:
            st.dataframe(
                containers_df,
                use_container_width=True,
                hide_index=True,
            )

    with right_column:
        st.markdown("#### Fulfillment-Center Capacity")

        if fulfillment_centers_df.empty:
            display_empty_state(
                "No fulfillment-center records were returned by the API."
            )
        else:
            st.dataframe(
                fulfillment_centers_df,
                use_container_width=True,
                hide_index=True,
            )


with recommendations_tab:
    st.subheader("Placement Recommendations")

    st.write(
        "Run the existing OR-Tools optimization engine and review "
        "container-to-fulfillment-center recommendations."
    )

    if st.button(
        "Run Placement Optimization",
        type="primary",
        use_container_width=False,
    ):
        try:
            response = requests.post(
                f"{API_BASE_URL}/optimize-placement",
                timeout=30,
            )
            response.raise_for_status()

            optimization_payload = response.json()
            st.session_state["optimization_payload"] = (
                optimization_payload
            )

            st.success("Optimization completed successfully.")

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the FastAPI backend. "
                "Confirm that the API is running."
            )

        except requests.exceptions.Timeout:
            st.error("The optimization request timed out.")

        except requests.exceptions.HTTPError as exc:
            st.error(f"Optimization failed: {exc}")

        except ValueError:
            st.error("The optimization endpoint returned invalid JSON.")

    optimization_payload = st.session_state.get(
        "optimization_payload"
    )

    if optimization_payload:
        recommendations_df = make_dataframe(
            optimization_payload
        )

        if recommendations_df.empty:
            st.json(optimization_payload)
        else:
            st.dataframe(
                recommendations_df,
                use_container_width=True,
                hide_index=True,
            )

        with st.expander("View raw optimization response"):
            st.json(optimization_payload)

    else:
        display_empty_state(
            "Run the optimizer to generate placement recommendations."
        )


with inventory_tab:
    st.subheader("Inventory Coverage and Risk")

    if coverage_df.empty:
        display_empty_state(
            "No inventory coverage records were returned by the API."
        )

    else:
        risk_df = add_risk_status(coverage_df)

        status_filter = st.multiselect(
            "Filter by inventory status",
            options=["Critical", "Watch", "Healthy", "Unknown"],
            default=["Critical", "Watch", "Healthy"],
        )

        filtered_risk_df = risk_df[
            risk_df["risk_status"]
            .astype(str)
            .isin(status_filter)
        ]

        st.dataframe(
            filtered_risk_df,
            use_container_width=True,
            hide_index=True,
        )

        coverage_column = first_existing_column(
            risk_df,
            [
                "days_of_cover",
                "inventory_coverage",
                "coverage_days",
            ],
        )

        fc_column = first_existing_column(
            risk_df,
            ["fc_code", "fulfillment_center", "destination_fc"],
        )

        sku_column = first_existing_column(
            risk_df,
            ["sku_id", "sku", "product_id"],
        )

        if coverage_column and fc_column:
            chart_data = risk_df.copy()
            chart_data[coverage_column] = pd.to_numeric(
                chart_data[coverage_column],
                errors="coerce",
            )

            tooltip_columns = [
                column
                for column in [
                    fc_column,
                    sku_column,
                    coverage_column,
                    "risk_status",
                ]
                if column is not None
            ]

            chart = (
                alt.Chart(chart_data)
                .mark_bar()
                .encode(
                    x=alt.X(
                        f"{fc_column}:N",
                        title="Fulfillment Center",
                    ),
                    y=alt.Y(
                        f"{coverage_column}:Q",
                        title="Days of Cover",
                    ),
                    color=alt.Color(
                        "risk_status:N",
                        title="Risk Status",
                    ),
                    tooltip=tooltip_columns,
                )
                .properties(
                    height=420,
                    title="Inventory Coverage by Fulfillment Center",
                )
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )


with copilot_tab:
    st.subheader("AI Planning Copilot")

    st.write(
        "Ask PlacementIQ to interpret the network, inventory risks, "
        "and optimizer recommendations."
    )

    if "copilot_messages" not in st.session_state:
        st.session_state["copilot_messages"] = []

    for message in st.session_state["copilot_messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    planner_question = st.chat_input(
        "Ask a supply-chain planning question"
    )

    if planner_question:
        st.session_state["copilot_messages"].append(
            {
                "role": "user",
                "content": planner_question,
            }
        )

        with st.chat_message("user"):
            st.write(planner_question)

        with st.chat_message("assistant"):
            with st.spinner("PlacementIQ is analyzing the network..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/agent/chat",
                        json={
                            "question": planner_question,
                        },
                        timeout=180,
                    )
                    response.raise_for_status()

                    payload = response.json()
                    answer = payload.get(
                        "answer",
                        "The agent returned an empty response.",
                    )
                    intent = payload.get(
                        "intent",
                        "unknown",
                    )

                except requests.exceptions.ConnectionError:
                    answer = (
                        "Could not connect to the PlacementIQ API. "
                        "Confirm that FastAPI is running."
                    )

                except requests.exceptions.Timeout:
                    answer = (
                        "The local model took too long to respond. "
                        "Try again or use a smaller Ollama model."
                    )

                except requests.exceptions.RequestException as exc:
                    answer = f"The planning agent failed: {exc}"

                if "intent" in locals():
                    st.caption(
                        f"Planning tool selected: `{intent}`"
                    )

                st.write(answer)

        st.session_state["copilot_messages"].append(
            {
                "role": "assistant",
                "content": answer,
            }
        )