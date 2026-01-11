import { useId } from "react";
import type { SignalFilters as SignalFiltersType } from "@/api/signals";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

interface SignalFiltersProps {
	filters: SignalFiltersType;
	onFiltersChange: (filters: SignalFiltersType) => void;
}

export function SignalFilters({
	filters,
	onFiltersChange,
}: SignalFiltersProps) {
	const id = useId();

	const handleChange = (key: keyof SignalFiltersType, value: string) => {
		const newFilters = { ...filters };
		if (value === "" || value === "all") {
			delete newFilters[key];
		} else if (key === "min_relevance") {
			newFilters[key] = Number.parseFloat(value);
		} else {
			(newFilters as Record<string, string>)[key] = value;
		}
		onFiltersChange(newFilters);
	};

	const handleReset = () => {
		onFiltersChange({});
	};

	return (
		<div className="flex flex-wrap items-end gap-4 p-4 bg-slate-50 rounded-lg">
			<div className="grid gap-1.5">
				<Label htmlFor={`${id}-event-timing`} className="text-xs">
					Event Timing
				</Label>
				<Select
					value={filters.event_timing ?? "all"}
					onValueChange={(v) => handleChange("event_timing", v)}
				>
					<SelectTrigger id={`${id}-event-timing`} className="w-40">
						<SelectValue placeholder="All" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All Events</SelectItem>
						<SelectItem value="future">Upcoming Events</SelectItem>
						<SelectItem value="past">Past Events</SelectItem>
						<SelectItem value="unknown">Date Unknown</SelectItem>
					</SelectContent>
				</Select>
			</div>

			<div className="grid gap-1.5">
				<Label htmlFor={`${id}-min-relevance`} className="text-xs">
					Min. Relevance
				</Label>
				<Select
					value={filters.min_relevance?.toString() ?? "all"}
					onValueChange={(v) => handleChange("min_relevance", v)}
				>
					<SelectTrigger id={`${id}-min-relevance`} className="w-32">
						<SelectValue placeholder="Any" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">Any</SelectItem>
						<SelectItem value="0.5">50%+</SelectItem>
						<SelectItem value="0.7">70%+</SelectItem>
						<SelectItem value="0.9">90%+</SelectItem>
					</SelectContent>
				</Select>
			</div>

			<div className="grid gap-1.5">
				<Label htmlFor={`${id}-from-date`} className="text-xs">
					From Date
				</Label>
				<Input
					id={`${id}-from-date`}
					type="date"
					className="w-36"
					value={filters.from_date ?? ""}
					onChange={(e) => handleChange("from_date", e.target.value)}
				/>
			</div>

			<div className="grid gap-1.5">
				<Label htmlFor={`${id}-to-date`} className="text-xs">
					To Date
				</Label>
				<Input
					id={`${id}-to-date`}
					type="date"
					className="w-36"
					value={filters.to_date ?? ""}
					onChange={(e) => handleChange("to_date", e.target.value)}
				/>
			</div>

			<Button variant="outline" size="sm" onClick={handleReset}>
				Reset
			</Button>
		</div>
	);
}
