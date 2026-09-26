"""Add foreign key to incidents table

Revision ID: d2a562a8d9e6
Revises: 9a6171f20a25
Create Date: 2026-09-26 08:31:34.504774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2a562a8d9e6'
down_revision: Union[str, Sequence[str], None] = '9a6171f20a25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key("reporter_id_fk", source_table="incidents", referent_table="users",
                          local_cols=["reporter_id"], remote_cols=["id"], ondelete="CASCADE")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("reporter_id_fk", table_name="incidents")
    pass
