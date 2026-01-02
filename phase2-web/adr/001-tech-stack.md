# ADR-001: Technology Stack Selection

**Status:** Accepted
**Date:** 2025-12-10
**Decision Makers:** Claude, User

---

## Context

Need to select a technology stack for the Phase 2 multi-user web todo application that evolved from the Phase 1 console app.

## Decision

### Backend
- **Language:** Python 3.13+
- **Framework:** FastAPI
- **ORM:** SQLModel
- **Database:** Neon PostgreSQL (serverless)
- **Authentication:** JWT tokens with bcrypt password hashing

### Frontend
- **Framework:** Next.js 16+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Context API

## Rationale

### Backend
- **FastAPI** provides automatic OpenAPI docs, async support, and type hints
- **SQLModel** combines SQLAlchemy and Pydantic for type-safe database operations
- **Neon PostgreSQL** offers serverless scaling and easy setup
- **JWT** allows stateless authentication suitable for API-first architecture

### Frontend
- **Next.js 16** provides App Router with server components for better performance
- **TypeScript** ensures type safety and better developer experience
- **Tailwind CSS** enables rapid UI development with utility classes
- **React Context** is sufficient for auth state without external libraries

## Consequences

### Positive
- Type safety across the stack
- Fast development with hot reload
- Automatic API documentation
- Serverless database scaling

### Negative
- Learning curve for Next.js App Router patterns
- SQLModel is less mature than SQLAlchemy alone

## Alternatives Considered

1. **Django + React** - More batteries-included but heavier
2. **Express + React** - JavaScript throughout but less type safety
3. **Supabase** - All-in-one but less flexibility

---
