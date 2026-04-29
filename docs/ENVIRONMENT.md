# Environment

## Purpose

This document defines the environment model for `autotrain`.

Use only the environment names defined here.

## Environment Names

- `local`
- `staging`
- `production`

Do not invent ad hoc names in docs or issues.

## Local

Purpose:

- platform development
- benchmark development
- local testing
- local operator workflows

Expected characteristics:

- Python-first runtime
- local `SQLite`
- filesystem artifacts
- optional local web UI
- optional local agent/provider integrations

## Staging

Purpose:

- shared preview of the hosted leg
- deployment verification
- integration validation

Expected characteristics:

- likely Vercel-hosted web UI
- likely shared cloud persistence when needed

## Production

Purpose:

- real hosted operator/control-plane environment

Expected characteristics:

- Vercel-hosted web UI
- cloud persistence such as `MongoDB Atlas`
- documented secrets and deployment procedures

## Secret Policy

Rules:

- secrets never go into git
- `.env` is local-only
- hosted secrets belong in the deployment platform secret store
- every expected secret must be documented by name and purpose

## Environment Variable Documentation Rule

When a new variable is introduced, document:

- variable name
- environment(s) used
- whether required or optional
- purpose
- example shape, not the real secret

## Planned Variables

These are the current local variables:

- `MISTRAL_API_KEY`
- `DATABASE_URL`
- `AUTOTRAIN_ENV`
- `APP_HOST`
- `APP_PORT`

### Variable Reference

`AUTOTRAIN_ENV`

- environments: `local`, later `staging` and `production`
- required: no
- default: `local`
- purpose: names the active runtime environment

`APP_HOST`

- environments: `local`
- required: no
- default: `127.0.0.1`
- purpose: local FastAPI bind host

`APP_PORT`

- environments: `local`
- required: no
- default: `8000`
- purpose: local FastAPI bind port

`DATABASE_URL`

- environments: `local`, later hosted environments
- required: no
- default: local `SQLite` path
- purpose: database connection string for platform state and metadata

`MISTRAL_API_KEY`

- environments: local or hosted when using Mistral-backed integrations
- required: optional for the current scaffold
- default: none
- purpose: provider credential for future Mistral-backed agent or model integrations

## Environment Ownership

Platform code must not assume:

- hosted-only execution
- Atlas-first storage
- one specific agent adapter

The local environment is the default implementation target.
