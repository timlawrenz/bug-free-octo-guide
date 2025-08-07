from bug_free_octo_guide.tools.prd_writer_tool import create_prd_draft

def test_create_prd_draft():
    """
    Tests that the create_prd_draft tool returns the expected placeholder text.
    """
    result = create_prd_draft("test request")
    assert "PRD Draft: placeholder" in result["output"]
