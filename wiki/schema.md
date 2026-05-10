# Wiki Schema

This file defines the structure and conventions for the Tim Keller Sermons knowledge base wiki. It is generated on first compile and co-evolved between human and LLM on subsequent runs.

**Human:** You can edit this file to rename topics, merge them, add conventions, or change the article structure. The compiler will respect your changes on the next run.

**Compiler:** Read this file before classifying sources. Follow its conventions. Add new topics here when discovered. Never remove topics without human approval.

## Topics

- `apologetics`: How Keller engages secular objections — exclusivity, absolutism, the afterlife — and his inside-out apologetic method
- `death-and-resurrection`: The bodily resurrection as the center of Christian hope; Easter preaching; what awaits believers
- `faith-and-doubt`: Intellectual and spiritual doubt as normal parts of the Christian life; how Keller ministers to skeptics and doubters
- `hope`: Christian hope vs. optimism; the three pillars of Christian joy; the new creation as physical restoration, not escape
- `identity`: The self in culture; the secular project of self-authorship; the gospel as giving identity before performance
- `idolatry`: Making good things into ultimate things; the broken-cistern structure; how idols enslave and the gospel displaces them
- `justice-and-mercy`: Social justice, shalom, care for the poor; how the gospel grounds justice without moralism
- `marriage-and-family`: Marriage, romantic love, singleness, parenting; the theological anthropology of relationships
- `prayer`: Lament, petition, listening, contemplation; how the gospel changes the grammar of prayer
- `salvation-and-justification`: Justification by faith; imputed righteousness; the forensic and relational dimensions of being made right with God
- `sanctification`: The process of becoming more like Christ; how growth happens through grace, not striving; the role of suffering
- `sin`: The anatomy of sin — idolatry, self-deception, addiction; moralism as another form of sin; the doctrine of sin as prerequisite for the gospel
- `spiritual-warfare`: The cosmic battle; the armor of God; how the Christian stands in spiritual conflict
- `suffering-and-lament`: Why God allows suffering; lament as a form of faith; the psalms of darkness; suffering's role in formation
- `the-bible`: Scripture's authority and sufficiency; Keller's method of expository preaching; the unity of the Old and New Testaments
- `the-church`: Gathered and scattered; the countercultural community; why you can't be a Christian without the church
- `the-cross-and-atonement`: What happened at Golgotha; penal substitution and other atonement models; the cross as the revelation of God's character
- `the-gospel-and-grace`: The content of the gospel; grace vs. moralism; how the gospel is different from religion
- `work-and-vocation`: Work as participation in God's creation; calling and career; rest and sabbath; the theology of cultural engagement

## Concepts

Cross-cutting patterns that span 3+ topic articles. Interpretive, not just factual.

- `the-two-ways-of-being-lost`: The elder-brother/younger-brother dynamic — both moralism and license are forms of being lost; only grace addresses both — connects [sin, idolatry, salvation-and-justification, the-gospel-and-grace, apologetics, faith-and-doubt, sanctification]
- `the-cultural-diagnostic-move`: Keller's three-step apologetic method: enter the secular aspiration → expose its internal tension → offer the gospel as resolution — connects [apologetics, idolatry, identity, hope, work-and-vocation, marriage-and-family, sin]
- `suffering-as-the-refinery`: Suffering is not an obstacle to transformation but its primary mechanism; the furnace forms faith, compassion, and hope that comfort cannot — connects [suffering-and-lament, hope, sanctification, prayer, faith-and-doubt, death-and-resurrection, spiritual-warfare]

## Article Structure

Each topic article follows this format, using these custom sections configured for Tim Keller Sermons:

- **Summary** [coverage] — standalone briefing, 2-4 paragraphs; someone reading only this should understand Keller's position
- **Core Argument** [coverage] — Keller's central theological move on this topic; the logic of his position
- **Key Sermons** [coverage] — table with title, date, scripture, series
- **Scripture Texts** [coverage] — the biblical passages Keller returns to most frequently on this topic, with brief description of how he uses each
- **Cultural Hooks** [coverage] — secular writers, films, cultural phenomena Keller uses as entry points or illustrations
- **Representative Quotes** [coverage] — direct quotes from sermons, with source attribution
- **Related Topics** [coverage] — links to other topics in this wiki, with brief explanation of connection
- **Sources** — backlinks to every raw sermon file that contributed to the article

Coverage tags: `[coverage: high — N sources]`, `[coverage: medium — N sources]`, `[coverage: low — N sources]`

## Naming Conventions

- Topic slugs: lowercase-kebab-case (e.g., `the-gospel-and-grace`, `suffering-and-lament`)
- Files: `{topic-slug}.md` in `topics/`
- Concept slugs: lowercase-kebab-case (e.g., `the-two-ways-of-being-lost`)
- Concept files: `{concept-slug}.md` in `concepts/`
- Dates: YYYY-MM-DD format in frontmatter; human-readable (e.g., "March 27, 2005") in tables
- Links: Markdown `[Title](slug.md)` style (not Obsidian wikilinks)

## Cross-Reference Rules

- Each topic article should link to 4-6 related topics in its Related Topics section
- Concept articles link back to all contributing topics in their Sources section
- When Keller's argument in one topic directly depends on another (e.g., hope depends on death-and-resurrection), note this in both Related Topics sections

## Evolution Log

- 2026-04-30: Scripture-refs compile — all 19 topics updated with dates from new Scripture metadata fields; ~130 missing Key Sermons dates filled in; ~130 newly-discovered sermons added to Sources sections across all topics
- 2026-04-15: Initial schema generated from 19 topics, 3 concepts — first compile of full sermon catalog (1,550 sermons)
