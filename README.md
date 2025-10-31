## Passwork Python Connector, CLI, and Docker

This repository contains the official Python connector, CLI utility, and Docker assets for integrating with the Passwork API. Use the Python connector for programmatic access and client‑side cryptography, the CLI for DevOps/CI tasks and direct API calls, and the Docker setup to run these tools in containerized environments.

### Components

- `passwork_client/` — Python library for building programmatic integrations with Passwork. Provides client‑side cryptography (master key handling), session management, and convenient APIs for CRUD operations on Passwork objects (items, vaults, users, shortcuts, snapshots). Suitable for backend services, automation scripts, and custom tooling.
- `cli/` — `passwork-cli`, a command‑line tool for DevOps and SRE workflows to use Passwork as a secrets manager. Retrieve and inject secrets into environment variables or command parameters, search by tags/folders, work with custom fields, refresh tokens, and perform direct API calls. Designed for local use, servers, and ephemeral CI agents.
- `docker/` — Docker assets to run the CLI in containers for CI/CD (e.g., GitHub Actions, GitLab CI, Bitbucket Pipelines). Enables isolated runtime without local Python dependencies; includes a Dockerfile and example pipeline configuration for easy integration.

### Documentation

- API overview: [API and integrations — intro](https://passwork.pro/tech-guides/api-and-integrations/intro/)
- Python connector: [Python connector](https://passwork.pro/tech-guides/api-and-integrations/python-connector/)
- CLI utility: [CLI utility](https://passwork.pro/tech-guides/api-and-integrations/cli-utility/)
- Docker image for CLI: [Docker container for CLI](https://passwork.pro/tech-guides/api-and-integrations/docker-container-for-cli/)

### Examples

Usage examples for both the Python connector and the CLI have been moved to a separate repository:

- Passwork API Integration Examples: [passwork-me/passwork-integration-examples](https://github.com/passwork-me/passwork-integration-examples)

This examples repository demonstrates common scenarios such as retrieving secrets, searching by tags/folders, managing items and vaults, working with shortcuts and snapshots, session handling, and direct API calls.
