import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure OpenAI Cost Estimator", layout="wide")
st.markdown(
    """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>""",
    unsafe_allow_html=True,
)

if "calculated_metrics" not in st.session_state:
    st.session_state["calculated_metrics"] = {}

# === Token Metrics ===
MODEL_COSTS = {
    "gpt-4o": {
        "input_token": 0.000001866,
        "output_token": 0.000007463801,
    },
    "gpt-4o-mini": {
        "input_token": 0.00000011196,
        "output_token": 0.0000004479
    }
}

# === Scenarios ===
SCENARIOS = {
    "Low": {
        "engagement_rate": 0.02,
        "conversations_per_user": 1.0,
        "avg_questions_per_convo": 2,
    },
    "Medium": {
        "engagement_rate": 0.03,
        "conversations_per_user": 1.8,
        "avg_questions_per_convo": 4,
    },
    "Heavy": {
        "engagement_rate": 0.05,
        "conversations_per_user": 2.6,
        "avg_questions_per_convo": 8,
    },
    "Custom": {
        "engagement_rate": 0.05,  # Default values; will be overridden
        "conversations_per_user": 2.1,
        "avg_questions_per_convo": 5,
    },
}


def get_default_cost_per_token(model_type):
    """
    Retrieve the default cost per token based on the selected model type.
    Parameters: model_type (str): The type of OpenAI model selected.
    Returns: float: The cost per token in GBP.
    """
    return MODEL_COSTS.get(model_type, {}) #.get("input_token", 0.000001866) 


def calculate_costs(params, cost_per_token, total_visitors, tokens_per_question, rag_tokens, tokens_per_answer):
    """
    Calculate the estimated cost and related metrics for the chatbot usage.
    Parameters:
        params (dict): Dictionary containing 'engagement_rate', 'conversations_per_user', and 'avg_questions_per_convo'.
        cost_per_token (float): Cost per token in GBP.
        total_visitors (int): Total number of unique visitors per month.
        tokens_per_question (int): Number of tokens per question.
        rag_tokens (int): Number of RAG tokens per question.
        tokens_per_answer (int): Number of tokens per answer.
    Returns:
        dict: A dictionary with calculated metrics and estimated cost.
    """
    engaged_users = total_visitors * params["engagement_rate"]
    total_conversations = engaged_users * params["conversations_per_user"]
    
    # Calculate tokens per conversation using the new formula
    tokens_per_conversation = 0
    previous_tokens = 0
    tokens_per_turn = tokens_per_question + rag_tokens + tokens_per_answer

    for i in range(1, params["avg_questions_per_convo"] + 1):
        current_tokens = tokens_per_turn
        if i > 1:
            tokens_per_conversation += current_tokens + previous_tokens
        else:
            tokens_per_conversation += current_tokens
        previous_tokens = current_tokens

    total_tokens = total_conversations * tokens_per_conversation
    estimated_cost = total_tokens * cost_per_token
    
    # Store results in Streamlit session state
    st.session_state['calculated_metrics'] = {
        "Engaged Users": engaged_users,
        "Total Conversations": total_conversations,
        "Tokens per Conversation": tokens_per_conversation,
        "Total Tokens": total_tokens,
        "Estimated Cost (GBP)": estimated_cost,
    }
    
    return st.session_state['calculated_metrics']

def main():
    st.header("Azure OpenAI API Cost Estimator")
    st.markdown("Estimates the monthly cost of the Azure OpenAI Service.")

    # Sidebar for Inputs
    st.sidebar.header("Token Inputs")

    # Model Selection
    model_type = st.sidebar.selectbox(
        "Select OpenAI Model",
        options=["gpt-4o", "gpt-4o-mini"],
        index=1,
        help="Sets the input and output cost per token.",
    )
    default_cost_per_input_token = get_default_cost_per_token(model_type).get("input_token", 0.000001866)
    default_cost_per_output_token = get_default_cost_per_token(model_type).get("output_token", 0.000007463801)
    
    # Custom Cost per Token Input
    custom_cost_per_token = st.sidebar.number_input(
        "Cost per Input Token",
        min_value=0.000000001,
        max_value=0.01,
        value=default_cost_per_input_token,
        format="%.10f",
        help="The cost per input token in GBP.",
    )
    # Custom Cost per Token Input
    custom_cost_per_output_token = st.sidebar.number_input(
        "Cost per Output Token",
        min_value=0.000000001,
        max_value=0.01,
        value=default_cost_per_output_token,
        format="%.10f",
        help="The cost per output token in GBP.",
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
        avg_questions_per_convo = st.sidebar.number_input(
            "Questions per Conversation (Turns)",
            min_value=1,
            value=4,
            step=1,
            help="The number of questions a user asks in a conversation (turn = user question + model response).",
        )

        # Input tokens
        tokens_per_question = st.sidebar.number_input(
            "Tokens per Question",
            min_value=100,
            max_value=10000,
            value=100,
            step=50,
            help="The number of tokens in an average question.",
        )
        # RAG tokens / Input tokens
        rag_tokens = st.sidebar.number_input(
            "RAG Tokens",
            min_value=1000,
            max_value=20000,
            value=2000,
            step=1000,
            help="Input tokens used during RAG process i.e. chunks submitted to model.",
        )
        # Output tokens
        tokens_per_answer = st.sidebar.number_input(
            "Tokens per Answer",
            min_value=200,
            max_value=10000,
            value=300,
            step=50,
            help="The number of tokens generated by the model in an average answer.",
        )
        tokens_per_turn = tokens_per_question + rag_tokens + tokens_per_answer

        custom_params = {
            "engagement_rate": engagement_rate,
            "conversations_per_user": conversations_per_user,
            "avg_questions_per_convo": avg_questions_per_convo,
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
            params, custom_cost_per_token, monthly_unique_visitors, tokens_per_question, rag_tokens, tokens_per_answer
        )
        data.append(
            {
                "Scenario": sc,
                "Engagement Rate (%)": f"{params['engagement_rate'] * 100:.1f}%",
                "Engaged Users": f"{st.session_state['calculated_metrics']['Engaged Users']:,.0f}",
                "Conversations per User": f"{params['conversations_per_user']:.1f}",
                "Qs per Conversation": f"{params['avg_questions_per_convo']:.0f}",
                "Cost per Token (GBP)": f"£{custom_cost_per_token:.10f}",
                "Est MonthlyCost (GBP)": f"£{estimated['Estimated Cost (GBP)']:,.2f}", 
                "Est Annual Cost (GBP)": f"£{estimated['Estimated Cost (GBP)'] * 12:.2f}",
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
            tokens_per_question, rag_tokens, tokens_per_answer
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
                    "Notes": f"Population ({int(council_population):,}) × Conversion Rate ({conversion_rate * 100:.2f}%)",
                },
                {
                    "Metric": "Engagement Rate",
                    "Value": f"{selected_params['engagement_rate'] * 100:.2f}%",
                    "Notes": "Percentage of visitors using chatbot",
                },
                {
                    "Metric": "Engaged Users",
                    "Value": f"{int(detailed_estimated['Engaged Users']):,}",
                    "Notes": f"Monthly Visitors ({int(monthly_unique_visitors):,}) × Engagement Rate ({selected_params['engagement_rate'] * 100:.2f}%)",
                },
                {
                    "Metric": "Conversations per User",
                    "Value": f"{selected_params['conversations_per_user']:.1f}",
                    "Notes": "Average conversations per engaged user",
                },
                {
                    "Metric": "Total Conversations",
                    "Value": f"{int(detailed_estimated['Total Conversations']):,}",
                    "Notes": f"Engaged Users ({int(detailed_estimated['Engaged Users']):,}) × Conversations per User ({selected_params['conversations_per_user']})",
                },
                {
                    "Metric": "Questions per Conversation",
                    "Value": f"{selected_params['avg_questions_per_convo']}",
                    "Notes": "Number of questions asked in a conversation (Turns)",
                },
                {
                    "Metric": "Tokens per Question",
                    "Value": f"{tokens_per_turn:,}",
                    "Notes": f"Question tokens ({tokens_per_question}) + RAG tokens ({rag_tokens:,}) + Answer tokens ({tokens_per_answer})",
                },
                {
                    "Metric": "Tokens per Conversation",
                    "Value": f"{int(detailed_estimated['Tokens per Conversation']):,}",
                    "Notes": f"Questions per conversation × 2 − 1 ({selected_params['avg_questions_per_convo'] * 2 -1}) × Tokens per Question ({tokens_per_turn:,})",
                },
                {
                    "Metric": "Total Monthly Tokens",
                    "Value": f"{int(detailed_estimated['Total Tokens']):,}",
                    "Notes": f"Total Conversations ({int(detailed_estimated['Total Conversations']):,}) × Tokens per Conversation ({int(detailed_estimated['Tokens per Conversation']):,})",
                },
                {
                    "Metric": "Cost per Input Token",
                    "Value": f"£{custom_cost_per_token:.10f}",
                    "Notes": "Price per token processed",
                },
                {
                    "Metric": "Est Monthly Cost",
                    "Value": f"£{detailed_estimated['Estimated Cost (GBP)']:.2f}",
                    "Notes": f"Total Tokens ({int(detailed_estimated['Total Tokens']):,}) × Cost per Token (£{custom_cost_per_token:.10f})",
                },
                {
                    "Metric": "Est Annual Cost",
                    "Value": f"£{detailed_estimated['Estimated Cost (GBP)'] * 12:.2f}",
                    "Notes": "Estimated Monthly Cost × 12",
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
