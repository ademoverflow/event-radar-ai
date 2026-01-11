import { useId, useState } from "react";
import type { Search, SearchCreate } from "@/api/searches";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

interface SearchFormProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	onSubmit: (data: SearchCreate) => void;
	search?: Search;
	isPending?: boolean;
}

export function SearchForm({
	open,
	onOpenChange,
	onSubmit,
	search,
	isPending,
}: SearchFormProps) {
	const id = useId();
	const [term, setTerm] = useState(search?.term ?? "");
	const [searchType, setSearchType] = useState<"keyword" | "hashtag">(
		search?.search_type ?? "keyword",
	);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onSubmit({
			term: term.replace(/^#/, ""), // Remove leading # if present
			search_type: searchType,
		});
	};

	const isEditing = !!search;

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>{isEditing ? "Edit Search" : "Add Search"}</DialogTitle>
					<DialogDescription>
						{isEditing
							? "Update the search settings."
							: "Add a keyword or hashtag to search for on LinkedIn."}
					</DialogDescription>
				</DialogHeader>
				<form onSubmit={handleSubmit}>
					<div className="grid gap-4 py-4">
						<div className="grid gap-2">
							<Label htmlFor={`${id}-type`}>Search Type</Label>
							<Select
								value={searchType}
								onValueChange={(v) => setSearchType(v as "keyword" | "hashtag")}
								disabled={isEditing}
							>
								<SelectTrigger id={`${id}-type`}>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="keyword">Keyword</SelectItem>
									<SelectItem value="hashtag">Hashtag</SelectItem>
								</SelectContent>
							</Select>
						</div>
						<div className="grid gap-2">
							<Label htmlFor={`${id}-term`}>
								{searchType === "hashtag" ? "Hashtag" : "Keyword"}
							</Label>
							<Input
								id={`${id}-term`}
								placeholder={
									searchType === "hashtag"
										? "events (without #)"
										: "conference 2024"
								}
								value={term}
								onChange={(e) => setTerm(e.target.value)}
								required
							/>
							{searchType === "hashtag" && (
								<p className="text-xs text-slate-500">
									Enter the hashtag without the # symbol
								</p>
							)}
						</div>
					</div>
					<DialogFooter>
						<Button
							type="button"
							variant="outline"
							onClick={() => onOpenChange(false)}
						>
							Cancel
						</Button>
						<Button type="submit" disabled={isPending}>
							{isPending
								? "Saving..."
								: isEditing
									? "Save Changes"
									: "Add Search"}
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
