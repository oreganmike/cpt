import streamlit as st

st.set_page_config(
    page_title="Cost Estimator Definitions", page_icon="📚", layout="wide"
)

st.markdown(
    """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>""",
    unsafe_allow_html=True,
)


st.title("Cost Estimator Parameters")

st.markdown(
    """
Parameters used in the Cost Estimator are explained here. 
"""
)

# Model Parameters
st.header("1. Model Parameters")

st.subheader("OpenAI Model Selection")
st.markdown(
    """
Model selection isn't that significant. For now it just allows for cost per token values to be pre-set. 
- **GPT-4o**: Sets a cost per completion token of 0.000009329801 (GBP)
- **GPT-4o-alt**: Sets a cost per completion token of 0.00000362 (GBP)

"""
)

st.subheader("Tokens per Turn")
st.markdown(
    """
**Definition**: The total number of tokens used in one complete exchange between a user and the chatbot.

This includes:
- Tokens from the user's question/input
- Tokens from the model's response

**Typical values**:
- Short exchanges: 200-400 tokens
- Medium exchanges: 400-800 tokens
- Long, detailed exchanges: 800+ tokens

**Example**:
- User question: "What are the council tax bands?" (7 tokens)
- Model response with detailed explanation (293 tokens)
- Total = 300 tokens per turn

**Note**:
- Backend RAG-related token generation isn't included e.g. generating embeddings, question parsing, generating queries, CoT, etc. 
- TODO include approx 6-8k tokens for each turn. 

"""
)

st.subheader("RAG Tokens")
st.markdown(
    """
**Definition**: The number of tokens consumed during the RAG process. 

- Essentially all RAG tokens consist of text chunks that are submitted to the model for a contexually aided response
- Embedding tokens are generated for the user's question. 
"""
)

st.subheader("Cost per Token")
st.markdown(
    """
**Definition**: The price charged by Azure OpenAI for processing one token.

- Measured in GBP
- Pre-set cost per token assumes pay-as-you-go pricing
"""
)

st.markdown("---")

# Population Metrics
st.header("2. Council Population Metrics")

st.subheader("Council Population")
st.markdown(
    """
**Definition**: The total number of residents in the council area.

This serves as the base for calculating potential citizen engagement:
- Used to estimate total reach
- Starting point for conversion calculations

"""
)

st.subheader("Conversion Rate")
st.markdown(
    """
**Definition**: Percentage of council population that are monthly active users of a council's website.

**Calculation**: (Monthly Active Users / Total Population) × 100

**Example**:
- Council Population: 220,000
- Monthly Active Users: 126,253
- Conversion Rate: 57.4%

This metric helps estimate how many citizens could engage in conversations. 
It's also a metric councils can easily provide from their Google Analytics data.

"""
)


st.markdown("---")

# Chatbot Engagement Metrics
st.header("3. Chatbot Engagement Metrics")

st.subheader("Engagement Rate")
st.markdown(
    """
**Definition**: Percentage of website visitors who interact with the chatbot.

Different scenarios provide different assumptions:
- **Low**: 2% (1 in 50 visitors use the chatbot)
- **Medium**: 3% (1 in 33 visitors use the chatbot)
- **Heavy**: 6% (1 in 17 visitors use the chatbot)

Based on very loose numbers from data.gov.uk
"""
)

st.subheader("Conversations per Engaged User")
st.markdown(
    """
**Definition**: Average number of separate conversations each engaged user has per month.

Scenario assumptions:
- **Low**: 1.0 (one conversation per user)
- **Medium**: 2.2 (some users have multiple conversations)
- **Heavy**: 4.6 (users regularly return for multiple queries)

A conversation is a complete interaction session, which includes multiple turns.
"""
)

st.subheader("Average Conversation Length (Turns)")
st.markdown(
    """
**Definition**: Average number of back-and-forth exchanges in a single conversation.

One turn consists of:
1. User input/question
2. Chatbot response

Scenario assumptions:
- **Low**: 3 turns (brief, focused interactions)
- **Medium**: 4 turns (standard query resolution)
- **Heavy**: 8 turns (detailed, multi-step interactions)

**Example of a 3-turn conversation**:
1. User asks about council tax → Bot responds
2. User asks for payment methods → Bot responds
3. User asks for payment deadline → Bot responds
"""
)


st.markdown("---")

# Cost Calculation Process
st.header("4. How Costs Are Calculated")
st.markdown(
    """
The final cost estimate follows this calculation process:

1. **Calculate Engaged Users**:
    ```
    Council Population × Conversion Rate × Engagement Rate
    ```

2. **Calculate Total Conversations**:
    ```
    Engaged Users × Conversations per User
    ```

3. **Calculate Total Tokens**:
    ```
    Total Conversations × Turns per Conversation × Tokens per Turn
    ```

4. **Calculate Final Cost**:
    ```
    Total Tokens × Cost per Token
    ```
"""
)
