import streamlit as st
import llm
import es_query
import urllib.parse

ELASTIC_LOGO = 'https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt601c406b0b5af740/620577381692951393fdf8d6/elastic-logo-cluster.svg'
APP_NAME = "Content Search Demo"
PROMPT_FAILED = "I'm unable to answer the question based on the results."

st.set_page_config(layout="wide", page_title=APP_NAME)

st.image(ELASTIC_LOGO, width=100)
st.title(APP_NAME)

# Main chat form
with st.form("chat_form"):
    sources = es_query.get_sources()
    source = st.selectbox('Source', sources)
    query = st.text_input("Query: ")
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        title, body, url, figures = es_query.search(source, query)

        st.write(f"## Elasticsearch ELSER Results")
        st.write(f"[_{title}_]({url})")
        st.write(f"**{body}**")
        if len(figures) > 0:
            cols = st.columns(len(figures))
            for i, fig in enumerate(figures):
                with cols[i]:
                    st.image(fig['url'], caption=fig['caption'])   

        st.write("---")
        st.write("## ML Q&A using ELSER Results")
        answer = es_query.ask_question(body, query)
        st.write(f"**{answer}**")

        st.write("---")
        st.write("## OpenAI Q&A using ELSER Results")

        prompt = f"Answer this question with a short answer: {query}\nUsing only the information from this Elastic Doc: {body}\nIf the answer is not contained in the supplied doc reply '{PROMPT_FAILED}' and nothing else"
        answer, time_taken, cost = llm.query(prompt)
        
        if PROMPT_FAILED in answer:
            st.write("Insufficient data in Elasticsearch results")
        else:
            st.write(f"**{answer.strip()}**")
            st.write(f"\nCost: ${cost:0.6f}, ChatGPT response time: {time_taken:0.4f} sec")


