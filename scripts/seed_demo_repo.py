from pathlib import Path


def seed_demo_repo(path: str = "demo_repo") -> None:
    base = Path(path)
    base.mkdir(parents=True, exist_ok=True)
    (base / "example.py").write_text("print('Hello from demo repo')\n", encoding="utf-8")


if __name__ == "__main__":
    seed_demo_repo()



