import { deleteExpense, getExpense } from "@/services/expenses";
import { Expense } from "@/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { router, useLocalSearchParams } from "expo-router";
import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import {
  Card,
  Divider,
  List,
  Chip,
  useTheme,
  Surface,
  Text,
  IconButton,
} from "react-native-paper";

export default function ViewExpenseScreen() {
  const { expenseId } = useLocalSearchParams<{ expenseId: string }>();
  const theme = useTheme();
  const queryClient = useQueryClient();

  const { data: expenseData } = useQuery<Expense>({
    queryKey: ["expense", expenseId],
    // TODO: query group members should be dynamic
    queryFn: async () => {
      const expense = await getExpense(parseInt(expenseId));
      return {
        ...expense,
        groupId: expense.group_id,
        timestamp: new Date(expense.timestamp),
      }; // Naming convention different for API response and UI
    },
    // staleTime: 1000 * 60, // Optional: Data is "fresh" for 1 minute (won't auto-refetch)
  });

  const mutation = useMutation({
    mutationFn: (id: string) => deleteExpense(parseInt(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["expense", expenseId],
      });
      queryClient.invalidateQueries({
        queryKey: ["expenses"],
      });
    },
  });

  const handleDelete = async () => {
    await mutation.mutateAsync(expenseId);
    router.back();
  };

  const handleEdit = () => {
    router.push({
      pathname: "/edit-expense",
      params: {
        expenseId: expenseId,
      },
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Surface mode="flat" style={styles.surface} elevation={0}>
        {/* Header Section */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <Text variant="titleLarge" style={styles.title}>
              {expenseData?.title}
            </Text>
            <Text variant="bodyMedium" style={styles.timestamp}>
              {expenseData?.timestamp?.toLocaleDateString()}
            </Text>
          </View>
          <View style={styles.headerActions}>
            <IconButton icon="pencil" size={24} onPress={handleEdit} />
            <IconButton icon="delete" size={24} onPress={handleDelete} />
          </View>
        </View>

        {/* Amount Section */}
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.expenseInfo}>
              <Text variant="labelLarge" style={styles.label}>
                Amount
              </Text>
              <Text
                variant="titleLarge"
                style={[styles.amount, { color: theme.colors.primary }]}
              >
                {expenseData?.amount}
              </Text>
            </View>
            <Divider />

            <View style={styles.expenseInfo}>
              <Text style={styles.label}>Group</Text>
              <View style={styles.groupContainer}>
                <Chip icon="account-group" mode="outlined" style={styles.chip}>
                  {expenseData?.groupId}
                </Chip>
              </View>
            </View>

            <Divider />

            <View style={styles.expenseInfo}>
              <Text style={styles.label}>Description</Text>
              <Text variant="bodyMedium" style={styles.description}>
                {expenseData?.description}
              </Text>
            </View>
          </Card.Content>
        </Card>

        {/* Splits Section */}
        <Card style={styles.card}>
          <List.Section>
            <List.Subheader style={styles.label}>Split Details</List.Subheader>
            {expenseData?.splits.map((split) => (
              <List.Item
                key={split.id}
                title={split.name}
                description="Share amount"
                left={(props) => <List.Icon {...props} icon="account" />}
                right={() => (
                  <Text style={styles.splitAmount}>{split.amount}</Text>
                )}
              />
            ))}
          </List.Section>
        </Card>
      </Surface>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  surface: {
    margin: 16,
    borderRadius: 8,
    padding: 16,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 12,
  },
  headerContent: {
    flex: 1,
  },
  headerActions: {
    flexDirection: "row",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 4,
  },
  timestamp: {
    fontSize: 14,
    opacity: 0.6,
  },
  divider: {
    marginVertical: 16,
  },
  card: {
    marginBottom: 16,
    borderRadius: 8,
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    marginBottom: 8,
  },
  amount: {
    fontSize: 36,
    fontWeight: "bold",
  },
  groupContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  chip: {
    marginRight: 8,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
  splitAmount: {
    fontSize: 16,
    fontWeight: "600",
    alignSelf: "center",
  },
  expenseInfo: {
    marginBottom: 10,
    marginTop: 10,
  },
});
