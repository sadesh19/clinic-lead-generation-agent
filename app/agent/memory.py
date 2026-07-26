"""
memory.py — Conversation memory for the agent.

Uses LangChain's in-memory chat history so the agent remembers
previous searches within a session (useful for follow-up queries
like "now search in Dubai too").
"""
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import List


class AgentMemory:
    """Thin wrapper around InMemoryChatMessageHistory."""

    def __init__(self) -> None:
        self._history = InMemoryChatMessageHistory()

    def add_user_message(self, content: str) -> None:
        self._history.add_user_message(content)

    def add_ai_message(self, content: str) -> None:
        self._history.add_ai_message(content)

    def get_messages(self) -> List[BaseMessage]:
        return self._history.messages

    def clear(self) -> None:
        self._history.clear()

    def to_dict_list(self) -> list:
        return [
            {"role": m.type, "content": m.content}
            for m in self._history.messages
        ]
