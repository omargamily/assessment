import { useQuery } from "@tanstack/react-query";
import { getCurrentUser, getAccessToken } from "../api";

export const useCurrentUser = () => {
  const hasToken = !!getAccessToken();

  const { data: user } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
    enabled: hasToken,
    retry: 1,
    staleTime: 1000 * 60 * 5,
    cacheTime: 1000 * 60 * 60,
  });

  return user;
};
