import {
	Building2,
	Calendar,
	CalendarCheck,
	CalendarClock,
	CircleHelp,
	ExternalLink,
	Gift,
	Mic2,
	Presentation,
	Sparkles,
	Store,
	Users,
	Video,
} from "lucide-react";
import type { Signal } from "@/api/signals";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

// Map event types to human-readable labels and icons
const EVENT_TYPE_CONFIG: Record<
	string,
	{ label: string; icon: React.ElementType }
> = {
	seminar: { label: "Seminar", icon: Presentation },
	convention: { label: "Convention", icon: Users },
	product_launch: { label: "Product Launch", icon: Sparkles },
	anniversary: { label: "Anniversary", icon: Gift },
	trade_show: { label: "Trade Show", icon: Store },
	conference: { label: "Conference", icon: Mic2 },
	webinar: { label: "Webinar", icon: Video },
	networking: { label: "Networking", icon: Users },
	other: { label: "Other Event", icon: Calendar },
};

// Map event timing to human-readable labels and icons
const EVENT_TIMING_CONFIG: Record<
	string,
	{
		label: string;
		icon: React.ElementType;
		variant: "success" | "secondary" | "warning";
	}
> = {
	future: { label: "Upcoming", icon: CalendarClock, variant: "success" },
	past: { label: "Past Event", icon: CalendarCheck, variant: "secondary" },
	unknown: { label: "Date Unknown", icon: CircleHelp, variant: "warning" },
};

interface SignalCardProps {
	signal: Signal;
}

export function SignalCard({ signal }: SignalCardProps) {
	const eventTypeConfig = signal.event_type
		? (EVENT_TYPE_CONFIG[signal.event_type] ?? {
				label: signal.event_type,
				icon: Calendar,
			})
		: null;

	const timingConfig = EVENT_TIMING_CONFIG[signal.event_timing] ?? {
		label: signal.event_timing,
		icon: CircleHelp,
		variant: "warning" as const,
	};

	const TimingIcon = timingConfig.icon;

	return (
		<Card>
			<CardContent className="p-4">
				<div className="flex items-start justify-between gap-4">
					<div className="flex-1 min-w-0">
						<div className="flex items-center gap-2 flex-wrap">
							{eventTypeConfig && (
								<Badge variant="info" className="flex items-center gap-1">
									<eventTypeConfig.icon className="h-3 w-3" />
									{eventTypeConfig.label}
								</Badge>
							)}
							<Badge
								variant={timingConfig.variant}
								className="flex items-center gap-1"
							>
								<TimingIcon className="h-3 w-3" />
								{timingConfig.label}
							</Badge>
							{signal.event_date && (
								<span className="text-xs text-slate-500 flex items-center gap-1">
									<Calendar className="h-3 w-3" />
									{new Date(signal.event_date).toLocaleDateString()}
									{signal.event_date_inferred && " (inferred)"}
								</span>
							)}
						</div>
						<p className="mt-2 text-sm text-slate-700">{signal.summary}</p>
						<div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
							{signal.companies_mentioned.length > 0 && (
								<span className="flex items-center gap-1">
									<Building2 className="h-3 w-3" />
									{signal.companies_mentioned.join(", ")}
								</span>
							)}
							{signal.people_mentioned.length > 0 && (
								<span className="flex items-center gap-1">
									<Users className="h-3 w-3" />
									{signal.people_mentioned.join(", ")}
								</span>
							)}
						</div>
						{signal.post && (
							<div className="mt-3 pt-3 border-t border-slate-100">
								<div className="flex items-center justify-between">
									<span className="text-xs text-slate-500">
										From: {signal.post.author_name}
									</span>
									<a
										href={signal.post.author_linkedin_url}
										target="_blank"
										rel="noopener noreferrer"
										className="text-xs text-blue-600 hover:underline flex items-center gap-1"
									>
										View on LinkedIn
										<ExternalLink className="h-3 w-3" />
									</a>
								</div>
							</div>
						)}
					</div>
					<div className="text-right shrink-0">
						<div className="text-lg font-semibold text-slate-900">
							{Math.round(signal.relevance_score * 100)}%
						</div>
						<div className="text-xs text-slate-500">relevance</div>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
