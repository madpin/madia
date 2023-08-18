import os
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import (
    ConversationBufferWindowMemory,
    ConversationTokenBufferMemory,
)
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType, load_tools
import logging

from langchain.chains import LLMChain

logger = logging.getLogger(__name__)


def _get_chat_model(open_ai_model="chatgpt-3.5-turbo", streaming=True) -> ChatOpenAI:
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


def search_llmmath(
    input_text,
    streaming=True,
    open_ai_model="gpt-3.5-turbo",
):
    llm = _get_chat_model(open_ai_model, streaming)
    tools = load_tools(
        ["ddg-search", "llm-math"],
        llm=llm,
    )

    agent = initialize_agent(
        tools, llm, agent="zero-shot-react-description", verbose=True
    )
    ans = agent.run(input_text)
    return ans


def single_message(
    input_text,
    system_message=None,
    streaming=True,
    open_ai_model="gpt-3.5-turbo",
):
    llm = _get_chat_model(open_ai_model, streaming)
    msgs = []
    if system_message:
        msgs.append(SystemMessage(content=system_message))
    msgs.append(HumanMessage(content=input_text))
    ans = llm.predict_messages(msgs)
    return ans.content


# def buffer_window_message(
#     input_text,
#     system_message=None,
#     streaming=True,
#     open_ai_model="gpt-3.5-turbo",
# ):
#     msgs = []
#     if system_message:
#         msgs.append(SystemMessagePromptTemplate.from_template(system_message))
#     msgs.extend(
#         (
#             MessagesPlaceholder(variable_name="chat_history"),
#             HumanMessagePromptTemplate.from_template("{question}"),
#         )
#     )
#     prompt = ChatPromptTemplate(messages=msgs)
#     llm = _get_chat_model(open_ai_model, streaming)
#     memory = ConversationTokenBufferMemory(
#         memory_key="chat_history",
#         return_messages=True,
#         max_token_limit=2000,
#         llm=llm,
#     )

#     chain = LLMChain(llm=llm, prompt=prompt, verbose=True, memory=memory)
#     ans = chain({"question": input_text})
#     logger.debug(f"Open Ai Conversation: {ans}")
#     return ans["text"]


class BufferedWindowMessage:
    def __init__(self, open_ai_model="gpt-3.5-turbo", streaming=True):
        self.llm = _get_chat_model(open_ai_model, streaming)
        self.memory = ConversationTokenBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000,
            llm=self.llm,
        )
        self.chain = None

    def get_response(self, input_text, system_message=None):
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
            llm=self.llm, prompt=prompt, verbose=False, memory=self.memory
        )

        ans = self.chain({"question": input_text})
        logger.debug(f"Open Ai Conversation: {ans}")
        return ans["text"]


class BufferedSearchWindowMessage:
    def __init__(self, open_ai_model="gpt-3.5-turbo", streaming=True):
        self.llm = _get_chat_model(open_ai_model, streaming)
        # self.memory = ConversationTokenBufferMemory(
        #     memory_key="chat_history",
        #     return_messages=True,
        #     max_token_limit=2000,
        #     llm=self.llm,
        # )
        # self.chain = None

    def get_response(self, input_text, system_message=None):
        print(input_text)
        search = GoogleSerperAPIWrapper()
        tools = [
            Tool(
                name="Intermediate Answer",
                func=search.run,
                description="useful for when you need to ask with search",
            )
        ]
        self_ask_with_search = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.SELF_ASK_WITH_SEARCH,
            verbose=False,
        )

        ans = self_ask_with_search.run(input_text)

        # logger.debug(f"Open Ai Conversation: {ans}")
        return ans
