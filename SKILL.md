---
name: resume-tailor
description: Tailor a LaTeX resume to a specific job posting and compile it to PDF locally. Use when the user pastes a job description or job URL and wants a resume for it, asks to customize/adapt their resume for a role, or asks how well they match a posting. Handles job sites that block scrapers, enforces a one-page layout, and reports requirement gaps instead of inventing qualifications.
---

# Resume Tailor

Turn a job posting into a tailored, compiled resume PDF — without fabricating anything.

## The core rule

**Tailoring means reorganizing, reweighting, and rewording what is already true. It never means adding skills or experience the person does not have.**

Every claim in the output must trace back to the master resume or to something the user stated in conversation. When the posting requires something the user lacks, say so in the report and leave it off the resume. Large employers increasingly state in their postings that misrepresenting qualifications is grounds for immediate disqualification, and a fabricated line collapses at the first interview question.

## Setup (first run)

Check for a master resume and a LaTeX compiler:

```bash
ls ~/Desktop/resumes/_master/master-resume.tex 2>/dev/null
command -v tectonic || ls ~/.local/bin/tectonic
```

- **No master resume** → ask the user for their current resume (`.tex` preferred; a PDF works — read it and rebuild as `.tex` from `templates/master-resume.tex`). Save it as the master. It is the single source of truth; when the user's experience changes, update the master, not just one tailored copy.
- **No compiler** → install Tectonic (single binary, no admin rights, ~19 MB):

```bash
bash scripts/install_tectonic.sh
```

Store tailored output next to the master, one folder per user, named `YYYY-MM_Company_Role.tex` / `.pdf`.

## Workflow

### 1. Get the posting

Try `WebFetch` first. If it returns 403 or an empty body, the site is blocking automated fetches — use the fallback, which sends a browser User-Agent and extracts both JSON-LD structured data and body text:

```bash
python3 scripts/fetch_jd.py "<url>"
```

If both fail, ask the user to paste the description text. Do not guess at the requirements.

### 2. Analyze before writing

Produce these four things internally before touching the resume:

1. **Hard gates** — degree field, graduation window, required certifications, work location, language requirements. If the user fails a stated hard gate, say so plainly and early. Do not quietly produce a resume for a role they are ineligible for; tell them, then let them decide.
2. **Keyword map** — the posting's recurring nouns and verbs (systems, methods, deliverables) matched against real items in the master.
3. **Gaps** — required or desirable items with no basis in the master. These go in the report, never in the resume.
4. **Rotation or track options** — many graduate programs list sub-tracks. Map the user's strengths to the specific track names; it makes the match legible to a screener.

### 3. Tailor

- **Summary**: rewrite fully for the role. Lead with whatever the posting treats as non-negotiable (a language requirement, a degree window, a named skill).
- **Section order**: put the most relevant section first. A partnerships role may need volunteer event experience above professional experience; a data role needs the opposite. Section headings can be renamed to match the domain (e.g. `Leadership` → `Leadership & Event Experience`) as long as the content is unchanged.
- **Bullets**: reorder within each role, merge weaker ones, and reword using the posting's vocabulary — but only where the underlying work genuinely matches. Keep every number that already exists; numbers are the strongest signal on the page.
- **Job titles**: never alter a real title. To clarify scope, append a factual qualifier: `Production Engineer Intern -- Packaging & Outbound Operations`.
- **Future roles**: an accepted-but-not-started job is listed as `Incoming <Month Year>` with scope described as selected-to-do, not as accomplished. Switch it to a normal date range only once the user confirms they have started.
- **Skills**: reorder categories so the most relevant sits first, and rename category labels to mirror the posting. Do not add a skill just because the posting asks for it.

### 4. Compile and verify one page

```bash
tectonic path/to/tailored.tex
python3 scripts/check_pages.py path/to/tailored.pdf
```

Entry-level and campus-hire resumes must be one page. If it spills, apply these in order — content first, typography last:

1. Merge or cut the least relevant bullet (usually the oldest role or a side project)
2. Tighten wording in the summary
3. Drop a whole low-relevance entry
4. Only then adjust spacing: `\titlespacing*{\section}{0pt}{3pt}{1pt}`, `\vspace{0.5pt}` in the entry macro, margins `0.4in` / top-bottom `0.3in`

Read the compiled PDF back to confirm the layout is clean — no orphaned lines, no overflowing skills row.

### 5. Report

Keep the resume itself in the file; keep the reply short. Cover:

- **Fit verdict** — including any hard gate the user fails, stated first
- **What changed** and why, tied to the posting's language
- **Gaps** — what the posting wants that the user does not have, and whether it is realistically closeable before an interview
- **Items to confirm** — anything inferred rather than known: dates, employer-internal details (system names, site names, figures), and any narrative detail reconstructed from thin information

Never present a reconstructed detail as fact. If a story's specifics were inferred, mark them and ask the user to correct them, because they will be asked about it.

## Application essays

The same rules apply to free-text application questions (autobiography, strengths and weaknesses, biggest setback, proudest achievement):

- Build from real projects in the master; if the emotional or procedural detail is unknown, write a plausible reconstruction and **explicitly flag which parts need the user's confirmation**.
- For "weakness" questions, use a real, specific, checkable gap with a concrete remediation plan. Screeners have read every version of "I work too hard."
- Offer a short variant (~350 words) alongside the full one; application forms often cap length.
- Keep claims consistent with the resume. If the resume omits a skill, the essay must not imply fluency in it.

## Files

| Path | Purpose |
|---|---|
| `scripts/fetch_jd.py` | Fetch a posting past scraper blocks; prints JSON-LD and body text |
| `scripts/check_pages.py` | Print a PDF's page count |
| `scripts/install_tectonic.sh` | Install the Tectonic LaTeX compiler to `~/.local/bin` |
| `templates/master-resume.tex` | Single-page LaTeX resume template to start a master from |
