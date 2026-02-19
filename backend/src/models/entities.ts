export type ScoreSourceType = "curated" | "community" | "estimated";
export type ScopeType = "category" | "brand" | "variant";

export interface ProfilePreferences {
  userId: string;
  climateWeight: number;
  healthWeight: number;
  ethicsWeight: number;
  animalWeight: number;
  financeWeight: number;
}

export interface SuggestionCandidate {
  variantId: string;
  categoryKey: string;
  displayName: string;
  brandName?: string;
  storeChainId?: string;
  isStoreBrand?: boolean;
  attributes?: {
    fatLevel?: string;
    grams?: number;
  };
}

export interface SustainabilitySignal {
  scopeType: ScopeType;
  scopeId: string;
  climate: number;
  health: number;
  ethics: number;
  animal: number;
  finance: number;
  confidence: number;
  sourceType: ScoreSourceType;
  reason: string;
}

export interface SuggestionResult {
  candidate: SuggestionCandidate;
  score: number;
  confidence: number;
  reasons: string[];
  estimated: boolean;
  priceBand?: {
    p25: number;
    p50: number;
    p75: number;
    currency: string;
  };
  cheaperAlternativeVariantId?: string;
}
