import { Building2, Calendar, ExternalLink, Users } from "lucide-react";
import type { Signal } from "@/api/signals";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

interface SignalCardProps {
	signal: Signal;
}

export function SignalCard({ signal }: SignalCardProps) {
	const timingVariant =
		signal.event_timing === "future"
			? "success"
			: signal.event_timing === "past"
				? "secondary"
				: "warning";

	return (
		<Card>
			<CardContent className="p-4">
				<div className="flex items-start justify-between gap-4">
					<div className="flex-1 min-w-0">
						<div className="flex items-center gap-2 flex-wrap">
							{signal.event_type && (
								<Badge variant="info">{signal.event_type}</Badge>
							)}
							<Badge variant={timingVariant}>{signal.event_timing}</Badge>
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
