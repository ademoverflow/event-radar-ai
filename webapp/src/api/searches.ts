import { apiClient } from "./client";

export interface Search {
	id: string;
	term: string;
	search_type: "keyword" | "hashtag";
	is_active: boolean;
	last_crawled_at: string | null;
	created_at: string;
	updated_at: string;
}

export interface SearchListResponse {
	items: Search[];
	total: number;
	limit: number;
	offset: number;
}

export interface SearchCreate {
	term: string;
	search_type: "keyword" | "hashtag";
}

export interface SearchUpdate {
	term?: string;
	is_active?: boolean;
}

export const searchesApi = {
	list: (params?: { limit?: number; offset?: number; is_active?: boolean }) => {
		const searchParams = new URLSearchParams();
		if (params?.limit) searchParams.set("limit", params.limit.toString());
		if (params?.offset) searchParams.set("offset", params.offset.toString());
		if (params?.is_active !== undefined)
			searchParams.set("is_active", params.is_active.toString());
		const query = searchParams.toString();
		return apiClient<SearchListResponse>(
			`/searches${query ? `?${query}` : ""}`,
		);
	},

	get: (id: string) => apiClient<Search>(`/searches/${id}`),

	create: (data: SearchCreate) =>
		apiClient<Search>("/searches", {
			method: "POST",
			body: JSON.stringify(data),
		}),

	update: (id: string, data: SearchUpdate) =>
		apiClient<Search>(`/searches/${id}`, {
			method: "PATCH",
			body: JSON.stringify(data),
		}),

	delete: (id: string) =>
		apiClient<void>(`/searches/${id}`, {
			method: "DELETE",
		}),

	triggerCrawl: (id: string) =>
		apiClient<{ message: string }>(`/searches/${id}/crawl`, {
			method: "POST",
		}),
};
