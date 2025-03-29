import typer
from pathlib import Path
from clair import notion_client, confluence_client
import logging


app = typer.Typer(help="Clair – your adversarial documentation auditor")

@app.command()
def audit(
    config: Path = typer.Option("config.yaml", help="Path to configuration file"),
    notion: bool = typer.Option(True, help="Include Notion in audit"),
    confluence: bool = typer.Option(True, help="Include Confluence in audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging")

):
    """
    Run a full audit of the documentation sources configured in Clair.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    typer.echo("🚀 Starting Clair audit...")
    typer.echo(f"🔧 Loading config from: {config}")

    if notion:
        typer.echo("🔍 Auditing Notion content...")
        notion_client.extract_and_analyze()

    if confluence:
        typer.echo("🔍 Auditing Confluence content...")
        confluence_client.extract_and_analyze()

    typer.echo("✅ Audit completed. Report available in /reports folder.")

if __name__ == "__main__":
    app()