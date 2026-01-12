## Mini SaaS, Production-Grade

Target Architecture

- All containerized. No pets. Only cattle.

- Frontend: React or simple HTML (served via Nginx)

- Backend: FastAPI or Node.js

- Database: PostgreSQL

- Cache: Redis

- Reverse Proxy: Nginx

- CI/CD: Jenkins

- IaC: Terraform

- Config: Ansible
---


# EC2 Layout
1. VM1 – Edge / App Node

    - Nginx

    - Frontend container

    - Backend container

2. VM2 – Data Node

    - PostgreSQL

    - Redis

    - Nightly backups