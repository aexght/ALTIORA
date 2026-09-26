# College Database Project — Phase 1 (Karnataka) Data Collection Report

## Scope of this pass
This is a **starter batch**, not the full 200–300 college dataset the original brief describes. It covers 17 Karnataka engineering institutions pulled directly from the Ministry of Education's official NIRF 2024 Engineering ranking pages. It is meant to prove out the pipeline and give you real, correctly-sourced rows to build against — not to be Phase 1 in full.

## 1. Data sources used
- **NIRF (nirfindia.org)** — official Ministry of Education ranking site. Fetched directly:
  - Top-100 Engineering ranking page (exact rank + score)
  - Rank-band 101–150 page (alphabetical, no exact rank published)
  - Rank-band 151–200 page (alphabetical, no exact rank published)
- **Official college websites** — `rvce.edu.in` / `naac.rvce.edu.in` and `bmsce.ac.in` for NAAC grade confirmation.
- Regulatory-body eligibility norms (NMC/NEET, and general AICTE/UGC/BCI/PCI/ICAR frameworks) for the course eligibility table — corroborated across several current sources rather than fetched from a single official PDF; flagged as such in that file's `Source` column.

## 2. Fields collected
From official NIRF pages: College name, city, state, NIRF rank or rank-band.
From official college sites: NAAC grade, for the 2 colleges checked so far (RVCE = A+, BMSCE = A++).

## 3. Missing-value strategy
Every field I could not confirm from an official, fetched source was left **blank** — not estimated. This includes Ownership (partially filled only where public institutional status is unambiguous, e.g. NIT/IIT = Government), NAAC grade for 15 of the 17 colleges, hostel availability, fees, and Official_Website for most rows.

## 4. Assumptions made
None on numeric data. The only judgment calls were:
- **Excluded Visvesvaraya Technological University** from the college list even though it appears in the NIRF Engineering ranking — it's an affiliating university, not a college a student directly applies to for a seat, so it doesn't fit the schema's purpose.
- Ownership type (Government/Private/Deemed) filled only where it's uncontested public knowledge (e.g., an NIT or IIT is unambiguously a central government institute); left blank elsewhere.

## 5. Fields estimated
**None.** Nothing in `college_database.csv` was guessed. Where I found conflicting figures across aggregator sites (e.g. one non-official site claimed RVCE's NAAC grade as A++, while RVCE's own site says A+), I used the official domain and ignored the aggregator claim rather than reconcile them by guessing.

## 6. Fields verified (with citation)
- College name, city, state, NIRF rank/band — verified against nirfindia.org (official) for all 17 colleges.
- NAAC grade + official website — now checked for all 17 colleges, each against the institution's own domain (or, for The National Institute of Engineering Mysuru, the official page plus strong independent corroboration where the official page itself was vague on the letter grade). Two fields were deliberately left blank rather than guessed:
  - **IIT Dharwad** — official site confirmed, but no NAAC grade found on it. Newer IITs are not always required to seek NAAC accreditation, so blank here likely reflects reality rather than a gap in my research.
  - **PES University** — official domain confirmed, but independent sources disagree on the letter (A / A+ / A++), and the official `naac.pes.edu` page didn't state one clearly in what I could retrieve. Left blank rather than pick one.
- Ownership refined for 2 colleges based on what the research turned up: Nitte Meenakshi Institute of Technology and NMAM Institute of Technology are both now constituent colleges of Nitte (Deemed-to-be-University) rather than standalone private colleges (a change effective October 2024 for NMIT).

All 17 rows in this starter batch now have verified NAAC status (or an explicit, explained blank) and an official website. Fees, hostel availability, and placement data are still blank for all 17 — that's the natural next batch.

## 7. Data limitations — please read before using this for the ML pipeline
This is the honest state of things:

- **17 of an eventual 50–70 Karnataka colleges** are in the file. The remaining ones (more private engineering colleges, plus non-engineering colleges — arts/science/commerce, medical, law, pharmacy, agriculture, management — since your course list covers BCA/B.Com/BBA/MBBS/LLB/B.Pharm/B.Sc Agriculture, not just engineering) still need to be pulled. Engineering was the fastest to source because NIRF has a clean official list; the other domains will need separate NIRF category pages (Medical, Pharmacy, Law, Management, Overall/College) plus AICTE/UGC/NAAC lookups.
- **NAAC grade, hostel availability, fees, and placement data are almost entirely blank.** These require visiting each college's own website individually — there's no single official portal that aggregates them. That's roughly 3–5 separate lookups *per college*, which is why this is slow going.
- **`Placement_Rating (High/Medium/Low)` cannot be populated from official sources at all**, for any college. No government or NAAC/NIRF portal publishes a categorical placement rating — that field only exists on private aggregator sites (Careers360, Shiksha, Collegedunia, etc.), which your brief explicitly asked me to avoid. Worth deciding now: either drop this column, or replace it with something officially quantifiable — e.g., NIRF's own "Graduation Outcomes" sub-score, which is published per institution on the same official ranking pages.
- **`college_course_mapping.csv` is essentially just a template right now.** Per-course seat counts and fees live in each college's own admission brochure or the relevant state counselling portal (KEA/COMEDK for Karnataka), not on NIRF. I did not fabricate any seat numbers or fees, as instructed — they're blank pending that lookup.
- The **course eligibility table** reflects well-established, slow-changing regulatory norms rather than a single fetched official PDF for each course (MBBS/NEET was directly cross-checked this session; the others are stable general knowledge flagged for verification). These change less often than college-specific data, but you should still confirm current-year figures against the named regulator before the ML pipeline goes live, since NEET/CLAT/PCI cutoffs are revised most years.

## Honest bottom line on scale
Verifying even this 17-college starter batch to the level of detail you specified (NAAC + fees + hostel + placement + website, each cited) would take on the order of 60–80 more searches just for these 17. Getting to 50–70 Karnataka colleges alone, fully verified, is realistically 250+ searches — and that's before Kerala, Tamil Nadu, Maharashtra, and the rest of India. That's beyond what a single chat response can responsibly do; it's Research-feature territory, or a project we chip away at in dedicated batches.
