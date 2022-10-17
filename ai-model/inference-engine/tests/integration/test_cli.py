from click.testing import CliRunner
from inference_engine import cli


def test_create_engine():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "new",
                "engine",
                "--path",
                "test_engine",
                "--name",
                "Test Engine",
                "--version",
                "v1",
                "--description",
                "Integration test for creating Inf Eng",
                "--author",
                "Tester",
                "--input_schema",
                "TextIO",
                "--output_schema",
                "MediaFileIO",
            ],
        )
        assert result.exit_code == 0
