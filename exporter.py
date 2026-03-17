import shutil
from pathlib import Path
from datetime import date
from jinja2 import Environment, FileSystemLoader
from store import Store
from store.entities import Rarities

BASE_DIR = Path(__file__).parent

RARITY_GLOW = {
    "common":    "#9ca3af",
    "uncommon":  "#4ade80",
    "rare":      "#60a5fa",
    "epic":      "#c084fc",
    "legendary": "#fbbf24",
    "mythic":    "#f87171",
}

def export(store: Store, output_path: Path = Path("./output/catalog.html")):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # copy pet images
    src_img = BASE_DIR / "templates" / "static" / "img"
    dst_img = output_path.parent / "static" / "img"
    if src_img.exists():
        dst_img.mkdir(parents=True, exist_ok=True)
        for pet in store.Pets.values():
            img = src_img / f"{pet.id}.png"
            if img.exists():
                shutil.copy2(img, dst_img / img.name)
            else:
                print(f"Warning: image not found: {img}")
    else:
        print(f"Warning: image source folder not found: {src_img}")

    # render template
    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))
    template = env.get_template("catalog.html")
    html = template.render(
        pets=store.Pets.values(),
        rarities=Rarities,
        rarity_glow=RARITY_GLOW,
        pet_count=len(store.Pets),
        last_updated=date.today().strftime("%Y-%m-%d"),
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path