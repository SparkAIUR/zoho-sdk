# Zoho Unified Python SDK – Repo Spec Pack

Generated: 2026-02-19

This folder contains a set of repo-ready specification documents for building a **modern, async-first, performance-oriented** Python SDK that unifies multiple Zoho products (starting with **Zoho CRM**) while keeping **upstream compatibility** through **auto-generation** from source specs (CRM: `json_details.json` + OAS; Creator/Analytics: OAS; Projects: docs/spec extraction).

## Table of contents

- [00-overview.md](00-overview.md) – goals, non-goals, user-facing API sketch
- [01-decision-matrix.md](01-decision-matrix.md) – decisions + rationale
- [architecture/10-architecture.md](architecture/10-architecture.md) – package + runtime architecture
- [architecture/20-core-transport.md](architecture/20-core-transport.md) – HTTP, retries, rate limits, timeouts
- [architecture/30-auth-and-token-cache.md](architecture/30-auth-and-token-cache.md) – OAuth, token store, Redis/SQLite
- [architecture/40-codegen.md](architecture/40-codegen.md) – IR, generators, golden tests, CI
- [architecture/50-products.md](architecture/50-products.md) – CRM/Creator/Analytics/Projects product notes
- [research/90-existing-python-libs.md](research/90-existing-python-libs.md) – analysis of 3rd-party libs you linked
- [roadmap.md](roadmap.md) – phased delivery plan

## How to use these docs

Treat these as guiding documents for implementing the library. They are written to be copied directly into a repository (or referenced from your internal RFC system).

