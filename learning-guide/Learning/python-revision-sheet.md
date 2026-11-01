# Python MLOps & GitOps: Senior Architect Revision Sheet

*Fast lookup reference for building, containerizing, and productionizing enterprise ML systems.*

---

## 1. Java ↔ Python Rosetta Stone

| Java Concept | Modern Python (3.12+) Equivalent | Key Architectural Difference |
|---|---|---|
| `Spring Boot` (`@RestController`) | `FastAPI` | Asynchronous coroutines run directly on ASGI event loop (`uvicorn`) without thread overhead. |
| `Tomcat` / `Netty` | `uvicorn` (uvloop) | Non-blocking event loop written in C (libuv). |
| `@RequestBody` DTO + `@Valid` | `Pydantic` v2 (`BaseModel`) | Rust-compiled validation (`pydantic-core`), 10x faster than pure Python. |
| `@ConfigurationProperties` | `pydantic-settings` | Strongly typed environment variable injection. |
| `pom.xml` / `build.gradle.kts` | `pyproject.toml` | Single standard file for metadata, dependencies, and tool settings (PEP 517/621). |
| Resolved Maven dependency tree | `uv.lock` | Deterministic cryptographic lockfile pinning exact transitive wheels. |
| `mvn` / `gradle` wrapper | `uv` | Rust package manager running 10-100x faster than pip/poetry with global content cache. |
| `JUnit 5` + Mockito | `pytest` + `httpx` | Function-level test discovery, fixture injection, plain `assert` syntax. |
| `Checkstyle` / `SpotBugs` | `ruff` | Blazingly fast Rust linter and formatter. |
| Java compiler type checking | `mypy` | Compile-time static type analysis of type annotations (`x: int -> str`). |
| `try-with-resources` | `with ... as f:` | Context manager protocol (`__enter__` / `__exit__`) guaranteeing cleanup. |
| `try / catch / finally` | `try / except / finally` | Maps 1:1; no checked vs unchecked exception distinction. |
| `Jedis` / `Lettuce` | `redis.asyncio` | Non-blocking Redis connection pool. |
| `Spring Kafka` | `aiokafka` | Asynchronous consumer and producer event loop iteration. |

---

## 2. The Zero-Dollar Production Stack (What We Implemented for $0)

| Capability | Enterprise Paid Tool | Zero-Dollar CNCF / OSS Replacement | Implemented Manifest / Command |
|---|---|---|---|
| **Traffic Routing & Rate Limiting** | AWS ALB ($25/mo) + Cloudflare WAF ($200/mo) | Ingress-NGINX with annotations | `helm/ml-app/templates/ingress.yaml` (`limit-rps: 100`) |
| **High Availability SLA** | Custom Drain Automation | Kubernetes PodDisruptionBudget (PDB) | `helm/ml-app/templates/pdb.yaml` (`minAvailable: 1`) |
| **Zero-Trust Network Isolation** | Calico Enterprise / Cilium Mesh | Kubernetes NetworkPolicies | `helm/ml-infra/templates/networkpolicy.yaml` |
| **Streaming ML Worker** | Dedicated Kafka Microservice Cluster | Async Python worker in K8s | `helm/ml-app/templates/worker-deployment.yaml` |
| **Proactive Alerting** | Datadog Alerting / NewRelic | Prometheus Alerting Rules | `helm/ml-infra/templates/prometheus-rules.yaml` |
| **Container Vulnerability Scanning** | Snyk / Prisma Cloud ($$$) | Aquasec Trivy Action | `.github/workflows/ci.yaml` (`trivy-action`) |
| **Git Secret Encryption** | HashiCorp Vault Cloud | Bitnami Sealed Secrets | Encrypted in Git, decrypted in cluster |

---

## 3. What CANNOT Be Done For Free (The Hard Economic Limits)

1. **Physical Multi-AZ Datacenter Redundancy:** True 99.99% availability requires 3 physically separated datacenters with isolated power grids. Cross-AZ egress bandwidth has per-GB cloud charges.
2. **Managed Cloud Load Balancers & Static IPv4:** Cloud providers charge ~$20/month for ALBs and ~$3.60/month per allocated IPv4 address.
3. **Corporate Apex Domain & Enterprise DNS:** Genuine `company.com` domains require annual ICANN registrar fees. Free dynamic DNS (`duckdns`) is blocked by enterprise firewalls.
4. **Automated 3 AM Voice/SMS Wake-Up Calls:** Telecom carriers bill per voice/SMS minute. Free Slack/Discord bots cannot bypass mobile phone "Do Not Disturb" during Sev-1 outages.
5. **High-Volume Log Retention (Splunk):** Splunk free license is capped at 500 MB/day with RBAC/alerts disabled. Multi-terabyte log retention requires commercial licenses and cloud storage.
6. **Continuous GPU Compute:** Deep learning/LLMs require NVIDIA GPUs (A10G/H100) costing $500–$2,500/month per instance.
7. **B2B SAML SSO & SOC-2 / HIPAA Auditing:** Okta/Entra ID place SAML behind enterprise paywalls. Formal compliance audits require third-party CPA firms.

---

## 4. Key Architectural Patterns

### 1. Fail-Open Cache Resilience
```python
async def get_cached_prediction(input_data: list[float]) -> list[float] | None:
    try:
        key = cache_key(input_data)
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Redis cache lookup failed: {e}. Falling back to model inference.")
    return None
```
*Rule:* Redis is an accelerator, not an authority. If Redis drops, log a warning and fall back to model inference. **Never return HTTP 500 due to cache failure.**

### 2. Versioned Cache Keys
*Format:* `pred:{MODEL_VERSION}:{MD5_HASH}`  
*Example:* `pred:v1:a8f5c...`  
*Rule:* Always embed `MODEL_VERSION` in the cache key so rolling out a new model version invalidates stale predictions immediately without manual cache flushing.

### 3. Non-Root Hardened Multi-Stage Dockerfile
*Rule:* Never run containers as root (`UID 0`) in production Kubernetes. Create `USER appuser` (`UID 1000`), copy only `.venv` and `src/` to the runtime container, and strip build toolchains.

### 4. Decoupled Polyrepo Pattern
*Rule:* Keep Application code (`project-one`) separate from GitOps manifests (`project-one-gitops`). App CI builds images and updates `values.yaml` in the GitOps repo. ArgoCD watches only the GitOps repo, eliminating recursive build loops.

---

## 5. Production War Stories Summary (12 Battle-Tested Bugs)

1. **ArgoCD 262KB Metadata Limit:** Large CRD OpenAPI schemas exceed client-side ETCD annotation limits. **Fix:** Install via `kubectl apply --server-side`.
2. **Helm Grafana & Prometheus Template Collision:** `{{status}}` and `{{ $labels }}` interpreted as Go template functions. **Fix:** Escape with `{{ `{{status}}` }}` and `{{ `{{ $labels.instance }}` }}`.
3. **Fluent Bit Localhost Network Barrier:** `127.0.0.1:8088` from inside Pod routes to loopback, not host. **Fix:** Point to host LAN IP (`192.168.29.122:8088`).
4. **Kafka KRaft Cold-Start Quorum Race:** Topic Job crashes before KRaft controller election finishes. **Fix:** Use init-container polling `kafka-broker-api-versions.sh`.
5. **Ruff BLE001 & Import Sorting CI Breakage:** Blind exception checking flagged by default. **Fix:** Configure `[tool.ruff.lint] ignore = ["BLE001"]`.
6. **ArgoCD SharedResourceWarning Conflict:** Two apps managing same ClusterRoleBinding. **Fix:** Delete legacy monolithic app before deploying modular charts.
7. **Rolling Update Port-Forward Severance:** `kubectl port-forward` dies when pods terminate. **Fix:** Restart port-forward daemon targeting `svc/ml-app`.
8. **Cached `:latest` Tag Masking Production Code:** Pods skip image pull if `:latest` is cached. **Fix:** Tag with immutable Git SHA (`sha-<commit>`) and set `imagePullPolicy: Always`.
9. **Cross-Namespace DNS Lookups:** Bare service names fail across namespaces due to `ndots:5`. **Fix:** Use strict FQDNs (`<svc>.<ns>.svc.cluster.local`).
10. **Async Redis Connection Pool Exhaustion:** Socket leaks under burst concurrency. **Fix:** Configure `socket_timeout=1.0` and `socket_connect_timeout=1.0`.
11. **Non-Root Permission Denied (UID 1000):** Runtime user unable to access root-installed `.venv`. **Fix:** `chown -R appuser:appgroup /app` and run `uv sync` as `USER appuser`.
12. **Monorepo Infinite GitOps Push Loop:** App CI pushing commit back to same repo triggering itself. **Fix:** Decouple into App repo and GitOps Platform repo.
