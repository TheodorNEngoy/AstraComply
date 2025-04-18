import typer
import yaml
from pathlib import Path
import requests

app = typer.Typer(help="AstraComply CLI")

API_URL = "http://localhost:8000"

@app.command()
def check(config: Path):
    """
    Run a risk assessment from a YAML answers file.
    """
    data = yaml.safe_load(config.read_text())
    resp = requests.post(f"{API_URL}/assess", json={"answers": data.get("answers", [])})
    resp.raise_for_status()
    tier = resp.json()["risk_tier"]
    typer.echo(f"🔍 Risk tier: {tier}")

@app.command()
def generate(config: Path, out: Path = Path("report.md")):
    """
    Generate the full report from a YAML answers file.
    """
    data = yaml.safe_load(config.read_text())
    resp = requests.post(f"{API_URL}/generate", json={"answers": data.get("answers", [])})
    resp.raise_for_status()
    doc = resp.json()["document"]
    out.write_text(doc)
    typer.echo(f"📄 Report written to {out.resolve()}")

if __name__ == "__main__":
    app()
