# Outage Detector: full details

[Back to the short README](../README.md)

**Live demo:** https://outage.albertycliu.xyz (fake data, no login)

> **Demo only.** This repository is a concept demo for showing a delivery pipeline.
> It does **not** call any real monitoring system. There is no PRTG, PagerDuty,
> JKB or HostMonitor client, no scheduler and no login. All numbers on screen are
> made-up rows that the backend loads into its own database when it starts. The
> Refresh buttons only re-stamp those rows so the "data is fresh" checks stay green.
> No credentials, internal addresses or company names are in this repo.

## 1. What it is and why it matters for an SRE job

**Outage Detector** is an operations dashboard that answers one question for an
on-call engineer: *is anything on fire, and how stale is that answer?* It shows
alert counts for two example infrastructures (Charlie and Delta) from three kinds of
monitoring feeds (HostMonitor, PRTG, JKB), with a health check per feed.

The application itself is deliberately simple. The point of the repo is the
delivery around it. It shows these SRE skills:

- **Containers:** one Dockerfile per component, a compose file for local use.
- **CI/CD (GitHub Actions):** test, build and push images to GHCR, then update the GitOps repo.
- **GitOps with Argo CD:** the cluster state lives in Git; Argo CD syncs it (automated sync, prune, self-heal).
- **Kubernetes (K3s):** Deployments, Services, a MariaDB StatefulSet with a PVC, Traefik IngressRoute, probes, resource requests and limits.
- **Secrets handling:** Secrets are created by hand and never stored in Git.
- **Health endpoints:** `/health/*` return 503 when a feed's data is stale (the freshness idea behind the dashboard).
- **Rollback:** by reverting one Git commit.

## 2. Architecture

| Component | Tech | Notes |
|---|---|---|
| frontend | Vue 3 + Quasar (Vite), served by nginx | nginx also proxies `/backend/` to the backend, so the browser talks to one origin |
| backend | Flask + SQLAlchemy under gunicorn (Python 3.8) | mostly read API over the database; `/refresh_*` routes only re-stamp the demo rows |
| database | MariaDB 11.1 | on start the backend loads `backend/db/schema.sql` and `backend/db/seed_demo_data.sql` |

Request flow: browser → nginx (`frontend`) → `/backend/...` → Flask (`backend`, port 5410) → MariaDB.

Kubernetes manifests live in the GitOps repo:
[`Albertycl/Gitops-apps`, `manifests/outage-report/`](https://github.com/Albertycl/Gitops-apps/tree/main/manifests/outage-report).

## 3. How to install and run

### a) Locally with Docker Compose

Prerequisites: Docker with the Compose plugin.

```bash
git clone https://github.com/Albertycl/Outage-report.git
cd Outage-report
cp .env.example .env            # set DB_PASSWORD to any value you like
docker compose up --build -d
```

Open <http://localhost:5431> (or `http://<server-ip>:5431` from another machine).
The backend is also published on `127.0.0.1:5430`. Change ports with
`FRONTEND_PORT`, `BACKEND_PORT` and `BACKEND_BIND` in `.env`.
Stop with `docker compose down` (add `-v` to delete the database volume).

### b) On Kubernetes (K3s) through Argo CD

Prerequisites: a cluster with Argo CD, Traefik and a storage class.

1. One-time bootstrap: apply the root app of the GitOps repo
   (`kubectl apply -f argocd/root-app.yaml` in `gitops-apps`). It picks up
   `apps/outage-report.yaml` and creates the `outage-report` namespace.
2. Create the Secret by hand (never in Git). Keys: `password` (the MariaDB
   application password) and `database-url`
   (`mysql+pymysql://outage:<password>@mariadb:3306/outage_report`):

   ```bash
   kubectl -n outage-report create secret generic outage-db \
     --from-literal=password='<choose one>' \
     --from-literal=database-url='mysql+pymysql://outage:<choose one>@mariadb:3306/outage_report'
   ```
3. After the first CI run, set the two GHCR packages
   (`outage-report-backend`, `outage-report-frontend`) to public. Until then the
   pods show `ImagePullBackOff`.
4. Check: `kubectl get applications -n argocd` shows `outage-report` as
   `Synced` and `Healthy`, and `kubectl get pods -n outage-report` shows all pods `Running`.
5. The IngressRoute host is set in `manifests/outage-report/ingress.yaml` in the
   GitOps repo; point a DNS record at your ingress address.

## 4. CI/CD and rollback

On every push to `main` (`.github/workflows/ci.yml`):

1. **test**: backend import check and frontend build (also runs on pull requests).
2. **build**: builds the two images and pushes them to GHCR
   (`ghcr.io/albertycl/outage-report-<part>`), tagged with the commit SHA and `latest`.
3. **update-gitops**: runs `kustomize edit set image` in
   `manifests/outage-report/` of `gitops-apps` and pushes with a deploy key
   (repo secret `GITOPS_DEPLOY_KEY`). Argo CD then syncs the cluster.

Rollback: `git revert` the "outage-report: deploy <sha>" commit in `gitops-apps`.
Argo CD's self-heal undoes a manual `kubectl rollout undo`, so Git is the only
place to roll back.

## 5. Monitoring and known limits

- Monitoring that exists: the container health checks, the Kubernetes readiness
  probes, and the app's own `/health/jkb`, `/health/prtg_alerts` and
  `/health/hostmonitor_report` routes (HTTP 503 when data is stale). The app
  exposes no Prometheus `/metrics`.
- Known limits: demo data only, no authentication, no real feeds, one replica,
  TLS depends on your own DNS and certificate setup.
