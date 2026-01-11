function getApiBaseUrl(): string {
	if (import.meta.env.VITE_CORE_URL) {
		return import.meta.env.VITE_CORE_URL;
	}
	// In development, use the same hostname as the webapp to avoid cross-origin issues
	const hostname =
		typeof window !== "undefined" ? window.location.hostname : "localhost";
	return `http://${hostname}:7999`;
}

const API_BASE_URL = getApiBaseUrl();

export async function apiClient<T>(
	endpoint: string,
	options: RequestInit = {},
): Promise<T> {
	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		...options,
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
			...options.headers,
		},
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({}));
		throw new Error(error.detail || `API error: ${response.status}`);
	}

	return response.json();
}
