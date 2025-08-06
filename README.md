# Grafana Observability Stack

Local observability stack equivalent to Grafana Cloud Free tier.

> [!WARNING]
> Please use [docker-otel-lgtm](https://github.com/grafana/docker-otel-lgtm) instead.

## Architecture

### Component Overview

This stack provides a comprehensive observability solution with the following components:

#### **Grafana** (port: 3001)
- **Purpose**: Unified dashboard and visualization platform
- **What it does**: 
  - Creates dashboards combining metrics, logs, and traces
  - Provides alerting capabilities
  - Correlates data across different observability signals
- **Why needed**: Central place to visualize and analyze all observability data

#### **Prometheus** (port: 9091)
- **Purpose**: Metrics collection, storage, and alerting
- **What it does**:
  - Scrapes metrics from applications and infrastructure
  - Stores time-series data efficiently
  - Provides powerful query language (PromQL)
  - Handles alerting rules
- **Why needed**: Essential for monitoring application performance, resource usage, and SLA metrics

#### **Tempo** (port: 3200)
- **Purpose**: Distributed tracing backend
- **What it does**:
  - Collects and stores distributed traces
  - Tracks requests across microservices
  - Identifies bottlenecks and errors in request flows
  - Integrates seamlessly with Grafana for trace visualization
- **Why needed**: Critical for understanding request flows, debugging performance issues, and identifying dependencies

#### **OpenTelemetry Collector** (ports: 4317/4318)
- **Purpose**: Unified telemetry data collection and processing
- **What it does**:
  - Receives traces, metrics, and logs from applications
  - Processes, filters, and transforms telemetry data
  - Routes data to appropriate backends (Prometheus, Tempo, Loki)
  - Provides vendor-neutral instrumentation
- **Why needed**: Standardizes telemetry collection and reduces vendor lock-in

#### **Loki** (port: 3100)
- **Purpose**: Log aggregation and storage system
- **What it does**:
  - Collects logs from applications and infrastructure
  - Stores logs efficiently with label-based indexing
  - Provides LogQL for querying logs
  - Integrates with Grafana for log visualization
- **Why needed**: Centralized logging for debugging, audit trails, and correlation with metrics/traces

#### **Promtail**
- **Purpose**: Log shipping agent for Loki
- **What it does**:
  - Discovers and collects logs from various sources
  - Adds labels and metadata to log entries
  - Ships logs to Loki for storage
- **Why needed**: Efficient log collection from Docker containers and system logs

#### **Node Exporter** (port: 9100)
- **Purpose**: System and hardware metrics collection
- **What it does**:
  - Exposes system metrics (CPU, memory, disk, network)
  - Provides hardware information
  - Monitors system health
- **Why needed**: Infrastructure monitoring to understand resource utilization and system health

### Data Flow
```
Applications
    ↓ (OpenTelemetry SDK)
OpenTelemetry Collector
    ↓
├── Prometheus (metrics) ──┐
├── Tempo (traces) ────────┤
└── Loki (logs) ───────────┤
    ↓                      ↓
Grafana (unified visualization)
```

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Launch

```bash
# Or using docker-compose directly
docker compose up -d
```

### Access URLs

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| Grafana | http://localhost:3001 | admin/admin | Dashboards and visualization |
| Prometheus | http://localhost:9091 | - | Metrics and alerting |
| Tempo | http://localhost:3200 | - | Distributed tracing |
| Node Exporter | http://localhost:9100 | - | Distributed tracing |

## Usage

### Commands

```bash
# Lifecycle management
docker compose up -d           # Start stack
docker compose down            # Stop stack
docker compose restart         # Restart stack

# Monitoring
docker compose ps              # Check service status
docker compose logs            # View all logs
docker compose logs grafana
docker compose logs otel
docker compose logs prometheus
docker compose logs tempo
docker compose logs grafana

# Maintenance
docker compose down -v         # Complete cleanup (including volumes)
```

## Testing with Sample Traces

To verify the observability stack is working correctly, you can generate sample traces:

```bash
# Useing Docker
docker build -f Dockerfile.trace-generator -t observability-trace-generator .
docker run --rm --network observability-stack_observability observability-trace-generator
```

```bash
# Using python
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc

# Run trace generator
python test-traces.py
```

### What the test generates:
- **User request traces**: Simulates API calls with authentication, database queries, and external API calls
- **Order processing traces**: Complex workflows with validation, inventory checks, payments, and notifications
- **Error scenarios**: Includes occasional failures to test error handling
- **Realistic timing**: Variable response times to simulate real-world conditions

### Viewing the traces:
1. Open Grafana: http://localhost:3001
2. Go to **Explore** → **Tempo**
3. Search for traces
4. Explore the trace timeline and spans

## Configuration Files

- `config/prometheus.yml` - Prometheus scraping configuration
- `config/tempo.yaml` - Tempo tracing backend configuration
- `config/otel-collector-config.yaml` - OpenTelemetry Collector pipeline configuration
- `config/grafana/provisioning/` - Grafana datasources and dashboards
- `config/promtail-config.yml` - Promtail log collection configuration

## Monitoring Targets

### Infrastructure
- **Host Metrics**: CPU, memory, disk usage, network traffic
- **Container Metrics**: Resource usage per container
- **System Logs**: Docker container logs, system events
