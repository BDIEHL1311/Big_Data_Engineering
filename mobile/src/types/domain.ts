export type SustainabilityLabel =
  | "Top Gesundheit"
  | "CO₂ hoch"
  | "Ethik kritisch"
  | "Günstigere Alternative verfügbar";

export interface ListItemViewModel {
  id: string;
  name: string;
  quantity: string;
  section: string;
  checked: boolean;
  labels: SustainabilityLabel[];
}

export interface SchemaSection {
  key: string;
  label: string;
  sequence: number;
}
