# src/main.py
"""
Main pipeline orchestration.
Can be run as CLI: python -m src.main --run
Or imported by GUI: from src.main import run_pipeline
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))



from service.pipeline_service import PipelineService



def run_pipeline(output_dir: Path = None) -> dict:
    """
    Execute the full data pipeline.
    
    Parameters
    ----------
    output_dir : Path, optional
        Directory to save outputs. Defaults to data/processed/
    
    Returns
    -------
    dict
        Metrics and paths of generated outputs
    """
    service = PipelineService()
    results = service.execute(output_dir)
    return results

def run_cli():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description="Run data pipeline")
    parser.add_argument("--output", "-o", help="Output directory", default=None)
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else None
    results = run_pipeline(output_dir)
    
    print("Pipeline complete!")
    print(f"Outputs: {results}")

if __name__ == "__main__":
    run_cli()