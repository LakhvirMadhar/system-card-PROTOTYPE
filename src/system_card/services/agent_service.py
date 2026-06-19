"""Wraps a minimal ADK agent over the registered tools, exposing a single run() entrypoint."""

import os
import uuid
from collections.abc import Callable
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.genai import types

from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig


def build_agent(model: ModelConfig, ollama_api_base: str) -> LlmAgent:
    """Builds an LlmAgent wired to every tool in a freshly populated registry.

    Args:
        model: The model and generation hyperparameters this agent should run
            with. Construct a separate ModelConfig per agent if different
            agents need different models — nothing here is shared global state.
        ollama_api_base: Where the local Ollama server is reachable.

    Returns:
        An LlmAgent ready to be run.
    """
    os.environ["OLLAMA_API_BASE"] = ollama_api_base

    registry = ToolRegistry()
    register_default_tools(registry)
    tool_functions: list[Callable[..., Any] | BaseTool | BaseToolset] = [
        entry.load() for entry in registry.entries()
    ]

    generation_config = types.GenerateContentConfig(
        temperature=model.temperature,
        top_p=model.top_p,
        max_output_tokens=model.max_output_tokens,
    )

    return LlmAgent(
        name="system_card_agent",
        description="A small agent exposing a handful of toy tools.",
        model=LiteLlm(model=f"ollama_chat/{model.model_name}"),
        instruction="Use the available tools to answer the user's request.",
        tools=tool_functions,
        generate_content_config=generation_config,
    )


class AgentService:
    """Runs the agent against a single user message and returns its final reply."""

    def __init__(self, agent: LlmAgent) -> None:
        """Wraps an in-memory runner around the given agent.

        Args:
            agent: The configured LlmAgent to run.
        """
        self._runner = InMemoryRunner(agent=agent)

    async def run(self, message: str) -> str:
        """Sends one message to the agent and returns its final text reply.

        Args:
            message: The user's message.

        Returns:
            The agent's final response text, or an empty string if it never replied.
        """
        user_id = "system-card-user"
        session_id = str(uuid.uuid4())

        await self._runner.session_service.create_session(
            app_name=self._runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        new_message = types.Content(role="user", parts=[types.Part(text=message)])

        reply = ""

        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        ):
            if event.is_final_response() and event.content is not None:
                parts = event.content.parts or []
                reply = "".join(part.text or "" for part in parts)

        return reply
