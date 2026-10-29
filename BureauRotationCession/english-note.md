# The Rotation of Concessions — Research Note (English)

**Yipeng Li** · 2026-10-21 · CC BY 4.0

This note summarises two working papers and the negative results that followed from
re-analysing them. It is meant for readers who want the argument without the full
Chinese apparatus.

## 1. What the two papers ask

**Officialdom (Western Zhou–2026).** Why does the same cycle recur: a low-ranking
attendant, censor or deputy acquires real power in a crisis, is later proscribed or
hollowed out, and power migrates to a new low-ranking post? The paper uses the
completeness–composability–transfer (C–A–T) triangle as a diagnostic, not a theorem.
Three paths are distinguished: the regular bureaucracy keeps A and T, conceding C; the
inner court keeps C and T, conceding A; outposted offices keep C and A, conceding T.

**Hunan relay system (Ming–Qing).** A reconstruction of the relay network of central
Hunan, organised with the GEPF three-layer model (geography/population, economy,
fiscal-institutions). Its entry point is two family memories: a grandfather running
boats on the Laodao River in the 1940s–50s, and a father working in Liuyang's fireworks
district in the 1980s–90s.

## 2. What survived re-analysis

- **Mode, not rate.** In a type-level control sample of 67 Tang–Song offices (including
  offices that never changed), the two paths do **not** differ in the probability of
  change (IRR 0.70, 95% CI 0.25–1.91; log-rank p=0.60). They do differ in the *mode* of
  failure: secession appears only on the outposted path (5/31 vs 0/20; Fisher p=0.14),
  while hollowing and proscription concentrate in the inner court (9/20 vs 5/31).
  The earlier p=0.003 (12/31 vs 1/25) is a conditional association within a sample
  selected on the outcome, not a marginal effect.
- **Rank and border do not rescue the rate claim.** With 109 types (Tang, Song, Ming,
  Qing) and covariates for rank and frontier posting, the outposted coefficient is
  0.66 (0.22–1.98); rank is 1.74 (0.77–3.96), border 1.28 (0.43–3.84). Regular offices
  change significantly less (OR 0.16, 0.03–0.91). Secession remains 6/6 on the
  outposted path.
- **Fusion precedes usurpation, not rupture in general.** Of 28 constitutional ruptures,
  all 13 usurpations had a fusion line (one office holding C, A and T) within the
  preceding 30 years, against 3/15 for purges, coups, civil wars and secessions
  (Fisher p≈1.5×10⁻⁵). The lead time is 1–16 years (median 2). Fusion is a precondition
  of dynastic replacement, not a general precursor of collapse.
- **A budget threshold.** From the accounting inequality, simultaneous full possession
  requires K ≥ 3+λ. A budget that is "enough for three" (K=3) is still insufficient when
  the interaction penalty is positive; fusion needs an emergency budget above 3+λ, which
  is why it appears in wars and crises and is dismantled afterwards.

## 3. What did not survive

- **Relay density.** The published ordering (fireworks 3.7 km, tea 4.1 km, minerals
  5.5 km, official 9.0 km) does not reproduce from the 28 key nodes (north 12.8 km,
  east 16.2, west 22.7, south 70.6; Mann–Whitney p=0.19). The published numbers are
  means over *all* relay posts, not distances between key towns; the two cannot be
  compared. The density hypothesis is withdrawn pending full station-level geocoding.
- **Toponym regression.** Recomputing the six-county cross-section gives
  y = 72.3 − 0.89T (R²=0.58), not y = 95.2 − 2.82T (r=−0.92, R²=0.85). The slope's 95% CI
  (−1.95 to 0.17) includes zero. Direction survives; strength does not. The old
  "2.82 percentage points per year" is withdrawn.
- **Reliability.** A blind re-code of 15 boundary cases agrees 13/15 (86.7%), Cohen's
  κ=0.55. The ambiguities are: when a transfer occurs, whether "名分" counts as T, and
  whether military command counts as A. The codebook needs three revisions; the full
  sample has not yet been re-coded.

## 4. What this implies

The framework's value is diagnostic, not predictive. It tells you which vertex an
institution concedes; it does not tell you when a regime falls. The two papers are
strongest where they are most modest: secession is a path-specific failure mode;
usurpation has a detectable fusion precondition; relay density and toponym decay were
over-claimed and are now downgraded.

## 5. Files and limits

Data: `cases.csv`, `control_tangsong.csv`, `control_extended.csv`, `control_all.csv`,
`rupture_events.csv`, `event_leadlag.csv`; interactive explorers for both papers.
The Hunan full network (510 posts) and the toponym panel remain to be built; the
reliability audit needs an independent coder. Nothing in this note is a prediction
about any current government.

---
*Chinese working papers: officialdom DOI 10.5281/zenodo.23497841 (concept);
Hunan DOI 10.5281/zenodo.23480795 (concept). This note is unpublished.*
<p>把让渡写成可核对的账，使后来者不必从零开始成为可能。</p>

