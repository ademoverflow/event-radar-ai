import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	type SearchCreate,
	type SearchUpdate,
	searchesApi,
} from "@/api/searches";

export const SEARCHES_QUERY_KEY = ["searches"];

export function useSearches(params?: {
	limit?: number;
	offset?: number;
	is_active?: boolean;
}) {
	return useQuery({
		queryKey: [...SEARCHES_QUERY_KEY, params],
		queryFn: () => searchesApi.list(params),
	});
}

export function useSearch(id: string) {
	return useQuery({
		queryKey: [...SEARCHES_QUERY_KEY, id],
		queryFn: () => searchesApi.get(id),
		enabled: !!id,
	});
}

export function useCreateSearch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: SearchCreate) => searchesApi.create(data),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: SEARCHES_QUERY_KEY });
		},
	});
}

export function useUpdateSearch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: SearchUpdate }) =>
			searchesApi.update(id, data),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: SEARCHES_QUERY_KEY });
		},
	});
}

export function useDeleteSearch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (id: string) => searchesApi.delete(id),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: SEARCHES_QUERY_KEY });
		},
	});
}

export function useTriggerSearchCrawl() {
	return useMutation({
		mutationFn: (id: string) => searchesApi.triggerCrawl(id),
	});
}
