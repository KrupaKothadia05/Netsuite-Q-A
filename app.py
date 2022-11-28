import streamlit as st
import requests


st.set_page_config(page_title="NetSuite Applications Online Help", page_icon=":book:", layout="wide")

st.title("NetSuite Applications Online Help")

text = st.text_input("Enter your question here")
noofdocs = st.selectbox(
    "Select the number of top matching documents",
    (1, 5, 10, 15, 20, 25)
)

base_url = "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/"
if text:
      results = requests.get("http://127.0.0.1:8000/query", params={"q": text})
      with st.spinner('Searching for answers'):
        print(results.status_code)
        results = results.json()
        print(results)
        # print(results.json())
        for item in results["answers"]:
          # heading = "<a href='https://www.w3schools.com'>Visit W3Schools.com!</a>"
          temp = item
          page_link = temp["meta"]["page_link"]
          heading = "[{}]({})".format(temp['meta']['name'], base_url + page_link)
          # st.title('NetSuite Applications Suite - {}'.format(temp['meta']['name']))
          st.title('NetSuite Applications Suite - {}'.format(heading))
          st.write('Tags - {}'.format(temp['meta']['tags']))
          print(temp['context'])
          print(temp["meta"]["page_link"])
          st.write(temp["context"])
      st.write("")
