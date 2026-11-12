# TaskBoard project review guidelines

These review guidelines summarize the requirements in the supplied
Docker/Kubernetes project brief. Apply a requirement only when it is relevant
to the changed lines. Review the diff, not the entire repository; do not report
pre-existing gaps or require bonus features.

## Application

- Use Node.js (Express or equivalent) or Django for a task application (APP-1).
- Provide CRUD operations and a task resource
  (`id`, `title`, `completed`, `created_at`) (APP-1, APP-2).
- Read database and application settings from environment variables
  `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `APP_PORT`
  (APP-3); do not hard-code configuration.
- `/healthz` reports process health without requiring the database (APP-4).
- `/readyz` reports ready only when the database connection works (APP-5).

## Docker

- Use a pinned, lightweight official base image; do not use the `latest` tag
  (DOC-1).
- Use a multi-stage build and run the final application container as non-root
  (DOC-2, DOC-3).
- Exclude development files and secrets from the image with `.dockerignore`;
  never bake credentials into an image (DOC-4).
- Version the image and either publish it to a registry or load it into the
  cluster (DOC-5).
- Provide a local `compose.yaml` setup for the application and database
  (DOC-6).

## Database

- Use PostgreSQL or MySQL with a pinned official image (DB-1).
- Run the stateful database with a StatefulSet and persistent storage (at least
  1 Gi); a Deployment is acceptable only when justified (DB-2, DB-4).
- Keep database credentials in a Kubernetes Secret and non-sensitive settings
  in a ConfigMap (DB-3).
- Expose the database only through an internal `ClusterIP` Service named `db`;
  do not expose it externally (DB-6).
- Initialize the schema and sample data from a supplied SQL script on first
  startup (DB-5).

## Kubernetes

- Place resources in the `taskboard` namespace and use coherent `app` and
  `tier: web|db` labels (K8S-1).
- Run the stateless web application in a Deployment with at least two replicas
  (K8S-2).
- Configure web liveness/readiness probes at `/healthz` and `/readyz`, and set
  CPU and memory requests and limits (K8S-4, K8S-5).
- Load configuration and secrets from ConfigMaps and Secrets; `DB_HOST` should
  resolve to the internal `db` Service (K8S-3).
- Expose the web application externally using NodePort, LoadBalancer, or
  Ingress. A NodePort such as `30080` is the baseline option (K8S-6).
- Make the deployment reproducible from a clean clone with one documented
  `kubectl apply` command (K8S-7).
- Do not deploy unmanaged bare Pods; use a Deployment or StatefulSet.

## Security and documentation

- Never commit plaintext passwords or include real credentials in Docker
  images. Provide a safe example Secret and document how to create the real one
  (SEC-1).
- Apply `runAsNonRoot: true` and `allowPrivilegeEscalation: false` to the web
  container (SEC-2).
- Keep setup, prerequisites, deployment, validation, and cleanup instructions
  reproducible from the README.

NetworkPolicy (SEC-3), database readiness probes (DB-7), Ingress (K8S-8),
autoscaling or Helm/Kustomize packaging (K8S-9), and image vulnerability
scanning (DOC-7) are bonus requirements, not baseline requirements. Do not
flag their absence unless the pull request claims to add them or introduces
a regression in an existing implementation.
