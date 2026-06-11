"""Configuration and composition root.

Holds the application's configuration and the wiring that assembles it: reading
settings from the environment, constructing concrete adapters, and injecting
them into application services to build the runnable MCP server.

What to put here:
    - Settings objects (e.g. pydantic-settings) and environment loading.
    - Dependency-injection / composition wiring (build the object graph here).
    - Server bootstrap configuration.

What NOT to put here:
    - Business rules or use-case logic.
    - Secrets or credentials in source: load them from the environment / a
      secrets manager.
"""
