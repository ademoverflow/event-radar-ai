import {
	Building2,
	Clock,
	Loader2,
	Pencil,
	Play,
	RefreshCw,
	Trash2,
	User,
} from "lucide-react";
import type { Profile } from "@/api/profiles";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Switch } from "@/components/ui/switch";

interface ProfileCardProps {
	profile: Profile;
	onEdit: (profile: Profile) => void;
	onDelete: (profile: Profile) => void;
	onToggleActive: (profile: Profile) => void;
	onTriggerCrawl: (profile: Profile, forceFull?: boolean) => void;
	isCrawling?: boolean;
}

export function ProfileCard({
	profile,
	onEdit,
	onDelete,
	onToggleActive,
	onTriggerCrawl,
	isCrawling = false,
}: ProfileCardProps) {
	const ProfileIcon = profile.profile_type === "company" ? Building2 : User;

	return (
		<Card>
			<CardContent className="p-4">
				<div className="flex items-start justify-between gap-4">
					<div className="flex items-start gap-3 min-w-0 flex-1">
						<div className="rounded-lg bg-slate-100 p-2">
							<ProfileIcon className="h-5 w-5 text-slate-600" />
						</div>
						<div className="min-w-0 flex-1">
							<div className="flex items-center gap-2">
								<h3 className="font-medium text-slate-900 truncate">
									{profile.display_name}
								</h3>
								<Badge
									variant={
										profile.profile_type === "company" ? "info" : "secondary"
									}
								>
									{profile.profile_type}
								</Badge>
							</div>
							<p className="text-sm text-slate-500 truncate mt-0.5">
								{profile.url}
							</p>
							<div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
								<span className="flex items-center gap-1">
									<Clock className="h-3 w-3" />
									Every {profile.crawl_frequency_hours}h
								</span>
								{profile.last_crawled_at && (
									<span>
										Last crawled:{" "}
										{new Date(profile.last_crawled_at).toLocaleDateString()}
									</span>
								)}
							</div>
						</div>
					</div>
					<div className="flex items-center gap-2">
						<Switch
							checked={profile.is_active}
							onCheckedChange={() => onToggleActive(profile)}
						/>
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<Button
									variant="ghost"
									size="icon"
									title="Trigger crawl"
									disabled={isCrawling}
								>
									{isCrawling ? (
										<Loader2 className="h-4 w-4 animate-spin" />
									) : (
										<Play className="h-4 w-4" />
									)}
								</Button>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end">
								<DropdownMenuItem
									onClick={() => onTriggerCrawl(profile, false)}
								>
									<Play className="h-4 w-4 mr-2" />
									Crawl new posts
								</DropdownMenuItem>
								<DropdownMenuItem onClick={() => onTriggerCrawl(profile, true)}>
									<RefreshCw className="h-4 w-4 mr-2" />
									Full re-crawl
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
						<Button
							variant="ghost"
							size="icon"
							onClick={() => onEdit(profile)}
							title="Edit"
						>
							<Pencil className="h-4 w-4" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							onClick={() => onDelete(profile)}
							title="Delete"
						>
							<Trash2 className="h-4 w-4 text-red-500" />
						</Button>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
