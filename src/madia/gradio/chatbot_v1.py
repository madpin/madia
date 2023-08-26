from __future__ import annotations

import gradio as gr
import openai
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage


class ShortProgressStringsHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        yield token


def cb_fn(_):
    CSS = """
    .contain { display: flex; flex-direction: column; }
    .gradio-container { height: 100vh !important; }
    #component-0 { height: 100%; }
    #component-2 { height: 100%; !important; }

    #chatbot { flex-grow: 1; overflow: auto;}
    """
    llm = ChatOpenAI(temperature=1.0, model="gpt-3.5-turbo-0613")

    def predict(message, history):
        history_langchain_format = []
        for human, ai in history:
            history_langchain_format.append(HumanMessage(content=human))
            history_langchain_format.append(AIMessage(content=ai))
        history_langchain_format.append(HumanMessage(content=message))
        gpt_response = llm(
            history_langchain_format, callbacks=[ShortProgressStringsHandler()]
        )
        return gpt_response.content

    gr.ChatInterface(predict, css=CSS, theme=gr.themes.Soft()).queue().launch()
