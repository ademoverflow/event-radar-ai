import { Link, useRouterState } from "@tanstack/react-router";
import { LogOut, Radar, User as UserIcon } from "lucide-react";
import { useLogout, useUser } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

export function Navbar() {
	const { data: user, isLoading } = useUser();
	const logout = useLogout();
	const routerState = useRouterState();
	const currentPath = routerState.location.pathname;

	const navLinks = [
		{ to: "/", label: "Dashboard" },
		{ to: "/profiles", label: "Profiles" },
		{ to: "/searches", label: "Searches" },
		{ to: "/signals", label: "Signals" },
	];

	return (
		<nav className="bg-white border-b border-slate-200 px-6 py-4">
			<div className="max-w-7xl mx-auto flex items-center justify-between">
				<div className="flex items-center gap-8">
					<Link to="/" className="flex items-center gap-2">
						<Radar className="w-6 h-6 text-blue-600" />
						<span className="text-xl font-semibold text-slate-900">
							Event Radar
						</span>
					</Link>

					{user && (
						<div className="flex items-center gap-1">
							{navLinks.map((link) => (
								<Link
									key={link.to}
									to={link.to}
									className={cn(
										"px-3 py-2 text-sm font-medium rounded-md transition-colors",
										currentPath === link.to
											? "bg-slate-100 text-slate-900"
											: "text-slate-600 hover:text-slate-900 hover:bg-slate-50",
									)}
								>
									{link.label}
								</Link>
							))}
						</div>
					)}
				</div>

				<div className="flex items-center gap-4">
					{isLoading ? (
						<div className="h-8 w-24 bg-slate-100 animate-pulse rounded" />
					) : user ? (
						<>
							<div className="flex items-center gap-2 text-slate-600">
								<UserIcon className="w-4 h-4" />
								<span className="text-sm">{user.email}</span>
							</div>
							<button
								type="button"
								onClick={() => logout.mutate()}
								disabled={logout.isPending}
								className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
							>
								<LogOut className="w-4 h-4" />
								<span>Logout</span>
							</button>
						</>
					) : (
						<Link
							to="/login"
							className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
						>
							Login
						</Link>
					)}
				</div>
			</div>
		</nav>
	);
}
