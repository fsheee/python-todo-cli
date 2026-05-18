"""
AI Agent module for Phase 3 Todo Chatbot

This module implements the AI agent that interprets user intent
and orchestrates todo operations through MCP tools.

Spec Reference: specs/agents/todo-agent.md
"""

from .todo_agent import process_chat_message

__all__ = ["process_chat_message"]
