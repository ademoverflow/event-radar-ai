"""cascade_delete_posts.

Revision ID: b8f2c3d4e5a6
Revises: a89a422dd59b
Create Date: 2026-01-11 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8f2c3d4e5a6"
down_revision: str | Sequence[str] | None = "a89a422dd59b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change FK constraints on linkedin_posts to CASCADE delete."""
    # Drop the old foreign key constraints
    op.drop_constraint(
        "linkedin_posts_profile_id_fkey", "linkedin_posts", type_="foreignkey"
    )
    op.drop_constraint(
        "linkedin_posts_search_id_fkey", "linkedin_posts", type_="foreignkey"
    )

    # Create new foreign key constraints with CASCADE delete
    op.create_foreign_key(
        "linkedin_posts_profile_id_fkey",
        "linkedin_posts",
        "linkedin_monitored_profiles",
        ["profile_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "linkedin_posts_search_id_fkey",
        "linkedin_posts",
        "linkedin_searches",
        ["search_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Revert FK constraints on linkedin_posts to SET NULL."""
    # Drop the CASCADE constraints
    op.drop_constraint(
        "linkedin_posts_profile_id_fkey", "linkedin_posts", type_="foreignkey"
    )
    op.drop_constraint(
        "linkedin_posts_search_id_fkey", "linkedin_posts", type_="foreignkey"
    )

    # Restore SET NULL constraints
    op.create_foreign_key(
        "linkedin_posts_profile_id_fkey",
        "linkedin_posts",
        "linkedin_monitored_profiles",
        ["profile_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "linkedin_posts_search_id_fkey",
        "linkedin_posts",
        "linkedin_searches",
        ["search_id"],
        ["id"],
        ondelete="SET NULL",
    )
