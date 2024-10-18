import streamlit as st
import openai

# OpenAI API 키 설정
openai.api_key = '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'

def query_to_sql(question, schema):
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"Translate this question to SQL query based on the schema {schema}: {question}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

st.title('Text to SQL Query Generator')

# 스키마 입력
schema = st.text_input("Enter your database schema:", "Schema example: Table1(column1, column2), Table2(column1, column2)")

# 사용자 질문 입력
question = st.text_area("Enter your question about the data:")

if st.button("Generate SQL Query"):
    if question:
        sql_query = query_to_sql(question, schema)
        st.text_area("Generated SQL Query:", sql_query, height=300)
    else:
        st.warning("Please enter a question.")