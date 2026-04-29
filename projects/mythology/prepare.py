from __future__ import annotations

import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "artifacts"
TRAIN_PATH = DATA_DIR / "train.txt"
VAL_PATH = DATA_DIR / "val.txt"
META_PATH = DATA_DIR / "meta.json"


CORPUS = [
    "At dawn the sun boat rose from the eastern reeds, and the ferryman sang to keep the dark serpent beneath the river of night.",
    "In the cedar court the storm god struck his bronze spear into the paving stone, and the mountain answered with a slow roll of thunder.",
    "The fox spirit borrowed a traveling singer's face, crossed the lantern bridge, and traded three careful lies for a bowl of rice wine.",
    "A smith of the north cooled a moon-bright blade in snowmelt, then promised the village it would only be drawn against oathbreakers.",
    "When the river maiden combed silver water through her hair, the fishermen left woven shells on the bank and asked for a gentle tide.",
    "The youngest giant hid his heart in a salt cave, but every midsummer the cave hummed like a bell and betrayed the secret to the brave.",
    "Three sisters spun winter from raven feathers, and by morning the orchard stood in white silence while the apple roots dreamed underground.",
    "The temple cat slept beside the grain jars all year, but on the feast of lamps it walked the rafters and judged every whispered prayer.",
    "Across the black steppe a rider followed a stag with burning antlers until both vanished into a ring of standing stones before sunrise.",
    "The sea king counted storms like coins and spent one to test the harbor walls, then returned the calm when the children sang back to him.",
    "Under the fig tree the old storyteller untied a knot of red thread, and each loosened loop became the memory of a hero's unfinished vow.",
    "A frost witch wrote her bargains on lake ice with a bone needle, trusting that anyone desperate enough to read them would already belong to winter.",
    "At the edge of the marsh, a lantern spirit blinked twice for danger and once for home, guiding lost travelers between reeds that sounded like flutes.",
    "The moon hare pounded herbs in a stone bowl, mixing sleep for restless kings and courage for shepherds who feared the forest gate.",
    "A bronze rooster on the palace roof crowed before dawn whenever treachery entered the courtyard, though no hand had wound it in a hundred years.",
    "The widow fed crumbs to a one-eyed crow all winter, and in spring the bird returned with a key that opened the buried gate of an older city.",
    "Beneath the glacier a sleeping dragon dreamed in blue light, and each dream rose through the ice as pillars that rang when touched by wind.",
    "A child left a ribbon for the orchard ghost, and by harvest the trees bent low enough for every small hand in the village to gather fruit.",
    "When the bell in the drowned chapel sounded through clear weather, the boatmen rowed in silence because someone below the water had spoken a name.",
    "The hermit of the red cliff taught that every echo belonged to a different ancestor, so travelers answered the rocks with careful respect.",
    "A lion carved in obsidian guarded the desert well, and only those who shared water before drinking could see the spring beneath the sand.",
    "On the longest night a baker shaped twelve loaves like stars, and the town swore the northern lights burned brighter for every loaf given away.",
    "The pearl diver carried a charm of knotted grass, but the sea spirits favored her because she always returned the smallest shell to the shore.",
    "In the hollow hill a silent queen kept a library of winter seeds, waiting for the year when the world forgot how to begin again.",
]


def build_splits() -> tuple[str, str]:
    train_items: list[str] = []
    val_items: list[str] = []
    for index, item in enumerate(CORPUS):
        if index % 5 == 0:
            val_items.append(item)
        else:
            train_items.append(item)
    return "\n".join(train_items) + "\n", "\n".join(val_items) + "\n"


def ensure_prepared() -> dict[str, int]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    train_text, val_text = build_splits()
    TRAIN_PATH.write_text(train_text, encoding="utf-8")
    VAL_PATH.write_text(val_text, encoding="utf-8")
    metadata = {
        "train_examples": len(train_text.splitlines()),
        "val_examples": len(val_text.splitlines()),
        "train_bytes": len(train_text.encode("utf-8")),
        "val_bytes": len(val_text.encode("utf-8")),
    }
    META_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    metadata = ensure_prepared()
    print(json.dumps(metadata))


if __name__ == "__main__":
    main()
