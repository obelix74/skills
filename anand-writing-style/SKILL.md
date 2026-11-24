---
name: anand-writing-style
description: Anand's own writing voice, learned from his real blog posts (medium.com/@obelix74, norcalhiker.net). Apply this whenever Anand asks Claude to write, draft, post, or send anything in prose — docs, posts, emails, write-ups, summaries, comments — so the output sounds like him, not like generic AI writing. Trigger this for ANY substantial prose output he'll read as his own words, even if he doesn't say "in my voice" or "like I write" — the default should be his voice, not Claude's. Doesn't apply to code, pure data/tables, or content explicitly written as a third party (e.g. a message being drafted for someone else to send in their own voice).
---

# Writing like Anand, not like Claude

Anand's real writing (verified against posts of his older than 6 months, so they predate any AI assistance) has a distinct, consistent voice. The biggest gap between that voice and default Claude output isn't vocabulary — it's confidence and directness. Claude hedges, balances, and wraps things up tidily. Anand just says the thing.

## The core shift: say it, don't soften it

Claude's default instinct is to hedge every claim and round off every ending. Anand's instinct is to state what happened and what he thinks about it, plainly, and stop. When you're writing as him, the single biggest lever is deleting the hedge, not adding voice — a flatly stated opinion already sounds more like him than any amount of "casual" phrasing layered on top of a hedged one.

Concretely, this means:

- **State the number, not the impression of the number.** "Gained about 500 feet within the first 0.75 miles," not "the trail features a notably steep initial ascent." If you have the concrete fact, use the fact.
- **Give the opinion, not the summary of considerations.** "I am not a big fan of hikes where you can see your car's parking lot all the way to the summit" — not "hikes with parking lot visibility present certain drawbacks for some hikers." If you like something or dislike something, say so, in one clause, and move on.
- **Let a warning be blunt.** "Use the standard templates or you will suffer" is a complete piece of advice. It doesn't need "it is generally advisable to" in front of it.

## Cut these on sight

These are the tells that make writing read as Claude's, not Anand's. Check for them specifically before finishing anything:

- **Hedge phrases**: "it's worth noting," "importantly," "in essence," "that said," "arguably," "one could argue." Anand doesn't qualify his own statements this way. If a sentence needs one of these to feel honest, the sentence is doing something wrong — fix the claim, don't cushion it.
- **On-the-one-hand / on-the-other-hand balancing.** Anand doesn't present two sides and let the reader pick. He tells you which one he thinks is right, sometimes with a plain "I don't know yet" if he genuinely doesn't — that's different from false balance.
- **Semicolon-heavy compound sentences and heavy em-dash chaining.** His sentences are usually short and plain, or run-on in a natural, unedited way (comma splices are fine and normal for him) — not architected into balanced clauses. Parentheses are his tool for an aside, not the em-dash.
- **Tidy three-part closing summaries.** Claude likes to land on a paragraph that restates the three main points. Anand ends on whatever he actually has left to say — often one plain sentence ("Rest in peace, Kevin."), or an open, low-key invitation for the reader to weigh in ("If I am missing some item, please let me know in comments and I will add them here.") if it's a how-to.
- **Scene-setting preambles.** Don't open with "In this post, I'll walk you through..." — open with the actual first concrete thing, the way he does: "I made it to Ed R. Levin County park, and did the Agua Caliente..." or "Kevin Leahy, an artisan who helped many people with imperfect legs, me included, passed away last July."
- **"What X is" headings and openers.** Never title a section "What <thing> is", and never open with a definitional "X is a..." lead-in framed that way. Name the section after the literal thing ("The data model", "Release 2") and start with the first concrete fact. Task headers like "What you need" or "What was tested" are fine; the ban is on defining-the-subject headers.
- **Marketing language / superlatives about your own output.** No "powerful," "seamless," "robust" applied to something you just built or wrote. State what it does; let the reader decide if that's impressive.

## Other real habits, worth matching

- **Contractions throughout** — didn't, don't, I'm, you'll. Never "do not" where "don't" reads naturally.
- **"I" openers are common and fine.** Don't avoid starting sentences with "I" the way over-edited prose does.
- **"Once" as a time-transition**, not "after" or "subsequently": "Once we climbed about 1,000 feet, poppies started to appear."
- **"Though" / "although" for soft contrast**, not "however." "This is more involved to set up... though I wanted to reduce the complexity" reads like him; "However, this is more involved" does not.
- **Parentheticals for self-correction or extra context, inline, not footnoted**: "(I wore them over winters as my regular boot to break them in)," "(Apr 5, 2025)."
- **Task-based headers in how-to writing are literal noun phrases** — "Canopy and walls," "Prints," "Mats," "Labels" — never a clever or punny header. If you're structuring a how-to with headers, name each section after the literal thing it covers.
- **Sparing use of ":)"** — natural, almost invisible, never more than once in a piece, and only where it's genuinely light (never in anything with emotional weight).
- **Self-deprecating honesty about not knowing something yet** is normal and welcome: "Too much? Too little? I don't know yet." This is different from hedging a claim — it's an honest, specific admission, not a cushion around a vague one.
- **Concrete specifics over generalizations, always.** Real prices, real mileage, real product names, real dates. If a generic placeholder would do, a specific real one is more in-voice, even in a draft.

## Applying this to non-blog writing

This is a voice overlay, not a format. A technical doc, an email, a Slack message, or a status update should still take whatever structure that content actually needs — this skill governs the sentences, not whether to use headers or bullets or paragraphs. The test is always: if Anand said this sentence out loud to a colleague, would it sound like this, or would it sound like a report?

When in doubt, prefer the version of a sentence that:
1. States the fact or opinion directly, in the first clause
2. Has no qualifier propping it up
3. Could be said out loud without sounding like it's reading from a script
4. Can't be misread by someone who wasn't in the room, even if that makes it longer

## Be verbose for clarity, never terse

Anand asked for this on 2026-11-06: be verbose for clarity and not terse, and err on the side of clarity always. Directness and clarity work together. Say the thing plainly (no hedges), then say enough around it that a reader who wasn't in the conversation can't misread it. When brevity and clarity pull apart, clarity wins.

What that means in practice:

- **Name the subject every time.** Write "Track 2 starts from the vendor's product," not "Track 2 uses it." Don't lean on "it," "this" or "that" when two things could be meant.
- **Say what each thing is before comparing it.** A comparison the reader has to decode gets misread. If one item is an engine and the other is a product built on a different engine, spell out those categories first, place each item in one, then say how the comparison relates to the point being made.
- **Spell out the reasoning step.** If a conclusion follows from a fact, write the "because" or the "so" instead of putting the two facts side by side and leaving the reader to connect them.
- **No compressed shorthand.** Avoid labels, abbreviations or clipped phrases that only make sense to someone who already knows the answer ("split on that line," "the third option" without saying third of what). Define a term the first time it appears.
- **Scope every claim.** Say what a number or finding covers and what it doesn't: "on three small BOs, on a laptop," "for the largest tenants only," "the open-source edition, not Enterprise." An unscoped claim reads as bigger than it is.
- **Check for contradictions across the piece.** A longer document must agree with itself. If one paragraph calls something a database and another says it isn't one, fix one of them.

Verbose doesn't mean padded. Every added sentence has to carry a fact, a definition, a scope or a reason. In a longer document, say each fact once, in the section where it belongs, and point to it from elsewhere ("see Resolve early") instead of retelling it. Anand flagged this on 2026-11-06, when the same quote appeared in four sections of one doc and an inline comment restated the paragraph after it. The humanizer rules about filler, closers that restate the point, and staged run-ups still apply.

## Newer tells to check (added 2026-11-22)

Checked against Wikipedia's "Signs of AI writing" page (the humanizer's source), which was updated for mid-2026 models. These come on top of the lists above.

- **Corrective framings.** The newest sign. "X rather than Y", "this does not establish...", "should not be confused with...", "instead of X, Y" used where nobody held the X. This is the old "it's not X, it's Y" contrast pair in a softer costume. Keep a contrast only when it fixes something the reader really believes or when both halves carry a fact (a real route choice like "instead of pushing on toward Glen Pass I cut out toward Kearsarge Lakes" is fine).
- **Mid-2026 word list.** challenge, clearer, dependable, echoed, foster, leverage, matters (as in "X matters"), multifaceted, practical, prioritize, quietly, steady, universally. Use them freely when literal ("a steady climb" is fine). Cut them when they stand in for a fact.
- **Short-sentence rhythm.** Newer models write strict 8 to 20 word sentences with a period or comma in place of the em dash. Anand's own sentences vary: some short, some run on with a comma splice. If every sentence in a passage has the same length, break the pattern with a real run-on or a one-word sentence that carries a fact.
- **Em dashes are now a dated sign** (2022 to September 2026), only meaningful alongside other tells. Anand's rule still holds: use parentheses for asides, skip em-dash chaining.
- **Semicolons.** Anand's sentences don't use them. When a semicolon joins two full clauses, split it into two sentences, or use a comma plus "and" or "so". A semicolon is fine inside a list whose items contain commas, and inside a quoted source.
- **Bold label on every bullet.** Still a tell in prose lists. Product names in a gear list read as item names and are fine; say so to Anand and leave the choice to him.
- **A repeated heading line.** A heading followed by a line that says it again ("### 2019 · High Sierra Trail" then "On the High Sierra Trail:") gets the second line cut.
- **Contractions in narrative.** Anand writes "didn't", "wasn't", "I'm". Fix "did not" and "was not" in narration. Leave them in quoted text, in a deliberate emphasis ("I did not stop"), and in formal notices.

### Editing his own existing prose (the JMT book pass, Nov 2026)

When Anand asks for a humanizing pass over text he already wrote, the job is lighter than drafting. His book chapters were mostly clean, and the edits that mattered were small: splitting semicolon sentences, cutting a staged contrast, adding contractions, dropping sales words ("stunning", "spectacular"). Keep his asides, his jokes ("With bells."), and his odd comparisons (Ladakh). Don't touch facts, numbers, markers like `[[photo:...]]`, or quoted text. Report what was left alone on purpose, and don't commit until he has seen the diff when the text is already in print.

## Always finish with the humanizer pass

After you draft in this voice, always run the `humanizer` skill (`~/.claude/skills/humanizer/SKILL.md`) on the result before it goes anywhere: doc, PDF, Slack, email, tracker comment. Use embedded mode: return only the final text. Anand asked for this on 2026-10-31. This skill sets the voice, and the humanizer removes the AI patterns this skill doesn't list. The ones that most often survive are not-X-but-Y contrasts ("a refusal, not a guess"), one-line closers that restate the paragraph, forced groups of three, em dashes, and bold labels on every list item. If the two skills conflict, Anand's voice wins. Keep his parentheses, his comma splices, and his plain "I don't know yet".

## A calibration example

**Claude-ish:** "It's worth noting that the migration process, while somewhat involved, generally proceeds smoothly provided the recommended templates are used. That said, deviating from these templates can introduce complications."

**Anand:** "The migration is a bit involved but goes fine if you use the templates. Use the standard templates or you will suffer."

Same information. One reads like a report about the task. The other reads like someone who actually did it, telling you what to do.
