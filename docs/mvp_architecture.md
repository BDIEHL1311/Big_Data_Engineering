# Einkaufsapp MVP-Spezifikation (Bring! + Laufweg + Nachhaltigkeit)

## Sichtbare Annahmen
1. **[A1] Region**: Initial nur Deutschland (Store-Chains: REWE, EDEKA, Lidl, Aldi).
2. **[A2] Produktdaten**: Es gibt keine vollständige Produktdatenbank im MVP; wir starten hybrid (kuratiert + Crowd + Schätzung).
3. **[A3] Filialgenauigkeit**: Schema standardmäßig auf Chain-Ebene, filialspezifisch optional.
4. **[A4] Traffic**: MVP-Ziel bis 20k MAU, daher monolithisches Backend + Postgres reicht.
5. **[A5] Moderation**: Community-Reports werden zunächst asynchron manuell geprüft, kein vollautomatisches Trust-System.

## 1) MVP-Scope (1 Seite)
- Nutzerregistrierung (Email/Passwort), Login, JWT-Session.
- Onboarding mit 5 Nachhaltigkeits-Slidern (0–100), später im Profil editierbar.
- Mehrere Einkaufslisten je Nutzer.
- ListItem-Erfassung über Freitext + Vorschlagssuche.
- Supermarkt-Auswahl je Liste (Chain + optional Location).
- Schema-Auswahl je Liste; ListItems werden nach SchemaSection sortiert.
- Nachhaltigkeitslabels je Item: „Top Gesundheit“, „CO₂ hoch“, „Ethik kritisch“, „Günstigere Alternative“.
- Offline-first: lokale SQLite-Kopie; Sync bei Online-Reconnect.
- Community: Schema erstellen, Versionen veröffentlichen, up/downvote, report.
- Transparenz: jedes Nachhaltigkeitssignal mit `score`, `confidence`, `reason`, `estimated`.

## 2) User Stories + Akzeptanzkriterien
1. **Als Nutzer** möchte ich ein Konto erstellen, um Listen auf mehreren Geräten zu nutzen.  
   **AK**: Registrierung liefert JWT; Passwort gehasht; Login/Renew funktioniert.
2. **Als Nutzer** möchte ich beim Start meine Nachhaltigkeitsgewichte setzen.  
   **AK**: 5 Slider, Summe wird normalisiert, Speicherung im Profil.
3. **Als Nutzer** möchte ich „Joghurt“ eingeben und Vorschläge sehen.  
   **AK**: Vorschläge enthalten generische + markenspezifische Treffer inkl. Score/Confidence.
4. **Als Nutzer** möchte ich eine Liste einem Markt-Schema zuordnen.  
   **AK**: Items werden in Gang-Reihenfolge gruppiert und bei Änderungen neu sortiert.
5. **Als Community-User** möchte ich ein Schema verbessern.  
   **AK**: Änderung erzeugt neue SchemaVersion; bestehende Nutzer bleiben auf alter Version bis Update.
6. **Als Nutzer** möchte ich offline abhaken können.  
   **AK**: Lokale Änderung sofort sichtbar; später conflict-aware Sync (last-write-wins + server revision).

## 3) Architekturdiagramm (Text)
```
[React Native App]
  ├─ UI Screens (Onboarding, Lists, Add Item, Schema)
  ├─ Local SQLite + Outbox Queue
  ├─ Sync Engine (delta pull/push)
  └─ API Client (REST + JWT)
            |
            v
[Node.js/TypeScript API]
  ├─ Auth Module (JWT, bcrypt)
  ├─ List Module
  ├─ Store Schema Module (versioned)
  ├─ Suggestion + Scoring Module
  ├─ Community Moderation Module
  └─ Audit/Telemetry (PII-minimiert)
            |
            v
[PostgreSQL]
  ├─ Core transactional tables
  ├─ JSONB for score explanations
  └─ materialized aggregates (optional later)

[Optional Redis]
  └─ Caching: hot suggestions, schema lookups, rate limits
```

## 4) Datenmodell (Entities + Beziehungen)
- **User**(id, email, password_hash, created_at, last_login_at)
- **ProfilePreferences**(user_id PK/FK, climate_weight, health_weight, ethics_weight, animal_weight, finance_weight, updated_at)
- **ShoppingList**(id, user_id FK, title, store_chain_id FK nullable, store_location_id FK nullable, schema_version_id FK nullable, revision, updated_at)
- **ListItem**(id, list_id FK, text, quantity, unit, product_variant_id FK nullable, category_key, checked, position_hint, updated_at)
- **Product**(id, category_key, canonical_name, default_unit)
- **ProductVariant**(id, product_id FK, brand_id FK nullable, name, fat_level, size_value, size_unit, is_store_brand, metadata_json)
- **BrandManufacturer**(id, name, parent_company, country_code)
- **StoreChain**(id, name, country_code)
- **StoreLocation**(id, store_chain_id FK, name, city, postal_code)
- **StoreSchema**(id, store_chain_id FK, store_location_id FK nullable, name, created_by FK User, status)
- **SchemaVersion**(id, schema_id FK, version_number, created_by FK, changelog, is_active, created_at)
- **SchemaSection**(id, schema_version_id FK, section_key, label, sequence)
- **SustainabilityScore**(id, scope_type[category|brand|variant], scope_id, climate_score, health_score, ethics_score, animal_score, finance_score, confidence, source_type[curated|community|estimated], reason_json, valid_from)
- **PriceObservation**(id, store_chain_id FK, store_location_id FK nullable, product_variant_id FK, observed_price, currency, observed_at, source)
- **SchemaVote**(id, schema_id FK, user_id FK, vote_type)
- **SchemaReport**(id, schema_id FK, user_id FK, reason, status, created_at)

**Beziehungen**:
- User 1:1 ProfilePreferences; User 1:n ShoppingList.
- ShoppingList 1:n ListItem.
- StoreSchema 1:n SchemaVersion 1:n SchemaSection.
- Product 1:n ProductVariant; BrandManufacturer 1:n ProductVariant.
- SustainabilityScore referenziert Kategorie/Brand/Variant.

## 5) API-Design (REST)
### Auth
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`

### Profile
- `GET /v1/profile/preferences`
- `PUT /v1/profile/preferences`

### Lists
- `GET /v1/lists`
- `POST /v1/lists`
- `GET /v1/lists/:id`
- `PATCH /v1/lists/:id`
- `POST /v1/lists/:id/items`
- `PATCH /v1/lists/:id/items/:itemId`
- `POST /v1/lists/:id/sort-preview` (returns grouped sections)

### Stores/Schemas
- `GET /v1/store-chains`
- `GET /v1/schemas?storeChainId=&locationId=`
- `POST /v1/schemas`
- `POST /v1/schemas/:id/versions`
- `POST /v1/schemas/:id/votes`
- `POST /v1/schemas/:id/reports`

### Suggestions/Scoring
- `GET /v1/suggestions?q=joghurt&storeChainId=rewe&limit=10`
- `GET /v1/products/:variantId/score?listId=...`
- `GET /v1/products/:variantId/alternatives?storeChainId=...`

### Sync
- `GET /v1/sync/pull?cursor=...`
- `POST /v1/sync/push` (batched mutations with clientMutationId)

## 6) Scoring- & Ranking-Algorithmen
### Pseudocode
```pseudo
function suggestProducts(query, userPrefs, storeChain):
  tokens = normalize(query)                # lowercase, singular, umlaut-map
  candidates = searchCategoryAndVariants(tokens)

  if storeChain:
    candidates = boostStoreMatches(candidates, storeChain)
    candidates = boostPrivateLabels(candidates, storeChain)

  scored = []
  for c in candidates:
    baseline = loadCategoryScore(c.category)
    brandSig = loadBrandScore(c.brand)
    variantSig = loadVariantScore(c.variant)

    merged = weightedMerge(
      baseline=0.45,
      brand=0.30,
      variant=0.25,
      missingPolicy="renormalize"
    )

    finalScore = dot(normalizeWeights(userPrefs), merged.criteriaScores)
    confidence = combineConfidence([baseline.conf, brandSig.conf, variantSig.conf])
    reasons = topReasons(merged)

    priceBand = derivePriceBand(c.category, c.size, storeChain)
    alt = findCheaperSimilar(candidates, c, tolerance={fat_level, size±15%})

    scored.append({candidate: c, finalScore, confidence, reasons, priceBand, alternative: alt})

  return sortBy(scored, [finalScore desc, confidence desc, storeRelevance desc])
```

### Finanzmodul
- Preisrange = P25/P50/P75 aus `PriceObservation` je (store_chain, category, normalized_size).
- Bei <8 Beobachtungen: fallback auf chain-level median + Hinweis „niedrige Datendichte“.
- Günstigere Alternative: gleiches `category_key`, kompatible Eigenschaften (Fettstufe/Größe), niedriger erwarteter Preis.

### Beispiel (vereinfacht)
- Query: „Joghurt“, Gewichte: Klima 30, Gesundheit 35, Ethik 10, Tierwohl 10, Preis 15.
- Kandidat A (Eigenmarke Bio): Kriterien [70, 82, 60, 78, 74], Score ~75.3, Confidence 0.81.
- Kandidat B (Premium Marke): [64, 76, 55, 62, 45], Score ~64.8, Confidence 0.74.

## 7) Sync-Strategie Offline/Online
- Client speichert Listen/Items lokal in SQLite + `outbox_mutations`.
- Jede Mutation enthält: `entity`, `op`, `payload`, `clientMutationId`, `localTimestamp`, `baseRevision`.
- Online:
  1. Push Outbox in Reihenfolge.
  2. Server validiert Revision, schreibt Event, gibt neue Revision zurück.
  3. Pull Delta seit `cursor`.
- Konfliktregel MVP:
  - `ListItem.checked` → latest timestamp wins.
  - Textfelder → server wins, Client bekommt conflict marker.

## 8) Roadmap (MVP → V1 → V2)
- **MVP (0–3 Monate)**: Auth, Listen, Schema-Sortierung, Basis-Scoring, Offline Sync, Community Versioning + Votes.
- **V1 (3–6 Monate)**: bessere Moderation (Trust Score), Filial-spezifische Genauigkeit, Preisbeobachtungen verbessern, Push Notifications.
- **V2 (6–12 Monate)**: personalisierte Routenvorschläge, OCR/Barcode Scan, Partner-Integrationen, explainable AI upgrades.

## 9) Risiken & harte Trade-offs
- Produktdatenlücken führen zu „geschätzten“ Scores → Transparenzlabel Pflicht.
- Community-Schemata können inkonsistent sein → Versionierung + Voting priorisiert Qualität statt Perfektion.
- Offline-Konflikte sind unvermeidbar → klare MVP-Konfliktstrategie statt komplexem CRDT.
- REST statt GraphQL vereinfacht Betrieb/Monitoring im MVP, reduziert aber Flexibilität für komplexe Aggregationen.

## 10) Tech-Entscheidungen (festgelegt)
- **Mobile**: React Native (Expo) – schnell für MVP, breite Talentbasis.
- **Backend**: Node.js + TypeScript (Fastify) – hohe Dev-Geschwindigkeit, gute Typisierung.
- **DB**: PostgreSQL (Core), Redis optional für Cache/Rate-Limit.
- **Auth**: Email/Passwort + JWT (access + refresh), bcrypt/argon2 für Hashing.
- **API**: REST.
- **Offline-first**: SQLite + Outbox/Delta-Sync.
