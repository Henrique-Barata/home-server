# Application Overview

## Purpose

**Expenses Tracker** is a lightweight, local-network web application for tracking shared household expenses between two users: **Henrique** and **Carlota**.

## Core Goals

1. Track all shared household expenses (rent, utilities, food, items, misc)
2. Provide monthly expense summaries
3. Track per-person spending to enable fair settlement
4. Export data to Excel (Google Sheets compatible)
5. Run efficiently on low-resource systems

## Key Design Principles

- **Simplicity over features**: Minimal dependencies, no heavy frameworks
- **Local-first**: Designed for LAN access, not public internet
- **Low resource usage**: SQLite file-based DB, vanilla HTML/CSS
- **Shared authentication**: Single password for both users (not multi-tenant)
- **Auditability**: All expense operations are logged

## Target Users

- **Henrique & Carlota** (hardcoded in configuration)
- Intended for couples or roommates tracking shared expenses
- Single household use case only

## Deployment Model

- Local machine or Raspberry Pi
- Flask development server (suitable for low-traffic LAN use)
- No production WSGI server required for intended use case
