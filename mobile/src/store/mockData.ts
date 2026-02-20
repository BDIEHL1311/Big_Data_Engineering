import { ListItemViewModel, SchemaSection } from "../types/domain";

export const schemaSections: SchemaSection[] = [
  { key: "obst", label: "Obst & Gemüse", sequence: 1 },
  { key: "backwaren", label: "Backwaren", sequence: 2 },
  { key: "milch", label: "Milchprodukte", sequence: 3 },
  { key: "tiefkuehl", label: "Tiefkühl", sequence: 4 },
  { key: "getraenke", label: "Getränke", sequence: 5 },
];

export const listItems: ListItemViewModel[] = [
  {
    id: "1",
    name: "Banane",
    quantity: "6 Stk",
    section: "obst",
    checked: false,
    labels: ["Top Gesundheit"],
  },
  {
    id: "2",
    name: "ja! Bio Joghurt",
    quantity: "2 x 500g",
    section: "milch",
    checked: false,
    labels: ["Top Gesundheit", "Günstigere Alternative verfügbar"],
  },
  {
    id: "3",
    name: "Pizza TK",
    quantity: "1 Pack",
    section: "tiefkuehl",
    checked: true,
    labels: ["CO₂ hoch"],
  },
];
