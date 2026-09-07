# CineWatch TV V1 API & Content Rights Qualification Register 001

**Document ID:** `CWTV-V1-RIGHTS-REGISTER-001`
**Product:** CineWatch TV
**Status:** ACTIVE / INITIAL QUALIFICATION
**Revision:** 001
**Date:** 2026-09-07
**Scope:** APIs, networks, studios, media providers, rights holders, and content/data sources

---

## 1. Purpose

This register records the permission and licensing state of external sources used or considered by CineWatch TV.

It is separate from the product blueprint because provider terms, contacts, and verdicts can change independently from product architecture.

The register does not treat a provider API key as permission to reproduce all underlying content.

Two separate gates are tracked:

1. **Provider/API permission**
2. **Underlying-content rights**

Where necessary, both must be satisfied before CineWatch enables a capability.

---

## 2. Release lifecycle used in provider enquiries

### V1 — Development

Approximate duration: 6 months.

- private;
- initially four authorized testers;
- no commercial activity;
- development/evaluation use.

### V2 — Production + Research

Approximate duration: 12 months.

- production-grade;
- still noncommercial;
- provider confirmation required where developer terms distinguish development from production;
- AI/ML research only where relevant search/inference/training permissions are explicitly qualified.

### V3 — Commercial

Future commercial operation after commercial/API/content rights are qualified.

---

## 3. Permission dimensions

Every provider should eventually have an explicit verdict for:

- V1 development;
- V2 noncommercial production;
- V3 commercial;
- API access;
- metadata display;
- full text/content display;
- image display;
- video embed;
- video hosting;
- link/provider handoff;
- caching;
- persistent storage;
- territory restrictions;
- attribution;
- branding;
- quota/rate limits;
- SLA/support;
- AI search;
- AI inference;
- AI training;
- underlying-content rights responsibility.

Unknown is not approval.

---

## 4. Status vocabulary

Contact workflow:

- `CONTACT_NOT_STARTED`
- `CONTACT_SENT`
- `ACKNOWLEDGED`
- `UNDER_REVIEW`
- `RESPONSE_RECEIVED`

Permission/result states:

- `QUALIFIED`
- `PENDING_PROVIDER_RESPONSE`
- `DEVELOPMENT_APPROVED`
- `V2_APPROVED`
- `COMMERCIAL_PATH_AVAILABLE`
- `CONDITIONAL`
- `CONTRACT_REQUIRED`
- `RIGHTSHOLDER_PERMISSION_REQUIRED`
- `RIGHTS_PENDING`
- `AI_SEARCH_ALLOWED`
- `AI_INFERENCE_ALLOWED`
- `AI_TRAINING_ALLOWED`
- `AI_TRAINING_PROHIBITED`
- `DECLINED`
- `DEFERRED`

---

## 5. Initial outreach checkpoint

Exactly five initial enquiries were sent on **2026-09-07 CAT**.

No additional provider outreach is included in this initial register revision.

| # | Provider / Rights Group | Public contact used | Sent (CAT) | Current contact status |
|---|---|---|---|---|
| 1 | TMDB | `sales@themoviedb.org` | 2026-09-07 08:16 | `CONTACT_SENT` |
| 2 | The Church of Jesus Christ of Latter-day Saints — Intellectual Property Office | `permissions@ChurchofJesusChrist.org` | 2026-09-07 08:17 | `CONTACT_SENT` |
| 3 | Genius | `api-sales@genius.com` | 2026-09-07 08:18 | `CONTACT_SENT` |
| 4 | Musixmatch | `sales@musixmatch.com` | 2026-09-07 08:18 | `CONTACT_SENT` |
| 5 | Warner Bros. Discovery | `clipandstilldept@wbd.com` with published WBD licensing CC contacts | 2026-09-07 08:18 | `CONTACT_SENT` |

Correspondence remains in the authorized Gmail account. Confidential replies, negotiated pricing, contracts, credentials, or private commercial terms SHALL NOT be copied into a public repository.

---

## 6. Provider qualification records

### 6.1 TMDB

**Provider:** The Movie Database (TMDB)
**Primary role considered:** movie/TV/person metadata, images, credits, seasons/episodes, videos, recommendations, reviews, watch-provider information
**Delivery:** HTTPS API + image CDN
**Initial status:** `CONTACT_SENT`

#### Public-terms snapshot

Current TMDB public documentation states that the developer API is free for noncommercial purposes with attribution and that a commercial service is available through sales. TMDB also states that it does not claim ownership of all images/data exposed by the API.

This snapshot is provisional. Provider correspondence and any executed agreement govern CineWatch-specific use.

#### Questions awaiting provider verdict

- V1 private development eligibility;
- V2 non-revenue production/research eligibility;
- V3 commercial licensing path;
- cache/persistent-storage rules;
- images and review display;
- watch-provider use;
- CineWatch canonical crosswalk usage;
- territory/rate-limit requirements;
- AI search;
- AI inference;
- AI training.

#### Current normalized verdict

| Dimension | State |
|---|---|
| V1 development | `PENDING_PROVIDER_RESPONSE` |
| V2 noncommercial production | `PENDING_PROVIDER_RESPONSE` |
| V3 commercial | `COMMERCIAL_PATH_AVAILABLE` / details pending |
| Metadata display | public developer terms appear available, exact CineWatch use pending |
| Images | attribution/rightsholder caveats apply; exact CineWatch use pending |
| Watch providers | pending |
| Cache/persistence | pending |
| AI search | pending |
| AI inference | pending |
| AI training | pending; default not training-eligible |
| Underlying media rights | separate from TMDB API permission |

---

### 6.2 The Church of Jesus Christ of Latter-day Saints

**Rights group:** Intellectual Property Office
**Primary role considered:** official links and authorized embeds for General Conference, Gospel Media, Church videos, music, Gospel Stream, official channels, and related metadata
**Preferred CineWatch model:** link/embed first; no assumed rehosting
**Initial status:** `CONTACT_SENT`

#### Public-terms snapshot

The Church maintains a formal permissions process for Church-owned material. Public permissions guidance states that many materials have personal/noncommercial uses, while broader organizational/project uses may require permission. The Intellectual Property Office publishes a permissions contact and an approximate response time of 45 days for requests.

This does not establish CineWatch permission by itself.

#### Questions awaiting provider verdict

- direct links;
- official player embeds;
- official YouTube embeds;
- General Conference sessions/talks;
- music and musical performances;
- Gospel Media/Gospel Stream;
- title/speaker/date/language/duration metadata;
- thumbnails/cards;
- any public API/feed/developer interface;
- cache/persistence;
- AI search;
- AI inference;
- AI training;
- future V3 commercial treatment and branding.

#### Current normalized verdict

| Dimension | State |
|---|---|
| V1 development | `PENDING_PROVIDER_RESPONSE` |
| V2 noncommercial production | `PENDING_PROVIDER_RESPONSE` |
| V3 commercial | `PENDING_PROVIDER_RESPONSE` |
| Direct links | likely possible but CineWatch-specific verdict pending |
| Official embeds | `PENDING_PROVIDER_RESPONSE` |
| Media hosting | not assumed |
| Metadata display | pending |
| Images/thumbnails | pending |
| AI search | pending |
| AI inference | pending |
| AI training | pending; default not training-eligible |
| Endorsement | CineWatch SHALL NOT imply Church sponsorship or endorsement |

---

### 6.3 Genius

**Provider:** Genius
**Primary role considered:** music metadata, artists, songs, annotations, and script/transcript-like resources where Genius exposes them
**Delivery:** OAuth2/HTTPS API and Genius web resources
**Initial status:** `CONTACT_SENT`

#### Public-terms snapshot

Genius API documentation displayed during qualification states that commercial use of the Genius API is not allowed without a license and directs commercial users to API sales.

The presence of lyrics, annotations, scripts, or transcript-like text on Genius does not by itself establish underlying-content redistribution or AI-training rights for CineWatch.

#### Questions awaiting provider verdict

- V1 private development;
- V2 non-revenue production;
- V3 commercial licensing;
- metadata versus full-content display;
- lyrics rights;
- annotations;
- script/transcript content;
- caching/storage;
- attribution/link-back;
- AI search;
- AI inference;
- AI training;
- underlying rightsholder responsibilities.

#### Current normalized verdict

| Dimension | State |
|---|---|
| V1 development | `PENDING_PROVIDER_RESPONSE` |
| V2 noncommercial production | `PENDING_PROVIDER_RESPONSE` |
| V3 commercial | `CONTRACT_REQUIRED` based on public docs; details pending |
| Metadata | pending |
| Lyrics | pending / content rights may be separate |
| Scripts/transcripts | `RIGHTSHOLDER_PERMISSION_REQUIRED` unless provider explicitly proves otherwise |
| Caching/persistence | pending |
| AI search | pending |
| AI inference | pending |
| AI training | pending; default not training-eligible |

---

### 6.4 Musixmatch

**Provider:** Musixmatch
**Primary role considered:** soundtrack/music metadata, lyrics where licensed, synchronized lyrics where separately permitted, translations, provider links
**Delivery:** authenticated HTTPS API
**Initial status:** `CONTACT_SENT`

#### Public-terms snapshot

Current Musixmatch documentation states that the API is available to selected partners and individual developers, directs lyric-display users to pricing/custom enquiry, and labels the published developer terms as noncommercial. Commercial/business users are directed to sales.

#### Questions awaiting provider verdict

- V1 development;
- V2 non-revenue production;
- V3 commercial arrangement;
- lyric display;
- translations;
- synchronized lyric use;
- film/TV companion-context use;
- synchronization alongside audiovisual playback;
- territory-level restrictions;
- caching/storage;
- attribution/tracking;
- AI search;
- AI inference;
- AI training.

#### Current normalized verdict

| Dimension | State |
|---|---|
| V1 development | `PENDING_PROVIDER_RESPONSE` |
| V2 noncommercial production | `PENDING_PROVIDER_RESPONSE` |
| V3 commercial | commercial/custom path publicly available; details pending |
| Music metadata | pending |
| Lyrics | license/product terms required |
| Synced lyrics | pending |
| Film/TV synchronization | no assumption; explicit verdict required |
| Caching/persistence | pending |
| AI search | pending |
| AI inference | pending |
| AI training | pending; default not training-eligible |

---

### 6.5 Warner Bros. Discovery

**Rights group:** Warner Bros. Discovery
**Relevant property families considered:** Warner Bros., HBO/Max, Discovery, Cartoon Network, Adult Swim, and related WBD film/television properties
**Primary role considered:** official metadata/links, trailers, BTS, interviews, events, promotional media, licensed clips/stills, production craft evidence
**Initial status:** `CONTACT_SENT`

#### Public-terms snapshot

WBD publishes a formal Clip & Still Licensing process. Its published licensing information requests detailed purpose, titles, clip/still usage, distribution media, territory, term, and ownership/contact information. It states that license fees depend on use and publishes separate routing for some property families, including HBO/Max.

This does not establish a general CineWatch API or broad content license.

#### Questions awaiting provider verdict

- V1 promotional metadata/link/embed use;
- V2 non-revenue production;
- V3 commercial licensing;
- API/syndication/partner feeds;
- official YouTube embeds;
- posters/stills/promotional photography;
- BTS/interviews/events;
- short clips;
- direct provider handoff;
- territory/brand requirements;
- cache/storage;
- AI search;
- AI inference;
- AI training;
- startup/evaluation arrangements.

#### Current normalized verdict

| Dimension | State |
|---|---|
| V1 development | `PENDING_PROVIDER_RESPONSE` |
| V2 noncommercial production | `PENDING_PROVIDER_RESPONSE` |
| V3 commercial | licensing path exists for clips/stills; broader CineWatch use pending |
| Metadata/API feed | pending |
| Official links | pending CineWatch-specific treatment |
| Embeds | pending |
| Clips/stills | formal licensing path exists; no CineWatch license yet |
| Cache/persistence | pending |
| AI search | pending |
| AI inference | pending |
| AI training | pending; default not training-eligible |

---

## 7. Immediate next outreach policy

No additional emails are sent as part of this revision.

When outreach resumes, the intended operating policy is:

- send in groups of five;
- separate batches by approximately twelve hours;
- review replies before increasing dependency on a provider;
- preserve one consistent V1/V2/V3 lifecycle explanation;
- tailor content/use questions per provider;
- never imply that noncommercial status overrides provider terms.

Future high-priority candidates include major network/studio groups, metadata services, music providers, cinema/showtime providers, and rightsholder/creator partnerships.

---

## 8. Evidence and confidentiality

Public provider terms may be cited in future revisions.

Private email responses may be summarized into normalized engineering verdicts, but the repository SHOULD NOT contain:

- confidential contracts;
- negotiated private pricing;
- access tokens;
- API keys;
- phone numbers not already public;
- private provider contacts supplied under confidence;
- personal identity documents;
- payment details.

Where a provider response becomes material, store an internal evidence reference outside public source control and record only the normalized verdict required by engineering.

---

## 9. Change protocol

A provider record changes only when one of the following occurs:

- provider reply;
- new agreement;
- provider terms change;
- API plan changes;
- rights-holder clarification;
- CineWatch use case changes;
- V1/V2/V3 lifecycle changes.

Every material change should update:

- status;
- evidence date;
- affected permission dimensions;
- engineering consequences;
- next review date.

---

## 10. Initial register lock

At Revision 001:

- five enquiries are confirmed sent;
- no provider reply has yet been normalized into an approval;
- unknown permission remains unknown;
- unknown AI-training permission remains not training-eligible;
- no API access is treated as automatic copyright permission;
- no public download or embed availability is treated as ownership.


---

## 11. Public terms evidence references

These public references supported the initial public-terms snapshot and should be rechecked when terms change or before a material integration decision:

- TMDB API FAQ: `https://developer.themoviedb.org/docs/faq`
- Church permissions portal: `https://permissions.churchofjesuschrist.org/`
- Genius API documentation: `https://docs.genius.com/`
- Musixmatch API getting started: `https://musixmatch.mintlify.app/getting-started`
- WBD Clip & Still Licensing information: `https://assets.www.warnerbros.com/drupal-root/public/licensing_submission_form_wbd.pdf`

Public references are evidence, not substitutes for provider-specific written verdicts.
