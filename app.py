import streamlit as st
import requests


st.set_page_config(page_title="NetSuite Applications Online Help", page_icon=":book:", layout="wide")

st.title("NetSuite Applications Online Help")

text = st.text_input("Enter your question here")
noofdocs = st.selectbox(
    "Select the number of top matching documents",
    (1, 5, 10, 15, 20, 25),
)

if text:
      with st.spinner('Searching for answers'):
        results = requests.get("http://127.0.0.1:8000/query", params={"q": text})
        print(results.status_code)
        results = results.json()
        print(results)
        # print(results.json())
        for item in results["answers"]:
          temp = item
          st.title('NetSuite Applications Suite - {}'.format(temp['meta']['name']))
          st.write('Tags - {}'.format(temp['meta']['tags']))
          print(temp['context'])
          st.write(temp["context"])
      st.write("")
