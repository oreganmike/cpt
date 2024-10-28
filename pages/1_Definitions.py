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
Model selection sets the cost per input token and cost per output token according to Azure's OpenAI pricing page. 

"""
)

# Convert cost per token information into a table
st.subheader("Cost per Input and Output Tokens")
st.markdown(
    """
**Definition**: The price charged by Azure OpenAI for processing one input token or generating one output token.

- Uses GBP (£)
- Uses Global Deployment pricing
- Units are in tokens rather than per hour
"""
)

# Create a DataFrame for the cost per token with formatted values
model_costs_data = {
    "Model": ["gpt-4o", "gpt-4o-mini"],
    "Cost per Input Token": ["{:.10f}".format(0.000001866), "{:.10f}".format(0.00000011196)],
    "Cost per Output Token": ["{:.10f}".format(0.000007463801), "{:.10f}".format(0.0000004479)],
    "Cost per 1M Input Tokens": ["{:.2f}".format(1.8660), "{:.2f}".format(0.11196)],
    "Cost per 1M Output Tokens": ["{:.2f}".format(11.1958), "{:.2f}".format(0.4479)],
}

model_costs_df = pd.DataFrame(model_costs_data)

# Display the table
st.table(model_costs_df)




st.markdown("---")



# Population Metrics
st.header("2. Council Metrics")

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
st.header("3. Chatbot Metrics")

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
- **Low**: 2 turns (brief, focused interactions)  
- **Medium**: 4 turns (standard query resolution)  
- **Heavy**: 8 turns (detailed, multi-step interactions)  

**Example of a 3-turn conversation**:  
1. User asks about council tax → RAG process → Bot responds  
2. User asks for payment methods → RAG process → Bot responds  
3. User asks for payment deadline → RAG process → Bot responds  
"""
)


st.subheader("User input tokens")
st.markdown(
    """
**Definition**: The number of tokens used in a user's input.
"""
)

# Create a DataFrame for typical token values
tokens_per_question_data = {
    "Exchange Type": ["Very Short", "Short", "Medium", "Long"],
    "Token Range": ["5-50", "50-100", "100-200", "200+"],
}

tokens_per_question_df = pd.DataFrame(tokens_per_question_data)

# Display the table
st.table(tokens_per_question_df)

st.markdown(
    """
**Example**:
- **User question: "What are the council tax bands?" (7 tokens)**
- RAG process: Generates embeddings, performs search, submits question to model with chunks (~2,000 tokens)
- Model response with detailed explanation (393 tokens)
- Total = 7 user input tokens

"""
)

st.subheader("RAG Tokens")
st.markdown(
    """
**Definition**: The number of tokens consumed during the RAG process.  
- Essentially all RAG tokens consist of text chunks that are submitted to the model for a contextually aided response
"""
)

# Create a DataFrame for RAG token example
rag_tokens_example_data = {
    "Component": ["User Question", "RAG Process", "Model Response"],
    "Tokens": [7, 2000, 393],
}

rag_tokens_example_df = pd.DataFrame(rag_tokens_example_data)

# Display the table
st.table(rag_tokens_example_df)

st.markdown(
    """
**Example**:
- User question: "What are the council tax bands?" (7 tokens)
- **RAG process: Generates embeddings, performs search, submits question to model with chunks (2,000 tokens)**
- Model response with detailed explanation (393 tokens)
- Total = 2,000 user input tokens

"""
)


st.subheader("Model output tokens")
st.markdown(
    """
**Definition**: The number of tokens the model generates for its response.
"""
)

st.markdown(
    """
**Example**:
- User question: "What are the council tax bands?" (7 tokens)  
- RAG process: Generates embeddings, performs search, submits question to model with chunks (~2,000 tokens)  
- **Model response with detailed explanation (393 tokens)**
- Total = 393 model output tokens

"""
)


st.subheader("Tokens per Conversation")
st.markdown(
    """
**Definition**: The total number of tokens consumed in a conversation is calculated using the formula:  
 Qn + Qn-1  
  
Where:  
- Qn &nbsp; is the number of tokens for the current question (including User input tokens, RAG tokens, and model output tokens).  
- Qn-1 &nbsp; is the number of tokens for the current question minus one.
"""
)

# Example data for a conversation with 3 questions
example_data = [
    {"Question": 1, "User input tokens": 100, "RAG Tokens": 2000, "Model output tokens": 300, "Input Tokens": 2400, "Notes":"1 + 0"},
    {"Question": 2, "User input tokens": 100, "RAG Tokens": 2000, "Model output tokens": 300, "Input Tokens": 4800, "Notes":"2 + 1"},
    {"Question": 3, "User input tokens": 100, "RAG Tokens": 2000, "Model output tokens": 300, "Input Tokens": 4800, "Notes":"3 + 2"},
    {"Question": 4, "User input tokens": 100, "RAG Tokens": 2000, "Model output tokens": 300, "Input Tokens": 4800, "Notes":"4 + 3"},
]

# Convert to DataFrame for display
example_df = pd.DataFrame(example_data)

# Display the table
st.table(example_df)

st.markdown(
    """
**Total Tokens for the Conversation**:  
- Example: 2,400 + 4,800 + 4,800 + 4,800 = 16,800 tokens
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
