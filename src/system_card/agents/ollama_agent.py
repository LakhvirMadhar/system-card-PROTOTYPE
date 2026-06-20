"""Defines the ollama_agent — its instruction, tools, and pinned model."""

from system_card.schemas.agent_spec import AgentSpec
from system_card.schemas.model_config import ModelConfig

NAME = "ollama_agent"

INSTRUCTION = (
    "Use the available tools to answer questions about which Ollama models "
    "are available locally. When you reply, name which tool(s) you used and "
    "what each one returned."
)

TOOL_NAMES = ("ollama_list",)

PINNED_MODEL_TAG = "gemma4:latest"
PINNED_MODEL_DIGEST = "c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"


def build_spec(model: ModelConfig) -> AgentSpec:
    """Builds this agent's spec for the given model configuration.

    Args:
        model: The model and generation hyperparameters to run this agent
            with — construct it from PINNED_MODEL_TAG/PINNED_MODEL_DIGEST.

    Returns:
        This agent's AgentSpec.
    """
    return AgentSpec(
        name=NAME,
        instruction=INSTRUCTION,
        model=model,
        tool_names=TOOL_NAMES,
    )
