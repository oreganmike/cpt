import streamlit as st
import pandas as pd

# === Token Metrics ===
MODEL_COSTS = {
    "gpt-3": 0.000002,  # Example cost per token in GBP
    "gpt-4": 0.0000036184,
}

# === Scenarios ===
SCENARIOS = {
    "Conservative": {
        "engagement_rate": 0.02,
        "conversations_per_user": 1.0,
        "avg_conversation_length": 3,
    },
    "Moderate": {
        "engagement_rate": 0.03,
        "conversations_per_user": 1.2,
        "avg_conversation_length": 4,
    },
    "Optimistic": {
        "engagement_rate": 0.05,
        "conversations_per_user": 1.5,
        "avg_conversation_length": 5,
    },
    "Custom": {
        "engagement_rate": 0.03,  # Default values; will be overridden
        "conversations_per_user": 1.2,
        "avg_conversation_length": 4,
    },
}


def get_default_cost_per_token(model_type):
    return MODEL_COSTS.get(
        model_type, 0.0000036184
    )  # Default to gpt-4 if not specified


def calculate_costs(params, cost_per_token, total_visitors):
    engaged_users = total_visitors * params["engagement_rate"]
    total_conversations = engaged_users * params["conversations_per_user"]
    tokens_per_conversation = (
        params["avg_conversation_length"] * 270
    )  # avg_tokens_per_turn
    total_tokens = total_conversations * tokens_per_conversation
    estimated_cost = total_tokens * cost_per_token
    return {
        "Engaged Users": engaged_users,
        "Total Conversations": total_conversations,
        "Tokens per Conversation": tokens_per_conversation,
        "Total Tokens": total_tokens,
        "Estimated Cost (GBP)": estimated_cost,
    }


def main():
    st.title("Azure OpenAI API Cost Estimator")
    st.markdown(
        """
    This application estimates the monthly cost of using Azure's OpenAI API based on various scenarios and user interactions.
    """
    )

    # Sidebar for Inputs
    st.sidebar.header("Input Parameters")

    # Model Selection
    model_type = st.sidebar.selectbox(
        "Select OpenAI Model",
        options=["gpt-3", "gpt-4"],
        index=1,
        help="Choose the OpenAI model you plan to use. Different models have different costs per token.",
    )
    default_cost_per_token = get_default_cost_per_token(model_type)

    # Custom Cost per Token Input
    custom_cost_per_token = st.sidebar.number_input(
        "Cost per Token (GBP)",
        min_value=0.000001,
        max_value=0.01,
        value=default_cost_per_token,
        format="%.8f",
        help="Enter the cost per token in GBP. You can override the default cost based on the selected model.",
    )

    # st.sidebar.markdown("---")  # Separator

    # Council Population Input
    st.sidebar.subheader("Council Metrics")
    council_population = st.sidebar.number_input(
        "Council Population",
        min_value=1,
        value=220000,
        step=1000,
        help="Enter the population of the council.",
    )

    # Conversion Rate Input
    conversion_rate = (
        st.sidebar.number_input(
            "Conversion Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=(126253 / 220000) * 100,  # Default based on North Somerset data
            step=0.1,
            help="Percentage of the council population that are monthly active users.",
        )
        / 100
    )  # Convert to decimal

    # Calculate Monthly Unique Visitors
    monthly_unique_visitors = council_population * conversion_rate

    # # Scenario Selection
    # scenario = st.sidebar.selectbox(
    #     "Select Scenario",
    #     options=list(SCENARIOS.keys()),
    #     help="Choose a predefined scenario or customize your own parameters.",
    #     index=3,
    # )

    scenario = "Custom"

    st.sidebar.subheader("Chatbot Metrics")
    # If Custom Scenario, show additional inputs
    if scenario == "Custom":
        engagement_rate = (
            st.sidebar.number_input(
                "Engagement Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=3.0,
                step=0.1,
                help="Percentage of visitors who engage with the chatbot.",
            )
            / 100
        )
        conversations_per_user = st.sidebar.number_input(
            "Conversations per Engaged User",
            min_value=0.0,
            value=1.2,
            step=0.1,
            help="Average number of conversations per engaged user.",
        )
        avg_conversation_length = st.sidebar.number_input(
            "Average Conversation Length (Turns)",
            min_value=1,
            value=4,
            step=1,
            help="Average number of turns (user request and model response) per conversation.",
        )
        custom_params = {
            "engagement_rate": engagement_rate,
            "conversations_per_user": conversations_per_user,
            "avg_conversation_length": avg_conversation_length,
        }
    else:
        custom_params = SCENARIOS[scenario]

    # Calculate costs for all scenarios
    data = []
    for sc, params in SCENARIOS.items():
        # If custom scenario is selected, override parameters
        if sc == "Custom" and scenario == "Custom":
            params = custom_params
        estimated = calculate_costs(
            params, custom_cost_per_token, monthly_unique_visitors
        )
        data.append(
            {
                "Scenario": sc,
                "Engagement Rate (%)": f"{params['engagement_rate'] * 100:.2f}",
                "Conversations per User": params["conversations_per_user"],
                "Avg Conversation Length (Turns)": params["avg_conversation_length"],
                "Cost per Token (GBP)": f"£{custom_cost_per_token:.8f}",
                "Estimated Cost (GBP)": f"£{estimated['Estimated Cost (GBP)']:.2f}",
            }
        )

    # Convert to DataFrame
    df = pd.DataFrame(data)
    st.subheader("Estimated Monthly Costs")
    st.table(df)

    # Bar Chart Visualization
    st.subheader("Cost Comparison Across Scenarios")
    cost_data = df[["Scenario", "Estimated Cost (GBP)"]].copy()
    # Convert 'Estimated Cost (GBP)' to numeric by stripping the currency symbol
    cost_data["Estimated Cost (GBP)"] = (
        cost_data["Estimated Cost (GBP)"].replace("[£,]", "", regex=True).astype(float)
    )
    st.bar_chart(cost_data.set_index("Scenario"))

    # Detailed Calculations for Selected Scenario
    if scenario != "Custom":
        selected_params = SCENARIOS[scenario]
    else:
        selected_params = custom_params

    detailed_estimated = calculate_costs(
        selected_params, custom_cost_per_token, monthly_unique_visitors
    )
    st.subheader(f"Detailed Calculation for {scenario} Scenario")
    st.write(f"**Council Population:** {int(council_population):,}")
    st.write(f"**Conversion Rate:** {conversion_rate * 100:.2f}%")
    st.write(f"**Estimated Monthly Unique Visitors:** {int(monthly_unique_visitors):,}")
    st.write(f"**Engaged Users:** {int(detailed_estimated['Engaged Users']):,}")
    st.write(
        f"**Total Conversations:** {int(detailed_estimated['Total Conversations']):,}"
    )
    st.write(
        f"**Tokens per Conversation:** {int(detailed_estimated['Tokens per Conversation']):,}"
    )
    st.write(f"**Total Tokens:** {int(detailed_estimated['Total Tokens']):,}")
    st.write(f"**Cost per Token:** £{custom_cost_per_token:.8f}")
    st.write(f"**Estimated Cost:** £{detailed_estimated['Estimated Cost (GBP)']:.2f}")

    # Option to download the table as CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Cost Estimates as CSV",
        data=csv,
        file_name="cost_estimates.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
