import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { authApi, type LoginCredentials, type User } from "@/api/auth";

export const AUTH_QUERY_KEY = ["auth", "user"];

export function useUser() {
	return useQuery<User | null>({
		queryKey: AUTH_QUERY_KEY,
		queryFn: async () => {
			try {
				return await authApi.getMe();
			} catch {
				return null;
			}
		},
		staleTime: 5 * 60 * 1000,
		retry: false,
	});
}

export function useLogin() {
	const queryClient = useQueryClient();
	const navigate = useNavigate();

	return useMutation({
		mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
			navigate({ to: "/" });
		},
	});
}

export function useLogout() {
	const queryClient = useQueryClient();
	const navigate = useNavigate();

	return useMutation({
		mutationFn: () => authApi.logout(),
		onSuccess: () => {
			queryClient.setQueryData(AUTH_QUERY_KEY, null);
			navigate({ to: "/login" });
		},
	});
}
