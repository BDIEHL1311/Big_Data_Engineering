import React from "react";
import { View, Text } from "react-native";

const criteria = ["Klima", "Gesundheit", "Ethik", "Tierwohl", "Preis-Leistung"];

export function OnboardingScreen() {
  return (
    <View style={{ padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 22, fontWeight: "700" }}>Deine Nachhaltigkeits-Prioritäten</Text>
      {criteria.map((criterion) => (
        <View key={criterion} style={{ padding: 12, backgroundColor: "#F5F5F5", borderRadius: 8 }}>
          <Text>{criterion}: 50</Text>
          <Text style={{ color: "#666" }}>Slider-Komponente (0–100) wird hier eingebunden.</Text>
        </View>
      ))}
    </View>
  );
}
