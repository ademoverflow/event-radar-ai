import { apiClient } from "./client";

export interface SignalPost {
	id: string;
	linkedin_post_id: string;
	author_name: string;
	author_linkedin_url: string;
	content: string;
	posted_at: string;
}

export interface Signal {
	id: string;
	event_type: string | null;
	event_timing: "past" | "future" | "unknown";
	event_date: string | null;
	event_date_inferred: boolean;
	companies_mentioned: string[];
	people_mentioned: string[];
	relevance_score: number;
	summary: string;
	created_at: string;
	post: SignalPost | null;
}

export interface SignalListResponse {
	items: Signal[];
	total: number;
	limit: number;
	offset: number;
}

export interface SignalFilters {
	event_type?: string;
	event_timing?: "past" | "future" | "unknown";
	min_relevance?: number;
	from_date?: string;
	to_date?: string;
	limit?: number;
	offset?: number;
}

export interface SignalStats {
	total_signals: number;
	signals_by_type: Record<string, number>;
	signals_by_timing: Record<string, number>;
	average_relevance: number;
}

export const signalsApi = {
	list: (filters?: SignalFilters) => {
		const searchParams = new URLSearchParams();
		if (filters?.event_type) searchParams.set("event_type", filters.event_type);
		if (filters?.event_timing)
			searchParams.set("event_timing", filters.event_timing);
		if (filters?.min_relevance !== undefined)
			searchParams.set("min_relevance", filters.min_relevance.toString());
		if (filters?.from_date) searchParams.set("from_date", filters.from_date);
		if (filters?.to_date) searchParams.set("to_date", filters.to_date);
		if (filters?.limit) searchParams.set("limit", filters.limit.toString());
		if (filters?.offset) searchParams.set("offset", filters.offset.toString());
		const query = searchParams.toString();
		return apiClient<SignalListResponse>(`/signals${query ? `?${query}` : ""}`);
	},

	get: (id: string) => apiClient<Signal>(`/signals/${id}`),

	getStats: () => apiClient<SignalStats>("/signals/stats"),
};
