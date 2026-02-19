import {
  ProfilePreferences,
  SuggestionCandidate,
  SuggestionResult,
  SustainabilitySignal,
} from "../models/entities";
import { scoreCandidate } from "./scoringService";

const MOCK_CANDIDATES: SuggestionCandidate[] = [
  {
    variantId: "v-rewe-bio-1",
    categoryKey: "joghurt",
    displayName: "ja! Bio Joghurt 3.8% 500g",
    brandName: "ja!",
    storeChainId: "rewe",
    isStoreBrand: true,
    attributes: { fatLevel: "3.8", grams: 500 },
  },
  {
    variantId: "v-skyr-1",
    categoryKey: "joghurt",
    displayName: "Skyr Natur 450g",
    brandName: "Arla",
    storeChainId: "edeka",
    attributes: { fatLevel: "0.2", grams: 450 },
  },
];

export function suggest(
  query: string,
  prefs: ProfilePreferences,
  storeChainId?: string,
): SuggestionResult[] {
  const normalized = query.trim().toLowerCase();
  const filtered = MOCK_CANDIDATES.filter((candidate) =>
    candidate.displayName.toLowerCase().includes(normalized),
  );

  const storeAdjusted = filtered.sort((a, b) => {
    const scoreA = Number(a.storeChainId === storeChainId) + Number(a.isStoreBrand);
    const scoreB = Number(b.storeChainId === storeChainId) + Number(b.isStoreBrand);
    return scoreB - scoreA;
  });

  return storeAdjusted.map((candidate) => {
    const signals: SustainabilitySignal[] = [
      {
        scopeType: "category",
        scopeId: candidate.categoryKey,
        climate: 62,
        health: candidate.displayName.includes("Skyr") ? 81 : 70,
        ethics: 56,
        animal: candidate.displayName.includes("Bio") ? 78 : 50,
        finance: candidate.isStoreBrand ? 77 : 55,
        confidence: 0.72,
        sourceType: "curated",
        reason: "Kategorie-/Mindestdaten",
      },
    ];

    return scoreCandidate(candidate, prefs, signals);
  });
}
