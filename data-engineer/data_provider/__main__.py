import typer
import typing as t
from data_provider.runner import Runner
from data_provider.runner import generate_annotations
import pathlib

app = typer.Typer()

@app.command()
def serve(
    endpoint: t.Annotated[str, typer.Argument(help="HTTP endpoint to call.")],
    min_delay: t.Annotated[int, typer.Option(help="Minimum delay for data generation.")] = 1000,
    max_delay: t.Annotated[int, typer.Option(help="Maximum delay for data generation.")] = 1000,
):
    if min_delay > max_delay:
        raise ValueError("Minimum delay must be smaller than maximum delay")

    if max_delay <= 0 or min_delay <= 0:
        raise ValueError("Both minimum and maximum delays must be strictly positive.")

    runner = Runner(endpoint, min_delay, max_delay)
    try:
        runner.run()
    except KeyboardInterrupt:
        pass

@app.command()
def generate(
    n: t.Annotated[int, typer.Argument(help="Number of annotations to generate.")],
    output_dir: t.Annotated[t.Optional[pathlib.Path], typer.Option(help="Where to output annotations.")] = None,
):
    generate_annotations(n, output_dir)

app()
