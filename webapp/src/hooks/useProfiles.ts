import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	type ProfileCreate,
	type ProfileUpdate,
	profilesApi,
} from "@/api/profiles";

export const PROFILES_QUERY_KEY = ["profiles"];

export function useProfiles(params?: {
	limit?: number;
	offset?: number;
	is_active?: boolean;
}) {
	return useQuery({
		queryKey: [...PROFILES_QUERY_KEY, params],
		queryFn: () => profilesApi.list(params),
	});
}

export function useProfile(id: string) {
	return useQuery({
		queryKey: [...PROFILES_QUERY_KEY, id],
		queryFn: () => profilesApi.get(id),
		enabled: !!id,
	});
}

export function useCreateProfile() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: ProfileCreate) => profilesApi.create(data),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: PROFILES_QUERY_KEY });
		},
	});
}

export function useUpdateProfile() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: ProfileUpdate }) =>
			profilesApi.update(id, data),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: PROFILES_QUERY_KEY });
		},
	});
}

export function useDeleteProfile() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (id: string) => profilesApi.delete(id),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: PROFILES_QUERY_KEY });
		},
	});
}

export function useTriggerProfileCrawl() {
	return useMutation({
		mutationFn: (id: string) => profilesApi.triggerCrawl(id),
	});
}
