import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/api/dashboard";

export const DASHBOARD_QUERY_KEY = ["dashboard"];

export function useDashboard() {
	return useQuery({
		queryKey: [...DASHBOARD_QUERY_KEY, "summary"],
		queryFn: () => dashboardApi.getSummary(),
		staleTime: 30 * 1000, // Consider fresh for 30 seconds
	});
}
