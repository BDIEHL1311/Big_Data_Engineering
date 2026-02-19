export interface SuggestionDto {
  candidate: {
    variantId: string;
    displayName: string;
  };
  score: number;
  confidence: number;
  reasons: string[];
  estimated: boolean;
}

export async function fetchSuggestions(query: string, storeChainId = "rewe"): Promise<SuggestionDto[]> {
  const baseUrl = process.env.EXPO_PUBLIC_API_BASE;
  if (!baseUrl) {
    throw new Error("EXPO_PUBLIC_API_BASE ist nicht gesetzt");
  }

  const url = `${baseUrl}/v1/suggestions?q=${encodeURIComponent(query)}&storeChainId=${encodeURIComponent(
    storeChainId,
  )}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API Fehler: ${response.status}`);
  }

  const json = (await response.json()) as { data: SuggestionDto[] };
  return json.data;
}
