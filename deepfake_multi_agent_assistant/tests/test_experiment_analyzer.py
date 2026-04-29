from pathlib import Path

from deepfake_agent_assistant.experiment_analyzer import analyze_csv


def test_analyze_csv(tmp_path: Path):
    path = tmp_path / "results.csv"
    path.write_text(
        "Method,Dataset,AUC,EER\n"
        "A,CDFv2,0.8,0.2\n"
        "B,CDFv2,0.9,0.1\n",
        encoding="utf-8",
    )
    summary = analyze_csv(path)
    assert "AUC" in summary
    assert "B" in summary
    assert "最高" in summary
