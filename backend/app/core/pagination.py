"""
Pagination utilities with enforced limits.
"""
from typing import Annotated
from fastapi import Query


# Pagination parameters with enforced max limits
def get_pagination_params(
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max 100 records per page")] = 20,
):
    """
    Get pagination parameters with validation.

    Args:
        skip: Number of records to skip (offset)
        limit: Number of records to return (max 100)

    Returns:
        tuple: (skip, limit)
    """
    return skip, limit


class PaginationParams:
    """Dependency class for pagination parameters."""

    def __init__(
        self,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        self.skip = skip
        self.limit = limit
