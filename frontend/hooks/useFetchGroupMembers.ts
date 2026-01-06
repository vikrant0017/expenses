import { getGroupMembers } from "@/services/groups";
import { Member } from "@/types";
import { useQuery } from "@tanstack/react-query";

export function useFetchGroupMembers(groupId: number) {
  const {
    data: members,
    isSuccess,
    isLoading,
    isError,
  } = useQuery<Member[]>({
    queryKey: ["members"],
    // TODO: query group members should be dynamic
    queryFn: async () => getGroupMembers(groupId),
    // staleTime: 1000 * 60, // Optional: Data is "fresh" for 1 minute (won't auto-refetch)
  });

  return {
    members,
    isSuccess,
    isError,
    isLoading,
  };
}
