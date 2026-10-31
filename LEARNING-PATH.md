# Python for Production ML Serving — Learning Path & Tracker

**Who this is for:** Shantanu — senior Java backend engineer (microservices, distributed systems, AWS, Kafka, Redis, performance work) learning Python to build and serve production-grade ML/AI systems with enterprise CI/CD and Kubernetes GitOps.

**The goal:** Bridge high-concurrency Java backend instincts directly into Python, cloud-native Kubernetes, GitOps (ArgoCD), Helm, and Observability (Splunk).

---

## Progress Tracker

| Module | Status | Notes |
|---|---|---|
| 0. Roadmap agreed | ✅ Done | Chose "productionizing ML" track over "building/training models" track |
| 1. Python fast-track for Java engineers | ✅ Done | Syntax, collections, comprehensions, type hints, classes/duck typing, error handling, context managers, venv/uv |
| 2. Professional project structure | ✅ Done | src/ layout, pyproject.toml, pytest, ruff, mypy, pre-commit, Docker, CI, logging, pydantic-settings |
| 3. Just enough ML to know what you're serving | ✅ Done | Weights/architecture, tensor shapes, training vs. inference, model formats, MLflow |
| 4. ML serving stack (home turf) | ✅ Done | FastAPI, async, model servers, Redis, Kafka, vector DBs, feature stores, drift monitoring, scaling |
| 5. Capstone project (code & tests) | ✅ Done | Full working repo — FastAPI + versioned async Redis caching + Kafka consumer + pytest + Docker + CI + mypy/ruff |
| **6. Cloud-Native Production & GitOps** | ✅ **Done** | **Kubernetes (MicroK8s), Probes, UID 1000 hardening, Helm 3 packaging, ArgoCD GitOps, GHCR CI pipeline, Splunk HEC** |

---

## Module 6: Cloud-Native Production Deployment & GitOps (NEW)

*Goal: Deploy the ML serving system into an enterprise Kubernetes environment with automated GitOps reconciliation, zero-downtime rolling updates, and log observability.*

- [x] **12-Factor Decoupled Configuration** — Replaced hardcoded `localhost` strings with injected environment variables (`REDIS_HOST`, `KAFKA_BOOTSTRAP_SERVERS`). (Java analogue: Spring `@Value` or `@ConfigurationProperties` injected via Kubernetes `ConfigMap`).
- [x] **Resilience & Graceful Degradation** — Wrapped Redis cache lookups and writes in `try/except` blocks. If Redis restarts or drops, the API falls back to computing inference directly with zero HTTP 500 errors to users.
- [x] **Kubernetes Probes (`/healthz` and `/readyz`)** —
  - `/healthz` (Liveness): Detects process deadlock. If failed, Kubelet restarts the pod.
  - `/readyz` (Readiness): Verifies model weights are loaded in RAM. If failed, traffic is not routed to this pod.
- [x] **Production Dockerfile Hardening** —
  - Non-root execution: Created user `appuser` (`UID 1000`) for Kubernetes PodSecurityStandards compliance.
  - Layer caching optimization: `uv sync --frozen --no-dev --no-install-project` installs external wheels into a cached layer before application code is copied.
- [x] **Production Helm Chart (`helm/ml-serving-capstone`)** —
  - Parameterized templates for Deployments, ClusterIP Services, ConfigMaps, and Horizontal Pod Autoscalers (HPA).
  - In-cluster dependencies: Deployed Redis and Apache Kafka in KRaft mode (no ZooKeeper!).
  - Verified with `microk8s helm3 lint` and `template`.
- [x] **GitOps with ArgoCD Engine** —
  - Installed ArgoCD in `argocd` namespace.
  - Created declarative `Application` CRD tracking `mastershantash/project-one.git`.
  - Configured `selfHeal: true` (auto-reverts manual `kubectl` tampering) and `prune: true` (cascade resource deletion).
- [x] **Automated CI/CD Pipeline (GitHub Actions)** —
  - Pipeline runs `pytest`, builds multi-arch Docker image with Buildx, and pushes to GitHub Container Registry (`ghcr.io`).
- [x] **Observability with Splunk Enterprise** —
  - Running Splunk container in Docker with ports `8000` (Web UI) and `8088` (HTTP Event Collector / HEC).
  - Prepared container stdout logging pipeline for cluster ingestion.

---

## Session Log Entry

- **2026-10-31** — Built and deployed **Module 6 (Cloud-Native Production Deployment & GitOps)** end-to-end:
  - Hardened `main.py`, `redis_cache.py`, and `kafka_worker.py` with environment variables, probes, and graceful cache degradation.
  - Created and passed all 5 pytest unit tests.
  - Hardened Dockerfile with non-root UID 1000 and optimized `uv` layer caching.
  - Packaged entire stack into a production Helm chart (`helm/ml-serving-capstone`).
  - Deployed ArgoCD on local MicroK8s cluster; exposed UI at `https://localhost:30781`.
  - Configured declarative GitOps Application; verified automated rolling update.
  - All 4 pods (`ml-serving-capstone` replicas x2, `redis`, `kafka`) running healthy in Kubernetes.
  - Verified live inference through Kubernetes service port-forward on `http://localhost:8001/predict` and Swagger UI at `http://localhost:8001/docs`.
