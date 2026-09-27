"""Convert lat/lng to PostGIS geometry column

Revision ID: 5f16f41eb415
Revises: 85dbbedcfa39
Create Date: 2026-09-27 11:49:19.213134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '5f16f41eb415'
down_revision: Union[str, Sequence[str], None] = '85dbbedcfa39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add as nullable first
    op.add_column('incidents', sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True))

    # 2. Backfill from existing lat/lng
    op.execute("""
        UPDATE incidents
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    """)

    # 3. Now enforce NOT NULL, since every row has a value
    op.alter_column('incidents', 'location', nullable=False)

    # 4. Add the index, then drop the old columns
    op.drop_column('incidents', 'latitude')
    op.drop_column('incidents', 'longitude')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('incidents', sa.Column('longitude', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('incidents', sa.Column('latitude', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    op.execute("""
        UPDATE incidents
        SET latitude = ST_Y(location::geometry),
            longitude = ST_X(location::geometry)
    """)

    op.alter_column('incidents', 'latitude', nullable=False)
    op.alter_column('incidents', 'longitude', nullable=False)
    op.drop_column('incidents', 'location')
    # ### end Alembic commands ###
