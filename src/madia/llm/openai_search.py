from madia.llm.utils import get_openai_chat_model
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType
import logging

logger = logging.getLogger(__name__)


class BufferedSearchWindowMessage:
    def __init__(self, open_ai_model="gpt-3.5-turbo", streaming=True):
        self.llm = get_openai_chat_model(open_ai_model, streaming)

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

        ans = self_ask_with_search.run(input_text)

        return ans.strip()
