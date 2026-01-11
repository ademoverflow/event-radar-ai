import { Navigate, Outlet } from "@tanstack/react-router";
import { useUser } from "@/hooks/useAuth";

export function ProtectedRoute() {
	const { data: user, isLoading } = useUser();

	if (isLoading) {
		return (
			<div className="flex items-center justify-center min-h-[50vh]">
				<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
			</div>
		);
	}

	if (!user) {
		return <Navigate to="/login" />;
	}

	return <Outlet />;
}
