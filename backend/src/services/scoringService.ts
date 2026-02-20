import {
  ProfilePreferences,
  SuggestionCandidate,
  SuggestionResult,
  SustainabilitySignal,
} from "../models/entities";

const clamp = (v: number, min = 0, max = 100): number => Math.max(min, Math.min(max, v));

const normalizeWeights = (prefs: ProfilePreferences): number[] => {
  const weights = [
    prefs.climateWeight,
    prefs.healthWeight,
    prefs.ethicsWeight,
    prefs.animalWeight,
    prefs.financeWeight,
  ];
  const sum = weights.reduce((acc, value) => acc + value, 0) || 1;
  return weights.map((weight) => weight / sum);
};

export function mergeSignals(signals: SustainabilitySignal[]): SustainabilitySignal {
  if (signals.length === 0) {
    return {
      scopeType: "category",
      scopeId: "fallback",
      climate: 50,
      health: 50,
      ethics: 50,
      animal: 50,
      finance: 50,
      confidence: 0.2,
      sourceType: "estimated",
      reason: "Keine Daten vorhanden, Kategorie-Basiswert geschätzt.",
    };
  }

  const weightByScope = {
    category: 0.45,
    brand: 0.3,
    variant: 0.25,
  };

  let divisor = 0;
  const merged = { climate: 0, health: 0, ethics: 0, animal: 0, finance: 0, confidence: 0 };

  for (const signal of signals) {
    const scopeWeight = weightByScope[signal.scopeType];
    divisor += scopeWeight;
    merged.climate += signal.climate * scopeWeight;
    merged.health += signal.health * scopeWeight;
    merged.ethics += signal.ethics * scopeWeight;
    merged.animal += signal.animal * scopeWeight;
    merged.finance += signal.finance * scopeWeight;
    merged.confidence += signal.confidence * scopeWeight;
  }

  return {
    scopeType: "variant",
    scopeId: "merged",
    climate: clamp(merged.climate / divisor),
    health: clamp(merged.health / divisor),
    ethics: clamp(merged.ethics / divisor),
    animal: clamp(merged.animal / divisor),
    finance: clamp(merged.finance / divisor),
    confidence: Math.max(0, Math.min(1, merged.confidence / divisor)),
    sourceType: signals.some((signal) => signal.sourceType === "estimated") ? "estimated" : "curated",
    reason: "Kombiniert aus Kategorie-, Marken- und Produktsignalen.",
  };
}

export function scoreCandidate(
  candidate: SuggestionCandidate,
  prefs: ProfilePreferences,
  signals: SustainabilitySignal[],
): SuggestionResult {
  const merged = mergeSignals(signals);
  const [wC, wH, wE, wA, wF] = normalizeWeights(prefs);

  const score =
    merged.climate * wC +
    merged.health * wH +
    merged.ethics * wE +
    merged.animal * wA +
    merged.finance * wF;

  const reasons = [
    merged.health > 70 ? "Top Gesundheit" : "Gesundheit mittel",
    merged.climate < 45 ? "CO₂ tendenziell hoch" : "Klima solide",
    merged.finance > 70 ? "Preis-Leistung gut" : "Preis-Leistung prüfen",
  ];

  return {
    candidate,
    score: Math.round(score * 10) / 10,
    confidence: merged.confidence,
    reasons,
    estimated: merged.sourceType === "estimated",
  };
}
