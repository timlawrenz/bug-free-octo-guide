def assemble_prd(goals: str, solution: str, api_changes: str, db_schema: str, implementation: str, testing: str) -> str:
    """Assembles a PRD from the provided sections."""
    return f"""
# Product Requirements Document

## Goals
{goals}

## Solution
{solution}

## API Changes
{api_changes}

## DB Schema
{db_schema}

## Implementation
{implementation}

## Testing
{testing}
"""
