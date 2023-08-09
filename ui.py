import streamlit as st
import llm
import es_query
import es_ml
import urllib.parse
import re

ELASTIC_LOGO = 'https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt601c406b0b5af740/620577381692951393fdf8d6/elastic-logo-cluster.svg'
APP_NAME = "Content Search Demo"

st.set_page_config(layout="wide", page_title=APP_NAME)

st.image(ELASTIC_LOGO, width=100)
st.title(APP_NAME)

def highlight_sentence(sentences, i):
    text = "### _\""
    for n, sentence in enumerate(sentences):
        escaped = escape_markdown(sentence)
        if n > 0:
            text = text + " "
        if i == n:
            text = text + ":orange[_" + escaped + "_]"
        else:
            text = text + escaped
    text = text + "\"_"
    return text

def escape_markdown(text: str, version: int = 1, entity_type: str = None) -> str:
    """
    Helper function to escape telegram markup symbols.

    Args:
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``1``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.
    """
    if int(version) == 1:
        escape_chars = r'_*`['
    elif int(version) == 2:
        if entity_type in ['pre', 'code']:
            escape_chars = r'\`'
        elif entity_type == 'text_link':
            escape_chars = r'\)'
        else:
            escape_chars = r'_*[]()~`>#+-=|{}.!'
    else:
        raise ValueError('Markdown version must be either 1 or 2!')

    text = text.replace("$", "").strip()

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# Main form
with st.form("chat_form"):
    sources = es_query.get_sources()
    source = st.selectbox('Source', sources)
    query = st.text_input("Query: ")
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        title, body, url, figures = es_query.search(source, query)

        st.write(f"#### [_{title}_]({url})")

        answer = es_ml.ask_question(body, query)
        context_answer = None
        if answer is not None:
            context_answer, i, sentences = es_ml.find_sentence_that_answers_question(body, query, answer)
            if context_answer is not None:
                text = highlight_sentence(sentences, i)
                st.markdown(text)
            else:
                escaped = escape_markdown(body)
                text = ":orange[_\"" + escaped + "\"_]"
                st.markdown(text)

        if len(figures) > 0:
            cols = st.columns(len(figures))
            for i, fig in enumerate(figures):
                with cols[i]:
                    st.image(fig['url'], caption=fig['caption'])   

        st.write("---")
        st.write("## OpenAI Q&A using ELSER Results")

        answer, time_taken, cost = llm.ask_question(body, query)
        
        if llm.PROMPT_FAILED in answer:
            st.write("Insufficient data in Elasticsearch results")
        else:
            st.write(f"**{answer.strip()}**")
            st.write(f"\nCost: ${cost:0.6f}, ChatGPT response time: {time_taken:0.4f} sec")
