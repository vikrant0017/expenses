import { AppConfig } from "@/utils/config";

interface SignUpPayload {
  name: string;
  username: string;
  password: string;
}

interface SignInPayload {
  username: string;
  password: string;
}

interface User {
  id: string;
  name: string;
  username: string;
}

export const signUp = async (payload: SignUpPayload): Promise<User> => {
  const res = await fetch(`${AppConfig.apiUrl}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return res.json();
};

export const signIn = async (payload: SignInPayload): Promise<User> => {
  const res = await fetch(`${AppConfig.apiUrl}/users`, {
    method: "GET",
  });

  // Mocking user login directly from frontend
  const users = (await res.json()) as (User & { password: string })[];
  const user = users.find(
    ({ username, password }) =>
      username === payload.username && password === payload.password,
  );

  if (!user) {
    throw new Error("AuthError - Incorrect username or password");
  }

  return user;
};
