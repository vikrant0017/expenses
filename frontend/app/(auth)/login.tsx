import React, { useState } from "react";
import { View, StyleSheet, ScrollView, Pressable } from "react-native";
import { TextInput, Button, Text, Surface } from "react-native-paper";
import { signIn } from "@/services/auth";
import { Link, router } from "expo-router";

export default function SignInScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleLogin = async () => {
    try {
      const _user = await signIn({
        username,
        password,
      });
      router.replace("/(tabs)");
    } catch (e) {
      setErrorMsg((e as Error).message);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Surface style={styles.surface} elevation={1}>
        <Text variant="headlineMedium" style={styles.title}>
          Login
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Login In to get started
        </Text>

        {errorMsg && (
          <Text variant="bodyMedium" style={{ color: "red", marginBottom: 16 }}>
            {errorMsg}
          </Text>
        )}

        <TextInput
          label="Username"
          value={username}
          onChangeText={setUsername}
          mode="outlined"
          style={styles.input}
          left={<TextInput.Icon icon="account" />}
        />

        <TextInput
          label="Password"
          value={password}
          onChangeText={setPassword}
          mode="outlined"
          secureTextEntry={!showPassword}
          style={styles.input}
          left={<TextInput.Icon icon="lock" />}
          right={
            <TextInput.Icon
              icon={showPassword ? "eye-off" : "eye"}
              onPress={() => setShowPassword(!showPassword)}
            />
          }
        />
        <Button
          mode="contained"
          style={styles.button}
          contentStyle={styles.buttonContent}
          onPress={handleLogin}
        >
          Login
        </Button>

        <View style={styles.footer}>
          <Text variant="bodyMedium">Dont have an account? </Text>
          <Link href="/signup" asChild>
            <Pressable>
              <Text variant="bodyMedium" style={styles.link}>
                SignUp
              </Text>
            </Pressable>
          </Link>
        </View>
      </Surface>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: "center",
    padding: 16,
    backgroundColor: "#f5f5f5",
  },
  surface: {
    padding: 24,
    borderRadius: 12,
    backgroundColor: "white",
  },
  title: {
    textAlign: "center",
    marginBottom: 8,
    fontWeight: "bold",
  },
  subtitle: {
    textAlign: "center",
    marginBottom: 32,
    opacity: 0.7,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
    marginBottom: 16,
  },
  buttonContent: {
    paddingVertical: 8,
  },
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginTop: 8,
  },
  link: {
    color: "#6200ee",
    fontWeight: "bold",
  },
});
