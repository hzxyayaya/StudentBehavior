import pytest

from student_behavior_model_stubs.cli import main


def test_main_raises_not_implemented_error() -> None:
    with pytest.raises(NotImplementedError, match="CLI is not implemented yet"):
        main([])
