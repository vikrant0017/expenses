import { AppConfig } from "@/utils/config";

export const getExpenses = async () => {
  const res = await fetch(`${AppConfig.apiUrl}/expenses`);
  const jsonRes = await res.json();
  return jsonRes;
};

export const getExpense = async (id: number) => {
  const res = await fetch(`${AppConfig.apiUrl}/expenses/${id}`);
  const jsonRes = await res.json();
  return jsonRes;
};

export const deleteExpense = async (id: number) => {
  const res = await fetch(`${AppConfig.apiUrl}/expenses/${id}`, {
    method: "DELETE",
  });
  const jsonRes = await res.json();
  return jsonRes;
};

export const editExpense = async (id: number, expense: any) => {
  const res = await fetch(`${AppConfig.apiUrl}/expenses/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(expense),
  });
  const jsonRes = await res.json();
  return jsonRes;
};

export const createExpense = async (expense: any) => {
  const res = await fetch(`${AppConfig.apiUrl}/expenses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(expense),
  });
  const jsonRes = await res.json();
  return jsonRes;
};
