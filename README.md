# resume-tailor

A [Claude Code](https://claude.com/claude-code) skill that turns a job posting into a tailored, compiled resume PDF — and tells you honestly where you fall short.

Paste a job URL or description. Claude reads the posting, compares it against your master resume, rewrites and reorders the relevant parts, compiles a one-page PDF locally, and reports which requirements you don't meet.

## Why

Most resume tools optimize for keyword stuffing. This one is built around the opposite constraint: **it never adds a skill or experience you don't have.** Tailoring here means reordering, reweighting, and rewording what is already true.

That constraint is practical, not just principled. Large employers state in their postings that misrepresenting qualifications is grounds for immediate disqualification, and an invented line falls apart at the first interview question. So gaps are reported to you instead of papered over — along with whether each one is realistically closeable before an interview.

## What it does

- **Reads postings that block scrapers.** Many job boards return 403 to plain HTTP clients. The fetcher sends a browser User-Agent and pulls the schema.org `JobPosting` block when the page has one.
- **Checks hard gates first.** Degree field, graduation window, location, language requirements. If you're ineligible, you hear it before anything else.
- **Rewrites for the role.** Summary rewritten, sections reordered, bullets reordered and reworded in the posting's vocabulary, skill categories relabelled — all from real material.
- **Compiles locally.** [Tectonic](https://tectonic-typesetting.github.io/) produces the PDF. No Overleaf round-trip, no LaTeX install, no admin password.
- **Enforces one page.** Content cuts first, spacing adjustments last, then verifies the page count.
- **Handles application essays too.** Autobiography, strengths and weaknesses, biggest setback — with any reconstructed detail explicitly flagged for you to correct.

## Install

```bash
git clone https://github.com/YOUR-USERNAME/resume-tailor.git ~/.claude/skills/resume-tailor
```

Then in Claude Code:

```
/resume-tailor
```

Or just paste a job posting and ask for a resume — the skill description triggers it.

### First run

Claude will ask for your current resume and save it as your master. `.tex` is preferred; a PDF works too — it will be read and rebuilt from `templates/master-resume.tex`.

The master is the single source of truth. When your experience changes, update the master rather than one tailored copy.

It will also install Tectonic if you don't have a LaTeX compiler:

```bash
bash scripts/install_tectonic.sh
```

Single binary to `~/.local/bin`, about 19 MB, no admin rights. The first compile downloads LaTeX packages and needs a network connection.

## Layout

```
resume-tailor/
├── SKILL.md                     # instructions Claude follows
├── scripts/
│   ├── fetch_jd.py              # fetch a posting past scraper blocks
│   ├── check_pages.py           # verify the PDF is one page
│   └── install_tectonic.sh      # install the LaTeX compiler
└── templates/
    └── master-resume.tex        # single-page template to start from
```

Tailored resumes are written next to your master as `YYYY-MM_Company_Role.tex` / `.pdf`.

## Standalone use

The scripts work without Claude:

```bash
python3 scripts/fetch_jd.py "https://example.com/jobs/123"
python3 scripts/check_pages.py resume.pdf --max 1
```

`check_pages.py` needs `pypdf` (`pip3 install pypdf`); the others use only the standard library.

## License

MIT
