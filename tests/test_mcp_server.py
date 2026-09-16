"""Tests for the MCP server: the engine's tools stay wired to the engine."""

from __future__ import annotations

import pytest

from fastmcp.exceptions import ToolError

from scriptengine.mcp.server import mcp


@pytest.mark.asyncio
async def test_tools_are_registered():
    tools = await mcp.list_tools()
    names = {tool.name for tool in tools}
    assert {"research", "verify_script", "script_path"} <= names


@pytest.mark.asyncio
async def test_research_returns_bundle_and_prompt():
    result = await mcp.call_tool(
        "research",
        {"subject": "Shibuya Incident", "series": "jjk", "words": 3000},
    )
    assert result.is_error is False
    data = result.structured_content
    assert isinstance(data, dict)
    assert data["subject"] == "Shibuya Incident"
    assert data["beats"]
    assert "=== VOICE RULES" in data["prompt"]
    assert "=== SCRIPT FORMAT" in data["prompt"]


@pytest.mark.asyncio
async def test_research_rejects_unindexed_series():
    # Over the wire the stdio server turns this into an error result for the
    # client; call_tool in-process wraps it in a ToolError.
    with pytest.raises(ToolError, match="not indexed"):
        await mcp.call_tool(
            "research",
            {"subject": "Anything", "series": "not-a-series"},
        )


@pytest.mark.asyncio
async def test_research_bare_character_name_is_qa():
    # A bare name routes qa (the router's bare-name rule: a name that asks
    # nothing is a lookup, not a story - router.py "A bare name ... is a
    # lookup, not a story"). Auto mode delegates to the router, so the
    # bundle's mode is qa, not narrative.
    result = await mcp.call_tool(
        "research",
        {"subject": "Maki Zenin", "series": "jjk", "words": 2000},
    )
    assert result.is_error is False
    data = result.structured_content
    assert data is not None
    assert data["mode"] == "qa"
    assert data["subject"] == "Maki Zenin"


@pytest.mark.asyncio
async def test_verify_script_reports_invented_tags():
    result = await mcp.call_tool(
        "verify_script",
        {"text": "Gojo is sealed. (Chapter 999)", "series": "jjk"},
)
    assert result.is_error is False
    data = result.structured_content
    assert data is not None
    assert data["passed"] is False
    assert data["findings"][0]["tag"] == "(Chapter 999)"


@pytest.mark.asyncio
async def test_verify_script_passes_real_tags():
    result = await mcp.call_tool(
        "verify_script",
        {"text": "Gojo is sealed. (Chapter 1)", "series": "jjk"},
)
    assert result.is_error is False
    data = result.structured_content
    assert data is not None
    assert data["passed"] is True


@pytest.mark.asyncio
async def test_script_path_names_the_video_folder():
    result = await mcp.call_tool("script_path", {"title": "Shibuya Incident Explained"})
    assert result.is_error is False
    content = result.structured_content
    assert content is not None
    path = str(content["result"])
    assert "Shibuya Incident Explained" in path
    assert "Script" in path
    assert path.endswith(".md")
