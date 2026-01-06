import { router } from "expo-router";
import React, { useState } from "react";
import { View, StyleSheet } from "react-native";
import { TextInput, Button } from "react-native-paper";

export default function CreateGroupForm() {
  const [groupName, setGroupName] = useState("");

  const handleSubmit = () => {
    router.replace("/group");
  };

  return (
    <View style={styles.container}>
      <TextInput
        label="Group Name"
        value={groupName}
        onChangeText={setGroupName}
        mode="outlined"
        style={styles.input}
      />
      <Button mode="contained" onPress={handleSubmit} style={styles.button}>
        Create
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
});
