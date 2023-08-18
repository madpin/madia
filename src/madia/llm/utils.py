from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import logging

logger = logging.getLogger(__name__)


def get_openai_chat_model(
    open_ai_model="chatgpt-3.5-turbo",
    streaming=True,
) -> ChatOpenAI:
    if streaming:
        return ChatOpenAI(
            model=open_ai_model,
            temperature=0.3,
            streaming=streaming,
            callbacks=[StreamingStdOutCallbackHandler()],
        )
    else:
        return ChatOpenAI(
            model=open_ai_model,
            temperature=0.3,
            streaming=streaming,
            callbacks=[],
        )
