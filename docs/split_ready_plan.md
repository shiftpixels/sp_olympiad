# SP Olympiad - Split-Ready Technical Boundaries

This note defines how to keep development inside `sp_olympiad` now, while making future extraction of paid modules safe and low-risk.

## Goal

- Keep current module stable and working.
- Continue building full flow in `sp_olympiad`.
- Prepare clean boundaries so `payments` and `certification/reports` can be moved to separate addons later.

## Non-Disruptive Rule

- No immediate module split.
- No rename/move of current models only for architecture.
- New code should follow boundary rules below so extraction can be done later with minimal refactor.

## Boundary 1: Domain Core (must stay in `sp_olympiad`)

Keep these concerns as core business domain:
- Event, category, accommodation, project, student, jury assignment/scoring domain rules.
- State machine and validations.
- Core ACL/rules required for domain safety.

Design rule:
- Core models must not depend on provider-specific payment APIs.
- Core models must not depend on certificate rendering internals.

## Boundary 2: Payment Integration (future addon candidate)

Future addon name (suggested): `sp_olympiad_payment`.

Develop now inside `sp_olympiad`, but isolate:
- A single integration layer file for payment flow orchestration.
- Payment callback handlers separated from domain compute logic.
- Mapping fields between project and transaction grouped in one place.

Extraction target later:
- Provider-specific logic, callbacks, settings UI, optional menus.
- Keep only neutral payment status fields in core if needed.

## Boundary 3: Certification/Reports (future addon candidate)

Future addon name (suggested): `sp_olympiad_certification` or `sp_olympiad_reports_plus`.

Develop now inside `sp_olympiad`, but isolate:
- Report builders/templates in dedicated report-focused files.
- Certificate text/layout logic separate from domain model methods.
- QR/verification generation encapsulated in helper/service-style functions.

Extraction target later:
- Report actions, templates, print flows, certificate assets.
- Keep only neutral result fields in core domain.

## Coding Rules For Future Split

- Avoid circular imports between domain and integration/report code.
- Keep feature flags/settings namespaced (`sp_olympiad.*` keys).
- Add clear method entry points (example intent): domain triggers service, service returns status/result.
- Put new files by concern, not by screen.

## Suggested Internal Folder Intent (within current module)

Without moving existing files now, place new code with this intent:
- `models/`: domain entities and business constraints.
- `services/payment_*`: payment orchestration and provider mapping.
- `services/certificate_*` or `report/services/*`: certificate/report preparation logic.
- `controllers/`: thin HTTP layer, delegate to services/domain.
- `report/`: QWeb/report actions and templates.

## Extraction Readiness Checklist

When deciding to split:
- Payment code can be removed with limited touches to domain models.
- Certificate/report code can be removed without breaking core workflows.
- Dependency graph is one-way (core -> extension interfaces, not reverse).
- Access rights and menus for payment/certification are already separable.

## Current Decision

- Continue implementation in `sp_olympiad` (single-module velocity).
- Apply boundaries immediately for all new code.
- Re-evaluate split after stable end-to-end flow and first production usage feedback.
