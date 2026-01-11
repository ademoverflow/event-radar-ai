import { TrendingUp } from "lucide-react";
import { useState } from "react";
import type { SignalFilters as SignalFiltersType } from "@/api/signals";
import { SignalCard } from "@/components/signals/SignalCard";
import { SignalFilters } from "@/components/signals/SignalFilters";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { useSignals } from "@/hooks/useSignals";

export function SignalsPage() {
	const [filters, setFilters] = useState<SignalFiltersType>({});
	const { data, isLoading, error } = useSignals(filters);

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
				<p className="text-red-600">Failed to load signals</p>
			</div>
		);
	}

	const handleLoadMore = () => {
		setFilters((prev) => ({
			...prev,
			offset: (prev.offset ?? 0) + (prev.limit ?? 50),
		}));
	};

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-2xl font-semibold text-slate-900">
					Detected Signals
				</h1>
				<p className="text-sm text-slate-500 mt-1">
					Event signals extracted from LinkedIn posts
				</p>
			</div>

			<SignalFilters filters={filters} onFiltersChange={setFilters} />

			{!data?.items.length ? (
				<EmptyState
					icon={TrendingUp}
					title="No signals found"
					description={
						Object.keys(filters).length > 0
							? "Try adjusting your filters to see more signals."
							: "Add profiles or searches to start detecting event signals."
					}
				/>
			) : (
				<>
					<div className="flex items-center justify-between text-sm text-slate-500">
						<span>
							Showing {data.items.length} of {data.total} signals
						</span>
					</div>

					<div className="space-y-4">
						{data.items.map((signal) => (
							<SignalCard key={signal.id} signal={signal} />
						))}
					</div>

					{data.items.length < data.total && (
						<div className="flex justify-center pt-4">
							<Button variant="outline" onClick={handleLoadMore}>
								Load More
							</Button>
						</div>
					)}
				</>
			)}
		</div>
	);
}
