import { apiClient } from "./client";

export interface Profile {
	id: string;
	url: string;
	profile_type: "company" | "personal";
	display_name: string;
	crawl_frequency_hours: number;
	is_active: boolean;
	last_crawled_at: string | null;
	created_at: string;
	updated_at: string;
}

export interface ProfileListResponse {
	items: Profile[];
	total: number;
	limit: number;
	offset: number;
}

export interface ProfileCreate {
	url: string;
	profile_type: "company" | "personal";
	display_name: string;
	crawl_frequency_hours?: number;
}

export interface ProfileUpdate {
	display_name?: string;
	crawl_frequency_hours?: number;
	is_active?: boolean;
}

export interface ProfileCrawlQueuedResponse {
	message: string;
	profile_id: string;
	profile_display_name: string;
}

export const profilesApi = {
	list: (params?: { limit?: number; offset?: number; is_active?: boolean }) => {
		const searchParams = new URLSearchParams();
		if (params?.limit) searchParams.set("limit", params.limit.toString());
		if (params?.offset) searchParams.set("offset", params.offset.toString());
		if (params?.is_active !== undefined)
			searchParams.set("is_active", params.is_active.toString());
		const query = searchParams.toString();
		return apiClient<ProfileListResponse>(
			`/profiles${query ? `?${query}` : ""}`,
		);
	},

	get: (id: string) => apiClient<Profile>(`/profiles/${id}`),

	create: (data: ProfileCreate) =>
		apiClient<Profile>("/profiles", {
			method: "POST",
			body: JSON.stringify(data),
		}),

	update: (id: string, data: ProfileUpdate) =>
		apiClient<Profile>(`/profiles/${id}`, {
			method: "PATCH",
			body: JSON.stringify(data),
		}),

	delete: (id: string) =>
		apiClient<void>(`/profiles/${id}`, {
			method: "DELETE",
		}),

	triggerCrawl: (id: string) =>
		apiClient<ProfileCrawlQueuedResponse>(`/profiles/${id}/crawl`, {
			method: "POST",
		}),
};
