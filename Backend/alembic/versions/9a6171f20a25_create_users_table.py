"""Create users table

Revision ID: 9a6171f20a25
Revises: ccaf340970dd
Create Date: 2026-09-25 19:56:06.976974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a6171f20a25'
down_revision: Union[str, Sequence[str], None] = 'ccaf340970dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("users",
                    sa.Column("id", sa.UUID(), nullable=False),
                    sa.Column("full_name", sa.String(), nullable=False),
                    sa.Column("phone_number", sa.String(), unique=True, nullable=False),
                    sa.Column("email", sa.String(), unique=True, nullable=False),
                    sa.Column("password", sa.String(), nullable=False),
                    sa.Column("role", sa.Enum("citizen", "responder", "admin", name="user_role"), nullable=False),
                    sa.Column("created_at", sa.TIMESTAMP(timezone=True), 
                              server_default=sa.text("now()"), nullable=False),
                    sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                              server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
                    sa.PrimaryKeyConstraint("id")
                    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    pass
