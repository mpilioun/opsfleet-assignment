from langgraph.graph.state import CompiledStateGraph

from src.agent.agent import build_agent


def test_build_agent_compiles():
    """Regression test: the whole graph (root + 2 subagents + tools + HITL +
    memory + skills backend) wires together without raising."""
    agent = build_agent()
    assert isinstance(agent, CompiledStateGraph)
