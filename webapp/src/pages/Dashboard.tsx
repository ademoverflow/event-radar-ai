import { Link } from "@tanstack/react-router";
import {
	Activity,
	Building2,
	Plus,
	Search,
	TrendingUp,
	Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { useDashboard } from "@/hooks/useDashboard";

export function Dashboard() {
	const { data: summary, isLoading, error } = useDashboard();

	if (isLoading) {
		return (
			<div className="flex items-center justify-center min-h-[50vh]">
				<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900" />
			</div>
		);
	}

	if (error) {
		return (
			<div className="text-center py-12">
				<p className="text-red-600">Failed to load dashboard data</p>
			</div>
		);
	}

	const stats = [
		{
			label: "Monitored Profiles",
			value: summary?.total_profiles ?? 0,
			active: summary?.active_profiles ?? 0,
			icon: Users,
			color: "text-blue-600",
			bgColor: "bg-blue-50",
		},
		{
			label: "Saved Searches",
			value: summary?.total_searches ?? 0,
			active: summary?.active_searches ?? 0,
			icon: Search,
			color: "text-purple-600",
			bgColor: "bg-purple-50",
		},
		{
			label: "Posts Collected",
			value: summary?.total_posts ?? 0,
			icon: Activity,
			color: "text-green-600",
			bgColor: "bg-green-50",
		},
		{
			label: "Signals Detected",
			value: summary?.total_signals ?? 0,
			icon: TrendingUp,
			color: "text-orange-600",
			bgColor: "bg-orange-50",
		},
	];

	return (
		<div className="space-y-8">
			<div className="flex items-center justify-between">
				<h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
				<div className="flex gap-3">
					<Button variant="outline" asChild>
						<Link to="/profiles">
							<Plus className="w-4 h-4 mr-2" />
							Add Profile
						</Link>
					</Button>
					<Button asChild>
						<Link to="/searches">
							<Plus className="w-4 h-4 mr-2" />
							Add Search
						</Link>
					</Button>
				</div>
			</div>

			{/* Stats Grid */}
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				{stats.map((stat) => (
					<Card key={stat.label}>
						<CardContent className="p-6">
							<div className="flex items-center gap-4">
								<div className={`p-3 rounded-lg ${stat.bgColor}`}>
									<stat.icon className={`w-6 h-6 ${stat.color}`} />
								</div>
								<div>
									<p className="text-sm text-slate-600">{stat.label}</p>
									<p className="text-2xl font-semibold text-slate-900">
										{stat.value}
									</p>
									{stat.active !== undefined && (
										<p className="text-xs text-slate-500">
											{stat.active} active
										</p>
									)}
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</div>

			{/* Recent Signals */}
			<Card>
				<CardHeader>
					<div className="flex items-center justify-between">
						<div>
							<CardTitle>Recent Signals</CardTitle>
							<CardDescription>
								Latest event signals detected from your monitored sources
							</CardDescription>
						</div>
						<Button variant="outline" size="sm" asChild>
							<Link to="/signals">View all</Link>
						</Button>
					</div>
				</CardHeader>
				<CardContent>
					{!summary?.recent_signals.length ? (
						<EmptyState
							icon={TrendingUp}
							title="No signals detected yet"
							description="Add profiles or searches to start monitoring for event signals."
						/>
					) : (
						<div className="space-y-4">
							{summary.recent_signals.map((signal) => (
								<div
									key={signal.id}
									className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg"
								>
									<div className="flex-1">
										<div className="flex items-center gap-2 mb-2 flex-wrap">
											{signal.event_type && (
												<Badge variant="info">{signal.event_type}</Badge>
											)}
											<Badge
												variant={
													signal.event_timing === "future"
														? "success"
														: signal.event_timing === "past"
															? "secondary"
															: "warning"
												}
											>
												{signal.event_timing}
											</Badge>
											<span className="text-xs text-slate-500">
												{new Date(signal.created_at).toLocaleDateString()}
											</span>
										</div>
										<p className="text-sm text-slate-700">{signal.summary}</p>
										{signal.companies_mentioned.length > 0 && (
											<div className="flex items-center gap-1 mt-2">
												<Building2 className="w-3 h-3 text-slate-400" />
												<span className="text-xs text-slate-500">
													{signal.companies_mentioned.join(", ")}
												</span>
											</div>
										)}
									</div>
									<div className="text-right shrink-0">
										<span className="text-sm font-medium text-slate-900">
											{Math.round(signal.relevance_score * 100)}%
										</span>
										<p className="text-xs text-slate-500">relevance</p>
									</div>
								</div>
							))}
						</div>
					)}
				</CardContent>
			</Card>

			{/* Signal Distribution */}
			{summary &&
				(Object.keys(summary.signals_by_type).length > 0 ||
					Object.keys(summary.signals_by_timing).length > 0) && (
					<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
						{Object.keys(summary.signals_by_type).length > 0 && (
							<Card>
								<CardHeader>
									<CardTitle className="text-base">Signals by Type</CardTitle>
								</CardHeader>
								<CardContent>
									<div className="space-y-3">
										{Object.entries(summary.signals_by_type).map(
											([type, count]) => (
												<div
													key={type}
													className="flex items-center justify-between"
												>
													<span className="text-sm text-slate-600 capitalize">
														{type}
													</span>
													<span className="text-sm font-medium text-slate-900">
														{count}
													</span>
												</div>
											),
										)}
									</div>
								</CardContent>
							</Card>
						)}

						{Object.keys(summary.signals_by_timing).length > 0 && (
							<Card>
								<CardHeader>
									<CardTitle className="text-base">Signals by Timing</CardTitle>
								</CardHeader>
								<CardContent>
									<div className="space-y-3">
										{Object.entries(summary.signals_by_timing).map(
											([timing, count]) => (
												<div
													key={timing}
													className="flex items-center justify-between"
												>
													<span className="text-sm text-slate-600 capitalize">
														{timing}
													</span>
													<span className="text-sm font-medium text-slate-900">
														{count}
													</span>
												</div>
											),
										)}
									</div>
								</CardContent>
							</Card>
						)}
					</div>
				)}
		</div>
	);
}
