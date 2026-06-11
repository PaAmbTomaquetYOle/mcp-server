"""Top-level package for the MCP server application.

This is the composition root of a hexagonal (ports & adapters) architecture.
The package is organised in concentric layers whose dependencies only ever
point inwards:

    infrastructure  ->  application  ->  domain

- ``domain``         : enterprise business rules (innermost, depends on nothing).
- ``application``    : use-case orchestration via abstract ports.
- ``infrastructure`` : adapters to the outside world (MCP, Slack, IO, config).

What to put here:
    Nothing but this package marker. Optionally a small, curated public API
    (``__all__`` / version metadata) if the project is consumed as a library.

What NOT to put here:
    Business logic, framework wiring, or eager imports of heavy submodules at
    import time (keep importing ``mcp_server`` cheap and side-effect free).
"""
