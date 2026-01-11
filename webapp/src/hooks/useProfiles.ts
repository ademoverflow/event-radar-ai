import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
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
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (id: string) => profilesApi.triggerCrawl(id),
		onSuccess: (data) => {
			toast.success("Crawl Started", {
				description: data.message,
				duration: 4000,
			});
			// Invalidate profiles to refresh last_crawled_at after background job completes
			// This won't show immediate update since the job runs async, but helps with subsequent refreshes
			queryClient.invalidateQueries({ queryKey: PROFILES_QUERY_KEY });
		},
		onError: (error: Error) => {
			toast.error("Failed to start crawl", {
				description: error.message || "An unexpected error occurred",
				duration: 5000,
			});
		},
	});
}
