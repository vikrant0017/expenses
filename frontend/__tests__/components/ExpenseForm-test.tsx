import { render, screen, userEvent } from "@testing-library/react-native";

import ExpenseForm from "@/components/ExpenseForm";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { PaperProvider } from "react-native-paper";
import { useFetchGroupMembers } from "@/hooks/useFetchGroupMembers";
import { useFetchUserGroups } from "@/hooks/useFetchUserGroups";

// Mock the useFetchUserGroup hook
jest.mock("@/hooks/useFetchGroupMembers", () => ({
  useFetchGroupMembers: jest.fn(),
}));

jest.mock("@/hooks/useFetchUserGroups", () => ({
  useFetchUserGroups: jest.fn(),
}));

// Create a function to generate a fresh client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Prevents Jest from timing out during failures
      },
    },
  });

describe("<ExpenseForm />", () => {
  const queryClient = createTestQueryClient();

  beforeEach(() => {
    // Mock the return value of useFetchUserGroup
    (useFetchUserGroups as jest.Mock).mockReturnValue({
      groups: [
        { id: 1, name: "Group 1" },
        { id: 2, name: "Group 2" },
      ],
    });

    (useFetchGroupMembers as jest.Mock).mockReturnValue({
      members: [
        { id: 1, name: "Member 1" },
        { id: 2, name: "Member 2" },
      ],
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test("ExpenseForm renders correctly", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PaperProvider>
          <ExpenseForm onSubmit={() => {}} onCancel={() => {}} />
        </PaperProvider>
      </QueryClientProvider>,
    );
    // Debug to see what's actually rendering
    // screen.debug();

    const user = userEvent.setup();

    // Using find by as RNTL was throwing error due to async Icon rendering
    expect(await screen.findByText("Save Expense")).toBeOnTheScreen();
    expect(screen.getByText("Cancel")).toBeOnTheScreen();

    expect(screen.getByText("Member 1")).toBeOnTheScreen();
    expect(screen.getByText("Member 2")).toBeOnTheScreen();

    // Open the Group dropdown
    const groupDropdown = screen.getByPlaceholderText("Select Group");
    await user.press(groupDropdown);
    expect(screen.getByText("Group 1")).toBeOnTheScreen();
    expect(screen.getByText("Group 2")).toBeOnTheScreen();

    // user.press(groupDropdown);
  });
});
