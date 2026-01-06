import * as React from "react";
import { View, StyleSheet } from "react-native";
import { useEffect } from "react";
import {
  TextInput,
  Button,
  List,
  Checkbox,
  SegmentedButtons,
} from "react-native-paper";
import { DatePickerInput } from "react-native-paper-dates";
import { Dropdown } from "react-native-paper-dropdown";
import { Expense, Member, Split } from "@/types";
import { useFetchGroupMembers } from "../hooks/useFetchGroupMembers";
import { useFetchUserGroups } from "@/hooks/useFetchUserGroups";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";

type SplitWithCheck = Split & { checked: boolean };

export type ExpenseFormData = Omit<Expense, "splits" | "id"> & {
  splits: SplitWithCheck[];
};

export interface ExpenseFormProps {
  expenseData?: ExpenseFormData;
  onSubmit: (expenseData: ExpenseFormData) => void;
  onCancel: () => void;
}

export default function ExpenseForm({
  expenseData,
  onSubmit,
  onCancel,
}: ExpenseFormProps) {
  // Controlled Inputs State
  const [formData, setFormData] = React.useState<ExpenseFormData>(
    (expenseData && { ...expenseData, splits: [] }) || {
      groupId: 1,
      amount: undefined,
      title: "",
      description: "",
      splits: [],
      timestamp: new Date(),
    },
  );

  const [splitType, setSplitType] = React.useState<"manual" | "equal">(
    expenseData ? "manual" : "equal",
  );

  const { members: groupMembers } = useFetchGroupMembers(1);
  const { groups } = useFetchUserGroups();

  // Since splits array from server only contains data for members that were part of split,
  // we need to show all members in split page with amount 0 and checked false in the UI
  const mergeSplitsAndMembers = (
    splits: SplitWithCheck[],
    members: Member[],
  ): SplitWithCheck[] => {
    return members.map(({ name, id }) => {
      const split = splits.find((s) => s.id === id);
      if (split) {
        return { name, id, amount: split.amount, checked: true };
      } else {
        return { name, id, amount: undefined, checked: true };
      }
    });
  };

  useEffect(() => {
    if (groupMembers) {
      setFormData((prevFormData) => ({
        ...prevFormData,
        splits: mergeSplitsAndMembers(expenseData?.splits || [], groupMembers),
      }));
    }
  }, [expenseData, groupMembers]);

  const handleTitleChange = (text: string) => {
    setFormData({ ...formData, title: text });
  };

  const handleAmountChange = (text: string) => {
    const amount = parseFloat(text) || 0;
    setFormData({ ...formData, amount: amount });
  };

  const handleDescriptionChange = (text: string) => {
    setFormData({ ...formData, description: text });
  };

  const handleGroupIdChange = (value: string | undefined) => {
    if (value) setFormData({ ...formData, groupId: parseInt(value) });
  };

  const handleTimestampChange = (date: Date | undefined) => {
    setFormData({ ...formData, timestamp: date || new Date() });
  };

  const handleSplitAmountChange = (splitId: number, value: string) => {
    // Allow input only upto 2 decimal places
    if (value?.includes(".") && value.split(".")[1].length > 2) {
      return;
    }

    setFormData((prevFormData) => ({
      ...prevFormData,
      splits: prevFormData.splits?.map((s) =>
        s.id === splitId ? { ...s, amount: parseFloat(value) || 0 } : s,
      ),
    }));
  };

  const checkedSignature = formData.splits?.map((s) => s.checked).join(",");

  useEffect(() => {
    if (formData.amount !== undefined && splitType === "equal") {
      const splitAmount =
        formData.amount / formData.splits.filter((s) => s.checked).length || 0;
      setFormData((prevFormData) => ({
        ...prevFormData,
        splits: prevFormData.splits?.map((s) => ({
          ...s,
          amount: s.checked ? splitAmount : 0,
        })),
      }));
    }
  }, [formData.amount, formData.splits, checkedSignature, splitType]);

  return (
    <KeyboardAwareScrollView bottomOffset={20}>
      <View style={styles.form}>
        <View style={styles.groupSelection}>
          <Dropdown
            label="Group"
            mode="outlined"
            placeholder="Select Group"
            options={(groups || []).map(({ id, name }) => ({
              label: name,
              value: id.toString(),
            }))}
            value={formData.groupId.toString()}
            onSelect={handleGroupIdChange}
          />
        </View>
        <TextInput
          label="Title"
          value={formData.title}
          onChangeText={handleTitleChange}
          mode="outlined"
          style={styles.input}
          placeholder="Title"
        />
        <TextInput
          label="Amount"
          value={formData?.amount?.toString()}
          onChangeText={handleAmountChange}
          keyboardType="decimal-pad"
          mode="outlined"
          style={styles.input}
          left={<TextInput.Icon icon="currency-rupee" />}
          placeholder="0.00"
        />
        <TextInput
          label="Description"
          value={formData.description}
          onChangeText={handleDescriptionChange}
          mode="outlined"
          style={styles.input}
        />
        <DatePickerInput
          locale="en"
          label="Date"
          mode="outlined"
          value={formData.timestamp}
          onChange={handleTimestampChange}
          inputMode="start"
        />
      </View>
      {/* Dynamic Split Input */}
      <View style={{ paddingLeft: 16 }}>
        <View>
          <SegmentedButtons
            value={splitType}
            onValueChange={setSplitType}
            buttons={[
              {
                value: "manual",
                label: "Manual",
              },
              {
                value: "equal",
                label: "Equal",
              },
            ]}
          />
        </View>
        {formData.splits?.map(({ name, id, amount: splitAmount, checked }) => (
          <List.Item
            key={id}
            title={name}
            left={() => (
              <View style={{ justifyContent: "center" }}>
                <Checkbox
                  status={checked ? "checked" : "unchecked"}
                  onPress={() => {
                    setFormData((prevFormData) => ({
                      ...prevFormData,
                      splits: prevFormData.splits?.map((s) =>
                        s.id === id ? { ...s, checked: !checked } : s,
                      ),
                    }));
                  }}
                />
              </View>
            )}
            right={() => (
              <TextInput
                label="Split"
                value={splitAmount?.toString()}
                disabled={!checked}
                editable={splitType === "equal" ? false : true}
                onChangeText={(value: string) => {
                  handleSplitAmountChange(id, value);
                }}
                mode="outlined"
                keyboardType="decimal-pad"
                style={styles.splitInput}
                placeholder="00.00"
              />
            )}
          />
        ))}
      </View>

      <View style={styles.footer}>
        <Button
          mode="contained"
          onPress={() => {
            onSubmit(formData);
          }}
          style={styles.button}
          // disabled={!amount || !title}
        >
          Save Expense
        </Button>
        <Button mode="outlined" onPress={onCancel} style={styles.button}>
          Cancel
        </Button>
      </View>
    </KeyboardAwareScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
  },
  form: {
    padding: 16,
  },
  input: {
    marginBottom: 16,
  },
  splitInput: {},
  categoryButton: {
    justifyContent: "flex-start",
  },
  footer: {
    padding: 16,
    gap: 12,
  },
  button: {},
  groupSelection: {
    marginBottom: 16,
  },
});
