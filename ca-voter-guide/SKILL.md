---
name: ca-voter-guide
description: >
  California November 3, 2026 general election voter decision guide. Use this skill whenever a user wants help deciding how to vote in California elections, asks about California candidates or propositions, wants to match their values to candidates, or asks about the November 2026 general election. Trigger for any mention of: California voting, California candidates, California propositions (Prop 1, 2, 3, 4, 5, 37–45, billionaire tax, voter ID, housing bond, CEQA/environmental review), California governor race, Becerra vs. Hilton, CA congressional race, CA-14 (Wahab vs. Hernandez), CA state legislature, local measures (e.g., Regional Transit Measure RTM, Pleasanton Measure HH), voter guide, ballot decisions. Also trigger when user mentions specific California candidates (Becerra, Hilton, Wahab, Hernandez, Bauer-Kahan, Bonta, Fiona Ma, etc.) in the context of voting. This skill is the authoritative source for California voter decision-making — use it even if the user just casually asks "who should I vote for?" or "how should I vote on the props?" without specifying California, if California context is clear from the conversation.
---

# California Voter Guide Skill — November 3, 2026 General Election

## Purpose
Help California voters make informed, values-aligned decisions across all races and measures on their ballot by:
1. Learning their congressional district, county, and city
2. Web-searching local ballot measures and races specific to their county and city
3. Gathering their policy stances across key issues
4. Matching their profile to the two finalists in every race and to each of the 14 statewide propositions
5. Presenting a clear, nonpartisan summary per race and measure — including local measures

## Critical Facts
- **Election date**: Tuesday, November 3, 2026 (polls 7 a.m.–8 p.m.)
- **System**: Top-two general — every partisan race now has exactly the two finalists from the June 2 primary (sometimes both from the same party)
- **Registration deadline**: October 19, 2026 (online/mail). After that, **Same-Day (Conditional) Voter Registration** is available at county election offices and vote centers through Election Day
- **Vote-by-mail**: All registered voters are mailed a ballot (mailing begins ~October 5). Mail ballots must be postmarked by Election Day and received within 7 days; drop boxes close 8 p.m. Election Day
- **14 statewide propositions** (Props 1–5 and 37–45) — the most tax measures on a CA ballot since 1994
- **No U.S. Senate race** in California this year
- **June 2 primary is over** — the primary-only content (crowded governor field, Alameda DA, Zone 7) is now historical context only

### June 2 Primary Results (context)
- **Governor**: Becerra (D) 28.0%, Hilton (R) 24.6%, Steyer (D) 22.8% — Becerra and Hilton advanced
- **Alameda County DA**: Ursula Jones Dickson won outright (64.3% vs. Price 25.5%, Krishan 10.2%) — **not on the November ballot**
- **CA-14 regular primary**: Wahab 34.3%, Hernandez 16.0%, Huang 15.9% — Wahab and Hernandez advanced
- **CA-14 special**: Wahab won the June 16 special primary (42.8%) and the August 18 special general over Hernandez (53.1%–46.9%); she now holds the seat for the rest of Swalwell's term

## Step 1: Establish Location & District

**Always collect all three of the following before proceeding — never assume any of them:**

1. **Congressional district** — use `ask_user_input_v0` with common options; always include "I'm not sure / Other"
2. **County** — ask which California county they live in (e.g., Alameda, Santa Clara, Los Angeles, San Diego)
3. **City** — ask their specific city (e.g., Pleasanton, Fremont, Oakland, San Jose)

These three pieces together determine:
- Which congressional and state legislative finalists are on their ballot
- Which county-level races and measures apply
- Which city-specific races and ballot measures apply

Ask district first, then county + city together in a second `ask_user_input_v0` call or as a simple follow-up text question.

If the user doesn't know their congressional district, direct them to: https://www.sos.ca.gov/elections/voting-resources/find-your-district — then wait for them to confirm before proceeding. Note: districts changed for 2026 after Prop 50 (2025) redrew congressional maps, so a voter's district may differ from 2024.

**Do NOT pre-select or default to any district, county, or city — even if the user's location appears in memory or prior context.**

If the user only wants help with the **statewide propositions**, location is not required — skip to Step 2 (Batches 1, 3, 6 and 7 are the most relevant) and then Step 4c.

---

### Step 1b: Web-Search Local Ballot Measures

Once county and city are known, **always web-search** for that specific location's ballot measures and races before presenting recommendations. Do not rely solely on what's pre-loaded in this skill — local measures change and vary widely. Use queries like:

- `"[City] ballot measures November 2026"`
- `"[County] County November 3 2026 ballot measures"`
- `"[City] city council mayor candidates November 2026"`

Good sources to check: Ballotpedia, local newspaper voter guides (e.g., Pleasanton Weekly, East Bay Times, LA Times, San Diego Union-Tribune), KQED, CalMatters, Local News Matters, and the county registrar's website.

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

**Batch 7 — Elections, Taxes & Growth (drives the November propositions):**
- Election rules (voter ID at the polls / public financing of campaigns / changing how recalls work)
- Taxing the wealthy (keep or raise taxes on high earners & billionaires vs. lock in limits on new taxes)
- Housing & infrastructure speed (streamline environmental review vs. keep current CEQA protections; state borrowing via bonds)

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

### Voter ID & Election Rules
- Require ID to vote; tighten election rules
- Keep current rules; voter ID makes voting harder
- Support public financing / reform of money in politics
- Not a priority

### Taxes on the Wealthy
- Keep or expand taxes on high earners and billionaires
- Keep current high-earner rates but no new wealth taxes
- Cut taxes and make new taxes harder to pass
- Not sure

### Environmental Review & Building
- Streamline CEQA to build housing/infrastructure faster
- Keep strong environmental review; target narrow fixes
- Build more but protect review for sensitive areas
- Not sure

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

## Step 4: Candidate & Measure Matching

### 4a. Governor (November 3 General)

| Issue | Xavier Becerra (D) | Steve Hilton (R) |
|-------|--------------------|------------------|
| Background | Former U.S. Rep (LA), CA Attorney General (2017–21), U.S. HHS Secretary under Biden | Former Fox News host, ex-adviser to UK PM David Cameron, "Small Business Owner" |
| Taxes / budget | Progressive income tax; supports Prop 3 (make high-earner rates permanent); open to taxing corporations whose workers rely on public aid | Eliminate state income tax on the first $150K of earnings, flat rate above; halve the gas tax |
| Prop 40 (billionaire tax) | Opposes | Opposes |
| Housing | Declare state emergency to fund ~40,000 approved affordable units; push cities to zone for apartments/duplexes; crack down on corporate home buying; expand down-payment aid; backs Prop 37 | "Starter homes" — cut fees/regulation for single-family homes; state loan program for first-time buyers; stop CEQA suits blocking construction; favors suburban over dense growth |
| Homelessness | Ongoing state funding for rental assistance + services; public dashboard of state-funded units; people offered shelter shouldn't stay on streets (no arrest language) | Make street camping illegal and have police clear encampments; fund sober housing over low-barrier shelters; overhaul homelessness spending |
| Immigration | Defend sanctuary law; criticizes indiscriminate ICE enforcement | Overturn sanctuary law limiting police–ICE cooperation; end Medi-Cal for undocumented immigrants; "lower the temperature" on deportations |
| Public safety | Voted for Prop 36; fully fund it incl. court-mandated drug treatment; doesn't back broadly longer sentences | Reopen closed prisons; reduce early release; expand rehabilitation; loosen limits on police stops |
| Climate / energy | Supports clean-energy goals but open to revising them (incl. 2035 gas-car ban) if gas/energy become unaffordable | Roll back clean-energy mandates and renewable purchase requirements; more in-state natural gas; forest restoration |
| Guns | Pro-gun-control record as AG | Reduce firearm restrictions |
| Reproductive rights | Pro-choice; endorsed by Planned Parenthood California | Has not made it a campaign focus; verify via current sources |
| Trump | Opposition is central — touts 100+ lawsuits as AG | Trump-endorsed; expects cooperative relationship to win more federal aid |
| Healthcare | Once backed single-payer; now expand state coverage, cut insurer admin costs, more telehealth, healthcare-worker loan repayment | End Medi-Cal for undocumented; more market competition; prevent provider consolidation |
| Education | No major new plan | Phonics; hold back 3rd graders not reading at grade level; easier teacher firing; charter conversions; public funds for private-school transfers; oppose trans youth in girls' sports |
| AI / tech | Ban social media under 16; transparency for AI in hiring; use AI for gov't efficiency | Lighter AI regulation; personally urges no smartphones under 16 (no mandate); supports pause on AI in young classrooms |
| Voter ID (Prop 39) | Opposes — says it makes voting harder | Supports |
| Key endorsements | CA Democratic Party, Planned Parenthood CA, Equality California, CA Faculty Association | Donald Trump, CA Republican Party, Nisei Farmers League |

**Context**: Polls show Becerra ahead but the race tightening — a Hilton-commissioned internal poll after the Sept. 30 CNN debate had Becerra 45.7%, Hilton 40.1%. Always web-search for current independent polls (PPIC, Berkeley IGS, Emerson) before presenting.

### 4b. Other Statewide Offices (finalists from the SOS certified list)

| Office | Candidate 1 | Candidate 2 |
|--------|-------------|-------------|
| Lieutenant Governor | Fiona Ma (D) — State Treasurer/CPA | Gloria Romero (R) — Educator/Businesswoman; former Democratic state senator |
| Attorney General | Rob Bonta* (D) — incumbent | Michael E. Gates (R) — Deputy U.S. Attorney; former Huntington Beach city attorney |
| Secretary of State | Shirley N. Weber* (D) — incumbent | Don Wagner (R) — Orange County Supervisor |
| Controller | Malia M. Cohen* (D) — incumbent | Herb W. Morgan (R) — Chief Investment Officer |
| Treasurer | Eleni Kounalakis (D) — Lieutenant Governor | Jennifer Hawks (R) — Retired Business Executive |
| Insurance Commissioner | Ben Allen (D) — State Senator | Jane Kim (D) — Attorney/Consumer Advocate (D-vs-D race) |
| Superintendent of Public Instruction (nonpartisan) | Richard Barrera — State Superintendent Advisor | Sonja Shaw — Chino Valley school board president (conservative; parental-rights focus) |
| Board of Equalization D1 | Nelson Esparza (D) | Shannon Grove (R) |
| Board of Equalization D2 (Bay Area) | Sally J. Lieber* (D) | John Pimentel (D) |
| Board of Equalization D3 | Mike Gipson (D) | Samuel P. Sukaton (D) |
| Board of Equalization D4 | Tom Umberg (D) | Denis Bilodeau (R) |

\* incumbent. Also on every ballot: **retention votes** (yes/no) for CA Supreme Court Associate Justices **Kelli M. Evans** and **Joshua Groban**, plus Court of Appeal justices for the voter's district.

For lesser-known offices, briefly describe what the office does, then match on the user's priorities (e.g., Insurance Commissioner → wildfire insurance availability and rate regulation; Superintendent → school choice/parental-rights vs. traditional public-school approach). Web-search candidate platforms before recommending.

### 4c. Statewide Propositions (14 measures)

Present each with: what YES does, what NO does, cost, and who's for/against. Match to the user's Batch 1, 3, 6 and 7 answers.

| Prop | Topic | YES means | NO means | Key support | Key opposition |
|------|-------|-----------|----------|-------------|----------------|
| **1** | Housing bond | State borrows **$11.25B** for affordable housing ($1.25B for veterans; also rental, student, farmworker, homeownership); ~$500–600M/yr repayment for ~25 yrs | No new housing bond | CA Dem Party, Gov. Newsom, Habitat for Humanity CA, U.S. Vets, CA Federation of Teachers | Some GOP lawmakers (CA GOP neutral) |
| **2** | Rainy day fund | Raise reserve deposit cap from 10% to 20% of General Fund taxes; allows paying down federal unemployment-insurance debt | Cap stays at 10% | CA Dem Party, Newsom | CA GOP, Reform California |
| **3** | High-earner income tax | Make permanent the 2012/2016 top rates (10.3% above ~$360K up to 12.3% above ~$721K) — currently set to expire after 2030; $5–16B/yr, mostly K-12 (89%) and community colleges (11%) | Rates expire as scheduled | Becerra, education groups, CA Dem Party | Anti-tax groups, CA GOP |
| **4** | Public campaign financing | Repeal the 1988 ban, allowing state & local public financing of campaigns | Ban stays (only charter cities like LA/SF can do it) | CA Dems, League of Women Voters | CA GOP, Reform California |
| **5** | Recall reform | Separate the "recall?" vote from the replacement election; recalled official could run in the successor election | Keep simultaneous recall + replacement ballot | CA Dems, League of Women Voters | CA GOP, Reform California |
| **37** | Middle-income homebuyer loans | CalHFA may borrow up to **$25B** for low-cost mortgages for buyers earning up to 2× area median income; private lenders bear default risk | No program | CA Dem Party, Becerra | Reform California (CA GOP neutral) |
| **38** | Immunology research bond | State borrows **$8.4B** for immunology research (cancer, Alzheimer's, heart disease); half to UC-affiliated institutes, half to public universities/nonprofits; 10% of resulting drug revenue returns to state | No bond | CA Dems and CA GOP | League of Women Voters |
| **39** | Voter ID | Require government ID at the polls, or last 4 digits of an ID on mail ballots; election officials must verify citizenship | Current rules stay | CA GOP, Reform California, Hilton | CA Dem Party, ACLU, Becerra |
| **40** | Billionaire tax | One-time **5% tax** on net worth (excl. real estate & retirement accounts) of ~200 Californians worth $1B+; tens of billions mainly for health care facing federal cuts, plus food aid & education | No tax | SEIU-UHW, progressive groups | Newsom, Becerra, Hilton, CA GOP, tech/business groups, some health & labor orgs |
| **41** | Tax audits / spending limit | Bars taxes that circumvent the 1979 state spending limit; state auditor must review new tax-funded programs (recommend 10% cuts); special taxes count toward the limit (possible refunds). **Conflicts with Prop 40** | No change | Anti-tax/business groups | Prop 40 backers, progressive groups |
| **42** | Ban wealth taxes | Bans new taxes on financial assets/wealth/personal property and retroactive taxes. **Conflicts with Prop 40** | No ban | Anti-tax/business groups | Prop 40 backers |
| **43** | Tax threshold | Citizen-initiated local special taxes need **2/3** instead of a simple majority (future measures only) | Simple majority stays | Howard Jarvis Taxpayers Assn., anti-tax groups | Local governments, transit/housing/education advocates |
| **44** | Clinic spending | Community clinics serving low-income patients must spend 90% of revenue on direct patient care; AG can fine violators | No mandate | SEIU-UHW | CA Dems and CA GOP, clinic associations |
| **45** | Environmental review | Speed up CEQA review/litigation for housing, schools, roads and other essential infrastructure | Current CEQA process stays | CA Chamber of Commerce, CA Hospital Assn., CA Council for Affordable Housing | CA Dem Party, Sierra Club California |

**Conflicting-measure rule**: If Prop 40 and Prop 41 or 42 both pass, the one with **more YES votes** wins and the other is void — so a voter who wants the billionaire tax should vote NO on 41 and 42, and one who opposes it should vote NO on 40 and YES on 41/42 if they also like those measures' broader limits. Explain this explicitly.

**Polling snapshot (CalMatters, Oct 2026)**: Prop 3 ~58% yes, Prop 42 ~54%, Prop 40 ~52%, Prop 41 ~51%, Prop 43 ~43%. Tax measures historically underperform early polling. Verify with a fresh search.

### 4d. Congressional Races

**CA-14 (Livermore, Pleasanton, Hayward, Union City, parts of Fremont and Dublin)** — Democrat vs. Democrat

| Candidate | Profile | Trump/Federal | Healthcare | Notes |
|-----------|---------|---------------|------------|-------|
| Aisha Wahab (D) | State senator; won the Aug 18 special and now holds the seat; CA Dem Party endorsed; progressive on housing, immigration, climate | Resist | Expand access | Running for the full term starting Jan 2027 |
| Melissa Hernandez (D) | Healthcare services director; former BART director; more moderate; affordability, reducing development barriers | Resist | Affordability focus | Lost the special 46.9%–53.1%; this is a rematch |

Since both are Democrats, match on progressive (Wahab) vs. moderate/pragmatic (Hernandez) and on the user's view of Wahab's record in the state Senate. Republican/independent voters often decide D-vs-D races — note that.

**Other Bay Area districts** (from the SOS certified list): CA-15 Kevin Mullin* (D) vs. Charles Hoelter (R); CA-16 Sam Liccardo* (D) vs. Peter Sundin Soulé (R); CA-17 Ro Khanna* (D) vs. Ritesh Tandon (R). For any other district, web-search `"California [N]th congressional district 2026 general election"`.

### 4e. State Legislature

- **Assembly District 16 (Tri-Valley/Pleasanton)**: Rebecca Bauer-Kahan* (D, incumbent since 2018) vs. Joseph A. Rubay (R, Alamo businessman) — rematch
- **Assembly District 20 (Hayward area)**: Liz Ortega* (D) vs. Patricia Muga (R)
- **Assembly District 24 (Fremont/Milpitas)**: Alex Lee* (D) vs. Max Hsia (R)
- **Assembly District 25 (San Jose)**: Ash Kalra* (D) vs. Himat Singh Bainiwal (R)
- **Senate District 10**: Scott Sakakihara (D) vs. Linda R. Price (R)

For any other district, search the SOS certified list (https://elections.cdn.sos.ca.gov/statewide-elections/2026-general/cert-list-candidates.pdf) or Ballotpedia.

---

### Local Races & Measures on the November 3 Ballot

**MANDATORY**: Before presenting any local measures, web-search for the user's specific county and city. Local measures are highly variable — a voter in San Jose sees completely different measures than one in Fremont or Pleasanton.

The data below covers **Alameda County and Tri-Valley cities** as a pre-loaded reference. For all other counties and cities, rely on web search results. Always present measures with: what it does, what it costs (if a tax), the threshold needed to pass, and the pro/con landscape.

#### Regional (Alameda, Contra Costa, San Mateo, Santa Clara, San Francisco)

**Measure RTM — Regional Transit Measure**
- **What it does**: Sales tax of 0.5% (Alameda, Contra Costa, San Mateo, Santa Clara) and 1% (San Francisco) for 14 years; ~$980M/year
- **Uses**: Prevent service cuts at BART, Caltrain, Muni, AC Transit, VTA, SamTrans as federal COVID aid runs out; some road repair; fiscal oversight/accountability requirements
- **Threshold**: Verify (citizen-initiated vs. agency-placed special tax determines majority vs. 2/3 — note Prop 43 would only affect future measures)
- **Pro**: Avoids drastic transit cuts and resulting traffic/pollution; regional coordination
- **Con**: Regressive sales tax; Tri-Valley and suburban voters pay but use BART less; concerns about transit agency spending and safety

#### Alameda County notes
- **No countywide DA race** — Jones Dickson won outright in June
- Special districts with contested seats: AC Transit, BART, EBMUD, East Bay Regional Park District (Ward 5: Olivia Sanwong* vs. Bruce Henry), Alameda County Water District
- City measures elsewhere: Oakland (Measure EE — strengthen mayor's role; FF — real property transfer tax; mayor race incl. Barbara Lee*), Berkeley (Measures U–AA), Alameda (L–N); school measures Dublin USD (I), San Lorenzo USD (J), Sunol Glen (K)

#### Pleasanton
- **Mayor**: Jack Balch* (incumbent, elected 2024) vs. Julie Testa (termed-out councilmember)
- **City Council District 1** (northwest; incumbent Jeff Nibert not running): Kathy Narum (former councilmember, Zone 7 board) vs. Vin Kruttiventi (2024 U.S. House candidate)
- **City Council District 3** (southwest): Jamie Yee (former PUSD trustee) vs. Reena Gupta (business owner, first-time candidate)
- **PUSD Board**: Area 2 — Laurie Walker* unopposed; Area 5 — open seat (verify whether anyone filed)
- **Measure HH — hotel tax**: Raises transient occupancy tax from 8% to 10% (July 2027) and 12% (July 2028); ~$1.4–2.8M/yr for general city services; simple majority. Pro: paid by visitors, not residents. Con: may make Pleasanton hotels less competitive

#### Livermore & Dublin
Contested city council/mayor races and Dublin USD Measure I are on the ballot — web-search `"Livermore November 2026 election"` / `"Dublin November 2026 election"` for candidates.

#### How to Find Your Exact Ballot
- **Voters Edge**: https://votersedge.org/ca (enter address for full personalized ballot)
- **ACVOTE Nov 3 election page**: https://acvote.alamedacountyca.gov/election-information/elections?id=260
- **Pleasanton-specific**: https://www.cityofpleasantonca.gov/our-government/elections-measures/
- **Official state Voter Information Guide**: https://voterguide.sos.ca.gov

## Step 5: Present Recommendations

Structure your output as follows:

```
## Your Voter Profile
[2-3 sentence synthesis of their stances]

## Race-by-Race Analysis

### Governor: Becerra vs. Hilton
**Best alignment**: [Candidate Name]
**Why**: [2-3 sentences tying their positions to user's stated values]
**Where they differ from you**: [honest note on mismatches]

### Other Statewide Offices
[One line per office: best alignment + reason]

### Congress — [District]
**Best alignment**: [Candidate Name]
**Why**: [2-3 sentences]

### State Legislature
[Best alignment per race]

## Propositions
| Prop | Your likely vote | Why (tied to your answers) |
[One row per prop; flag the 40/41/42 conflict and any props where the user's values pull both ways]

## Local Races & Measures
[From the web search in Step 1b]
```

## Step 6: Resources & Next Steps
Always close with:
- Registration check: https://voterstatus.sos.ca.gov (deadline Oct 19; same-day registration after that)
- Track your ballot: https://california.ballottrax.net
- Official Voter Information Guide: https://voterguide.sos.ca.gov
- CalMatters voter guide: https://calmatters.org/california-voter-guide-2026/
- KQED voter guide: https://www.kqed.org/voterguide
- Alameda County Registrar (drop boxes, vote centers): https://acvote.alamedacountyca.gov

## Tone & Style Guidelines
- Nonpartisan framing: present candidate positions factually, not editorially
- Do not advocate for one party over another
- For D-vs-D or R-vs-R races, focus on ideological and experience differences
- If user explicitly asks "who should I vote for?" or "how should I vote on Prop X?" — give a values-aligned recommendation grounded in their stated preferences, while noting it's their decision
- Keep analysis focused on user's stated priorities; don't pad with every issue
- Always note that candidate positions may have evolved; recommend primary sources

## Data Freshness Warning
This skill was updated October 5, 2026, from the SOS certified list of candidates (Aug 27, 2026), CalMatters, KQED, Pleasanton Weekly and Local News Matters. Always web-search for the latest polling, endorsements, debate news and local measure details before presenting recommendations. After November 3, results replace this guide — tell the user the election is over and offer to look up outcomes.
