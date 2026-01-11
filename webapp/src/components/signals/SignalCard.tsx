import {
	Briefcase,
	Building2,
	Calendar,
	CalendarCheck,
	CalendarClock,
	CircleHelp,
	ExternalLink,
	Gift,
	Landmark,
	Mic2,
	Presentation,
	Sparkles,
	Store,
	Users,
	Video,
	Vote,
} from "lucide-react";
import type { Signal } from "@/api/signals";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip";

// Map event types to human-readable labels, icons, and descriptions
const EVENT_TYPE_CONFIG: Record<
	string,
	{ label: string; icon: React.ElementType; description: string }
> = {
	seminar: {
		label: "Seminar",
		icon: Presentation,
		description: "Educational or training session, often with expert speakers",
	},
	convention: {
		label: "Convention",
		icon: Users,
		description: "Large gathering of professionals or enthusiasts in a field",
	},
	product_launch: {
		label: "Product Launch",
		icon: Sparkles,
		description: "Introduction of a new product or service to the market",
	},
	anniversary: {
		label: "Anniversary",
		icon: Gift,
		description: "Company milestone or celebration event",
	},
	trade_show: {
		label: "Trade Show",
		icon: Store,
		description: "Exhibition where companies showcase products and services",
	},
	conference: {
		label: "Conference",
		icon: Mic2,
		description: "Professional meeting with presentations and discussions",
	},
	congress: {
		label: "Congress",
		icon: Landmark,
		description:
			"Large professional gathering, often annual, for an industry or organization",
	},
	general_assembly: {
		label: "General Assembly",
		icon: Vote,
		description:
			"Annual meeting of company shareholders or organization members",
	},
	webinar: {
		label: "Webinar",
		icon: Video,
		description: "Online seminar or presentation",
	},
	networking: {
		label: "Networking",
		icon: Users,
		description: "Event focused on building professional connections",
	},
	corporate_event: {
		label: "Corporate Event",
		icon: Briefcase,
		description:
			"Internal company event (team building, kick-off, company meeting)",
	},
	other: {
		label: "Other Event",
		icon: Calendar,
		description: "Business event that doesn't fit other categories",
	},
};

// Map event timing to human-readable labels, icons, and descriptions
const EVENT_TIMING_CONFIG: Record<
	string,
	{
		label: string;
		icon: React.ElementType;
		variant: "success" | "secondary" | "warning";
		description: string;
	}
> = {
	future: {
		label: "Upcoming",
		icon: CalendarClock,
		variant: "success",
		description: "This event is scheduled to happen in the future",
	},
	past: {
		label: "Past Event",
		icon: CalendarCheck,
		variant: "secondary",
		description: "This event has already taken place",
	},
	unknown: {
		label: "Date Unknown",
		icon: CircleHelp,
		variant: "warning",
		description: "The timing of this event could not be determined",
	},
};

interface SignalCardProps {
	signal: Signal;
}

export function SignalCard({ signal }: SignalCardProps) {
	const eventTypeConfig = signal.event_type
		? (EVENT_TYPE_CONFIG[signal.event_type] ?? {
				label: signal.event_type,
				icon: Calendar,
				description: "Business event detected in the post",
			})
		: null;

	const timingConfig = EVENT_TIMING_CONFIG[signal.event_timing] ?? {
		label: signal.event_timing,
		icon: CircleHelp,
		variant: "warning" as const,
		description: "Event timing status",
	};

	const TimingIcon = timingConfig.icon;

	return (
		<TooltipProvider>
			<Card>
				<CardContent className="p-4">
					<div className="flex items-start justify-between gap-4">
						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2 flex-wrap">
								{eventTypeConfig && (
									<Tooltip>
										<TooltipTrigger asChild>
											<Badge
												variant="info"
												className="flex items-center gap-1 cursor-help"
											>
												<eventTypeConfig.icon className="h-3 w-3" />
												{eventTypeConfig.label}
											</Badge>
										</TooltipTrigger>
										<TooltipContent>
											<p className="max-w-xs">{eventTypeConfig.description}</p>
										</TooltipContent>
									</Tooltip>
								)}
								<Tooltip>
									<TooltipTrigger asChild>
										<Badge
											variant={timingConfig.variant}
											className="flex items-center gap-1 cursor-help"
										>
											<TimingIcon className="h-3 w-3" />
											{timingConfig.label}
										</Badge>
									</TooltipTrigger>
									<TooltipContent>
										<p className="max-w-xs">{timingConfig.description}</p>
									</TooltipContent>
								</Tooltip>
								{signal.event_date && (
									<Tooltip>
										<TooltipTrigger asChild>
											<span className="text-xs text-slate-500 flex items-center gap-1 cursor-help">
												<Calendar className="h-3 w-3" />
												{new Date(signal.event_date).toLocaleDateString()}
												{signal.event_date_inferred && " *"}
											</span>
										</TooltipTrigger>
										<TooltipContent>
											<p className="max-w-xs">
												{signal.event_date_inferred
													? "Date was inferred from context (not explicitly stated)"
													: "Date was explicitly mentioned in the post"}
											</p>
										</TooltipContent>
									</Tooltip>
								)}
							</div>
							<p className="mt-2 text-sm text-slate-700">{signal.summary}</p>
							<div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
								{signal.companies_mentioned.length > 0 && (
									<Tooltip>
										<TooltipTrigger asChild>
											<span className="flex items-center gap-1 cursor-help">
												<Building2 className="h-3 w-3" />
												{signal.companies_mentioned.join(", ")}
											</span>
										</TooltipTrigger>
										<TooltipContent>
											<p>Companies or organizations mentioned</p>
										</TooltipContent>
									</Tooltip>
								)}
								{signal.people_mentioned.length > 0 && (
									<Tooltip>
										<TooltipTrigger asChild>
											<span className="flex items-center gap-1 cursor-help">
												<Users className="h-3 w-3" />
												{signal.people_mentioned.join(", ")}
											</span>
										</TooltipTrigger>
										<TooltipContent>
											<p>People mentioned (speakers, organizers, etc.)</p>
										</TooltipContent>
									</Tooltip>
								)}
							</div>
							{signal.post && (
								<div className="mt-3 pt-3 border-t border-slate-100">
									<div className="flex items-center justify-between flex-wrap gap-2">
										<a
											href={signal.post.author_linkedin_url}
											target="_blank"
											rel="noopener noreferrer"
											className="text-xs text-slate-600 hover:text-slate-900 hover:underline"
										>
											By: {signal.post.author_name}
										</a>
										<a
											href={`https://www.linkedin.com/feed/update/urn:li:activity:${signal.post.linkedin_post_id}`}
											target="_blank"
											rel="noopener noreferrer"
											className="text-xs text-blue-600 hover:underline flex items-center gap-1"
										>
											View Post
											<ExternalLink className="h-3 w-3" />
										</a>
									</div>
								</div>
							)}
						</div>
						<Tooltip>
							<TooltipTrigger asChild>
								<div className="text-right shrink-0 cursor-help">
									<div className="text-lg font-semibold text-slate-900">
										{Math.round(signal.relevance_score * 100)}%
									</div>
									<div className="text-xs text-slate-500">relevance</div>
								</div>
							</TooltipTrigger>
							<TooltipContent>
								<p className="max-w-xs">
									How relevant this signal is for business opportunities
									(0-100%)
								</p>
							</TooltipContent>
						</Tooltip>
					</div>
				</CardContent>
			</Card>
		</TooltipProvider>
	);
}
