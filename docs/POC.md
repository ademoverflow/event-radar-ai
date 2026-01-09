# PoC – LinkedIn Signal Detection for Event Opportunities

## Purpose of the PoC

The goal of this Proof of Concept (PoC) is to **validate the technical feasibility** of detecting event-related business opportunities on LinkedIn using automated crawling and LLM-based analysis.

This PoC is not meant to deliver a full product, but to **prove that valuable commercial signals can be reliably extracted from LinkedIn content** at scale.  
If successful, the same approach will later be extended to Instagram and X (Twitter).

---

## Scope of the PoC

The PoC focuses exclusively on **LinkedIn** and on **signal detection**, not on advanced CRM features or complex workflows.

The core question we want to answer is:

> *Is it technically feasible to continuously collect LinkedIn content and extract meaningful insights about past or future events using automation and LLMs?*

---

## Core Feature: LinkedIn Signal Engine

The PoC will implement a **LinkedIn Signal Engine** based on two complementary sources of signals.

---

### 1. Profile-Based Monitoring (User-Defined Sources)

Users can manually add:
- A **company LinkedIn profile**
- A **personal LinkedIn profile** (decision-maker, agency, journalist, event professional, etc.)

For each added profile:
- The system schedules **recurrent crawling** of the profile’s latest posts.
- New posts are automatically retrieved at a defined frequency.
- Each post is analyzed by an **LLM** to extract event-related signals, such as:
  - Past events (seminars, conventions, product launches, anniversaries, trade shows)
  - Upcoming or hinted future events
  - Event timing (explicit or inferred)
  - Type of event
  - Involved companies, brands, or partners
  - Named people (decision-makers, organizers, agencies)

This allows users to build a **custom watchlist** of strategic companies and individuals and monitor them continuously.

---

### 2. Keyword & Hashtag-Based Discovery (Platform-Driven Sources)

In parallel, the platform performs **active discovery** by crawling LinkedIn content based on:
- Keywords (e.g. *seminar, convention, stand, anniversary, event, launch*)
- Hashtags (e.g. *#event, #seminaire, #corporateevent, #salon*)

The system:
- Retrieves recent public posts matching the configured keywords or hashtags.
- Filters noise and irrelevant content.
- Uses an LLM to analyze each post and extract:
  - Event relevance
  - Event type and timeframe
  - Mentioned companies and people
  - Potential commercial interest level

This creates a **stream of newly detected opportunities** beyond the user’s manually added profiles.

---

## User Isolation & Configuration

Each user has:
- Their own private workspace
- Their own list of monitored profiles
- Their own keyword / hashtag configurations
- Their own crawling frequency and alert settings

No data is shared across users.

---

## Key Technical Hypothesis to Validate

The **main objective of the PoC** is to validate:

- Whether LinkedIn can be **scraped reliably and sustainably**, either via:
  - A custom scraper, or
  - A third-party scraping SaaS
- Whether the retrieved content is **sufficiently rich and consistent** to allow:
  - Event detection
  - Entity extraction
  - Temporal inference
  - Business signal qualification using an LLM

The UI, dashboard, and workflows are intentionally kept simple.  
They serve only to **make the signal detection usable and observable**, not to optimize user experience at this stage.

---

## Expected Outcome of the PoC

At the end of the PoC, we should be able to demonstrate:

- Automated LinkedIn content collection (profiles + keywords)
- Recurrent crawling without manual intervention
- LLM-based extraction of structured event signals from unstructured posts
- A clear assessment of LinkedIn scraping feasibility (technical, operational, and risk-wise)

This PoC will determine whether the project can move forward to a full MVP and multi-platform expansion.

---
