import { useQuery } from "@tanstack/react-query";
import * as React from "react";
import { ScrollView, Text, View } from "react-native";
import { Divider, FAB, List } from "react-native-paper";
import { Link, router } from "expo-router";
import { getGroups } from "@/services/groups";
import { Group } from "@/types";

const Groups = () => {
  const { data: groups } = useQuery<Group[]>({
    queryKey: ["groups"], // The unique key for this data
    queryFn: getGroups, // The function that returns the promise
    // staleTime: 1000 * 60, // Optional: Data is "fresh" for 1 minute (won't auto-refetch)
  });

  const [state, setState] = React.useState({ open: false });

  const onStateChange = ({ open }: { open: boolean }) => setState({ open });

  const { open } = state;

  return (
    <>
      <ScrollView style={{ flex: 1 }}>
        <List.Section>
          {groups?.map((group) => (
            <View key={group.id}>
              <Link
                href={{
                  pathname: "/group",
                  params: {
                    groupId: group.id,
                  },
                }}
              >
                <List.Item
                  title={group.name}
                  description={"3 members"}
                  right={() => <Text>{"idk"}</Text>}
                />
              </Link>
              <Divider />
            </View>
          ))}
        </List.Section>
      </ScrollView>

      <FAB.Group
        open={open}
        visible
        icon={open ? "close" : "plus"}
        actions={[
          {
            icon: "account-multiple-plus",
            label: "Create Group",
            onPress: () => {
              router.push("/create-group");
            },
          },
          {
            icon: "account-multiple-plus",
            label: "Join Group",
            onPress: () => {
              router.push("/join-group");
            },
          },
        ]}
        onStateChange={onStateChange}
      />
    </>
  );
};

export default Groups;
