# pkgprobe API — Deployment Guide

## Overview

The pkgprobe API runs as a FastAPI service with three endpoint tiers:

- `/v1/analyze` (free) -- static analysis, no VM required
- `/v1/trace` (pro) -- VMware trace, requires VM host
- `/v1/auto-wrap` -- trace + PSADT wrapper + .intunewin packaging

## Quick start (analyze-only, no VM)

```bash
docker compose up -d
```

This starts the API with only `/v1/analyze` enabled. No VMware or trace infrastructure needed.

Test:

```bash
curl -F "installer=@setup.exe" http://localhost:8000/v1/analyze
curl http://localhost:8000/health
```

## Full deployment (with trace + auto-wrap)

### Host requirements

- VMware Workstation (or ESXi with vmrun CLI access)
- A prepared Windows VM snapshot with:
  - VMware Tools installed
  - ProcMon at `C:\trace\tools\procmon.exe`
  - IntuneWinAppUtil (for .intunewin packaging)
  - Clean snapshot named `TRACE_BASE` (or custom name)
- Docker for the API container

### Environment variables

Create a `.env` file:

```env
# Trace VM
TRACE_ENABLED=true
TRACE_VMX_PATH=C:\VMs\TraceVM\TraceVM.vmx
TRACE_SNAPSHOT_NAME=TRACE_BASE
TRACE_GUEST_USERNAME=Administrator
TRACE_GUEST_PASSWORD=your_password

# Optional API key auth
PKGPROBE_API_AUTH_ENABLED=false
```

Run:

```bash
docker compose --env-file .env up -d
```

## Database

SQLite by default (stored in Docker volume at `/data/pkgprobe_api.db`).

For PostgreSQL, set:

```env
DATABASE_URL=postgresql://user:pass@host:5432/pkgprobe
```

Tables are auto-created on first startup.

## API endpoints

| Endpoint | Method | Tier | Description |
|----------|--------|------|-------------|
| `/health` | GET | public | Health check |
| `/v1/analyze` | POST | free | Static analysis |
| `/v1/trace` | POST | pro | VMware trace |
| `/v1/auto-wrap` | POST | auto_wrap | Trace + wrapper |
| `/v1/artifacts/{id}` | GET | auto_wrap | Download .intunewin |

All authenticated endpoints require `X-API-Key` header.

## Rate limits

| Tier | Requests per minute |
|------|-------------------|
| free | 60 |
| pro | 300 |
| auto_wrap | 600 |
