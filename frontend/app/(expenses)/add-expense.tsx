import * as React from "react";
import { useRouter } from "expo-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createExpense } from "@/services/expenses";
import ExpenseForm, { ExpenseFormData } from "@/components/ExpenseForm";

export default function AddExpenseScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createExpense,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
      router.back();
    },
  });

  // TODO: This must be queried from server

  const handleSave = (formData: ExpenseFormData) => {
    // TODO: Implement save functionality
    const { amount, title, description, groupId, splits, timestamp } = formData;
    mutation.mutate({
      amount,
      title,
      description,
      group_id: groupId,
      splits: splits,
      timestamp,
    });
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <>
      <ExpenseForm onSubmit={handleSave} onCancel={handleCancel} />
    </>
  );
}
