# Known Constraints & Trade-offs

## Intentional Limitations

### Single Household Design
- **Constraint**: Only two fixed users (Henrique & Carlota)
- **Trade-off**: No user management overhead, simpler data model
- **Impact**: Cannot be used by multiple households without code changes

### Shared Authentication
- **Constraint**: Single password for both users
- **Trade-off**: Simple auth without password management
- **Impact**: No per-user permissions or activity tracking by user account

### SQLite Database
- **Constraint**: Limited concurrent write access
- **Trade-off**: No database server to manage, file-based backup
- **Impact**: Not suitable for high-concurrency scenarios (not a problem for 2 users)

### No API
- **Constraint**: All interactions through web UI
- **Trade-off**: Simpler implementation, server-side rendering
- **Impact**: Cannot integrate with mobile apps or external services

### Euro Currency Only
- **Constraint**: Hardcoded € formatting in exports
- **Trade-off**: Simplified implementation
- **Impact**: Users in other regions need to modify export.py

## Technical Constraints

### Development Server
- Uses Flask's built-in development server
- Suitable for LAN use with 1-2 users
- Not production-hardened (no rate limiting, etc.)

### No ORM
- Raw SQL queries in models
- More control but more verbose
- Must handle SQL injection prevention manually (parameterized queries)

### No JavaScript
- All interactions are full page loads
- Simple and reliable but less dynamic
- No real-time updates

### No Test Suite
- No automated tests currently
- Manual testing only
- Risk of regression when making changes

## Known Gaps

### Missing Features
- [ ] Recurring variable expenses automation
- [ ] Receipt/image attachment
- [ ] Budget tracking/limits
- [ ] Email notifications
- [ ] Mobile-optimized views

### Technical Debt
- [ ] No database migrations framework (Alembic, etc.)
- [ ] No test coverage
- [ ] Password stored in config file (should use hashing)
- [x] ~~No CSRF protection on forms~~ (Open Redirect fixed, CSRF still needed)
- [x] ~~Open Redirect vulnerability~~ (Fixed 2026-01-06)

## Security Considerations

### Current State
- Password in plaintext in config (env var recommended)
- No HTTPS by default
- Session-based auth with cookie
- **Open Redirect Protection**: Login uses endpoint whitelist (fixed 2026-01-06)
- **Hardcoded USER_ID**: Intentional design for single-user local app (accepted risk)

### Acceptable Because
- Local network only
- Trusted household members
- No sensitive data beyond expense amounts

### If Public Exposure Needed
1. Use proper secret management
2. Enable HTTPS
3. Add CSRF protection
4. Hash the password
5. Add rate limiting
