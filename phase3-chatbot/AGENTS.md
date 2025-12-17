# AGENTS.md — Phase 3

## Overview
This document defines all agents used in Phase 3 of the project, their responsibilities, and how they interact with each other. Agents are autonomous units capable of performing tasks, communicating with other agents, and using subagents or skills when necessary.

---

## 1. Primary Agents

### 1.1 Claude Agent
- **Purpose:** Acts as the main reasoning and decision-making agent.
- **Responsibilities:**
  - Interpret high-level tasks.
  - Delegate sub-tasks to relevant subagents.
  - Maintain the state of ongoing tasks.
- **Subagents:** Task Parser, Spec Executor
- **Skills:** Language understanding, task decomposition

### 1.2 BetterAuth Agent
- **Purpose:** Handles authentication and authorization.
- **Responsibilities:**
  - Issue, verify, and refresh JWT tokens.
  - Validate user credentials.
  - Ensure access control across services.
- **Subagents:** Token Validator
- **Skills:** JWT management, encryption, user validation

### 1.3 GPT Integration Agent
- **Purpose:** Handles all interactions with GPT models.
- **Responsibilities:**
  - Send prompts and receive responses from GPT models.
  - Select the appropriate GPT model per task.
- **Subagents:** Model Selector, Prompt Formatter
- **Skills:** Prompt engineering, model orchestration

---

## 2. Subagents

### 2.1 Task Parser
- **Purpose:** Breaks down complex tasks into manageable subtasks.
- **Responsibilities:**
  - Analyze input instructions.
  - Generate sub-tasks for execution by other agents.
- **Skills:** NLP, task decomposition

### 2.2 Spec Executor
- **Purpose:** Executes tasks according to project specifications.
- **Responsibilities:**
  - Reads project specs.
  - Ensures outputs comply with defined rules.
- **Skills:** Specification enforcement, code generation

### 2.3 Token Validator
- **Purpose:** Validates JWTs and user sessions.
- **Responsibilities:**
  - Verify token authenticity.
  - Match user ID from token with requested resources.
- **Skills:** Security, authentication

### 2.4 Model Selector
- **Purpose:** Chooses the most suitable GPT model for the task.
- **Responsibilities:**
  - Compare models based on task type.
  - Route prompts to correct GPT instance.
- **Skills:** Model management, task classification

### 2.5 Prompt Formatter
- **Purpose:** Prepares prompts for GPT models.
- **Responsibilities:**
  - Convert tasks or questions into optimized prompt formats.
  - Ensure prompts follow best practices for model accuracy.
- **Skills:** Prompt engineering, text processing

---

## 3. Agent Communication

- Agents communicate asynchronously via internal messages or event queues.
- Subagents report progress and results back to their parent agent.
- Agents use a shared **Source of Truth** for task tracking and state management.

---

## 4. Source of Truth

- **Location:** `/project/source_truth.md` or central database.
- **Purpose:** Keeps track of:
  - Active tasks
  - Completed tasks
  - Agent states
  - Execution logs

---

## 5. Notes
- All agents must be modular and replaceable.
- New agents or subagents can be added following the same structure.
- Skills are reusable and can be shared between multiple agents.
