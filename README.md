# Husky Buddy

> A data-driven app designed to connect Northeastern University students.

Husky Buddy helps NEU students find peers for coffee chats, study groups, and
informal networking by matching them on shared interests, majors, courses, and
availability. The app is built as a full-stack project for Northeastern's
**CS 3200 — Database Design (Spring 2026)**, forked from the course template
maintained by Dr. Fontenot.

---

## Team

| Name | GitHub |
| ---- | ------ |
| Tori Smith| [@smtori](https://github.com/smtori) |
| Matthew Chao | [@mchao02](https://github.com/mchao02) |
| Vinay Goenka | [@vinaygoenka](https://github.com/vinaygoenka) |
| Aarish Kodnaney | [@AarishKod](https://github.com/AarishKod) |
| Simran Seghal | [@simransehgal21](https://github.com/simransehgal21) |


---

## Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Python)
- **Backend / REST API:** [Flask](https://flask.palletsprojects.com/)
- **Database:** MySQL 8 (initialized from SQL scripts in `database-files/`)
- **Orchestration:** Docker + Docker Compose
- **Language:** Python 3.11

---

## Repository Structure

```text
Husky_Buddy_Temp/
├── api/                 # Flask REST API (application/business logic layer)
├── app/                 # Streamlit frontend
├── database-files/      # SQL scripts auto-run by MySQL on first boot (alphabetical order)
├── datasets/            # Source data used for seeding / ML
├── docs/                # Project documentation
├── ml-src/              # Jupyter notebooks and ML model development
├── docker-compose.yaml  # Team/production compose file
├── sandbox.yaml         # Personal sandbox compose file (alt. ports)
└── README.md
```

---

## Prerequisites

Before you start, make sure you have the following installed:

1. **Git** — a terminal client, GitHub Desktop, or the VS Code Git plugin.
2. **Docker Desktop** — [download here](https://www.docker.com/products/docker-desktop/). This is what actually runs the app.
3. **Python 3.11** via [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install) or Anaconda — for IDE autocompletion and linting only; the app itself runs in containers.
4. **VS Code** with the Python extension (recommended).

### (Optional) Local Python environment for editor support

```bash
conda create -n db-proj python=3.11
conda activate db-proj

cd api
pip install -r requirements.txt
cd ../app/src
pip install -r requirements.txt
```

---

## Quick Start

For a teammate who has just cloned the repo and wants to get running:

```bash
# 1. Clone
git clone https://github.com/smtori/Husky_Buddy_Temp.git
cd Husky_Buddy_Temp

# 2. Create the secrets file (see next section for details)
cp api/.env.template api/.env
# ...then edit api/.env and set a DB password

# 3. Build and start all services
docker compose up -d

# 4. Open the app
# Streamlit → http://localhost:8501
# Flask API → http://localhost:4000
```

To stop everything:

```bash
docker compose down
```

---

## Configuring the `.env` File

The MySQL container and the Flask API both read credentials from **`api/.env`**.
This file is git-ignored — **every team member must create their own** before
running `docker compose`.

1. From the repo root, copy the template:

   ```bash
   cp api/.env.template api/.env
   ```

2. Open `api/.env` in your editor. On the last line, **replace the `<...>`
   placeholder** with a database password of your choosing. A typical file
   looks like this:

   ```env
   SECRET_KEY=some-random-flask-secret
   DB_USER=root
   DB_HOST=db
   DB_PORT=3306
   DB_NAME=husky-buddy-orig
   MYSQL_ROOT_PASSWORD=your-password-here
   ```

3. Save the file. You do **not** need to restart your shell — Docker Compose
   reads it at container-start time.

---

## Running the Containers

### Team repo (default)

Uses `docker-compose.yaml`. Ports: `8501` (Streamlit), `4000` (Flask), `3306` (MySQL).

| Action | Command |
| ------ | ------- |
| Start all services in the background | `docker compose up -d` |
| Stop and delete all containers | `docker compose down` |
| Start only the database | `docker compose up db -d` |
| Stop (but keep) containers | `docker compose stop` |
| Restart after a code crash | `docker compose restart` |
| **Rebuild DB from SQL files** | `docker compose down -v && docker compose up -d` |

> The first time the MySQL container is **created**, it executes every `.sql`
> file in `database-files/` in **alphabetical order**. If you change a SQL
> file, you must recreate the container (last row above) — simply restarting
> it will not re-run the scripts.

### Personal sandbox (optional, for experiments)

A separate `sandbox.yaml` file exists so you can run an isolated copy of the
stack on different ports without interfering with your team's setup:

```bash
docker compose -f sandbox.yaml up -d
docker compose -f sandbox.yaml down
```

---

## Service Endpoints

Once the stack is running:

| Service | URL | Notes |
| ------- | --- | ----- |
| Streamlit app | <http://localhost:8501> | Click **Always Rerun** in the top-right menu so it hot-reloads on code changes. |
| Flask REST API | <http://localhost:4000> | Routes live under `api/backend/`. |
| MySQL | `localhost:3306` | User `root`, password from `api/.env`. |

---

## Development Notes

### Hot reload

Changes to files in `api/` and `app/src/` are reflected **without rebuilding**.
If a change crashes the app container, fix the bug and run
`docker compose restart`.

### Changing the schema

Because MySQL only runs the SQL scripts on first container creation, any edit
to files under `database-files/` requires:

```bash
docker compose down -v       # drops the DB volume
docker compose up -d         # recreates and re-seeds
```

> **Note:** `down -v` removes **all** volumes defined by the compose file. For this project that's only the MySQL data volume, which is exactly what we want to reset.

### Role-Based Access Control (RBAC)

The Streamlit app ships with a lightweight RBAC demo (no real auth). User
"roles" are tracked in `st.session_state` and controlled by
`app/src/modules/nav.py`, which decides which sidebar links each role sees.
Pages under `app/src/pages/` are prefixed by role number (`0_`, `1_`, `2_`,
etc.) — we'll adapt these to Husky Buddy's actual user types (e.g. *Student*,
*Student Org Admin*, *System Admin*) as the project evolves.

---

## Acknowledgments

- Forked from the [NEU-CS3200/26S-Project-Template](https://github.com/NEU-CS3200/26S-Project-Template) by Dr. Fontenot.
- Built for **CS 3200 — Database Design**, Northeastern University, Spring 2026.
