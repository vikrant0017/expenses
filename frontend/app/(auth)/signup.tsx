import React, { useState } from "react";
import { View, StyleSheet, ScrollView } from "react-native";
import { TextInput, Button, Text, Surface } from "react-native-paper";
import { signUp } from "@/services/auth";
import { Link } from "expo-router";

export default function SignUpScreen() {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSignUp = () => {
    signUp({
      name,
      username,
      password,
    });
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Surface style={styles.surface} elevation={1}>
        <Text variant="headlineMedium" style={styles.title}>
          Create Account
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Sign up to get started
        </Text>

        <TextInput
          label="Name"
          value={name}
          onChangeText={setName}
          mode="outlined"
          style={styles.input}
          left={<TextInput.Icon icon="account-circle" />}
        />

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

        {/*<TextInput
          label="Confirm Password"
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          mode="outlined"
          secureTextEntry={!showConfirmPassword}
          style={styles.input}
          left={<TextInput.Icon icon="lock-check" />}
          right={
            <TextInput.Icon
              icon={showConfirmPassword ? "eye-off" : "eye"}
              onPress={() => setShowConfirmPassword(!showConfirmPassword)}
            />
          }
        />*/}

        <Button
          mode="contained"
          style={styles.button}
          contentStyle={styles.buttonContent}
          onPress={handleSignUp}
        >
          Sign Up
        </Button>

        <View style={styles.footer}>
          <Text variant="bodyMedium">Already have an account? </Text>
          <Link href="/">
            <Text variant="bodyMedium" style={styles.link}>
              Log In
            </Text>
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
