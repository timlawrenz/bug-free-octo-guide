from bug_free_octo_guide.tools.prd_assembler_tool import assemble_prd

def test_assemble_prd():
    """
    Tests that the assemble_prd tool returns a formatted PRD.
    """
    goals = "Allow users to comment on documents."
    solution = "Add a `Comment` model."
    api_changes = "Add a `POST /documents/:id/comments` endpoint."
    db_schema = "Add a `comments` table."
    implementation = "Create a `CreateComment` command."
    testing = "Add a request spec for the new endpoint."

    prd = assemble_prd(goals, solution, api_changes, db_schema, implementation, testing)

    assert "Product Requirements Document" in prd
    assert "Goals" in prd
    assert "Solution" in prd
    assert "API Changes" in prd
    assert "DB Schema" in prd
    assert "Implementation" in prd
    assert "Testing" in prd
