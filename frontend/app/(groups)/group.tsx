import { getGroup, getGroupMembers } from "@/services/groups";
import { useQuery } from "@tanstack/react-query";
import { useLocalSearchParams } from "expo-router";
import React from "react";
import { View, StyleSheet, ScrollView } from "react-native";
import { Card, Text, Avatar, Divider, Chip, List } from "react-native-paper";

export default function GroupScreen() {
  const { groupId } = useLocalSearchParams<{ groupId: string }>();

  const { data: groupInfo } = useQuery({
    queryKey: ["group", groupId],
    queryFn: async () => getGroup(parseInt(groupId)),
  });

  const { data: members } = useQuery({
    queryKey: ["members"],
    queryFn: async () => getGroupMembers(parseInt(groupId)),
  });

  if (!groupInfo || !members) return <>Loading</>;

  return (
    <ScrollView style={styles.container}>
      {/* Group Info Card */}
      <Card style={styles.card} mode="elevated">
        <Card.Content>
          <Text variant="headlineMedium" style={styles.groupName}>
            {groupInfo.name}
          </Text>
          <Divider style={styles.divider} />

          <View style={styles.infoRow}>
            <Text variant="labelLarge" style={styles.label}>
              Total Members:
            </Text>
            <Chip icon="account-group" style={styles.chip}>
              {members.length}
            </Chip>
          </View>

          <View style={styles.infoRow}>
            <Text variant="labelLarge" style={styles.label}>
              Created
            </Text>
            <Text variant="bodyLarge">{groupInfo.created || "12:12:12"}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text variant="labelLarge" style={styles.label}>
              Code
            </Text>
            <Text variant="bodyLarge">{groupInfo.code}</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card} mode="elevated">
        <List.Section>
          <List.Subheader>Members</List.Subheader>
          {members.map((member) => (
            <List.Item
              key={member.id}
              title={member.name}
              description={member.username}
              left={(props) => (
                <Avatar.Text {...props} size={48} label={member.name[0]} />
              )}
            />
          ))}
        </List.Section>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  card: {
    margin: 16,
    marginBottom: 8,
  },
  groupName: {
    fontWeight: "bold",
    marginBottom: 8,
  },
  divider: {
    marginVertical: 16,
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },
  label: {
    marginRight: 8,
    fontWeight: "600",
  },
  chip: {
    height: 32,
  },
  memberRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
  },
  avatar: {
    marginRight: 16,
  },
  memberInfo: {
    flex: 1,
  },
  memberName: {
    fontWeight: "500",
    marginBottom: 4,
  },
  memberEmail: {
    color: "#666",
  },
  memberDivider: {
    marginVertical: 4,
  },
});
