import { apiClient } from "./client";
import type { Signal } from "./signals";

export interface DashboardSummary {
	total_profiles: number;
	active_profiles: number;
	total_searches: number;
	active_searches: number;
	total_posts: number;
	total_signals: number;
	signals_by_type: Record<string, number>;
	signals_by_timing: Record<string, number>;
	recent_signals: Signal[];
}

export const dashboardApi = {
	getSummary: () => apiClient<DashboardSummary>("/dashboard/summary"),
};
