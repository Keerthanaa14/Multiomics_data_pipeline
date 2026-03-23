import json
from pathlib import Path


class BronzeWriter:

    def save(self, studies_by_repo):
        for repo, studies in studies_by_repo.items():

            for s in studies:
                path = Path("data/bronze") / repo / s["study_id"]
                path.mkdir(parents=True, exist_ok=True)

                with open(path / "metadata.json", "w") as f:
                    json.dump(s, f, indent=2)