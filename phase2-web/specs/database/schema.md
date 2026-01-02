# Database Schema Specification

> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10
> **Database:** Neon Serverless PostgreSQL

---

## Overview

This document defines the database schema for the multi-user todo web application. The schema supports user authentication and task management with proper referential integrity.

---

## Tables

### users

Stores user account information. Managed by Better Auth.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    name VARCHAR(255),
    image TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Columns:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | gen_random_uuid() | Primary key |
| `email` | VARCHAR(255) | No | - | User email (unique) |
| `email_verified` | BOOLEAN | No | FALSE | Email verification status |
| `name` | VARCHAR(255) | Yes | NULL | Display name |
| `image` | TEXT | Yes | NULL | Profile image URL |
| `created_at` | TIMESTAMPTZ | No | NOW() | Account creation time |
| `updated_at` | TIMESTAMPTZ | No | NOW() | Last update time |

---

### sessions

Stores active user sessions. Managed by Better Auth.

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE UNIQUE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**Columns:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | gen_random_uuid() | Primary key |
| `user_id` | UUID | No | - | FK to users.id |
| `token` | VARCHAR(255) | No | - | Session token (unique) |
| `expires_at` | TIMESTAMPTZ | No | - | Session expiration |
| `ip_address` | VARCHAR(45) | Yes | NULL | Client IP address |
| `user_agent` | TEXT | Yes | NULL | Client user agent |
| `created_at` | TIMESTAMPTZ | No | NOW() | Session creation time |
| `updated_at` | TIMESTAMPTZ | No | NOW() | Last update time |

---

### accounts

Stores OAuth provider accounts. Managed by Better Auth.

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_account_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_account_id)
);

-- Indexes
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
```

**Columns:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | gen_random_uuid() | Primary key |
| `user_id` | UUID | No | - | FK to users.id |
| `provider` | VARCHAR(50) | No | - | OAuth provider name |
| `provider_account_id` | VARCHAR(255) | No | - | Provider's user ID |
| `access_token` | TEXT | Yes | NULL | OAuth access token |
| `refresh_token` | TEXT | Yes | NULL | OAuth refresh token |
| `expires_at` | TIMESTAMPTZ | Yes | NULL | Token expiration |
| `created_at` | TIMESTAMPTZ | No | NOW() | Account link time |
| `updated_at` | TIMESTAMPTZ | No | NOW() | Last update time |

---

### tasks

Stores user tasks (todo items).

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_title_not_empty CHECK (LENGTH(TRIM(title)) > 0),
    CONSTRAINT chk_title_length CHECK (LENGTH(title) <= 255),
    CONSTRAINT chk_description_length CHECK (description IS NULL OR LENGTH(description) <= 2000)
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

**Columns:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | gen_random_uuid() | Primary key |
| `user_id` | UUID | No | - | FK to users.id |
| `title` | VARCHAR(255) | No | - | Task title |
| `description` | TEXT | Yes | NULL | Task description |
| `completed` | BOOLEAN | No | FALSE | Completion status |
| `created_at` | TIMESTAMPTZ | No | NOW() | Task creation time |
| `updated_at` | TIMESTAMPTZ | No | NOW() | Last update time |

**Constraints:**
| Constraint | Type | Rule |
|------------|------|------|
| `chk_title_not_empty` | CHECK | Title must have non-whitespace characters |
| `chk_title_length` | CHECK | Title max 255 characters |
| `chk_description_length` | CHECK | Description max 2000 characters |

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐
│   users     │       │  accounts   │
├─────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)     │
│ email       │  │    │ user_id(FK) │──┐
│ name        │  │    │ provider    │  │
│ ...         │  │    │ ...         │  │
└─────────────┘  │    └─────────────┘  │
                 │                      │
                 │    ┌─────────────┐  │
                 │    │  sessions   │  │
                 │    ├─────────────┤  │
                 ├────│ user_id(FK) │──┤
                 │    │ token       │  │
                 │    │ ...         │  │
                 │    └─────────────┘  │
                 │                      │
                 │    ┌─────────────┐  │
                 │    │   tasks     │  │
                 │    ├─────────────┤  │
                 └────│ user_id(FK) │──┘
                      │ title       │
                      │ completed   │
                      │ ...         │
                      └─────────────┘
```

---

## SQLModel Definitions

### User Model

```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    email_verified: bool = Field(default=False)
    name: str | None = Field(default=None, max_length=255)
    image: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
    sessions: list["Session"] = Relationship(back_populates="user")
    accounts: list["Account"] = Relationship(back_populates="user")
```

### Task Model

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

### Session Model

```python
class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="sessions")
```

### Account Model

```python
class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: str = Field(max_length=50)
    provider_account_id: str = Field(max_length=255)
    access_token: str | None = Field(default=None)
    refresh_token: str | None = Field(default=None)
    expires_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="accounts")

    class Config:
        # Unique constraint on (provider, provider_account_id)
        table_args = (
            UniqueConstraint("provider", "provider_account_id"),
        )
```

---

## Migrations

### Initial Migration

```sql
-- Migration: 001_initial_schema
-- Created: 2025-12-10

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    name VARCHAR(255),
    image TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_account_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_account_id)
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_title_not_empty CHECK (LENGTH(TRIM(title)) > 0),
    CONSTRAINT chk_title_length CHECK (LENGTH(title) <= 255),
    CONSTRAINT chk_description_length CHECK (description IS NULL OR LENGTH(description) <= 2000)
);

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);
```

---

## Data Retention

| Table | Retention Policy |
|-------|------------------|
| `users` | Permanent (until account deletion) |
| `sessions` | Auto-cleanup expired sessions daily |
| `accounts` | Permanent (cascade delete with user) |
| `tasks` | Permanent (cascade delete with user) |

---

## Backup Strategy

- **Neon Point-in-Time Recovery:** Enabled (7-day retention)
- **Daily Snapshots:** Automated via Neon
- **Cross-Region Replication:** Configured for disaster recovery

---

## Related Specifications

- `/specs/features/task-crud.md` - Task CRUD feature specification
- `/specs/features/authentication.md` - Authentication feature specification
- `/specs/api/rest-endpoints.md` - REST API endpoints

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
