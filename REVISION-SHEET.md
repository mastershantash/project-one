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

## 2. Essential Commands Cheat Sheet

### Part I: Application & Toolchain (`uv`)
```bash
# Environment & Dependencies
uv sync                                    # Create .venv and install all dependencies from lockfile
source .venv/bin/activate                  # Activate virtual environment
uv add <package>                           # Add runtime dependency to pyproject.toml and lock
uv add --dev <package>                     # Add development dependency

# Code Quality & Static Analysis
uv run ruff check .                        # Check code style, unused imports, anti-patterns
uv run ruff check --fix .                  # Automatically fix lint and import sorting
uv run ruff format .                       # Format code adhering to standard PEP 8
uv run mypy src/                           # Run strict static type analysis

# Automated Testing
uv run pytest -v                           # Execute test suite with verbose output

# Local Execution
uv run uvicorn ml_serving_capstone.main:app --host 0.0.0.0 --port 8000 --reload
```

### Part II: Kubernetes & GitOps Platform
```bash
# MicroK8s Management
microk8s status --wait-ready               # Check cluster status
microk8s kubectl get pods -A               # View all running pods across namespaces
microk8s kubectl logs -n ml-app -l app.kubernetes.io/name=ml-app --tail=50

# Helm Packaging & Linting
helm lint helm/ml-infra                    # Lint platform chart
helm lint helm/ml-app                      # Lint workload chart

# ArgoCD CLI & Credentials
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
argocd app list                            # List live synchronized applications
argocd app sync ml-app                     # Manually trigger immediate reconciliation

# Cross-Namespace Ingress Port Forwarding
microk8s kubectl port-forward -n ml-app svc/ml-app 8001:80 --address 0.0.0.0
```

---

## 3. Port & URL Matrix

| Service | Namespace | Access Type | Port | External URL | Default Credentials |
|---|---|---|---|---|---|
| **ArgoCD Web UI** | `argocd` | NodePort | 8080 | `https://localhost:30781` | `admin` / (From initial secret) |
| **Kafka UI** | `ml-infra` | NodePort | 8080 | `http://localhost:30880` | Anonymous |
| **Grafana Dashboards** | `ml-infra` | NodePort | 3000 | `http://localhost:30300` | `admin` / `admin` |
| **Splunk Enterprise** | Host Docker | Host Port | 8000 | `http://localhost:8000` | `admin` / `Changeme123!` |
| **Splunk HEC** | Host Docker | Host Port | 8088 | `https://localhost:8088` | Token: `2a58141a-232e-41ea-9b7c-5ee487970abe` |
| **Prometheus Server** | `ml-infra` | ClusterIP | 9090 | `http://prometheus:9090` | Internal scrape target |
| **ML Serving API** | `ml-app` | NodePort / pf | 8000 | `http://localhost:8001` | Anonymous (`/docs` for Swagger) |

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
2. **Helm Grafana Go Template Collision:** `{{status}}` in dashboard JSON interpreted as Go template function. **Fix:** Escape with `{{ `{{status}}` }}`.
3. **Fluent Bit Localhost Network Barrier:** `127.0.0.1:8088` from inside Pod routes to loopback, not host. **Fix:** Point to host LAN IP (`192.168.29.122:8088`).
4. **Kafka KRaft Cold-Start Quorum Race:** Topic Job crashes before KRaft controller election finishes. **Fix:** Use init-container polling `kafka-broker-api-versions.sh`.
5. **Ruff BLE001 & Import Sorting CI Breakage:** Blind exception checking flagged by default. **Fix:** Configure `[tool.ruff.lint] ignore = ["BLE001"]`.
6. **ArgoCD SharedResourceWarning Conflict:** Two apps managing same ClusterRoleBinding. **Fix:** Delete legacy monolithic app before deploying modular charts.
7. **Rolling Update Port-Forward Severance:** `kubectl port-forward` dies when pods terminate. **Fix:** Restart port-forward daemon targeting `svc/ml-app`.
8. **Cached `:latest` Tag Masking Production Code:** Pods skip image pull if `:latest` is cached. **Fix:** Tag with immutable Git SHA (`sha-<commit>`) and set `imagePullPolicy: Always`.
9. **Cross-Namespace DNS Lookups:** Bare service names fail across namespaces. **Fix:** Use strict FQDNs (`<svc>.<ns>.svc.cluster.local`).
10. **Async Redis Connection Pool Exhaustion:** Socket leaks under burst concurrency. **Fix:** Configure `socket_timeout=1.0` and `socket_connect_timeout=1.0`.
11. **Non-Root Permission Denied (UID 1000):** Runtime user unable to access root-installed `.venv`. **Fix:** `chown -R appuser:appgroup /app` and run `uv sync` as `USER appuser`.
12. **Monorepo Infinite GitOps Push Loop:** App CI pushing commit back to same repo triggering itself. **Fix:** Decouple into App repo and GitOps Platform repo.
