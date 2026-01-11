import { useUser } from "@/hooks/useAuth";

export function Dashboard() {
	const { data: user } = useUser();

	return (
		<div>
			<h1 className="text-2xl font-semibold text-slate-900 mb-6">Dashboard</h1>
			<div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
				<p className="text-slate-600">
					Welcome back, <span className="font-medium">{user?.email}</span>
				</p>
			</div>
		</div>
	);
}
