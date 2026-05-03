import json

from src.training.qlora import load_chatml_jsonl


def test_load_chatml_jsonl(tmp_path):
    sample = {
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "ask"},
            {"role": "assistant", "content": "answer"},
        ],
        "metadata": {"domain": "mfix-exa"},
    }
    path = tmp_path / "train.jsonl"
    path.write_text(json.dumps(sample, ensure_ascii=False) + "\n", encoding="utf-8")

    rows = load_chatml_jsonl(path)
    assert len(rows) == 1
    assert "[system]" in rows[0]["prompt"]
    assert rows[0]["target"] == "answer"
