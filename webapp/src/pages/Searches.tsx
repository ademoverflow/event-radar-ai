import { Plus, Search } from "lucide-react";
import { useState } from "react";
import type { SearchCreate, Search as SearchType } from "@/api/searches";
import { SearchCard } from "@/components/searches/SearchCard";
import { SearchForm } from "@/components/searches/SearchForm";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/empty-state";
import {
	useCreateSearch,
	useDeleteSearch,
	useSearches,
	useTriggerSearchCrawl,
	useUpdateSearch,
} from "@/hooks/useSearches";

export function SearchesPage() {
	const { data, isLoading, error } = useSearches();
	const createSearch = useCreateSearch();
	const updateSearch = useUpdateSearch();
	const deleteSearch = useDeleteSearch();
	const triggerCrawl = useTriggerSearchCrawl();

	const [isFormOpen, setIsFormOpen] = useState(false);
	const [editingSearch, setEditingSearch] = useState<SearchType | undefined>();
	const [deletingSearch, setDeletingSearch] = useState<
		SearchType | undefined
	>();

	const handleCreate = (formData: SearchCreate) => {
		createSearch.mutate(formData, {
			onSuccess: () => {
				setIsFormOpen(false);
			},
		});
	};

	const handleEdit = (search: SearchType) => {
		setEditingSearch(search);
	};

	const handleUpdate = (formData: SearchCreate) => {
		if (!editingSearch) return;
		updateSearch.mutate(
			{
				id: editingSearch.id,
				data: {
					term: formData.term,
				},
			},
			{
				onSuccess: () => {
					setEditingSearch(undefined);
				},
			},
		);
	};

	const handleToggleActive = (search: SearchType) => {
		updateSearch.mutate({
			id: search.id,
			data: { is_active: !search.is_active },
		});
	};

	const handleDelete = (search: SearchType) => {
		setDeletingSearch(search);
	};

	const confirmDelete = () => {
		if (!deletingSearch) return;
		deleteSearch.mutate(deletingSearch.id, {
			onSuccess: () => {
				setDeletingSearch(undefined);
			},
		});
	};

	const handleTriggerCrawl = (search: SearchType) => {
		triggerCrawl.mutate(search.id);
	};

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
				<p className="text-red-600">Failed to load searches</p>
			</div>
		);
	}

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-2xl font-semibold text-slate-900">
						Saved Searches
					</h1>
					<p className="text-sm text-slate-500 mt-1">
						Keywords and hashtags being monitored on LinkedIn
					</p>
				</div>
				<Button onClick={() => setIsFormOpen(true)}>
					<Plus className="w-4 h-4 mr-2" />
					Add Search
				</Button>
			</div>

			{!data?.items.length ? (
				<EmptyState
					icon={Search}
					title="No searches yet"
					description="Add keywords or hashtags to discover event-related content on LinkedIn."
					action={
						<Button onClick={() => setIsFormOpen(true)}>
							<Plus className="w-4 h-4 mr-2" />
							Add Search
						</Button>
					}
				/>
			) : (
				<div className="space-y-4">
					{data.items.map((search) => (
						<SearchCard
							key={search.id}
							search={search}
							onEdit={handleEdit}
							onDelete={handleDelete}
							onToggleActive={handleToggleActive}
							onTriggerCrawl={handleTriggerCrawl}
						/>
					))}
				</div>
			)}

			{/* Create Search Form */}
			<SearchForm
				open={isFormOpen}
				onOpenChange={setIsFormOpen}
				onSubmit={handleCreate}
				isPending={createSearch.isPending}
			/>

			{/* Edit Search Form */}
			<SearchForm
				open={!!editingSearch}
				onOpenChange={(open) => !open && setEditingSearch(undefined)}
				onSubmit={handleUpdate}
				search={editingSearch}
				isPending={updateSearch.isPending}
			/>

			{/* Delete Confirmation Dialog */}
			<Dialog
				open={!!deletingSearch}
				onOpenChange={(open) => !open && setDeletingSearch(undefined)}
			>
				<DialogContent>
					<DialogHeader>
						<DialogTitle>Delete Search</DialogTitle>
						<DialogDescription>
							Are you sure you want to delete the search "
							{deletingSearch?.search_type === "hashtag" ? "#" : ""}
							{deletingSearch?.term}"? This action cannot be undone.
						</DialogDescription>
					</DialogHeader>
					<DialogFooter>
						<Button
							variant="outline"
							onClick={() => setDeletingSearch(undefined)}
						>
							Cancel
						</Button>
						<Button
							variant="destructive"
							onClick={confirmDelete}
							disabled={deleteSearch.isPending}
						>
							{deleteSearch.isPending ? "Deleting..." : "Delete"}
						</Button>
					</DialogFooter>
				</DialogContent>
			</Dialog>
		</div>
	);
}
