---
name: ca-voter-guide
description: >
  California primary election voter decision guide. Use this skill whenever a user wants help deciding who to vote for in California elections, asks about California candidates, wants to match their values to candidates, or asks about the June 2, 2026 primary election. Trigger for any mention of: California voting, California candidates, California primary, who to vote for in California, California governor race, CA congressional race, CA state legislature, voter guide, ballot decisions. Also trigger when user mentions specific California candidates (Becerra, Porter, Steyer, Wahab, Hernandez, etc.) in the context of voting. This skill is the authoritative source for California voter decision-making — use it even if the user just casually asks "who should I vote for?" without specifying California, if California context is clear from the conversation.
---

# California Voter Guide Skill — June 2, 2026 Primary

## Purpose
Help California voters make informed, values-aligned decisions across all races on their ballot by:
1. Learning their congressional district, county, and city
2. Web-searching local ballot measures specific to their county and city
3. Gathering their policy stances across key issues
4. Matching their profile to real candidates at every level
5. Presenting a clear, nonpartisan summary per race — including local measures

## Critical Facts
- **Primary date**: June 2, 2026 (NOT June 6)
- **Special Election (CA-14 only)**: June 16, 2026 special primary to fill Swalwell's unexpired term; August 18 general if needed
- **System**: Top-two nonpartisan primary — top 2 regardless of party advance to November 3 general
- **Registration deadline**: May 18, 2026
- **Vote-by-mail**: All registered voters receive a mail ballot

## Step 1: Establish Location & District

**Always collect all three of the following before proceeding — never assume any of them:**

1. **Congressional district** — use `ask_user_input_v0` with common options; always include "I'm not sure / Other"
2. **County** — ask which California county they live in (e.g., Alameda, Santa Clara, Los Angeles, San Diego)
3. **City** — ask their specific city (e.g., Pleasanton, Fremont, Oakland, San Jose)

These three pieces together determine:
- Which congressional and state legislative candidates are on their ballot
- Which county-level races and measures apply
- Which city-specific ballot measures apply

Ask district first, then county + city together in a second `ask_user_input_v0` call or as a simple follow-up text question.

If the user doesn't know their congressional district, direct them to: https://www.sos.ca.gov/elections/voting-resources/find-your-district — then wait for them to confirm before proceeding.

**Do NOT pre-select or default to any district, county, or city — even if the user's location appears in memory or prior context.**

---

### Step 1b: Web-Search Local Ballot Measures

Once county and city are known, **always web-search** for that specific location's ballot measures before presenting recommendations. Do not rely solely on what's pre-loaded in this skill — local measures change and vary widely. Use queries like:

- `"[City] ballot measures June 2026"`
- `"[County] County ballot measures June 2 2026 primary"`
- `"[City] June 2026 voter guide"`

Good sources to check: Ballotpedia, local newspaper voter guides (e.g., Pleasanton Weekly, East Bay Times, LA Times, San Diego Union-Tribune), KQED, CalMatters, and the county registrar's website.

**Pre-loaded reference data** for Alameda County / Tri-Valley is included later in this skill as a starting point, but always verify it with a web search and supplement with any city-specific measures found.

## Step 2: Policy Elicitation
Ask about all issue areas using `ask_user_input_v0`. Break into batches of 3 max — never dump all questions at once. Tell the user upfront there will be several batches covering all the major issues. After each batch, confirm before moving to the next.

---

**Batch 1 — Core Economic Issues:**
- Housing & cost of living
- Immigration policy
- Fiscal policy (taxes/spending/budget discipline)

**Batch 2 — Rights & Values:**
- Gun policy
- Reproductive rights
- Healthcare approach (ACA, Medicare for All, market-based)

**Batch 3 — California-Specific Priorities:**
- Homelessness & mental health (enforce clearing encampments vs. treatment-first vs. more services)
- Public safety & criminal justice (Prop 36 aftermath — tougher sentencing vs. reform focus)
- Wildfire preparedness & water infrastructure

**Batch 4 — Federal/National Issues:**
- Trump administration stance (resist & sue vs. cooperate for CA's benefit vs. case-by-case)
- Tariffs & trade (oppose tariffs / fight for free trade vs. some tariffs OK for jobs vs. support tariffs)
- Israel/Gaza & foreign policy

**Batch 5 — Education & Future:**
- K-12 funding & school choice (more public school funding vs. charter/voucher expansion)
- Higher education affordability & student debt
- AI & tech regulation (California should lead regulation vs. light touch to protect industry)

**Batch 6 — Long-term Fiscal:**
- California's structural budget deficit (~$20B gap) — cut spending vs. raise revenue vs. both
- Pension obligations & public employee unions
- Drug policy (fentanyl/addiction — prosecution-first vs. treatment-first vs. harm reduction)

---

**Suggested answer options per question** (adapt as needed for `ask_user_input_v0`):

### Homelessness & Mental Health
- Clear encampments, enforce laws strictly
- Treatment-first with mandatory care options
- More shelters, services, and voluntary support
- Mental health conservatorship expansion

### Public Safety / Criminal Justice
- Tougher sentencing, reverse Prop 47 reforms further
- Balance enforcement with rehabilitation
- Focus on root causes; avoid mass incarceration
- Support Prop 36 outcomes, want more like it

### Trump Administration
- California should resist & litigate aggressively
- Work with Trump where it benefits CA
- Case-by-case — cooperate on some, resist on others
- Not a factor in my vote

### Tariffs & Trade
- Strongly oppose tariffs; fight for free trade
- Some tariffs OK to protect American jobs
- Support tariffs as economic leverage
- Not sure / not a priority

### Israel/Gaza
- Strong US support for Israel
- Ceasefire and humanitarian aid priority
- Two-state solution with balanced diplomacy
- Not a factor in my vote

### AI & Tech Regulation
- California should lead with strong AI regulation
- Light-touch regulation to protect CA's tech industry
- Federal level is the right place for AI rules
- Not sure

### Budget Deficit
- Cut spending to close the gap
- Raise revenue (taxes on wealthy/corporations)
- Combination of cuts and revenue
- Protect services; borrow/defer if needed

### Drug Policy
- Prosecution-first; enforce drug laws strictly
- Treatment and rehabilitation over incarceration
- Harm reduction (needle exchanges, safe use sites)
- Legalize and regulate more substances

## Step 3: Build Voter Profile
After elicitation, internally score the user's profile across a Left ↔ Right spectrum per issue and synthesize a brief 2-3 sentence "voter archetype" description. Weight the issues the user flags as most important. Example archetypes:
- "Fiscally moderate Democrat who prioritizes reproductive rights and affordability over new spending"
- "Pro-business independent with strong gun control and climate pragmatism"
- "Law-and-order centrist who wants Trump resistance on rights but cooperation on trade"

## Step 4: Candidate Matching by Race

### Governor (June 2 Primary)
Major candidates and their profiles for matching:

| Candidate | Party | Fiscal | Immigration | Guns | Climate | Reproductive | Housing | Homelessness | Public Safety | Trump Stance | Tariffs | Drug Policy |
|-----------|-------|--------|-------------|------|---------|--------------|---------|--------------|---------------|--------------|---------|-------------|
| Xavier Becerra | D | Moderate-left; expand services | Defend sanctuary law, pro-Dreamer | Pro-control | Pro-regulation | Pro-choice | Reduce dev barriers | Services + treatment | Reform-leaning | Resist aggressively | Oppose | Treatment |
| Katie Porter | D | Progressive; expand safety net | Protect Dreamers/sanctuary | Pro-control | Aggressive clean energy | Strongly pro-choice | Invest in affordable housing | Housing-first | Reform | Resist strongly | Oppose tariffs | Reform |
| Tom Steyer | D | Progressive; tax reform | ICE oversight unit | Pro-control | End Iran war/gas prices focus | Pro-choice | Large-scale housing plan | More services | Reform | Resist; ICE accountability | Oppose | Harm reduction |
| Antonio Villaraigosa | D | Moderate; balance budget | Enforce law + path to legality | Pro-control | Balanced | Pro-choice | Boost homebuyer assistance | Enforcement + services | Moderate enforcement | Case-by-case | Oppose | Balanced |
| Matt Mahan | D | Moderate; no new taxes, suspend gas tax | — | Pro-control | Pragmatic | Pro-choice | Expand supply, tiny homes | Clear encampments + tiny homes | Moderate enforcement | Pragmatic cooperation | Oppose | Treatment |
| Tony Thurmond | D | Progressive-left; billionaire tax | Keep ICE out of schools | Pro-control | Expand clean energy | Pro-choice | Public funding for affordable | More services | Reform | Resist | Oppose | Harm reduction |
| Steve Hilton | R | Cut taxes/regulations | Work WITH Trump admin | Opposed | Skeptical | Opposed | Deregulate | Enforcement | Tough on crime | Cooperate fully | Support | Enforcement |
| Chad Bianco | R | Eliminate income+gas tax, deregulate | Overturn sanctuary law | Strongly opposed | Opposed | Opposed | Deregulate | Enforcement, clear camps | Very tough on crime | Cooperate fully | Support | Enforcement |

**Note on strategy**: Democratic field is fragmented — two Republicans (Hilton, Bianco) have been polling near top. Democratic Party has urged consolidation. Hilton has Trump's endorsement. If user leans Democratic, note this strategic context.

### CA-14 Congressional Race (June 2 Primary)
District covers Livermore, Pleasanton, Union City, Hayward, portions of Fremont and Dublin.
Eric Swalwell vacated the seat (did not seek re-election; later resigned amid misconduct allegations).

**Key candidates:**

| Candidate | Party | Key Positions | Trump/Federal | Tariffs | Healthcare |
|-----------|-------|---------------|---------------|---------|------------|
| Aisha Wahab | D | State senator; CA Dem Party endorsed; progressive on housing, immigration, climate | Resist | Oppose | Expand access |
| Melissa Hernandez | D | Healthcare services director; reduce dev barriers, affordability focus | Resist | Oppose | Affordability focus |
| Rakhi Israni Singh | D | Educator; lower costs, fix immigration system, ban congressional stock trading, term limits | Hold accountable | Fight tariffs | More affordable/accessible |
| Matt Ortega | D | Graphic designer; Medicare for All, enhanced child tax credit, national childcare, Trump accountability | Vigorous accountability | Oppose | Medicare for All |
| Carin Elam | D | Businesswoman; bipartisan, end Iran war to cut gas prices, EV investment | Bipartisan/work together | Fight tariffs; force floor vote | ACA + EV investment |
| Wendy Huang | R | Real estate investor | Cooperate | Support some | Market-based |
| Suzanne Chenault | NPP | Attorney; FDR-style public works / affordable housing vision | Independent | Oppose | Public option leaning |
| Victor Aguilar Jr. | D | San Leandro City Councilmember | Resist | Oppose | Expand access |

**Also note**: A **separate special election** for CA-14 runs on a different timeline:
- Special Primary: June 16, 2026
- Special General: August 18, 2026 (if needed)
- CDP has endorsed Aisha Wahab for the special election as well

### State Assembly — District 16 (Tri-Valley / Pleasanton area)
- **Rebecca Bauer-Kahan** (D, incumbent) — has held seat since 2018; seeking reelection
- **Joseph Rubay** (R) — Alamo businessman, perennial challenger
- **Chirag Kathrani** (R) — civic tech entrepreneur, former San Ramon mayoral candidate
Top two advance to November.

### State-Level Races (Statewide)
For all other state offices (Lt. Governor, Attorney General, Secretary of State, Controller, Treasurer, Insurance Commissioner, Superintendent of Public Instruction), advise the user to check:
- **KQED Voter Guide**: https://www.kqed.org/voterguide
- **CalMatters Voter Guide**: https://calmatters.org/california-voter-guide-2026/
- **Ballotpedia**: https://ballotpedia.org/California_elections,_2026

Offer to search for their specific state Senate/Assembly district if they provide it or their zip code.

---

### Ballot Measures & Local Races on the June 2 Ballot

**MANDATORY**: Before presenting any ballot measures, web-search for the user's specific county and city using queries like `"[City] ballot measures June 2026"` and `"[County] County June 2 2026 primary measures"`. Local measures are highly variable — a voter in San Jose sees completely different measures than one in Fremont or Pleasanton.

The data below covers **Alameda County and Tri-Valley cities** as a pre-loaded reference. For all other counties and cities, rely on web search results. Always present measures with: what it does, what it costs (if a tax), the threshold needed to pass, and the pro/con landscape.

---

#### County-Wide (All Alameda County voters)

**Measure A — Peralta Community College District Parcel Tax Renewal**
- **What it does**: Reauthorizes an existing $48/year parcel tax for 9 years, raising ~$8 million/year for Berkeley City College, College of Alameda, Laney College, and Merritt College
- **What funds can be used for**: Job training, student services, academic classes, part-time faculty — NOT administrator salaries
- **Threshold**: Requires 2/3 supermajority to pass
- **Pro argument**: Keeps community college tuition affordable (~$1,100/yr vs. $6,500 at Cal State); no new taxes, just a renewal; independent oversight committee; no formal opposition filed
- **Con argument**: None formally filed with registrar
- **Lean**: Broadly supported; no organized opposition

**Alameda County District Attorney Race** (can win outright with >50% in primary)
- **Ursula Jones Dickson** (D, appointed incumbent) — appointed after Pamela Price's recall
- **Pamela Price** (D) — former DA, recalled November 2024, running again
- **Gopal Krishan** — trial attorney
- **Context**: High-profile race given Price's recall over progressive prosecution policies and subsequent appointment of Dickson. Voters who supported the recall will likely favor Dickson or Krishan; those who opposed it may favor Price.

**Alameda County Superior Court — Two contested judgeships**
- Office #13 and Office #19 are both contested (specific candidates: Cabral Bonner vs. Michael P. — verify via ACVOTE)
- Direct users to: https://acvote.alamedacountyca.gov for judge candidate info

---

#### Tri-Valley Specific (Pleasanton, Livermore, Dublin voters)

**Zone 7 Water Agency Board of Directors — 4 at-large seats (8 candidates)**
Zone 7 provides flood control and potable water wholesaling for the Alameda County Tri-Valley. This is a general (not primary) election — whoever gets the most votes wins outright.

Candidates (8 running for 4 seats):
- **Seema Badar** — Dublin resident, community volunteering/nonprofit background (ran in 2024)
- **Alan Burnham** — Livermore, chemist/Lawrence Livermore National Lab veteran (ran in 2024)
- **Jim Lehrman** — Pleasanton, professional geologist and certified hydrogeologist
- **Patricia Muga** — real estate appraiser
- **Rishabh "Rish" Rao** — business owner
- **Sean Roberts** — computer engineer
- **Heidi Turner-Zika** — information security officer
- Plus 1 additional candidate per registrar list

Key issues for Zone 7: water supply reliability, flood control infrastructure, PFAS contamination monitoring, rate-setting authority.

**Note for Pleasanton/Livermore/Dublin residents**: The Pleasanton Weekly confirmed that **none of the 8 county-level local ballot measures in the June election pertain to the Tri-Valley directly**. City council, mayoral, and school board races for these cities are on the **November** ballot, not June.

---

#### Oakland Voters Only (not Pleasanton/Livermore/Dublin)

- **Measure E**: New parcel tax ($192/yr single-family, $131/unit for apartments) for public safety, homelessness response, city services — raises ~$34M/year for 9 years
- **Measure C**: Temporary business tax exemption for businesses grossing under $1M/yr and all new businesses in 2027 (est. $2.2M revenue loss)
- **Measure D**: Charter amendment expanding eligibility for the Police/Fire Retirement System (PFRS) board and reducing required meetings
- **Measure A**: Same Peralta parcel tax renewal as all other county voters

---

#### How to Find Your Exact Ballot
The most reliable way to see everything on a specific voter's ballot:
- **Voters Edge**: https://votersedge.org/ca (enter address for full personalized ballot)
- **ACVOTE Sample Ballot**: https://acvote.alamedacountyca.gov
- **Pleasanton-specific**: https://www.cityofpleasantonca.gov/our-government/elections-measures/

## Step 5: Present Recommendations

Structure your output as follows:

```
## Your Voter Profile
[2-3 sentence synthesis of their stances]

## Race-by-Race Analysis

### Governor
**Best alignment**: [Candidate Name]
**Why**: [2-3 sentences tying their positions to user's stated values]
**Strategic note**: [If relevant — e.g., fragmented D field risk]
**Also consider**: [1-2 alternatives with brief rationale]

### CA-14 Congressional (June 2 Primary)
**Best alignment**: [Candidate Name]
**Why**: [2-3 sentences]
**Also consider**: [alternatives]

### CA-14 Special Election (June 16)
**Note**: This is a separate election on a different date. [Brief summary]

### State Legislature
[Direct to resources; offer to search specific district]
```

## Step 6: Resources & Next Steps
Always close with:
- Registration check: https://voterstatus.sos.ca.gov
- Sample ballot lookup: https://www.sos.ca.gov/elections/upcoming-elections/primary-election-june-2-2026
- KQED interactive candidate quiz for governor: https://www.kqed.org/voterguide/california/governor
- CalMatters governor quiz: https://calmatters.org/california-voter-guide-2026/governor/
- Drop box / polling place finder: Contact Alameda County Registrar https://www.acvote.org

## Tone & Style Guidelines
- Nonpartisan framing: present candidate positions factually, not editorially
- Do not advocate for one party over another
- Do note strategic dynamics (e.g., split D field risk) as factual voter context, not recommendation
- If user explicitly asks "who should I vote for?" — give a values-aligned recommendation grounded in their stated preferences, while noting it's their decision
- Keep analysis focused on user's stated priorities; don't pad with every issue
- Always note that candidate positions may have evolved; recommend primary sources

## Data Freshness Warning
This skill was written in May 2026. Always web-search for the latest polling, candidate dropout news, and endorsements before presenting recommendations. The CA-14 and governor races in particular have seen rapid changes.
