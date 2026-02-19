import React, { useState } from "react";
import { View, Text, TextInput, Pressable } from "react-native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useNavigation } from "@react-navigation/native";
import { fetchSuggestions, SuggestionDto } from "../api/client";
import { listItems, schemaSections } from "../store/mockData";
import { RootStackParamList } from "../App";

type NavigationProp = NativeStackNavigationProp<RootStackParamList, "ShoppingList">;

export function ShoppingListScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [query, setQuery] = useState("Joghurt");
  const [suggestions, setSuggestions] = useState<SuggestionDto[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadSuggestions = async () => {
    setError(null);
    try {
      const data = await fetchSuggestions(query, "rewe");
      setSuggestions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    }
  };

  return (
    <View style={{ padding: 16 }}>
      <Text style={{ fontSize: 22, fontWeight: "700", marginBottom: 12 }}>Liste: Woche (REWE Standard)</Text>
      <View style={{ flexDirection: "row", gap: 8, marginBottom: 12 }}>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Produkt suchen"
          style={{ flex: 1, borderColor: "#ccc", borderWidth: 1, borderRadius: 8, padding: 8 }}
        />
        <Pressable onPress={loadSuggestions} style={{ backgroundColor: "#0a7", padding: 10, borderRadius: 8 }}>
          <Text style={{ color: "white" }}>Suchen</Text>
        </Pressable>
      </View>

      {error ? <Text style={{ color: "#b00020", marginBottom: 8 }}>{error}</Text> : null}
      {suggestions.slice(0, 2).map((s) => (
        <Text key={s.candidate.variantId} style={{ marginBottom: 4 }}>
          Vorschlag: {s.candidate.displayName} ({s.score}/100, Conf {Math.round(s.confidence * 100)}%)
        </Text>
      ))}

      <View style={{ flexDirection: "row", gap: 8, marginVertical: 12 }}>
        <Pressable onPress={() => navigation.navigate("Onboarding")} style={{ backgroundColor: "#eee", padding: 8, borderRadius: 8 }}>
          <Text>Zu Präferenzen</Text>
        </Pressable>
        <Pressable onPress={() => navigation.navigate("Community")} style={{ backgroundColor: "#eee", padding: 8, borderRadius: 8 }}>
          <Text>Community</Text>
        </Pressable>
      </View>

      {schemaSections.map((section) => {
        const items = listItems.filter((item) => item.section === section.key);
        if (items.length === 0) {
          return null;
        }

        return (
          <View key={section.key} style={{ marginBottom: 14 }}>
            <Text style={{ fontSize: 16, fontWeight: "600" }}>{section.label}</Text>
            {items.map((item) => (
              <View
                key={item.id}
                style={{ paddingVertical: 8, borderBottomColor: "#E8E8E8", borderBottomWidth: 1 }}
              >
                <Text>
                  {item.checked ? "✅" : "⬜️"} {item.name} ({item.quantity})
                </Text>
                <Text style={{ color: "#2f6f3e" }}>{item.labels.join(" • ")}</Text>
              </View>
            ))}
          </View>
        );
      })}
    </View>
  );
}
