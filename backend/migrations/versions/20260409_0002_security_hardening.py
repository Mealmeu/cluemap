from alembic import op
import sqlalchemy as sa


revision = "20260409_0002"
down_revision = "20260409_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=False),
        sa.Column("successful", sa.Boolean(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_login_attempts_id"), "login_attempts", ["id"], unique=False)
    op.create_index(op.f("ix_login_attempts_email"), "login_attempts", ["email"], unique=False)
    op.create_index(op.f("ix_login_attempts_ip_address"), "login_attempts", ["ip_address"], unique=False)
    op.create_index(op.f("ix_login_attempts_attempted_at"), "login_attempts", ["attempted_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_login_attempts_attempted_at"), table_name="login_attempts")
    op.drop_index(op.f("ix_login_attempts_ip_address"), table_name="login_attempts")
    op.drop_index(op.f("ix_login_attempts_email"), table_name="login_attempts")
    op.drop_index(op.f("ix_login_attempts_id"), table_name="login_attempts")
    op.drop_table("login_attempts")
