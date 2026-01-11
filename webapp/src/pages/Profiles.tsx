import { Plus, Users } from "lucide-react";
import { useState } from "react";
import type { Profile, ProfileCreate } from "@/api/profiles";
import { ProfileCard } from "@/components/profiles/ProfileCard";
import { ProfileForm } from "@/components/profiles/ProfileForm";
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
	useCreateProfile,
	useDeleteProfile,
	useProfiles,
	useTriggerProfileCrawl,
	useUpdateProfile,
} from "@/hooks/useProfiles";

export function ProfilesPage() {
	const { data, isLoading, error } = useProfiles();
	const createProfile = useCreateProfile();
	const updateProfile = useUpdateProfile();
	const deleteProfile = useDeleteProfile();
	const triggerCrawl = useTriggerProfileCrawl();

	const [isFormOpen, setIsFormOpen] = useState(false);
	const [editingProfile, setEditingProfile] = useState<Profile | undefined>();
	const [deletingProfile, setDeletingProfile] = useState<Profile | undefined>();

	const handleCreate = (formData: ProfileCreate) => {
		createProfile.mutate(formData, {
			onSuccess: () => {
				setIsFormOpen(false);
			},
		});
	};

	const handleEdit = (profile: Profile) => {
		setEditingProfile(profile);
	};

	const handleUpdate = (formData: ProfileCreate) => {
		if (!editingProfile) return;
		updateProfile.mutate(
			{
				id: editingProfile.id,
				data: {
					display_name: formData.display_name,
					crawl_frequency_hours: formData.crawl_frequency_hours,
				},
			},
			{
				onSuccess: () => {
					setEditingProfile(undefined);
				},
			},
		);
	};

	const handleToggleActive = (profile: Profile) => {
		updateProfile.mutate({
			id: profile.id,
			data: { is_active: !profile.is_active },
		});
	};

	const handleDelete = (profile: Profile) => {
		setDeletingProfile(profile);
	};

	const confirmDelete = () => {
		if (!deletingProfile) return;
		deleteProfile.mutate(deletingProfile.id, {
			onSuccess: () => {
				setDeletingProfile(undefined);
			},
		});
	};

	const handleTriggerCrawl = (profile: Profile) => {
		triggerCrawl.mutate(profile.id);
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
				<p className="text-red-600">Failed to load profiles</p>
			</div>
		);
	}

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-2xl font-semibold text-slate-900">
						Monitored Profiles
					</h1>
					<p className="text-sm text-slate-500 mt-1">
						LinkedIn profiles being monitored for event signals
					</p>
				</div>
				<Button onClick={() => setIsFormOpen(true)}>
					<Plus className="w-4 h-4 mr-2" />
					Add Profile
				</Button>
			</div>

			{!data?.items.length ? (
				<EmptyState
					icon={Users}
					title="No profiles yet"
					description="Add LinkedIn profiles to start monitoring for event signals."
					action={
						<Button onClick={() => setIsFormOpen(true)}>
							<Plus className="w-4 h-4 mr-2" />
							Add Profile
						</Button>
					}
				/>
			) : (
				<div className="space-y-4">
					{data.items.map((profile) => (
						<ProfileCard
							key={profile.id}
							profile={profile}
							onEdit={handleEdit}
							onDelete={handleDelete}
							onToggleActive={handleToggleActive}
							onTriggerCrawl={handleTriggerCrawl}
						/>
					))}
				</div>
			)}

			{/* Create Profile Form */}
			<ProfileForm
				open={isFormOpen}
				onOpenChange={setIsFormOpen}
				onSubmit={handleCreate}
				isPending={createProfile.isPending}
			/>

			{/* Edit Profile Form */}
			<ProfileForm
				open={!!editingProfile}
				onOpenChange={(open) => !open && setEditingProfile(undefined)}
				onSubmit={handleUpdate}
				profile={editingProfile}
				isPending={updateProfile.isPending}
			/>

			{/* Delete Confirmation Dialog */}
			<Dialog
				open={!!deletingProfile}
				onOpenChange={(open) => !open && setDeletingProfile(undefined)}
			>
				<DialogContent>
					<DialogHeader>
						<DialogTitle>Delete Profile</DialogTitle>
						<DialogDescription>
							Are you sure you want to delete "{deletingProfile?.display_name}"?
							This action cannot be undone.
						</DialogDescription>
					</DialogHeader>
					<DialogFooter>
						<Button
							variant="outline"
							onClick={() => setDeletingProfile(undefined)}
						>
							Cancel
						</Button>
						<Button
							variant="destructive"
							onClick={confirmDelete}
							disabled={deleteProfile.isPending}
						>
							{deleteProfile.isPending ? "Deleting..." : "Delete"}
						</Button>
					</DialogFooter>
				</DialogContent>
			</Dialog>
		</div>
	);
}
