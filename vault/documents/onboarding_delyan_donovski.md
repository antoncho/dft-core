---
title: "Onboarding: Delyan Donovski — Executive Secretary (GILC)"
classification: Governance+Ethics+StrategicDesign
validators:
  - role: "Ethics Steward"
  - role: "Governance Architect"
  - role: "Data Steward"
license: Public-Licensed / CodexLinked
tags: [onboarding, executive, secretary, librarian, archive, administration]
links:
  - stitchia-protocol-dev/docs/GILC_Fabrica_Blueprint.md
  - stitchia-protocol-dev/docs/Tech_Stack.md
  - stitchia-protocol-dev/docs/Business_Stack.md
---

# Onboarding: Executive Secretary — GILC

Welcome Delyan Donovski. This scroll establishes initial access, responsibilities, and deliverables for the Executive Secretary, overseeing business administration and leading Librarian + Archive functions across GILC and Digital Fabrica.

## Role Summary
- Function: Executive Secretary (GILC)
- Domains: Business Administration, Librarian & Archive, Bookkeeping
- Mandate: Document, index, and steward official records, research, and papers; ensure compliance and reproducibility of institutional knowledge.

## Responsibilities
- Governance Administration: scheduling, minutes, resolutions, seal logs
- Librarian & Archive: ingestion, indexing, retention, discovery
- Bookkeeping: document-level evidence and cross-references to financial entries
- Registry Hygiene: ensure scrolls use frontmatter and validators; maintain ledger integrity
- Braid Hygiene: ensure cross-links, tags, and ontology are present

## Deliverables (First 30–60 Days)
- Establish Archive Policy v1 (classification, retention, access levels)
- Index existing scrolls; fill missing validators/tags; propose ontology terms
- Create filing schema mapping: people, roles, programs, proposals, assets
- Produce quarterly Governance Records Pack (minutes, resolutions, ledger snapshot)

## Initial Access
- GitHub: Digital-Fabrica/dft-core (Docs + Kernel)
- Vault paths: `vault/documents/`, `vault/registry/`, `vault/braids/`
- Frontend: `stitchia-protocol-dev/frontend/` for dashboard review

## Operating Procedures
1) Author or receive documents in markdown; apply frontmatter
2) Run `./quantum process <file>`; verify `ethics_status` and tags
3) If required, request validator seals via `./quantum seal` commands
4) Confirm braid links and dashboard data (if applicable)

## Ethics & Compliance
- Use non-promissory language for any treasury or incentives material
- Respect privacy and license constraints in Legal Kernel
- Require validator presence on governance-impacting scrolls

## KPIs
- % scrolls with validators + tags
- Avg. time from draft to sealed
- Braid cohesion (avg. edges per scroll)

## Sign-off
Upon validator approval, this onboarding is considered active and effective.

