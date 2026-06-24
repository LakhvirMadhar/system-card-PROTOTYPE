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

from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.agent_spec import AgentSpec

ToolFunction = Callable[..., Any] | BaseTool | BaseToolset


def effective_instruction(spec: AgentSpec) -> str:
    """Reconstructs the full instruction ADK actually sends to the model.

    ADK's identity request processor (google.adk.flows.llm_flows.identity)
    silently appends a "You are an agent..." preamble naming the agent and
    its description onto the configured instruction, for any agent run in
    the default "chat" mode (the only mode InMemoryRunner accepts for a root
    agent — "single_turn" would suppress this, but isn't usable here). The
    system card's recorded instruction has to include this, or it wouldn't
    match what the model is actually given — defeating the card's purpose.

    This reproduces that processor's exact string format (a private, but
    small and stable, part of ADK) rather than calling it directly, since
    it's not part of ADK's public API.

    Args:
        spec: The agent spec whose effective instruction to compute.

    Returns:
        spec.instruction with ADK's identity preamble appended, exactly as
        the model actually receives it.
    """
    identity = f'You are an agent. Your internal name is "{spec.name}".'
    if spec.description:
        identity += f' The description about you is "{spec.description}".'

    return f"{spec.instruction}\n\n{identity}"


def build_agent_from_spec(
    spec: AgentSpec, tool_registry: ToolRegistry, ollama_api_base: str
) -> LlmAgent:
    """Builds an LlmAgent from a registered agent spec, resolving its tools by name.

    Args:
        spec: The agent's name, instruction, model, and equipped tool names.
        tool_registry: Registry to resolve spec.tool_names against. Construct
            a separate ModelConfig per spec if different agents need
            different models — nothing here is shared global state.
        ollama_api_base: Where the local Ollama server is reachable.

    Returns:
        An LlmAgent ready to be run.
    """
    os.environ["OLLAMA_API_BASE"] = ollama_api_base

    tool_functions: list[ToolFunction] = [
        tool_registry.get(name).load() for name in spec.tool_names
    ]

    model = spec.model
    generation_config = types.GenerateContentConfig(
        temperature=model.temperature,
        top_p=model.top_p,
        top_k=model.top_k,
        seed=model.seed,
        presence_penalty=model.presence_penalty,
        frequency_penalty=model.frequency_penalty,
        stop_sequences=list(model.stop_sequences) if model.stop_sequences is not None else None,
        max_output_tokens=model.max_output_tokens,
    )

    return LlmAgent(
        name=spec.name,
        description=spec.description,
        model=LiteLlm(model=f"ollama_chat/{model.model_name}"),
        instruction=spec.instruction,
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
