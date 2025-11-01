from pathlib import Path

from metaclass_registry import _home


def test_get_home_dir():
    """Test get_home_dir returns the user's home directory."""
    # Should return a valid path that matches Path.home()
    result = _home.get_home_dir()
    expected = str(Path.home())
    assert result == expected
    assert Path(result).exists()
    assert Path(result).is_dir()
