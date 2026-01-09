# AI Knowledge Base

This folder serves as the **authoritative knowledge base** for AI agents working on this application.

## Purpose

AI agents should use these documents as the **first and primary source of truth** when:
- Understanding application architecture and behavior
- Proposing new features or improvements
- Making refactoring decisions
- Debugging issues

## Document Index

| File | Description |
|------|-------------|
| [01-overview.md](01-overview.md) | Application purpose, goals, and design principles |
| [02-architecture.md](02-architecture.md) | Tech stack, project structure, patterns |
| [03-features.md](03-features.md) | Complete feature documentation |
| [04-domain.md](04-domain.md) | Domain concepts and business logic |
| [05-data-persistence.md](05-data-persistence.md) | Database schema and access patterns |
| [06-conventions.md](06-conventions.md) | Coding standards and patterns |
| [07-constraints.md](07-constraints.md) | Known limitations and trade-offs |
| [08-roadmap.md](08-roadmap.md) | Future improvements and version history |

## Maintenance Rules

This folder is a **living document system**. AI agents must:

1. **Check before scanning**: Use this folder instead of reading entire codebase
2. **Update on changes**: When behavior, architecture, or conventions change
3. **Add new concepts**: When new features or patterns are introduced
4. **Record decisions**: Document trade-offs and constraints when discovered

## Quick Reference

- **Users**: Henrique & Carlota (hardcoded)
- **Database**: SQLite at `data/expenses.db`
- **Auth**: Single shared password via Flask-Login
- **Categories**: Food, Utilities, Fixed (Rent/Internet), Stuff (custom types), Other
- **Currency**: Euros (€)
- **Export**: Excel via openpyxl

## Last Updated

**2026-01-06** - Initial knowledge base creation
