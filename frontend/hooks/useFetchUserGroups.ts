import { getGroups } from "@/services/groups";
import { Member } from "@/types";
import { useQuery } from "@tanstack/react-query";

export function useFetchUserGroups() {
  const {
    data: groups,
    isSuccess,
    isLoading,
    isError,
  } = useQuery<Member[]>({
    queryKey: ["groups"],
    // TODO: query group members should be dynamic
    queryFn: async () => getGroups(),
    // staleTime: 1000 * 60, // Optional: Data is "fresh" for 1 minute (won't auto-refetch)
  });

  return {
    groups,
    isSuccess,
    isError,
    isLoading,
  };
}
