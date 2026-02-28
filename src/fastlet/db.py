try:
    from piping_bag import (
        close_pool,
        create_queries_dependency,
        get_pool,
        init_pool,
        setup,
    )
except ImportError:
    raise ImportError(
        "fastlet.db requires the 'core' extra. "
        "Install with: pip install 'fastlet[db]'"
    ) from None

__all__ = [
    "close_pool",
    "create_queries_dependency",
    "get_pool",
    "init_pool",
    "setup",
]
