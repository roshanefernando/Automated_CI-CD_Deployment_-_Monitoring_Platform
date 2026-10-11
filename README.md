# DeployFlow

DeployFlow is a DevOps portfolio project that demonstrates a complete local CI/CD workflow for a Python FastAPI application.

The project includes a Task Management REST API, PostgreSQL persistence, Docker containerization, GitHub Actions CI, GitHub Container Registry image publishing, local Kubernetes deployment with kind, and monitoring with Prometheus and Grafana.

## Problem Statement

Modern backend applications need more than working API endpoints. They need automated testing, repeatable container builds, safe deployment practices, observability, and clear rollback procedures.

DeployFlow demonstrates these practices in a small, practical MVP that can run locally without paid cloud infrastructure.

## Objectives

- Build a clean FastAPI REST API.
- Store task data in PostgreSQL.
- Containerize the application with Docker.
- Run automated linting, tests, and image builds with GitHub Actions.
- Publish Docker images to GitHub Container Registry.
- Deploy the application locally to Kubernetes using kind.
- Monitor API health, request rate, errors, latency, and availability.
- Document setup, troubleshooting, scaling, and rollback.

## Technology Stack

- Python 3.13
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Pytest
- Ruff
- Docker
- Docker Compose
- GitHub Actions
- GitHub Container Registry
- Kubernetes
- kind
- Prometheus
- Grafana

## Architecture

```mermaid
flowchart LR
    Developer[Developer Workstation] --> GitHub[GitHub Repository]

    GitHub --> Actions[GitHub Actions CI]
    Actions --> Tests[Ruff + Pytest]
    Actions --> Build[Docker Build]
    Build --> GHCR[GitHub Container Registry]

    Developer --> Compose[Docker Compose]
    Compose --> API[FastAPI API]
    Compose --> DB[(PostgreSQL)]
    Compose --> Prometheus[Prometheus]
    Compose --> Grafana[Grafana]

    Developer --> Kind[kind Kubernetes Cluster]
    Kind --> K8sAPI[FastAPI Deployment]
    Kind --> K8sDB[(PostgreSQL PVC)]

    Prometheus --> API
    Grafana --> Prometheus
    K8sAPI --> K8sDB
    API --> DB