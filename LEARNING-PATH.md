# Python for Production ML Serving & GitOps — Learning Path & Tracker

**Who this is for:** Senior Java Backend / Distributed Systems Engineers learning Python, Cloud-Native Kubernetes, and GitOps to build and productionize high-throughput ML systems.

**The Curriculum Design:** Split cleanly into two self-contained parts:
- **Part I: The Application Layer** (Python 3.12, `uv`, `src/` layout, scikit-learn, async Redis, FastAPI, Kafka streaming, Ruff, Mypy, Pytest, Docker).
- **Part II: The Platform & GitOps Layer** (MicroK8s v1.30, Splunk HEC, Polyrepo pattern, Dual Namespaces, Helm charts, KRaft Kafka, Kafka UI, Prometheus, Grafana, ArgoCD, GHCR CI/CD, 12 War Stories, Senior Q&A).

---

## Master Progress Tracker

| Section | Topic | Status | Key Deliverable / Verification |
|---|---|---|---|
| **00** | Java ↔ Python Rosetta Stone | ✅ Complete | Mental model bridging JVM, Maven, Spring Boot, Netty, threads to asyncio & GIL |
| **PART I** | **The Application Layer** | | **Python Microservice & Hardened Container** |
| 01 | Toolchain & Environment Setup | ✅ Complete | Python 3.12, Astral `uv`, Git, standalone binary caching |
| 02 | Modern Project Scaffolding | ✅ Complete | Strict `src/` layout, package imports, directory tree |
| 03 | Modern Dependencies & Lockfiles | ✅ Complete | Declarative `pyproject.toml`, cryptographic `uv.lock`, `.venv` |
| 04 | The ML Model Serving Logic | ✅ Complete | `model.py`, scikit-learn, `@lru_cache` singleton weights |
| 05 | Asynchronous Redis Caching Layer | ✅ Complete | `redis_cache.py`, versioned MD5 keys, fail-open resilience, 1s socket timeouts |
| 06 | FastAPI Serving REST API | ✅ Complete | `main.py`, Pydantic v2 DTOs, `/healthz`, `/readyz`, `/predict`, JSON logging |
| 07 | Prometheus Instrumentation | ✅ Complete | `prometheus-fastapi-instrumentator`, OpenMetrics `/metrics` endpoint |
| 08 | Event-Driven Kafka Streaming Worker | ✅ Complete | `kafka_worker.py`, `aiokafka` consumer/producer loop, graceful shutdown |
| 09 | Static Analysis & Type Safety | ✅ Complete | `uv run ruff check --fix`, `uv run mypy src/`, zero warnings |
| 10 | Automated Pytest Suite | ✅ Complete | `tests/test_model.py`, `tests/test_api.py`, 6 passing tests |
| 11 | Production Multi-Stage Dockerfile | ✅ Complete | Non-root `UID 1000` (`appuser`), 3-step `uv` cache layers, `.dockerignore` |
| 12 | Local Verification Runbook | ✅ Complete | Bare-metal `uvicorn` and local Docker container cURL verification |
| **PART II** | **The Platform & GitOps Layer** | | **Cloud-Native Kubernetes & GitOps Platform** |
| 13 | Local Kubernetes Cluster (MicroK8s) | ✅ Complete | MicroK8s v1.30, user permissions, RBAC, CoreDNS, hostpath-storage |
| 14 | Splunk Enterprise & HEC Setup | ✅ Complete | Docker container, Web UI (8000), HEC port 8088, token auth |
| 15 | The Decoupled Polyrepo Pattern | ✅ Complete | `project-one` (App repo) & `project-one-gitops` (Platform repo) |
| 16 | Dual-Namespace Topology & DNS | ✅ Complete | `ml-infra` vs `ml-app`, blast-radius isolation, CoreDNS FQDN routing |
| 17 | Shared Platform Helm Chart | ✅ Complete | `helm/ml-infra` (Redis, KRaft Kafka, Kafka UI, Prometheus, Grafana, Fluent Bit) |
| 18 | Workload Serving Helm Chart | ✅ Complete | `helm/ml-app` (Deployment, ClusterIP, ConfigMap, HPA) |
| 19 | Declarative Topics & Kafka UI | ✅ Complete | Init-container TCP readiness polling, Kafka UI NodePort 30880 |
| 20 | ArgoCD GitOps Engine Setup | ✅ Complete | Server-Side Apply install (bypassing 262KB CRD limit), NodePort 30781 |
| 21 | Multi-App GitOps Manifests | ✅ Complete | `infra-app.yaml` & `workload-app.yaml`, automated sync, self-healing |
| 22 | Enterprise CI/CD & GHCR Integration | ✅ Complete | GitHub Actions, Git SHA tagging (`sha-<commit>`), GitOps writeback |
| 23 | Cluster Runbook & Port Matrix | ✅ Complete | Consolidated endpoint matrix, smoke-test scripts, health checks |
| 24 | Production War Stories (12 Bugs) | ✅ Complete | In-depth root cause and fixes for all 12 production issues encountered |
| 25 | Senior Engineering Revision Q&A | ✅ Complete | 15 advanced interview questions bridging Java, MLOps, and Kubernetes |

---

## Detailed Curriculum Structure

### Part I: The Application Layer
1. **Toolchain Setup:** Installing Python 3.12 and Astral's `uv`. Verifying standalone binary cache.
2. **Scaffolding:** Implementing the standard `src/` layout (`src/ml_serving_capstone/`). Preventing false-positive imports during testing.
3. **Dependencies:** Managing runtime and dev dependencies in `pyproject.toml`. Generating deterministic `uv.lock`.
4. **ML Inference Model:** Constructing `model.py` with scikit-learn Linear Regression. Using `@lru_cache` as a singleton provider.
5. **Resilient Redis Caching:** Implementing async cache in `redis_cache.py`. Key hashing (`pred:v1:<md5>`), TTL expiration (3600s), and fail-open exception shielding.
6. **FastAPI REST API:** Developing `main.py` with Pydantic v2 schemas. Exposing Kubernetes Liveness (`/healthz`) and Readiness (`/readyz`) probes.
7. **Telemetry:** Integrating `prometheus-fastapi-instrumentator` for OpenMetrics standard scraping.
8. **Kafka Worker:** Asynchronous stream processing with `aiokafka`. Consuming inference requests and emitting predictions.
9. **Code Quality:** Enforcing zero warnings with `ruff` (linter/formatter) and `mypy` (static type checker).
10. **Testing Suite:** Comprehensive unit and integration testing with `pytest` and `httpx`.
11. **Container Hardening:** Multi-stage Dockerfile running strictly as `USER appuser` (UID 1000). Optimizing layer caching for dependencies.
12. **Local Runbook:** Full verification workflows on bare metal and Docker before cluster deployment.

### Part II: The Platform & GitOps Layer
13. **Kubernetes Runtime:** Installing MicroK8s v1.30 on Linux with snap. Enabling RBAC, CoreDNS, and hostpath storage.
14. **Splunk Logging:** Deploying Splunk Enterprise container with HTTP Event Collector (HEC) on port 8088.
15. **Polyrepo Architecture:** Decoupling application source (`project-one`) from infrastructure manifests (`project-one-gitops`) to eliminate CI/CD loops.
16. **Dual Namespaces:** Isolating stateful infrastructure (`ml-infra`) from stateless workloads (`ml-app`). FQDN cross-namespace resolution.
17. **Platform Helm Chart (`ml-infra`):** Declarative packaging for Redis, KRaft Kafka, Kafka UI, Prometheus, Grafana, and Fluent Bit.
18. **Workload Helm Chart (`ml-app`):** Declarative packaging for ML API deployment, services, resource bounds, and HPA.
19. **Declarative Kafka Topics:** Deploying topic provisioning Kubernetes Job with init-container TCP polling barrier.
20. **ArgoCD Engine:** Installing ArgoCD using `--server-side` apply to bypass the 262KB ETCD metadata annotation limit. Exposing via NodePort 30781.
21. **GitOps Applications:** Authoring declarative `Application` CRDs for platform and workload with automated self-healing.
22. **CI/CD & GHCR:** GitHub Actions workflows for static analysis, automated testing, building multi-tag OCI images with Git SHA tags, and automated GitOps writeback.
23. **Cluster Runbook:** Port matrix and end-to-end smoke testing procedures.
24. **Production War Stories:** 12 battle-tested bugs and solutions (CRD limits, Go template escaping, localhost networking, KRaft quorum races, etc.).
25. **Revision Q&A:** 15 senior-level technical interview questions bridging enterprise Java and cloud-native MLOps.
