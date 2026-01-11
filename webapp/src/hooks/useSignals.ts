import { useQuery } from "@tanstack/react-query";
import { type SignalFilters, signalsApi } from "@/api/signals";

export const SIGNALS_QUERY_KEY = ["signals"];

export function useSignals(filters?: SignalFilters) {
	return useQuery({
		queryKey: [...SIGNALS_QUERY_KEY, filters],
		queryFn: () => signalsApi.list(filters),
	});
}

export function useSignal(id: string) {
	return useQuery({
		queryKey: [...SIGNALS_QUERY_KEY, id],
		queryFn: () => signalsApi.get(id),
		enabled: !!id,
	});
}

export function useSignalStats() {
	return useQuery({
		queryKey: [...SIGNALS_QUERY_KEY, "stats"],
		queryFn: () => signalsApi.getStats(),
	});
}
