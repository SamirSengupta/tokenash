# 011. Deployment

**Status:** done

## Deployment Profiles

### Docker Profile

**Image:** `tokenash/tokenash:latest`

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

RUN pip install tokenash

EXPOSE 8787

ENTRYPOINT ["tokenash", "proxy"]
CMD ["--host", "0.0.0.0", "--port", "8787"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  tokenash:
    image: tokenash/tokenash:latest
    ports:
      - "8787:8787"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TOKENASH_MODE=token
    volumes:
      - tokenash-data:/root/.tokenash

volumes:
  tokenash-data:
```

**Run:**
```bash
docker-compose up -d
```

---

### Native Profile

**Installation:**
```bash
pip install tokenash
```

**Run:**
```bash
tokenash proxy --host 0.0.0.0 --port 8787
```

---

### Embedded Profile

**Usage:**
```python
from tokenash import TokenashClient

client = TokenashClient(
    api_key="your-api-key",
    base_url="http://localhost:8787"
)

result = await client.compress(messages)
```

---

## Cloud Presets

### AWS (EC2/ECS)

```yaml
# ~/.tokenash/config.yaml
deployment:
  profile: aws
  instance_type: t3.medium

compression:
  enabled: true
  max_tokens: 8192

cache:
  backend: redis
  redis_url: redis://localhost:6379
```

### Google Cloud (Cloud Run)

```yaml
deployment:
  profile: gcp
  region: us-central1
  memory: 512Mi
  cpu: 1
```

### Azure (Container Apps)

```yaml
deployment:
  profile: azure
  resource_group: tokenash-rg
```

---

## Runtime Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOKENASH_MODE` | `token` | Proxy mode (`token` or `cache`) |
| `TOKENASH_PORT` | `8787` | Proxy port |
| `TOKENASH_HOST` | `127.0.0.1` | Proxy host |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `TOKENASH_TELEMETRY` | `off` (opt-in) | Set to `on` to opt in to telemetry |

### Config File

```yaml
# ~/.tokenash/config.yaml
proxy:
  host: 0.0.0.0
  port: 8787

compression:
  enabled: true
  max_tokens: 4096
  overlap_tokens: 512
  content_sensitivity: 0.5
  preserve_system_messages: true
  priority_tokens: 1024

cache:
  enabled: true
  ttl: 3600
  max_size: 10000

telemetry:
  metrics:
    enabled: true
  tracing:
    enabled: false

learn:
  enabled: false
```

---

## Resource Requirements

| Deployment | CPU | Memory | Storage |
|------------|-----|--------|---------|
| Minimal | 0.5 core | 512MB | 1GB |
| Default | 1 core | 1GB | 5GB |
| Enterprise | 2 cores | 2GB | 20GB |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-draft | 2026-04-16 | Initial deployment document |
