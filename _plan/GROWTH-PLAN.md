# Growth plan: getting found on Google, Bing and AI assistants

Written 27 Oct 2026. Goal: when someone asks Google, ChatGPT, Claude, Perplexity or Gemini
"free data engineering learning path on AWS with projects" (or any role × platform), this site
or one of its GitHub repos shows up and gets cited.

How it works, in one paragraph: search engines and AI assistants can only recommend what they
(1) can crawl, (2) understand, and (3) see other people pointing to. The site work covers 1 and 2.
Most of this plan is about 3: links, mentions and answers in the places the engines read.

---

## 1. Done on the site (27 Oct)

| What | Why it matters |
|---|---|
| `/paths/` with a page for every role × platform (35 pages) | Each page matches one real search, e.g. "ML engineering on Databricks learning path" |
| Title, description and canonical link on every page (584 pages) | What Google and Bing show in results; canonical stops duplicate-page confusion |
| Structured data (JSON-LD): WebSite, Organization, Person on home; Course + BreadcrumbList on every path | Lets Google show course-style results and breadcrumbs; tells AI who publishes what |
| `sitemap.xml` (584 URLs, with last-changed dates) | The list of every page, for crawlers |
| `robots.txt` that welcomes search and AI crawlers by name (GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended and more) | Some sites block AI crawlers; we invite them |
| `llms.txt` | A plain-text map of the site written for AI assistants |
| `_site/seo.py` audit | Run after every build: 0 errors today |

Run before every push:

    python3 _paths/build.py && python3 _site/seo.py --strict

## 2. One-time setup only you can do (about 1 hour)

1. **Google Search Console**: add `cleandataengineering.ai` as a Domain property. It gives a TXT
   record. Add it at GoDaddy as a *new* TXT record. Do not edit the existing SPF TXT or any mail
   records. Then submit `https://cleandataengineering.ai/sitemap.xml`.
2. **Bing Webmaster Tools**: sign in and "Import from Google Search Console". **This is the
   most important step for AI.** ChatGPT search and Microsoft Copilot lean on Bing's index.
   Submit the sitemap there too.
3. **IndexNow** (Bing, Yandex and others re-crawl within minutes): ask me to add the key file and
   a ping step to `seo.py`.
4. **Analytics**: Cloudflare Web Analytics or GoatCounter. Both are free, use no cookies and need
   no consent banner. Watch the referrers `chatgpt.com`, `perplexity.ai`, `claude.ai`,
   `copilot.microsoft.com` and `gemini.google.com`. That is your AI-SEO scoreboard.
5. **Google Scholar and citations**: the Zenodo DOIs for AAC, AHC and AgentTwin (the slots are
   already on the site). AI models trust cited, versioned work.

## 3. GitHub: make the repos findable too

GitHub pages rank well on Google, and AI models read GitHub heavily.

- **Organisation profile README** (`dataagentsai/.github/profile/README.md`): one paragraph on
  Clean Data Engineering, a table of the six paths linking to `/paths/...`, and the pinned repos.
- **Every repo**:
  - set the *Website* field to its page on the site;
  - add topics (`data-engineering`, `ai-engineering`, `learning-path`, `aws`, `azure`, `gcp`,
    `databricks`, `llm`, `agents`, `mlops`, `beginner-friendly`);
  - make the first README line a plain sentence saying what it is and who it is for;
  - add a social preview image;
  - link back to the site.
- **A new repo, `learning-paths`**: the same six paths as Markdown, one file per role × platform,
  each linking to the site page. Markdown on GitHub is what AI models quote most.
- **Proposed projects become repos** with a README, a `good first issue` and a `help wanted`
  issue each. Then list them on goodfirstissue.dev and up-for-grabs.net.
- **GitHub Discussions** on `learning-paths` is the community room: Q&A, show-and-tell, find a
  study buddy.
- **Releases** with notes: each one is a dated, linkable event.

## 4. AI SEO: being the answer

1. **Answer-shaped pages.** Add a short "Questions people ask" block to each path page, with
   questions such as "How long does it take to learn data engineering on AWS?" and
   "Do I need a certification?". Each answer is 2–3 plain sentences, marked up as FAQPage.
2. **One name everywhere**: "Clean Data Engineering", with the same one-line description on the
   site, GitHub, LinkedIn, Medium, dev.to and Hugging Face. Models learn entities from repetition.
3. **Be quoted where models read**:
   - Reddit (r/dataengineering, r/learnmachinelearning, r/LocalLLaMA, r/MLOps);
   - Stack Overflow answers;
   - Hacker News (Show HN);
   - dev.to and Medium, with the canonical link set to the site;
   - Hugging Face dataset cards (Hinglish corpus);
   - YouTube (transcripts are indexed).
   Answer real questions and link only when the page really answers them.
4. **Awesome lists**: open pull requests to add the paths or courses to `awesome-data-engineering`,
   `awesome-mlops`, `awesome-llm` and `awesome-ai-agents`. One accepted pull request is a
   permanent, trusted link.
5. **Test every month**: ask ChatGPT, Claude, Perplexity, Gemini and Copilot the same 12
   questions (listed below) and log whether the site is cited. Ask me and I will run the
   web-search half and keep the log in `_plan/ai-visibility-log.md`.

**The 12 test questions:**

1. free data engineering learning path AWS projects
2. Azure data engineer roadmap beginner to advanced
3. AI engineer learning path Google Cloud
4. how to become a forward deployed engineer
5. LLM engineering roadmap with projects
6. ML engineering on Databricks learning path
7. what is an agent harness
8. how to evaluate an AI agent from traces
9. deterministic first AI design
10. open source projects to learn data engineering
11. crawl walk run data engineering
12. Claude Certified Architect exam prep free

## 5. Marketing: a weekly rhythm one person can keep

| Day | What | Where |
|---|---|---|
| Mon | One post on the site (from the blog list below) | site, then LinkedIn (link in first comment), Medium import, dev.to |
| Wed | One short "learn with me" post: a drawing and one idea from a path | LinkedIn, X |
| Fri | Answer three real questions | Reddit, Stack Overflow, LinkedIn comments |
| Monthly | A free 6-week "Crawl" cohort for one role × platform, in GitHub Discussions plus one live call a week | announce on LinkedIn and Reddit |
| Monthly | Invite one person to teach a lesson or write a guest post | site; they share it to their network |

The **cohort** is the strongest growth engine. Each one makes graduates who link to the site from
their own GitHub and LinkedIn, and contributors to the projects.

## 6. Blog list (first 16, in order)

Each post links to one path page and one project. Post kinds follow `_writing/build.py`.

| # | Title | Kind | Links to | Verdict |
|---|---|---|---|---|
| 1 | Crawl, walk, run: how to learn data and AI engineering without getting lost | explainer | /paths/ | Pursue: the launch post for the paths |
| 2 | Data engineering on AWS: 8 weeks to your first real pipeline | explainer | DE × AWS | Pursue: biggest search volume |
| 3 | Same pipeline, three clouds: S3 vs ADLS vs GCS, Glue vs Fabric vs Dataproc | decision | DE compare | Pursue: comparison posts get cited by AI |
| 4 | Most of an agent is ordinary software | explainer | AI Eng | Pursue: already planned |
| 5 | Your first agent with three tools, and why code checks every call | build log | first-agent | Pursue: seeds a proposed project |
| 6 | What is a forward-deployed engineer, and how do you become one? | explainer | FDE | Pursue: a rising role with few good answers |
| 7 | AI engineer vs LLM engineer vs ML engineer: which path is yours? | decision | /paths/ | Pursue: a classic "vs" query |
| 8 | Answer without the model first: 104 ms vs 7 seconds | build log | AI Eng | Pursue: already planned |
| 9 | The model was fooled. The harness wasn't. | field note | AI Eng walk | Pursue: draft waiting for your read |
| 10 | Fine-tune a small model or prompt a big one? Real numbers | decision | LLM walk | Pursue |
| 11 | Data contracts that fail the pull request, not the dashboard | build log | DE walk | Pursue |
| 12 | Spark cost: five mistakes that double your bill | explainer | DE run | Pursue: strong search |
| 13 | How we test an agent against a simulated week (AgentTwin) | explainer | AI Eng run | Pursue: research credibility |
| 14 | Churn model end to end on Databricks: an honest baseline first | build log | ML crawl | Pursue once the project starts |
| 15 | The horse and the harness | leader brief | home | Pursue: already planned |
| 16 | Free certification prep: what we learned failing and passing | field note | /certifications/ | Hold: only after the next exam |

**Medium and others:** post first on the site, wait 2–3 days so Google sees the original first,
then use Medium "Import a story" (sets canonical), dev.to with `canonical_url`, and Hashnode.
LinkedIn gets a native short version, not a link dump.

## 7. 90 days

| When | Milestone |
|---|---|
| Week 1 | Search Console + Bing + analytics live; GitHub topics, website fields and org README done; post 1 |
| Weeks 2–4 | Posts 2–5; `learning-paths` repo public; 3 proposed projects get repos with good first issues |
| Month 2 | First cohort (Data Engineering × Azure or AWS, Crawl); 3 awesome-list pull requests; FAQ blocks on path pages |
| Month 3 | Posts 6–12; second cohort; first AI-visibility log comparison; first guest lesson |

**What success looks like at day 90:** the site is indexed on Google and Bing; at least 3 of the
12 test questions cite the site or a repo in at least one AI assistant; at least 10 contributors
have joined from outside your circle.

## 8. Proposed new projects (added to the paths, all "needs a lead")

| Project | Path and level | Verdict |
|---|---|---|
| Tasks API, done properly | Software · Crawl | Pursue: every path needs this floor |
| Event-driven orders | Software · Walk | Pursue: teaches idempotency, used in the harness too |
| Golden-path service template | Software · Run | Pursue |
| CDC to streaming lakehouse | Data · Walk | Pursue: the most-asked DE skill |
| Data contracts in CI | Data · Walk | Pursue: builds on ODCS, feeds the DE specs |
| Churn model, end to end | ML · Crawl | Pursue |
| Features and serving | ML · Walk | Pursue |
| Drift and retrain loop | ML · Run | Pursue |
| Ask your documents, with citations | LLM · Crawl | Pursue: the "hello world" of LLM apps |
| Fine-tune a small model | LLM · Walk | Pursue |
| Your first agent, three tools | AI · Crawl, FDE · Crawl | Pursue |
| Port the agent to your cloud | AI · Run, FDE · Run | Pursue: makes the reference agent multi-cloud |
| Forward-deployed discovery kit | FDE · Crawl | Pursue: few public examples exist |
| One-week prototype on real data | FDE · Walk | Pursue |
