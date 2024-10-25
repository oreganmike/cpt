import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure OpenAI Cost Estimator", layout="wide")
st.markdown(
    """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>""",
    unsafe_allow_html=True,
)

# === Token Metrics ===
MODEL_COSTS =  {
    "gpt-4o": {
        "input_token": 0.000001866,
        "output_token": 0.000007463801,
    }
}

# === Scenarios ===
SCENARIOS = {
    "Low": {
        "engagement_rate": 0.02,
        "conversations_per_user": 1.0,
        "avg_conversation_length": 2,
    },
    "Medium": {
        "engagement_rate": 0.03,
        "conversations_per_user": 1.8,
        "avg_conversation_length": 4,
    },
    "Heavy": {
        "engagement_rate": 0.05,
        "conversations_per_user": 2.6,
        "avg_conversation_length": 8,
    },
    "Custom": {
        "engagement_rate": 0.05,  # Default values; will be overridden
        "conversations_per_user": 2.1,
        "avg_conversation_length": 5,
    },
}

def get_default_cost_per_token(model_type):
    """
    Retrieve the default cost per token based on the selected model type.
    Parameters: model_type (str): The type of OpenAI model selected.
    Returns: float: The cost per token in GBP.
    """
    return MODEL_COSTS.get(model_type["input_token"], 0.000001866)  # Default to gpt-4o if not specified

def calculate_costs(params, cost_per_token, total_visitors, tokens_per_turn):
    """
    Calculate the estimated cost and related metrics for the chatbot usage.
    Parameters:
        params (dict): Dictionary containing 'engagement_rate', 'conversations_per_user', and 'avg_conversation_length'.
        cost_per_token (float): Cost per token in GBP.
        total_visitors (int): Total number of unique visitors per month.
        tokens_per_turn (int): Number of tokens per conversation turn.
    Returns:
        dict: A dictionary with calculated metrics and estimated cost.
    """
    engaged_users = total_visitors * params["engagement_rate"]
    total_conversations = engaged_users * params["conversations_per_user"]
    tokens_per_conversation = params["avg_conversation_length"] * tokens_per_turn
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
        options=["gpt-4o"],
        index=0,
        help="Sets the cost per token.",
    )
    default_cost_per_token = get_default_cost_per_token(model_type)

    # Custom Cost per Token Input
    custom_cost_per_token = st.sidebar.number_input(
        "Cost per Input Token (GBP)",
        min_value=0.000001,
        max_value=0.01,
        value=default_cost_per_token,
        format="%.8f",
        help="Enter the cost per token in GBP.",
    )

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

    scenario = "Custom"

    st.sidebar.subheader("Chatbot Metrics")
    if scenario == "Custom":
        engagement_rate = (
            st.sidebar.number_input(
                "Engagement Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=3.0,
                step=0.1,
                help="Percentage of active users who engage with the chatbot.",
            )
            / 100
        )
        conversations_per_user = st.sidebar.number_input(
            "Conversations per Engaged User",
            min_value=0.0,
            value=1.2,
            step=0.1,
            help="Conversations a user has per visit.",
        )
        avg_conversation_length = st.sidebar.number_input(
            "Average Conversation Length (Turns)",
            min_value=1,
            value=4,
            step=1,
            help="The number of turns per conversation (turn = user request + model response).",
        )
        # Custom Cost per Token Input
        chat_tokens_per_turn = st.sidebar.number_input(
            "Tokens per Turn",
            min_value=200,
            max_value=10000,
            value=300,
            step=100,
            help="User request tokens + model response tokens.",
        )
        # Custom Cost per Token Input
        rag_tokens = st.sidebar.number_input(
            "RAG Tokens",
            min_value=1000,
            max_value=20000,
            value=8000,
            step=1000,
            help="Completion tokens used during RAG process i.e. chunks submitted to model.",
        )
        tokens_per_turn = chat_tokens_per_turn + rag_tokens

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
            params, custom_cost_per_token, monthly_unique_visitors, tokens_per_turn
        )
        data.append(
            {
                "Scenario": sc,
                "Engagement Rate (%)": f"{params['engagement_rate'] * 100:.2f}",
                "Conversations per User": params["conversations_per_user"],
                "Avg Conversation Length (Turns)": params["avg_conversation_length"],
                "Cost per Token (GBP)": f"£{custom_cost_per_token:.8f}",
                "Est Cost (GBP)": f"£{estimated['Est Cost (GBP)']:.2f}",
            }
        )

    # Convert to DataFrame
    df = pd.DataFrame(data)
    st.subheader("Estimated Monthly Costs")
    st.table(df)

    with st.expander("Show Custom Scenario Details"):

        # Detailed Calculations for Selected Scenario
        if scenario != "Custom":
            selected_params = SCENARIOS[scenario]
        else:
            selected_params = custom_params

        detailed_estimated = calculate_costs(
            selected_params,
            custom_cost_per_token,
            monthly_unique_visitors,
            tokens_per_turn,
        )

        st.subheader(f"Calculation for {scenario} Scenario")

        # Create a DataFrame for custom scenario 
        detailed_df = pd.DataFrame(
            [
                {
                    "Metric": "Council Population",
                    "Value": f"{int(council_population):,}",
                    "Notes": "Total population in council area",
                },
                {
                    "Metric": "Conversion Rate",
                    "Value": f"{conversion_rate * 100:.2f}%",
                    "Notes": "Percentage of population who visit the website",
                },
                {
                    "Metric": "Monthly Unique Visitors",
                    "Value": f"{int(monthly_unique_visitors):,}",
                    "Notes": "Population × Conversion Rate",
                },
                {
                    "Metric": "Engagement Rate",
                    "Value": f"{selected_params['engagement_rate'] * 100:.2f}%",
                    "Notes": "Percentage of visitors using chatbot",
                },
                {
                    "Metric": "Engaged Users",
                    "Value": f"{int(detailed_estimated['Engaged Users']):,}",
                    "Notes": "Monthly Visitors × Engagement Rate",
                },
                {
                    "Metric": "Conversations per User",
                    "Value": f"{selected_params['conversations_per_user']}",
                    "Notes": "Average conversations per engaged user",
                },
                {
                    "Metric": "Total Conversations",
                    "Value": f"{int(detailed_estimated['Total Conversations']):,}",
                    "Notes": "Engaged Users × Conversations per User",
                },
                {
                    "Metric": "Conversation Length",
                    "Value": f"{selected_params['avg_conversation_length']} turns",
                    "Notes": "Number of back-and-forth exchanges (Turns)",
                },
                {
                    "Metric": "RAG Tokens",
                    "Value": f"{rag_tokens:,}",
                    "Notes": "Tokens consumed during RAG process for each turn",
                },
                {
                    "Metric": "Tokens per Turn",
                    "Value": f"{chat_tokens_per_turn:,}",
                    "Notes": "Chat tokens in one exchange (user question + RAG process + model response)",
                },
                {
                    "Metric": "Tokens per Conversation",
                    "Value": f"{int(detailed_estimated['Tokens per Conversation']):,}",
                    "Notes": "Conversation Length × Tokens per Turn",
                },
                {
                    "Metric": "Total Monthly Tokens",
                    "Value": f"{int(detailed_estimated['Total Tokens']):,}",
                    "Notes": "Total Conversations × Tokens per Conversation",
                },
                {
                    "Metric": "Cost per Input Token",
                    "Value": f"£{custom_cost_per_token:.8f}",
                    "Notes": "Price per token processed",
                },
                {
                    "Metric": "Estimated Monthly Cost",
                    "Value": f"£{detailed_estimated['Est Cost (GBP)']:.2f}",
                    "Notes": "Total Tokens × Cost per Token",
                },
            ]
        )

        # Display the table with custom formatting and auto-height
        st.dataframe(
            detailed_df,
            column_config={
                "Metric": "Metric",
                "Value": st.column_config.Column(
                    "Value",
                    width="medium",
                ),
                "Notes": st.column_config.Column(
                    "Notes",
                    width="large",
                ),
            },
            hide_index=True,
            height=((len(detailed_df) + 1) * 35)
            + 3,  # Calculate height based on number of rows plus header
            use_container_width=True,  # Use full width of the container
        )


if __name__ == "__main__":
    main()
