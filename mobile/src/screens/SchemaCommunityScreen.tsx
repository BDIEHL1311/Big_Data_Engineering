import React from "react";
import { View, Text } from "react-native";

const schemaRows = [
  { name: "REWE Standard", version: "v1.4", votes: 124, quality: "Stabil" },
  { name: "REWE Köln Innenstadt", version: "v0.9", votes: 37, quality: "In Prüfung" },
];

export function SchemaCommunityScreen() {
  return (
    <View style={{ padding: 16, gap: 10 }}>
      <Text style={{ fontSize: 22, fontWeight: "700" }}>Community-Schemata</Text>
      {schemaRows.map((schema) => (
        <View key={schema.name} style={{ backgroundColor: "#f7f7f7", padding: 12, borderRadius: 8 }}>
          <Text style={{ fontWeight: "600" }}>{schema.name}</Text>
          <Text>{schema.version} • Votes: {schema.votes}</Text>
          <Text>Status: {schema.quality}</Text>
        </View>
      ))}
    </View>
  );
}
