import tempfile
from pathlib import Path
from src.data_loader import save_sample_data
import pandas as pd
import subprocess


def test_train_smoke():
    tmpdir = Path(tempfile.mkdtemp())
    data_path = tmpdir / 'sample.csv'
    save_sample_data(str(data_path), n=200)
    out_dir = tmpdir / 'models'
    cmd = ['python', 'scripts/train.py', '--data-path', str(data_path), '--output', str(out_dir)]
    # Run training script; ensure it exits 0
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + '\n' + res.stderr
