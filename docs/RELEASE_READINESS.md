# Release readiness

## Candidate scope

This release packages the universal exact three-dimensional proper-zero
reconstruction theorem of Theorem 4.6, its auxiliary signature and
exchange/certificate cross-checks, and the seven cited exact audits E-A58,
E-A60, E-A61, E-A63, E-A69, E-A71, and E-A72.

The title, abstract, README, claim ledger, source lock, reviewer guide, and
reproduction instructions use the same boundary. The theorem is not described
as generic or conditional. The signature exceptional set is explicitly
auxiliary.

## Required release gates

- [x] title-named PDF only; no retained `paper/main.pdf`;
- [x] no date printed beneath the author;
- [x] permanent GitHub companion locator in the manuscript and citation file;
- [x] all 20 rendered pages inspected with no visual defect;
- [x] zero undefined-reference, citation, overfull, or underfull warnings;
- [x] 19 focused tests pass normally and under optimized Python where routed;
- [x] E-A58/E-A60/E-A61/E-A63/E-A69/E-A71/E-A72 exact verify-existing replay;
- [x] normal and `python -O` aggregate receipts byte-identical;
- [x] 60-entry closed source manifest;
- [x] normal and optimized isolated manifest-only replay;
- [x] release attestation binds manifest, PDF, receipt, seven payloads, and four
  E-A69 certificates;
- [x] private-path, secret, placeholder, email, and newline scans clean;
- [ ] repository committed under the noreply identity;
- [ ] remote SHA, public visibility, default branch, and first CI run verified;
- [ ] two independent post-publication red teams adjudicated: paper and repo.

The final three rows are completed only after the remote exists. If either red
team finds a high or blocking defect, publication returns to HOLD until a new
commit and rerun close it.

## Non-release claims

This repository does not claim all-zero reconstruction, dimension above three,
arbitrary/noisy input extraction, numerical stability, industrial deployment,
novelty, priority, DOI, arXiv deposit, journal submission, or acceptance.
