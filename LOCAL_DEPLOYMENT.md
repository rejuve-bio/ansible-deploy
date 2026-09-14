# Local Deployment Guide

Run all 5 Rejuve Bio services on your own machine. Everything runs from public
prebuilt Docker images - no GitHub credentials needed, no source to build.

## Prerequisites

Nothing to install by hand. The playbook checks for Docker, Docker Compose,
and the `community.docker` Ansible collection, and offers to install
anything missing (asking first - nothing installs without your say-so).

## 1. Get the repository

```bash
git clone https://github.com/rejuve-bio/ansible-deploy.git
cd ansible-deploy
```

## 2. (Optional) Choose where services get deployed

By default, services deploy under `~/services`. To use a different
directory:

```bash
cp .env.example .env
```

Edit `.env` and set `LOCAL_BASE_DIR=/path/you/want`. Then, in every new
terminal session before running the playbook:

```bash
set -a; source .env; set +a
```

## 3. Set up each service

Each service has a `.env.example` file - copy it to a real `.env` file and
fill in your own values. The real file is gitignored and never committed.

### Platform UI

Nothing to fill in - no secrets involved.

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml --tags Platform_UI_Local
```

### Authentication Service

```bash
cp playbooks/roles/Authentication_Service/templates/.env.example \
   playbooks/roles/Authentication_Service/templates/.env
```

Fill in:
- `JWT_SECRET_KEY`, `SECRET_KEY` - any random string
- `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_SECRET` - only needed for Google/GitHub login ([Google console](https://console.cloud.google.com/), [GitHub OAuth apps](https://github.com/settings/developers))
- `MAIL_PASSWORD` - a Gmail app password, only needed for password-reset emails

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml --tags Authentication_Service_Local
```

### Annotation Service

```bash
cp playbooks/roles/annotation-query-backend/templates/env.j2.example \
   playbooks/roles/annotation-query-backend/templates/env.j2
```

Fill in:
- `NEO4J_PASSWORD`, `HUMAN_NEO4J_PASSWORD`, `FLY_NEO4J_PASSWORD` - your Neo4j server credentials
- `GEMINI_API_KEY` - only needed for AI-generated query titles
- `MAIL_USERNAME`/`MAIL_PASSWORD` - only needed for email features
- `SENTRY_DSN`, `AXIOM_TOKEN` - optional, leave blank to disable monitoring
- `MORK_DATA_ROOT`, `MORK_DATA_DIR`, `FLY_MORK_DATA_DIR` - only if you have this dataset

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml --tags annotation_Local
```

### Hypothesis Generation

```bash
cp playbooks/roles/Hypothesis/templates/.env.example \
   playbooks/roles/Hypothesis/templates/.env
```

Fill in:
- `ANTHROPIC_API_KEY`, `HF_TOKEN`, `OPENAI_API_KEY` - only needed if you switch a feature to that provider
- `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` - your MinIO credentials
- `MAIL_PASSWORD` - only needed for email features
- `PROLOG_OUT_V2_PATH`, `PROLOG_OUT_V3_PATH` - only if you have this dataset
- `SWIPL_HOST`, `GO_LLM_URL`, `ANNOTATION_URL` - only if you run these external services

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml --tags hypothesis_Local
```

### AI Assistant

```bash
cp playbooks/roles/AI_Assistant/templates/ai-assistant.env.example \
   playbooks/roles/AI_Assistant/templates/ai-assistant.env
```

Fill in:
- `GEMINI_API_KEY` - only needed if `BASIC_LLM_PROVIDER`/`ADVANCED_LLM_PROVIDER` is set to `gemini`
- `LOCAL_MODEL_HOST`, `LOCAL_MODEL_API_KEY` - your local-model inference server
- `MONGO_PASSWORD` - any password you choose
- `NEO4J_PASSWORD` - your local Neo4j credentials

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml --tags AI_Assistant_Local
```

## 4. Or deploy everything at once

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml \
  --tags Platform_UI_Local,Authentication_Service_Local,annotation_Local,hypothesis_Local,AI_Assistant_Local
```

## Verifying it worked

Only Platform UI is meant to be opened in a browser - the other 4 are
backend APIs it talks to internally, so a bare URL just returns `404`
(that's normal, it means the server is up, just no page at `/`).

Open **http://localhost:3210** and try registering/logging in, running an
annotation query, and creating a hypothesis project - that exercises all 5
services end to end.

To check a backend service directly, confirm its container is running
instead of opening it in a browser:

```bash
docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'auth-service-local|annotation-service-local|hypothesis-local-api-service-1|ai-assistant-local'
```

All 5 services share a Docker network (`rejuve-services-net`) and reach each
other by container name automatically.
