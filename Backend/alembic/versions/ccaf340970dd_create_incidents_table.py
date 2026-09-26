"""Create incidents table

Revision ID: ccaf340970dd
Revises: 
Create Date: 2026-09-25 19:30:56.887013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccaf340970dd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("incidents",
                    sa.Column("id", sa.UUID(), nullable=False),
                    sa.Column("title", sa.String(), nullable=False),
                    sa.Column("description", sa.String(), nullable=False),
                    sa.Column("category", sa.String(), nullable=False),
                    sa.Column("severity", sa.Enum("low", "medium", "high", "critical", name="incident_severity"), nullable=True),
                    sa.Column("status", sa.Enum("reported", "verified", "resolved", "unverified", "in_progress", "rejected", name="incident_status"), nullable=False),
                    sa.Column("latitude", sa.Float(), nullable=False),
                    sa.Column("longitude", sa.Float(), nullable=False),
                    sa.Column("address", sa.String(), nullable=False),
                    sa.Column("city", sa.String(), nullable=False),
                    sa.Column("state", sa.String(), nullable=False),
                    sa.Column("created_at", sa.TIMESTAMP(timezone=True), 
                              server_default=sa.text("now()"), nullable=False),
                    sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                              server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
                    sa.Column("reporter_id", sa.UUID(), nullable=False),
                    sa.PrimaryKeyConstraint("id")
                    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("incidents")
    pass
