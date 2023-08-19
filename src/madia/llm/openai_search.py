from __future__ import annotations

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper

from madia.llm.utils import FileLoggerHandler, response_strip
from madia.logger import LoggingMixin, get_logger
from madia.repl.utils import delete_stdout_content, temporary_stdout

logger = get_logger(__name__)


class BufferedSearchWindowMessage(LoggingMixin):
    def __init__(self, open_ai_model="gpt-3.5-turbo", streaming=True):
        self.streaming = streaming
        self.llm = ChatOpenAI(
            model=open_ai_model,
            temperature=0.3,
            streaming=streaming,
            callbacks=[FileLoggerHandler()],
        )

    def get_response(self, input_text, system_message=None):
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

        with temporary_stdout():
            ret = self_ask_with_search.run(input_text)

        return response_strip(ret)
