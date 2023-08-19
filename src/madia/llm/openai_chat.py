from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager
from math import ceil

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)

from madia.llm.utils import MyCustomSyncHandler

logger = logging.getLogger(__name__)


class BufferedWindowMessage:
    def __init__(self, open_ai_model="gpt-3.5-turbo", streaming=True):
        self.streaming = streaming
        self.llm = ChatOpenAI(
            model=open_ai_model,
            temperature=0.3,
            streaming=True,
            callbacks=[MyCustomSyncHandler()],
        )

        self.memory = ConversationTokenBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000,
            llm=self.llm,
        )
        self.chain = None

    def get_response(self, input_text, system_message=None, streaming=None):
        streaming = streaming or (streaming is None and self.streaming)
        msgs = []
        if system_message:
            msgs.append(SystemMessagePromptTemplate.from_template(system_message))
        msgs.extend(
            (
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}"),
            )
        )
        prompt = ChatPromptTemplate(messages=msgs)

        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=False,
            memory=self.memory,
            # callbacks=[StreamingStdOutCallbackHandler()]
            # if streaming
            # else [MyCustomSyncHandler()],
        )

        # with temporary_stdout():
        ret = self.chain({"question": input_text})

        return ret["text"]
