import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Cost Estimator Definitions", page_icon="📚", layout="wide"
)

st.markdown(
    """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>""",
    unsafe_allow_html=True,
)


st.header("Cost Estimator Parameters")

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
**GPT-4o**: 
- Sets a cost per input completion token of 0.000001866 (GBP)
- Sets a cost per output completion token of 0.000007463801 (GBP)

Note: 
- A user's question + chunks of text returned from a similarity search = input tokens
- The model's response to the user's question + chunks = output tokens
"""
)

st.subheader("Tokens per Question")
st.markdown(
    """
**Definition**: The total number of tokens used in one complete exchange between a user and the chatbot.

This includes:
- Tokens from the user's question/input
- Tokens from the RAG process
- Tokens from the model's response

**Typical values**:
- Short exchanges: 200-400 tokens
- Medium exchanges: 400-800 tokens
- Long, detailed exchanges: 800+ tokens

**Example**:
- User question: "What are the council tax bands?" (7 tokens)
- RAG process: Generates embeddings, performs search, submits question to model with chunks (~2,000 tokens)
- Model response with detailed explanation (393 tokens)
- Total = 2,400 tokens per question

"""
)

st.subheader("RAG Tokens")
st.markdown(
    """
**Definition**: The number of tokens consumed during the RAG process. 
- Essentially all RAG tokens consist of text chunks that are submitted to the model for a contexually aided response

**Example**:
- User question: "What are the council tax bands?" (7 tokens)
- RAG process: Generates embeddings, performs search, submits question to model with chunks (2,000 tokens)
- Model response with detailed explanation (393 tokens)
- Total = 2,000 RAG tokens

"""
)
st.subheader("Cost per Input Token")
st.markdown(
    """
**Definition**: The price charged by Azure OpenAI for processing one input token.

- Uses GBP (£)
- Pre-set cost per token assumes pay-as-you-go pricing
- Cost per input token defaults to gpt-4o-mini at 0.00000011196

"""
)

st.subheader("Cost per Output Token")
st.markdown(
    """
**Definition**: The price charged by Azure OpenAI for generating one output token.

- Uses GBP (£)
- Pre-set cost per token assumes pay-as-you-go pricing
- Cost per output token defaults to gpt-4o-mini at 0.0000004479

"""
)

st.subheader("Tokens per Conversation")
st.markdown(
    """
**Definition**: The total number of tokens consumed in a conversation will be the sum of the tokens for each question plus the previous question's tokens.  

In a chatbot interaction, each subsequent question includes the previous question and answer for context.   
This means that the token count for each question in a conversation is current + previous.  
Expressed as a simple formula it could look like: Qn + Qn-1  

**Calculation**:
- For each question in a conversation, the tokens include:  
  - Tokens from the current question  
  - RAG tokens for contextual processing  
  - Tokens from the model's response  

**Example Calculation**:
"""
)

# Example data for a conversation with 3 questions
example_data = [
    {"Turn": 1, "Tokens per Question": 100, "RAG Tokens": 2000, "Tokens per Answer": 300, "Input Tokens": 2400, "Notes":"1 + 0"},
    {"Turn": 2, "Tokens per Question": 100, "RAG Tokens": 2000, "Tokens per Answer": 300, "Input Tokens": 4800, "Notes":"2 + 1"},
    {"Turn": 3, "Tokens per Question": 100, "RAG Tokens": 2000, "Tokens per Answer": 300, "Input Tokens": 4800, "Notes":"3 + 2"},
    {"Turn": 4, "Tokens per Question": 100, "RAG Tokens": 2000, "Tokens per Answer": 300, "Input Tokens": 4800, "Notes":"4 + 3"},
]

# Convert to DataFrame for display
example_df = pd.DataFrame(example_data)

# Display the table
st.table(example_df)

st.markdown(
    """
- **Total Tokens for the Conversation**: 
  - Example: 2400 + 4800 + 4800 + 4800= 14,400 tokens
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

This metric helps estimate how many citizens actively interact with the council's website.  
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

A conversation is a complete interaction session, which includes multiple questions.  
"""
)

st.subheader("Questions per Conversation (Turns)")
st.markdown(
    """
**Definition**: Average number of questions asked in a single conversation.  

One turn consists of:  
1. User input/question  
2. RAG process  
3. Chatbot response  

Scenario assumptions:  
- **Low**: 3 turns (brief, focused interactions)  
- **Medium**: 4 turns (standard query resolution)  
- **Heavy**: 8 turns (detailed, multi-step interactions)  

**Example of a 3-turn conversation**:  
1. User asks about council tax → RAG process → Bot responds  
2. User asks for payment methods → RAG process → Bot responds  
3. User asks for payment deadline → RAG process → Bot responds  
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
    Total Conversations × Questions per Conversation × Tokens per Question
    ```

4. **Calculate Final Cost**:  
    ```
    Total Tokens × Cost per Token
    ```
"""
)
