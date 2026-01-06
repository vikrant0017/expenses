import { Stack } from "expo-router";
import {
  PaperProvider,
  MD3LightTheme as DefaultTheme,
} from "react-native-paper";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import * as React from "react";
import { KeyboardProvider } from "react-native-keyboard-controller";

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: "tomato",
    secondary: "yellow",
  },
};

const queryClient = new QueryClient();

export default function RootLayout() {
  return (
    <KeyboardProvider>
      <PaperProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <Stack>
            <Stack.Screen name="(tabs)" options={{ headerShown: false }} />

            <Stack.Screen
              name="(auth)/login"
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="(auth)/signup"
              options={{ headerShown: false }}
            />

            <Stack.Screen
              name="(expenses)/add-expense"
              options={{ headerTitle: "Add Expense" }}
            />
            <Stack.Screen
              name="(expenses)/edit-expense"
              options={{ headerTitle: "Edit Expense" }}
            />
            <Stack.Screen
              name="(expenses)/view-expense"
              options={{ headerTitle: "View Expense" }}
            />

            <Stack.Screen
              name="(groups)/group"
              options={{ headerTitle: "Group" }}
            />
            <Stack.Screen
              name="(groups)/create-group"
              options={{ presentation: "modal", headerTitle: "Create Group" }}
            />
            <Stack.Screen
              name="(groups)/join-group"
              options={{ presentation: "modal", headerTitle: "Join Group" }}
            />
          </Stack>
        </QueryClientProvider>
      </PaperProvider>
    </KeyboardProvider>
  );
}
