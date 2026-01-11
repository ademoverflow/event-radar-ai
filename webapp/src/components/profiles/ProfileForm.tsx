import { useId, useState } from "react";
import type { Profile, ProfileCreate } from "@/api/profiles";
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

interface ProfileFormProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	onSubmit: (data: ProfileCreate) => void;
	profile?: Profile;
	isPending?: boolean;
}

export function ProfileForm({
	open,
	onOpenChange,
	onSubmit,
	profile,
	isPending,
}: ProfileFormProps) {
	const id = useId();
	const [url, setUrl] = useState(profile?.url ?? "");
	const [profileType, setProfileType] = useState<"company" | "personal">(
		profile?.profile_type ?? "company",
	);
	const [displayName, setDisplayName] = useState(profile?.display_name ?? "");
	const [crawlFrequency, setCrawlFrequency] = useState(
		profile?.crawl_frequency_hours?.toString() ?? "24",
	);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onSubmit({
			url,
			profile_type: profileType,
			display_name: displayName,
			crawl_frequency_hours: Number.parseInt(crawlFrequency, 10),
		});
	};

	const isEditing = !!profile;

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>
						{isEditing ? "Edit Profile" : "Add Profile"}
					</DialogTitle>
					<DialogDescription>
						{isEditing
							? "Update the LinkedIn profile settings."
							: "Add a LinkedIn profile to monitor for event signals."}
					</DialogDescription>
				</DialogHeader>
				<form onSubmit={handleSubmit}>
					<div className="grid gap-4 py-4">
						<div className="grid gap-2">
							<Label htmlFor={`${id}-url`}>LinkedIn URL</Label>
							<Input
								id={`${id}-url`}
								type="url"
								placeholder="https://www.linkedin.com/company/example"
								value={url}
								onChange={(e) => setUrl(e.target.value)}
								required
								disabled={isEditing}
							/>
						</div>
						<div className="grid gap-2">
							<Label htmlFor={`${id}-type`}>Profile Type</Label>
							<Select
								value={profileType}
								onValueChange={(v) =>
									setProfileType(v as "company" | "personal")
								}
								disabled={isEditing}
							>
								<SelectTrigger id={`${id}-type`}>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="company">Company</SelectItem>
									<SelectItem value="personal">Personal</SelectItem>
								</SelectContent>
							</Select>
						</div>
						<div className="grid gap-2">
							<Label htmlFor={`${id}-name`}>Display Name</Label>
							<Input
								id={`${id}-name`}
								placeholder="Company or Person Name"
								value={displayName}
								onChange={(e) => setDisplayName(e.target.value)}
								required
							/>
						</div>
						<div className="grid gap-2">
							<Label htmlFor={`${id}-frequency`}>Crawl Frequency (hours)</Label>
							<Select value={crawlFrequency} onValueChange={setCrawlFrequency}>
								<SelectTrigger id={`${id}-frequency`}>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="6">Every 6 hours</SelectItem>
									<SelectItem value="12">Every 12 hours</SelectItem>
									<SelectItem value="24">Every 24 hours</SelectItem>
									<SelectItem value="48">Every 48 hours</SelectItem>
									<SelectItem value="168">Weekly</SelectItem>
								</SelectContent>
							</Select>
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
									: "Add Profile"}
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
