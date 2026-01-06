import { router } from "expo-router";
import React from "react";
import { View, StyleSheet, ScrollView } from "react-native";
import { Avatar, Button, Card, Text, Divider, List } from "react-native-paper";

export default function ProfileScreen() {
  const handleLogout = () => {
    router.navigate("/(auth)");
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Avatar.Text size={80} label="VP" style={styles.avatar} />
        <Text variant="headlineMedium" style={styles.name}>
          Vikrant Pradhan
        </Text>
        <Text variant="bodyMedium" style={styles.email}>
          pradhan.vikrant.17@gmail.com
        </Text>
      </View>

      {/* Account Information */}
      <Card style={styles.accountInfo}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            Account Information
          </Text>
          <Divider style={styles.divider} />

          <List.Item
            title="Name"
            description="Vikrant"
            left={(props) => <List.Icon {...props} icon="account" />}
          />
          <List.Item
            title="Username"
            description="vikrant17"
            left={(props) => <List.Icon {...props} icon="account" />}
          />
        </Card.Content>
      </Card>

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <Button
          mode="contained"
          icon="logout"
          onPress={handleLogout}
          style={styles.logoutButton}
        >
          Logout
        </Button>

        <Button
          mode="outlined"
          icon="delete"
          onPress={() => {}}
          style={styles.deleteButton}
          buttonColor="transparent"
          textColor="#d32f2f"
        >
          Delete Account
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    alignItems: "center",
    paddingVertical: 32,
    marginBottom: 16,
  },
  avatar: {
    marginBottom: 16,
  },
  name: {
    fontWeight: "bold",
    marginBottom: 4,
  },
  email: {},
  accountInfo: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontWeight: "bold",
    marginBottom: 8,
  },
  divider: {
    marginBottom: 8,
  },
  actionsContainer: {
    paddingHorizontal: 16,
    paddingVertical: 24,
    gap: 12,
  },
  logoutButton: {
    paddingVertical: 6,
  },
  deleteButton: {
    paddingVertical: 6,
  },
  footer: {
    alignItems: "center",
    paddingVertical: 24,
  },
  footerText: {},
});
