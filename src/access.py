"""Access levels: what the server may do with the account.

Levels are cumulative. The default, payments, keeps every tool available.
"""
import os
from enum import IntEnum


class AccessLevel(IntEnum):
    READ = 0       # accounts, balances, transactions, beneficiaries, documents
    TRANSFERS = 1  # + transfers between your own accounts
    PAYMENTS = 2   # + payments to saved beneficiaries


_READ_SCOPES = "accounts balances transactions documents.statements documents.taxcertificates"

SCOPES = {
    AccessLevel.READ: _READ_SCOPES,
    AccessLevel.TRANSFERS: _READ_SCOPES + " transfers",
    AccessLevel.PAYMENTS: _READ_SCOPES + " transfers beneficiarypayments",
}


def access_level_from_env() -> AccessLevel:
    """Read INVESTEC_ACCESS_LEVEL, failing on unknown values."""
    raw = os.getenv("INVESTEC_ACCESS_LEVEL", "payments")
    try:
        return AccessLevel[raw.strip().upper()]
    except KeyError:
        raise ValueError(
            f"INVESTEC_ACCESS_LEVEL must be read, transfers or payments, not {raw!r}"
        ) from None
