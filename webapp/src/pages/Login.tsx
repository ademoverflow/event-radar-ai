import { Navigate } from "@tanstack/react-router";
import { Radar } from "lucide-react";
import { useId, useState } from "react";
import { useLogin, useUser } from "@/hooks/useAuth";

export function LoginPage() {
	const { data: user, isLoading: isUserLoading } = useUser();
	const login = useLogin();

	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");

	const emailId = useId();
	const passwordId = useId();

	if (isUserLoading) {
		return (
			<div className="flex items-center justify-center min-h-[60vh]">
				<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
			</div>
		);
	}

	if (user) {
		return <Navigate to="/" />;
	}

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		login.mutate({ email, password });
	};

	return (
		<div className="min-h-[70vh] flex items-center justify-center px-4 -mt-8">
			<div className="w-full max-w-md">
				<div className="text-center mb-8">
					<div className="flex items-center justify-center gap-2 mb-2">
						<Radar className="w-8 h-8 text-blue-600" />
						<h1 className="text-2xl font-semibold text-slate-900">
							Event Radar
						</h1>
					</div>
					<p className="text-slate-600">Sign in to your account</p>
				</div>

				<div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
					<form onSubmit={handleSubmit} className="space-y-6">
						{login.isError && (
							<div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
								{login.error.message}
							</div>
						)}

						<div>
							<label
								htmlFor={emailId}
								className="block text-sm font-medium text-slate-700 mb-2"
							>
								Email
							</label>
							<input
								id={emailId}
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								required
								autoComplete="email"
								className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 placeholder-slate-400"
								placeholder="you@example.com"
							/>
						</div>

						<div>
							<label
								htmlFor={passwordId}
								className="block text-sm font-medium text-slate-700 mb-2"
							>
								Password
							</label>
							<input
								id={passwordId}
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								required
								autoComplete="current-password"
								className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 placeholder-slate-400"
								placeholder="Enter your password"
							/>
						</div>

						<button
							type="submit"
							disabled={login.isPending}
							className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
						>
							{login.isPending ? "Signing in..." : "Sign in"}
						</button>
					</form>
				</div>
			</div>
		</div>
	);
}
