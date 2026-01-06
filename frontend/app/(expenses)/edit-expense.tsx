import * as React from "react";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { editExpense, getExpense } from "@/services/expenses";
import ExpenseForm, { ExpenseFormData } from "@/components/ExpenseForm";

export default function EditExpenseScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { expenseId } = useLocalSearchParams<{ expenseId: string }>();

  const mutation = useMutation({
    mutationFn: ({ id, expense }: { id: number; expense: any }) =>
      editExpense(id, expense),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["expense", expenseId],
      });
      queryClient.invalidateQueries({
        queryKey: ["expenses"],
      });
      router.back();
    },
  });

  const { data: expenseData } = useQuery<ExpenseFormData>({
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

  const handleEdit = (formData: ExpenseFormData) => {
    // TODO: Implement save functionality
    const { amount, title, description, groupId, splits, timestamp } = formData;
    mutation.mutate({
      id: parseInt(expenseId),
      expense: {
        id: expenseId,
        amount,
        title,
        description,
        group_id: groupId,
        splits,
        timestamp,
      },
    });
  };

  const handleCancel = () => {
    router.back();
  };

  if (!expenseData) {
    return <>Error Loading Expense Data</>;
  }

  return (
    <ExpenseForm
      expenseData={expenseData}
      onSubmit={handleEdit}
      onCancel={handleCancel}
    />
  );
}
