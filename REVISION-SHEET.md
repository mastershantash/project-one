# Python for Senior Java Engineers: Quick Revision Sheet

*Fast lookup cheat sheet for building and deploying production-grade ML applications.*

---

## 1. Java ↔ Python Rosetta Stone

| Java Concept | Python / MLOps Equivalent | Notes |
|---|---|---|
| `Spring Boot` (`@RestController`) | `FastAPI` | `@app.post("/predict")`, async/await first class |
| `Tomcat` / `Netty` | `uvicorn` | ASGI server running the event loop |
| `@RequestBody` DTO + `@Valid` | `Pydantic` v2 (`BaseModel`) | Automatic type validation & 422 responses before handler runs |
| `@ConfigurationProperties` | `pydantic-settings` | Loads & validates typed config from environment variables |
| `pom.xml` / `build.gradle` | `pyproject.toml` | Single file for dependencies, packaging, and tool config |
| Resolved Maven dependency tree | `uv.lock` | Pins exact transitive dependency tree for reproducible builds |
| `mvn` / `gradle` wrapper | `uv` | Ultra-fast Rust-based package installer (`uv sync`, `uv run`) |
| `JUnit 5` | `pytest` | Test discovery (`test_*.py`), plain `assert` statements |
| `Checkstyle` / `Spotless` | `ruff` | Blazing fast linter and formatter |
| Java compiler type checking | `mypy` | Static analysis of type hints (`x: int -> str`) |
| `try-with-resources` | `with ... as f:` | Context manager guaranteeing deterministic cleanup |
| `try / catch / finally` | `try / except / finally` | Maps 1:1; no checked vs unchecked exception distinction |

---

## 2. ML Serving Core Concepts

### Model Representation
A model file is learned numerical weights + a computational graph.
* **Training (`.fit()`):** High compute, slow, batch/offline. **Never run inside an online serving request.**
* **Inference (`.predict()`):** Forward pass calculation ($y = Wx + b$), fast (ms), lightweight. **100% of serving.**

### Synchronous vs. Asynchronous Inference
* **FastAPI (Sync Path):** Used when the caller is blocked waiting for an immediate answer (UI request, real-time checkout scoring).
* **Kafka (Async Path):** Used for decoupling, high-throughput streaming, and batch requests where the client does not wait synchronously.

### Predictive Cache-Aside Pattern
1. Generate deterministic MD5 hash of input features:
   ```python
   key = f"pred:{MODEL_VERSION}:" + hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
   ```
2. **Always include `MODEL_VERSION` in the cache key** so redeploying a retrained model automatically invalidates obsolete predictions.
3. **Graceful Degradation:** Wrap Redis lookups in `try/except`. If Redis is down, log a warning and run model inference directly. Never fail an API request due to cache unavailability!

---

## 3. Production Docker Hardening

```dockerfile
FROM python:3.12-slim

# 1. Non-root user for Kubernetes PodSecurity standards
RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup -s /bin/bash -m appuser
WORKDIR /app

# 2. Copy prebuilt uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 3. Layer caching: install third-party dependencies BEFORE copying code
COPY pyproject.toml uv.lock README.md ./
RUN chown -R appuser:appgroup /app
USER appuser
RUN uv sync --frozen --no-dev --no-install-project

# 4. Copy application source
COPY --chown=appuser:appgroup src/ ./src/
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "ml_serving_capstone.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Kubernetes Probes & Lifecycle

| Probe | Endpoint | Function | K8s Failure Action |
|---|---|---|---|
| **Liveness** | `/healthz` | Checks if event loop is unblocked | Restarts container (`SIGKILL`) |
| **Readiness** | `/readyz` | Checks if ML model weights are loaded in RAM | Removes pod from Service endpoints (no 503s) |

---

## 5. Helm & GitOps (ArgoCD)

### Helm Structure
* `Chart.yaml`: Metadata & SemVer.
* `values.yaml`: Configurable contracts (`replicaCount: 2`, `resources`, `env`).
* `templates/`: Parameterized Kubernetes manifests (`deployment.yaml`, `service.yaml`, `configmap.yaml`, `hpa.yaml`).

### GitOps vs. Push CI/CD
* **Traditional Push:** CI holds admin cluster credentials (`KUBECONFIG`) and executes `kubectl apply`. Massive attack surface.
* **GitOps Pull (ArgoCD):** Cluster pulls from Git. Zero inbound firewall rules needed.
* **Self-Healing (`selfHeal: true`):** If someone deletes a deployment with `kubectl`, ArgoCD detects the drift and recreates it in seconds to match Git.

---

## 6. Real Bugs Logged & Fixed

1. **`async def` without `await`**: An `async def` function that runs synchronous blocking code (like `redis.Redis`) blocks the entire server event loop! Must use `redis.asyncio` with `await`.
2. **Missing `await` call**: Calling an async function without `await` produces an unexecuted coroutine warning and silently no-ops.
3. **Docker layer cache failure**: `uv sync` requires `README.md` if declared in `pyproject.toml`. Missing `README.md` breaks build.
4. **CRD Annotation 256KB Limit**: Applying huge CRDs with `kubectl apply` fails due to `last-applied-configuration`. Fix: `kubectl apply --server-side`.
5. **ArgoCD Empty Remote Repo**: Applying an ArgoCD application before pushing local commits to GitHub results in `ComparisonError: remote repository is empty`. Push first!
