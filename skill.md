---
name: taskboard-project-guidelines
description: Project context and implementation guidelines for AI assistants working on the TaskBoard Docker and Kubernetes project.
---

# TaskBoard Project Guidelines (Docker and Kubernetes)

## 1. Purpose and scope

This document is the project-specific source of context for AI assistants
working on TaskBoard. Read it before planning or changing project code,
configuration, tests, deployment resources, or documentation.

TaskBoard is a small task-management web application that is containerized with
Docker and deployed to Kubernetes. Keep the solution understandable,
reproducible, configurable, secure, and straightforward to demonstrate.

Do not introduce a different architecture (such as multiple microservices, an
externally hosted database, or a mandatory cloud dependency) without explicit
team approval. Avoid complexity that does not meet a requirement or provide a
clear, documented benefit.

## 2. Establish the current project facts first

Do not assume that a technology or deployment choice has already been made.
Inspect the current source, tests, configuration, and documentation before
proposing or implementing changes. In particular:

- The project brief allows Node.js (Express or equivalent) or Django, and
  PostgreSQL or MySQL.
- Once a choice is established in the repository or explicitly agreed by the
  team, use it consistently. Do not mix framework-specific conventions,
  database variables, ports, or commands.
- Distinguish mandatory project requirements from recommendations and bonus
  features. Apply a requirement only to the relevant change.
- If an important choice remains unresolved and materially affects
  compatibility or architecture, ask the team rather than silently choosing.
  For small implementation details, use the simplest consistent option and
  document it when it affects future work.

## 3. Functional scope and application contract

TaskBoard must let users create, list, complete, and delete tasks. A task has
at least these fields:

- `id`
- `title`
- `completed`
- `created_at`

Provide a REST API under `/api/tasks` and/or a simple HTML interface usable from
the host computer. Keep the application contract consistent across local
development, Docker Compose, and Kubernetes.

The application must read its database and server settings from these
environment variables:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `APP_PORT`

Do not hard-code connection settings or credentials. In Kubernetes, `DB_HOST`
must resolve to the internal Service named `db`.

Implement separate health endpoints:

- `GET /healthz`: return success when the application process is functioning;
  this endpoint must not require a database connection.
- `GET /readyz`: return success only when the application can reach the
  database; return HTTP 503 when it cannot.

A temporary database outage must not cause liveness failures and a restart
loop for the web container. Showing the serving Pod name from `HOSTNAME` is
optional.

## 4. Reference Kubernetes architecture

All TaskBoard Kubernetes resources belong in the `taskboard` namespace.

```text
Host browser
    |
    | HTTP: http://<node-ip>:30080
    | or Ingress: http://taskboard.local (bonus)
    v
web Service (NodePort is the baseline)
    |
    v
web Deployment (at least 2 replicas)
    |  non-sensitive settings <- ConfigMap
    |  credentials             <- Secret
    |
    |  Kubernetes DNS: db
    v
db Service (ClusterIP only)
    |
    v
db StatefulSet (1 replica)
    |  schema/sample data <- SQL initialization script
    v
PersistentVolumeClaim (at least 1 Gi)
```

Structural requirements:

- The stateless web application runs in a `Deployment` with at least two
  replicas. Its Pods must be interchangeable.
- The stateful database runs in a `StatefulSet` with persistent storage. A
  `Deployment` is acceptable only when the choice is justified in project
  documentation.
- The database Service is named `db`, has type `ClusterIP`, and is not exposed
  outside the cluster.
- Expose the web application using NodePort, LoadBalancer, or Ingress. NodePort
  `30080` is the baseline option.
- Use ConfigMaps for non-sensitive configuration and a Secret for credentials.
- Database storage must have a capacity of at least `1Gi`.

If `docs/architecture.png` exists, keep it consistent with the actual
manifests. Do not add or update a diagram that would misrepresent the deployed
architecture.

## 5. Technology and image choices

The project brief allows the following options:

| Area | Allowed or expected options |
|---|---|
| Application | Node.js (Express or equivalent) or Django |
| Database | PostgreSQL or MySQL |
| Local cluster | minikube (recommended), kind, or Kubernetes in Docker Desktop |
| Web exposure | NodePort, LoadBalancer, or Ingress |
| Deployment | `kubectl apply -f k8s/` or `kubectl apply -k k8s/` |

Use explicit, stable image versions; never use the `latest` tag. Use official
lightweight base images where practical. The brief gives `postgres:16-alpine`
as an example, but verify compatibility with the chosen database version and
the project files before adopting it. Pin versions consistently in Docker,
Compose, and Kubernetes.

## 6. Docker and local development

The web application's Dockerfile should:

1. Use an official, lightweight base image with an explicit version.
2. Use a multi-stage build where appropriate, keeping build tools and
   development dependencies out of the runtime image.
3. Run the application as a non-root user.
4. Use `.dockerignore` to exclude irrelevant or sensitive files, including
   `.git`, `.env`, dependency folders, caches, and local build artifacts as
   appropriate for the selected stack.
5. Never copy real credentials into an image.
6. Use a versioned image tag, such as `taskboard-web:1.0.0`, rather than
   `latest`.
7. Keep the final image small without removing runtime dependencies.

Provide a root-level `compose.yaml` that starts the web application and its
database with `docker compose up`. Local configuration should follow the same
environment-variable contract as Kubernetes. Keep real secrets out of Git;
document how developers provide local values safely.

Image scanning with a tool such as Trivy is a bonus, not a baseline
requirement.

## 7. Kubernetes implementation practices

### 7.1 Namespace, labels, and controllers

- Put all application resources in `namespace: taskboard`.
- Use consistent labels, including `app: taskboard` and `tier: web` or
  `tier: db`.
- Ensure Service selectors and controller `selector.matchLabels` exactly match
  the Pod labels.
- Do not deploy unmanaged application Pods. Use a `Deployment` or
  `StatefulSet`.

### 7.2 Configuration, initialization, and secrets

- Use a ConfigMap (for example `web-config`) for non-sensitive web settings.
- Provide a SQL initialization script for the schema and sample data.
- Mount the SQL script in the appropriate initialization directory for the
  selected official database image, after verifying that image's behavior.
- Use a Kubernetes Secret (for example `db-credentials`) for the database
  password and other genuinely sensitive values.
- Inject configuration and credentials using `envFrom`, `configMapKeyRef`,
  and/or `secretKeyRef` as appropriate.
- Database name and username may be non-sensitive ConfigMap values when
  consistent with the project brief; the password belongs in a Secret.

Never put a real password in Git, source code, examples, logs, or a Docker
image. Do not ask users to paste credentials into chat or print them during
validation. Base64-encoding a Kubernetes Secret is not encryption and must not
be described as adequate protection.

The repository may include a clearly labeled example manifest with fake
placeholder values, but never real credentials. Document how to create the
actual Secret outside Git, for example with `kubectl create secret generic`.
Production deployments may additionally need encryption at rest for etcd,
appropriate RBAC, and/or an external secret manager; do not imply those are
already configured.

### 7.3 Database persistence

- Use a PVC of at least `1Gi`, directly or through StatefulSet
  `volumeClaimTemplates`.
- Mount it at the data path expected by the selected database image.
- Deleting a database Pod must not delete its PVC or lose persisted data.
- Explain the data impact before suggesting commands that delete a PVC or
  database data. Do not describe destructive cleanup as harmless.
- Consider local-cluster storage behavior when describing persistence; a PVC
  does not by itself guarantee backups or production-grade durability.

### 7.4 Services and network

- Name the database Service `db` and keep it `ClusterIP`.
- Connect to the database through the in-cluster DNS name `db` and the selected
  database port.
- Expose only the web Service outside the cluster.
- Ingress and NetworkPolicy are bonus features. A NetworkPolicy requires a
  compatible cluster network plugin; do not assume it is enforced everywhere.

### 7.5 Probes and resources

- Configure the web liveness probe to use `/healthz`.
- Configure the web readiness probe to use `/readyz`.
- Set CPU and memory requests and limits for each container.
- Choose resource values that are reasonable for the documented local cluster;
  avoid limits that prevent a modest machine from running the baseline project.
- A database readiness probe, HPA, and Helm/Kustomize packaging are bonus
  features, not baseline requirements.

## 8. Suggested repository structure

Preserve an existing coherent structure. Otherwise, a layout like this is
appropriate:

```text
taskboard/
├── app/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...                    # application code
├── compose.yaml
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 10-configmap.yaml
│   ├── 11-secret.example.yaml
│   ├── 12-db-init-configmap.yaml
│   ├── 20-db-statefulset.yaml
│   ├── 21-db-service.yaml
│   ├── 30-web-deployment.yaml
│   ├── 31-web-service.yaml
│   └── 40-ingress.yaml        # bonus
├── docs/
│   └── architecture.png
├── README.md
└── skill.md
```

Numeric filenames aid navigation but do not guarantee Kubernetes apply order.
Document dependencies or provide a clear deployment procedure. Avoid creating
empty scaffolding or files that do not support an agreed task.

## 9. Reproducible deployment and documentation

A person should be able to clone the repository and deploy the project to a
clean cluster by following the README, without undocumented steps.

The README should explain:

- Prerequisites and versions, including Docker, `kubectl`, and the selected
  local cluster tool.
- The chosen application and database stack.
- How to build and load or publish the web image.
- How to create the real Kubernetes Secret without committing it.
- The deployment command, such as `kubectl apply -f k8s/` or
  `kubectl apply -k k8s/`.
- How to access and validate the application.
- How to clean up, including a clear warning if cleanup removes persistent
  data.

Before claiming a deployment works, verify its actual prerequisites: image
availability in the cluster, Secret creation, StorageClass availability,
network plugin support for NetworkPolicies, and Ingress controller availability
when those features are used.

## 10. Acceptance scenarios

Preserve these baseline demonstration scenarios. Run the relevant safe checks
for the change; do not perform destructive tests on useful data without a
backup and explicit authorization.

| ID | Scenario | Expected result |
|---|---|---|
| T1 | Apply the manifests and inspect resources in `taskboard` | Pods become `Running` and `Ready`; the project brief targets under two minutes. |
| T2 | Open the web Service | The page loads and tasks are visible. |
| T3 | Create tasks and refresh | Tasks remain available. |
| T4 | Delete the database Pod `db-0` | It is recreated and tasks remain present. |
| T5 | Delete a web Pod | It is replaced and the other replica can continue serving requests. |
| T6 | Temporarily scale the database to zero replicas | Web Pods become unready without a restart loop, then recover when the database returns. |
| T7 | Inspect Services | `db` is `ClusterIP` and is not externally exposed. |
| T8 | Check Git and image contents for credentials | No real password is present. |
| T9 | Change the web image tag | A rolling update is observable and `kubectl rollout undo` can roll it back. |

Restore nominal replica counts after tests that change them.

## 11. Working rules for AI assistants

For each task:

1. **Inspect before editing.** Read this file, the relevant README sections,
   source files, tests, Docker/Compose configuration, and Kubernetes manifests.
   Check the worktree and preserve unrelated user changes.
2. **State the evidence.** Separate repository facts, project requirements,
   recommendations, assumptions, and unresolved decisions. Do not claim to
   have inspected the whole project when you have only read part of it.
3. **Make focused changes.** Follow established names, stack choices, versions,
   formatting, and patterns. Avoid unrelated refactors and unnecessary
   dependencies.
4. **Preserve integration contracts.** Check environment variables, API
   behavior, labels/selectors, Service names, ports, volume paths, and probe
   semantics across components.
5. **Protect secrets and data.** Never commit real credentials, expose the
   database externally, or run destructive data operations without clear
   explanation and authorization.
6. **Validate the change.** Run the smallest relevant tests, linters, builds,
   and configuration checks available. Report exactly what ran and its result.
   If a check cannot run, say why and provide the command to run.
7. **Keep documentation in sync.** Update the README and, when relevant, the
   architecture diagram when changing the stack, architecture, variables,
   ports, commands, prerequisites, or deployment behavior.
8. **Explain non-obvious choices.** Briefly state the reason and impact of
   choices that affect compatibility, security, or future work.

### Do not

- Add a real password, token, private key, or `.env` file to the repository.
- Expose the `db` Service outside the cluster.
- Replace the database StatefulSet with a Deployment without documented
  justification.
- Set the target web replica count below two.
- Deploy unmanaged Pods for the application or database.
- Conflate liveness and readiness into one probe.
- Use `latest` for container images.
- Delete a PVC or database data as part of cleanup without warning and
  authorization.
- Add heavy infrastructure, an operator, a chart, or a new dependency without
  a clear benefit and documented rationale.
- Treat a bonus feature as mandatory or a mandatory requirement as optional.
- Claim tests, builds, security checks, or deployments passed unless they were
  actually run.

## 12. Resolving conflicts

When instructions appear to conflict, use this order:

1. Applicable security and safety constraints.
2. The team's latest explicit decision, provided it does not violate a
   requirement or constraint.
3. Existing repository behavior and conventions when they remain consistent
   with the agreed project direction.
4. Mandatory project requirements summarized here.
5. General Docker/Kubernetes recommendations, favoring the simplest suitable
   option.

Do not silently change architecture or hide a real conflict. Explain the
incompatibility and ask for a decision when the available evidence does not
identify a safe, compatible resolution.

## 13. Expected technical response

When proposing or making a change, briefly report:

- The files created or changed and the purpose of the change.
- Any assumptions or decisions that affect the implementation.
- The validation commands run and their results, or the commands still to run.
- Any manual action needed, such as creating a Secret or loading an image into
  minikube.

**Overall goal:** a simple, understandable, secure, persistent, and reproducible
TaskBoard application that can be deployed to a local Kubernetes cluster and
demonstrated using scenarios T1–T9.
