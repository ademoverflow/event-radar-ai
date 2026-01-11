import { apiClient } from "./client";

export interface User {
	id: string;
	email: string;
	is_active: boolean;
	created_at: string;
}

export interface LoginCredentials {
	email: string;
	password: string;
}

export const authApi = {
	login: (credentials: LoginCredentials) =>
		apiClient<{ message: string }>("/auth/login", {
			method: "POST",
			body: JSON.stringify(credentials),
		}),

	logout: () =>
		apiClient<{ message: string }>("/auth/logout", {
			method: "POST",
		}),

	getMe: () => apiClient<User>("/users/me"),
};
