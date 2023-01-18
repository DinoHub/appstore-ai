import click
from transformers import AutoModel, AutoTokenizer


@click.command()
@click.option(
    "-m",
    "--model",
    type=str,
    required=True,
    help="The model name to be cached.",
)
@click.option(
    "-t",
    "--tokenizer-only",
    is_flag=True,
    help="Only cache the tokenizer.",
)
def main(model: str, tokenizer_only: bool):
    AutoTokenizer.from_pretrained(model)
    if not tokenizer_only:
        AutoModel.from_pretrained(model, output_hidden_states=True)


if __name__ == "__main__":
    main()

