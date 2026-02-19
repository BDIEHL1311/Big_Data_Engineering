import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { OnboardingScreen } from "./screens/OnboardingScreen";
import { ShoppingListScreen } from "./screens/ShoppingListScreen";
import { SchemaCommunityScreen } from "./screens/SchemaCommunityScreen";

export type RootStackParamList = {
  Onboarding: undefined;
  ShoppingList: undefined;
  Community: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="ShoppingList">
        <Stack.Screen name="ShoppingList" component={ShoppingListScreen} options={{ title: "Einkauf" }} />
        <Stack.Screen name="Onboarding" component={OnboardingScreen} options={{ title: "Präferenzen" }} />
        <Stack.Screen name="Community" component={SchemaCommunityScreen} options={{ title: "Schemata" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
