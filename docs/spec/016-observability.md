# 016. Observability

**Status:** done

## Telemetry

### Metrics

Tokenash exposes Prometheus metrics at `/metrics`.

**Key Metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `tokenash_requests_total` | Counter | Total requests |
| `tokenash_tokens_original` | Counter | Original token count |
| `tokenash_tokens_compressed` | Counter | Compressed token count |
| `tokenash_savings_percent` | Histogram | Savings distribution |
| `tokenash_cache_hits_total` | Counter | Cache hits |
| `tokenash_cache_misses_total` | Counter | Cache misses |
| `tokenash_compression_duration_seconds` | Histogram | Compression latency |
| `tokenash_request_duration_seconds` | Histogram | Total request latency |

**Prometheus scrape config:**
```yaml
scrape_configs:
  - job_name: 'tokenash'
    static_configs:
      - targets: ['localhost:8787']
    metrics_path: '/metrics'
```

---

### Tracing

OpenTelemetry tracing support.

**Configuration (Langfuse):**
```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
TOKENASH_LANGFUSE_ENABLED=1
# Optional: override endpoint and service name
# LANGFUSE_BASE_URL=https://cloud.langfuse.com
# TOKENASH_LANGFUSE_SERVICE_NAME=tokenash
```

**Spans:**
| Span | Description |
|------|-------------|
| `tokenash.proxy.request` | Full request lifecycle |
| `tokenash.compression` | Compression operation |
| `tokenash.cache.lookup` | Cache check |
| `tokenash.provider.call` | Provider API call |

---

### Logging

**Log Levels:**

| Level | Use Case |
|-------|----------|
| `DEBUG` | Detailed debugging |
| `INFO` | General operation |
| `WARNING` | Degraded operation |
| `ERROR` | Failures |

**Log Format (JSON):**
```json
{
  "timestamp": "2026-04-16T12:00:00Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "abc123",
  "savings": 0.45,
  "duration_ms": 120
}
```

**Configuration:**
```bash
# Logging level is controlled via the --log-level CLI flag (tokenash proxy --log-level debug)
# or RUST_LOG env var for the Rust proxy. No TOKENASH_LOG_LEVEL env var exists.
```

Or in config:
```yaml
logging:
  level: INFO
  format: json
```

---

## Dashboard

**URL:** `http://localhost:8787/dashboard`

**Metrics Shown:**
- Total savings over time
- Requests per day
- Cache hit rate
- Top compressed endpoints
- Session overview

**Requires:** the proxy process to be running. The dashboard is served by default at `/dashboard`.

---

## Alerting

### Recommended Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | error_rate > 5% | warning |
| LowSavings | savings < 20% | warning |
| CacheDown | cache_hits < 10% for 1h | critical |
| ProxyDown | health check fails | critical |

**Alert rule example (Prometheus):**
```yaml
groups:
  - name: tokenash
    rules:
      - alert: HighErrorRate
        expr: rate(tokenash_errors_total[5m]) / rate(tokenash_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in Tokenash"
```

---

## Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Basic health check |
| `/livez` | GET | Liveness check (process alive) |
| `/readyz` | GET | Readiness check (can serve traffic) |

**Health response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Readiness response:**
```json
{
  "ready": true,
  "checks": {
    "database": true,
    "cache": true,
    "provider": true
  }
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-draft | 2026-04-16 | Initial observability document |
