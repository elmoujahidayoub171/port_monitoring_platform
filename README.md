# PortMonitor

Network monitoring console that collects OS-level network activity (sockets,
ports, processes, connections) into PostgreSQL and visualizes it through a
Flask dashboard with live KPIs, sparklines, and generated alerts.

## Architecture

```
collector (app/data)  ->  manager (app/services)  ->  PostgreSQL 16 (app/migrations)
                          ->  analytics (app/analytics)  ->  dashboard (app/blueprints)
```

| Layer | Location | Role |
|---|---|---|
| Data | `app/data/` | Reads host state via `ss`, `lsof`, `ps`, then clean + transform |
| Services | `app/services/` | `process_connection_port_manager.py` orchestrates collect -> store |
| Database | `app/database/`, `app/repositories/` | Connection + row upserts |
| Schema | `app/migrations/` | SQL migrations applied on first DB boot |
| Analytics | `app/analytics/` | Statistics, alert generation, metric history |
| Dashboard | `app/blueprints/dashboard/`, `dashboard/` | Flask web UI + templates/static |

## Services (docker compose)

| Service | Container | Purpose | Ports |
|---|---|---|---|
| `database` | `my-postgres` | PostgreSQL 16, auto-runs migrations | host `5431` -> `5432` |
| `data_collector` | `portmonitor-collector` | Ongoing collection loop (every 5 min) | none (host pid/net) |
| `analytics` | `portmonitor-statistics` | Scheduled statistics pass | none |
| `dashboard` | `my-dashboard` | Flask web UI | `5000` |

## Requirements

- Docker + Docker Compose (v2)
- A `.env` file at the repo root with your DB credentials:

```env
HOSTNAME=localhost
DB_NAME=port_monitoring_db
DB_USER=you
DB_PASSWORD=your_password
DB_PORT=5431
```

> `DB_PORT` is the host-facing port for the container DB. Keep it free
> (5432 is often used by a local Postgres). Inside the compose network the
> dashboard/analytics services always reach Postgres on internal port 5432.

## Quick start

```bash
docker compose up -d --build
```

- First boot creates the DB/user and applies the SQL migrations; the schema is
  rebuilt only on an empty volume.
- The collector's first pass populates data within ~5 minutes.
- Open the dashboard: http://localhost:5000

## Useful commands

```bash
docker compose ps                       # service status
docker compose logs -f data_collector   # follow one service's logs
docker compose logs --tail=50 dashboard # last N lines

# run each service individually
docker compose up -d database
docker compose up -d data_collector
docker compose up -d dashboard
docker compose up -d analytics

# one-off collector pass (overrides the loop)
docker compose run --rm data_collector python -m app.services.process_connection_port_manager

# stop / restart
docker compose restart data_collector
docker compose stop analytics
docker compose start analytics
```

## Full reset (containers, images, volumes)

```bash
docker compose down -v --rmi all
docker image prune -af
docker volume prune -f
docker compose up -d --build
```

`-v` deletes the `pgdata` volume (all stored data).

## Run without Docker (local dev)

Requires a local PostgreSQL with the schema applied, then:

```bash
pip3 install -r requirements.txt
python run.py          # serves Flask on 0.0.0.0:5000
```

## Environment notes

- The collector runs with `pid: host`, `network_mode: host` and elevated
  privileges because it must inspect the host's sockets and processes.
- In older setups the collector ran as an unprivileged user via `sudo -n`;
  add the following to `/etc/sudoers` (via `sudo visudo`) if you run the
  pipeline on the host without Docker:

```
username ALL=(root) NOPASSWD : /usr/bin/ss
username ALL=(root) NOPASSWD : /usr/bin/lsof
username ALL=(root) NOPASSWD : /usr/bin/ps
```