import { useQuery } from "@tanstack/react-query";
import * as React from "react";
import { ScrollView, Text, View } from "react-native";
import { Divider, FAB, List } from "react-native-paper";
import { getExpenses } from "@/services/expenses";
import { Link, router } from "expo-router";
import { Expense } from "@/types";

const Expenses = () => {
  const { data: expenses } = useQuery<Expense[]>({
    queryKey: ["expenses"], // The unique key for this data
    queryFn: getExpenses, // The function that returns the promise
    // staleTime: 1000 * 60, // Optional: Data is "fresh" for 1 minute (won't auto-refetch)
  });

  return (
    <>
      <ScrollView style={{ flex: 1 }}>
        <List.Section>
          {expenses?.map((expense) => (
            <View key={expense.id}>
              <Link
                href={{
                  pathname: "/view-expense",
                  params: {
                    expenseId: expense.id,
                  },
                }}
              >
                <List.Item
                  title={expense.title}
                  description={new Date(expense.timestamp).toLocaleString()}
                  right={() => <Text>₹{expense.amount}</Text>}
                />
              </Link>
              <Divider />
            </View>
          ))}
        </List.Section>
      </ScrollView>

      <FAB
        icon="plus"
        style={{ position: "absolute", margin: 14, right: 0, bottom: 0 }}
        onPress={() => router.push("/add-expense")}
      />
    </>
  );
};

export default Expenses;
