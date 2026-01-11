import { Hash, Pencil, Play, Search, Trash2 } from "lucide-react";
import type { Search as SearchType } from "@/api/searches";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";

interface SearchCardProps {
	search: SearchType;
	onEdit: (search: SearchType) => void;
	onDelete: (search: SearchType) => void;
	onToggleActive: (search: SearchType) => void;
	onTriggerCrawl: (search: SearchType) => void;
}

export function SearchCard({
	search,
	onEdit,
	onDelete,
	onToggleActive,
	onTriggerCrawl,
}: SearchCardProps) {
	const SearchIcon = search.search_type === "hashtag" ? Hash : Search;

	return (
		<Card>
			<CardContent className="p-4">
				<div className="flex items-start justify-between gap-4">
					<div className="flex items-start gap-3 min-w-0 flex-1">
						<div className="rounded-lg bg-slate-100 p-2">
							<SearchIcon className="h-5 w-5 text-slate-600" />
						</div>
						<div className="min-w-0 flex-1">
							<div className="flex items-center gap-2">
								<h3 className="font-medium text-slate-900">
									{search.search_type === "hashtag" ? "#" : ""}
									{search.term}
								</h3>
								<Badge
									variant={
										search.search_type === "hashtag" ? "info" : "secondary"
									}
								>
									{search.search_type}
								</Badge>
							</div>
							<div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
								<span>
									Created: {new Date(search.created_at).toLocaleDateString()}
								</span>
								{search.last_crawled_at && (
									<span>
										Last crawled:{" "}
										{new Date(search.last_crawled_at).toLocaleDateString()}
									</span>
								)}
							</div>
						</div>
					</div>
					<div className="flex items-center gap-2">
						<Switch
							checked={search.is_active}
							onCheckedChange={() => onToggleActive(search)}
						/>
						<Button
							variant="ghost"
							size="icon"
							onClick={() => onTriggerCrawl(search)}
							title="Trigger crawl"
						>
							<Play className="h-4 w-4" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							onClick={() => onEdit(search)}
							title="Edit"
						>
							<Pencil className="h-4 w-4" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							onClick={() => onDelete(search)}
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
