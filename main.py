import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page config
st.set_page_config(page_title="Azure OpenAI Cost Estimator", layout="wide")

# Hides streamlits header, footer and hambuger menu so folks dont break shit
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>""", unsafe_allow_html=True,)

# Get last modified date/time to incolude in title for last published date
def get_last_modified_time():
    file_path = __file__
    last_modified_timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(last_modified_timestamp).strftime("%d %B %Y at %I:%M%p").lower().replace(" 0", " ")

last_modified_datetime = get_last_modified_time()

# ss
if "calculated_metrics" not in st.session_state:
    st.session_state["calculated_metrics"] = {}

# Static vars
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

SCENARIOS = {
    "Low": {
        "engagement_rate": 0.02,
        "conversations_per_user": 1.0,
        "avg_questions_per_convo": 2,
    },
    "Medium": {
        "engagement_rate": 0.03,
        "conversations_per_user": 2.2,
        "avg_questions_per_convo": 4,
    },
    "Heavy": {
        "engagement_rate": 0.06,
        "conversations_per_user": 4.6,
        "avg_questions_per_convo": 8,
    },
    "Custom": {
        "engagement_rate": 0.05,  # Default values; will be overridden by user inputs
        "conversations_per_user": 2.1,
        "avg_questions_per_convo": 5,
    },
}

# funcs
def get_default_cost_per_token(model_type):
    """
    Get cost per token based on selection
    Parameters:
        model_type (str): The selected OpenAI model.
    Returns:
        dict: Dict containing input and output token costs
    """
    return MODEL_COSTS.get(model_type, {}) 

def calculate_costs(params, cost_per_token, total_visitors, tokens_per_question, rag_tokens, tokens_per_answer):
    """
    Calculate est costs and chatbot usage 
    Parameters:
        params (dict): Contains 'engagement_rate', 'conversations_per_user', and 'avg_questions_per_convo'.
        cost_per_token (float): Cost per input token in GBP.
        total_visitors (int): Number of unique visitors per month
        tokens_per_question (int): Tokens per user question
        rag_tokens (int): Tokens used during the RAG process
        tokens_per_answer (int): Tokens per model answer
    Returns:
        dict: Calculated metrics and est cost
    """
    engaged_users = total_visitors * params["engagement_rate"]
    total_conversations = engaged_users * params["conversations_per_user"]
    
    tokens_per_turn = tokens_per_question + rag_tokens + tokens_per_answer
    tokens_per_conversation = 0
    previous_tokens = 0

    # See def page for explanation on what toekns are used in conversations 
    for i in range(1, params["avg_questions_per_convo"] + 1):
        current_tokens = tokens_per_turn
        if i > 1:
            tokens_per_conversation += current_tokens + previous_tokens
        else:
            tokens_per_conversation += current_tokens
        previous_tokens = current_tokens

    total_tokens = total_conversations * tokens_per_conversation
    estimated_cost = total_tokens * cost_per_token
    
    # Add to ss
    st.session_state['calculated_metrics'] = {
        "Engaged Users": engaged_users,
        "Total Conversations": total_conversations,
        "Tokens per Conversation": tokens_per_conversation,
        "Total Tokens": total_tokens,
        "Estimated Cost (GBP)": estimated_cost,
    }
    
    return st.session_state['calculated_metrics']

def get_sidebar_inputs():
    """
    Collect user inputs from sidebar controls
    Returns:
        dict: A dictionary containing all user inputs.
    """
    st.sidebar.header("Token Inputs")

    # Model Selection
    model_type = st.sidebar.selectbox(
        "Select OpenAI Model",
        options=["gpt-4o", "gpt-4o-mini"],
        index=1,
        help="Sets the input and output cost per token.",
    )
    default_costs = get_default_cost_per_token(model_type)
    default_cost_per_input_token = default_costs.get("input_token", 0.000001866)
    default_cost_per_output_token = default_costs.get("output_token", 0.000007463801)
    
    # Custom Token Costs (changes all scenario values)
    custom_cost_per_token = st.sidebar.number_input(
        "Cost per Input Token",
        min_value=0.000000001,
        max_value=0.01,
        value=default_cost_per_input_token,
        format="%.10f",
        help="The cost per input token in GBP.",
    )
    
    custom_cost_per_output_token = st.sidebar.number_input(
        "Cost per Output Token",
        min_value=0.000000001,
        max_value=0.01,
        value=default_cost_per_output_token,
        format="%.10f",
        help="The cost per output token in GBP.",
    )

    # Council Metrics
    st.sidebar.subheader("Council Metrics")
    council_population = st.sidebar.number_input(
        "Council Population",
        min_value=1,
        value=220000,
        step=1000,
        help="Enter the population of the council.",
    )

    conversion_rate = (
        st.sidebar.number_input(
            "Conversion Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=(126253 / 220000) * 100,  # Default based on North Somerset's data
            step=0.1,
            help="Percentage of the council population that are monthly active users.",
        )
        / 100  # Convert to decimal
    )

    # Calculate monthly unique visitors
    monthly_unique_visitors = council_population * conversion_rate

    # Chatbot inputs for custom scenario
    st.sidebar.subheader("Chatbot Metrics")
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

    # Token Inputs
    tokens_per_question = st.sidebar.number_input(
        "User Input Tokens",
        min_value=100,
        max_value=10000,
        value=100,
        step=50,
        help="The number of tokens in a user's question.",
    )
    rag_tokens = st.sidebar.number_input(
        "RAG Tokens",
        min_value=1000,
        max_value=20000,
        value=2000,
        step=1000,
        help="Number of tokens used during RAG process, i.e., chunks submitted to model.",
    )
    tokens_per_answer = st.sidebar.number_input(
        "Model Output Tokens",
        min_value=200,
        max_value=10000,
        value=300,
        step=50,
        help="The number of tokens the model generates for its response.",
    )

    return {
        "model_type": model_type,
        "custom_cost_per_token": custom_cost_per_token,
        "custom_cost_per_output_token": custom_cost_per_output_token,
        "council_population": council_population,
        "conversion_rate": conversion_rate,
        "monthly_unique_visitors": monthly_unique_visitors,
        "engagement_rate": engagement_rate,
        "conversations_per_user": conversations_per_user,
        "avg_questions_per_convo": avg_questions_per_convo,
        "tokens_per_question": tokens_per_question,
        "rag_tokens": rag_tokens,
        "tokens_per_answer": tokens_per_answer,
    }

def generate_scenarios(user_inputs, custom_costs):
    """
    Generate cost est for each scenario    
    Parameters:
        user_inputs (dict): User inputs from the sidebar.
        custom_costs (dict): Custom cost per token inputs.
    Returns:
        pd.DataFrame: DataFrame containing cost ests for each scenario
    """
    data = []
    for scenario_name, params in SCENARIOS.items():
        if scenario_name == "Custom":
            # Override custom scenrio params with user inputs
            current_params = {
                "engagement_rate": user_inputs["engagement_rate"],
                "conversations_per_user": user_inputs["conversations_per_user"],
                "avg_questions_per_convo": user_inputs["avg_questions_per_convo"],
            }
        else:
            # Use scenarios values
            current_params = params

        estimated = calculate_costs(
            current_params,
            custom_costs["custom_cost_per_token"],
            user_inputs["monthly_unique_visitors"],
            user_inputs["tokens_per_question"],
            user_inputs["rag_tokens"],
            user_inputs["tokens_per_answer"]
        )

        data.append({
            "Scenario": scenario_name,
            "Engagement Rate (%)": f"{current_params['engagement_rate'] * 100:.1f}%",
            "Engaged Users": f"{estimated['Engaged Users']:,.0f}",
            "Conversations per User": f"{current_params['conversations_per_user']:.1f}",
            "Qs per Conversation": f"{current_params['avg_questions_per_convo']:.0f}",
            "Cost per Token (GBP)": f"£{custom_costs['custom_cost_per_token']:.10f}",
            "Est Monthly Cost (GBP)": f"£{estimated['Estimated Cost (GBP)']:,.2f}", 
            "Est Annual Cost (GBP)": f"£{estimated['Estimated Cost (GBP)'] * 12:.2f}",
        })
    return pd.DataFrame(data)

def display_estimated_costs(df):
    """
    Est monthly costs as a table.
    Parameters:
        df (pd.DataFrame): DataFrame containing cost ests.
    """
    st.subheader("Estimated Monthly Costs")
    st.table(df)

def display_detailed_calculation(selected_params, detailed_estimated, user_inputs, custom_costs):
    """
    Breakdown of the cost calcs
    Parameters:
        selected_params (dict): Parameters for the selected scenario.
        detailed_estimated (dict): Calcd metrics.
        user_inputs (dict): User inputs from sidebar controls
        custom_costs (dict): Custom cost per token inputs
    """
    st.subheader("Calculation for Custom Scenario")

    tokens_per_turn = user_inputs['tokens_per_question'] + user_inputs['rag_tokens'] + user_inputs['tokens_per_answer']
    
    # Included in-line values in the notes section so examples are easier to understand
    detailed_data = [
        {
            "Metric": "Council Population",
            "Value": f"{int(user_inputs['council_population']):,}",
            "Notes": "Total population in council area",
        },
        {
            "Metric": "Conversion Rate",
            "Value": f"{user_inputs['conversion_rate'] * 100:.2f}%",
            "Notes": "Percentage of population who visit the website",
        },
        {
            "Metric": "Monthly Unique Visitors",
            "Value": f"{int(user_inputs['monthly_unique_visitors']):,}",
            "Notes": f"Population ({int(user_inputs['council_population']):,}) × Conversion Rate ({user_inputs['conversion_rate'] * 100:.2f}%)",
        },
        {
            "Metric": "Engagement Rate",
            "Value": f"{selected_params['engagement_rate'] * 100:.2f}%",
            "Notes": "Percentage of visitors using chatbot",
        },
        {
            "Metric": "Engaged Users",
            "Value": f"{int(detailed_estimated['Engaged Users']):,}",
            "Notes": f"Monthly Visitors ({int(user_inputs['monthly_unique_visitors']):,}) × Engagement Rate ({selected_params['engagement_rate'] * 100:.2f}%)",
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
            "Metric": "Tokens per Turn",
            "Value": f"{tokens_per_turn:,}",
            "Notes": f"User input tokens ({user_inputs['tokens_per_question']}) + RAG tokens ({user_inputs['rag_tokens']:,}) + Answer tokens ({user_inputs['tokens_per_answer']})",
        },
        {
            "Metric": "Tokens per Conversation",
            "Value": f"{int(detailed_estimated['Tokens per Conversation']):,}",
            "Notes": f"Questions per conversation × Tokens per Turn ({tokens_per_turn:,})",
        },
        {
            "Metric": "Total Monthly Tokens",
            "Value": f"{int(detailed_estimated['Total Tokens']):,}",
            "Notes": f"Total Conversations ({int(detailed_estimated['Total Conversations']):,}) × Tokens per Conversation ({int(detailed_estimated['Tokens per Conversation']):,})",
        },
        {
            "Metric": "Cost per Input Token",
            "Value": f"£{custom_costs['custom_cost_per_token']:.10f}",
            "Notes": "Price per input token processed",
        },
        {
            "Metric": "Est Monthly Cost",
            "Value": f"£{detailed_estimated['Estimated Cost (GBP)']:.2f}",
            "Notes": f"Total Tokens ({int(detailed_estimated['Total Tokens']):,}) × Cost per Token (£{custom_costs['custom_cost_per_token']:.10f})",
        },
        {
            "Metric": "Est Annual Cost",
            "Value": f"£{detailed_estimated['Estimated Cost (GBP)'] * 12:.2f}",
            "Notes": "Estimated Monthly Cost × 12",
        },
    ]

    detailed_df = pd.DataFrame(detailed_data)

    st.dataframe(
        detailed_df,
        hide_index=True,
        height=((len(detailed_df) + 1) * 35) + 3, # Hacky workaround to avoid scrollbars on the table
        use_container_width=True, 
    )

def main():
    st.header("Azure OpenAI API Cost Estimator")
    st.markdown(f"Estimates the monthly cost of the Azure OpenAI Service. Last updated on: {last_modified_datetime}")

    # Collect user inputs
    user_inputs = get_sidebar_inputs()
    custom_costs = {
        "custom_cost_per_token": user_inputs["custom_cost_per_token"],
        "custom_cost_per_output_token": user_inputs["custom_cost_per_output_token"],
    }

    # Eval cost ests
    cost_estimates_df = generate_scenarios(user_inputs, custom_costs)
    display_estimated_costs(cost_estimates_df)

    with st.expander("Show Custom Scenario Details"):
        custom_params = {
            "engagement_rate": user_inputs["engagement_rate"],
            "conversations_per_user": user_inputs["conversations_per_user"],
            "avg_questions_per_convo": user_inputs["avg_questions_per_convo"],
        }

        detailed_estimated = calculate_costs(
            custom_params,
            custom_costs["custom_cost_per_token"],
            user_inputs["monthly_unique_visitors"],
            user_inputs["tokens_per_question"],
            user_inputs["rag_tokens"],
            user_inputs["tokens_per_answer"]
        )

        display_detailed_calculation(custom_params, detailed_estimated, user_inputs, custom_costs)

if __name__ == "__main__":
    main()
