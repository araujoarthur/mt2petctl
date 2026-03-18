import shutil
from pathlib import Path
from datetime import date
from jinja2 import Environment, FileSystemLoader
from store import Store
from store.entities import Rarities
from playwright.sync_api import sync_playwright
from config import get_html_output_path


BASE_DIR = Path(__file__).parent

RARITY_GLOW = {
    "common":    "#9ca3af",
    "uncommon":  "#4ade80",
    "rare":      "#60a5fa",
    "epic":      "#c084fc",
    "legendary": "#50462f",
    "mythic":    "#f87171",
}

def export(store: Store, output_path: Path = Path("./output/index.html")):
    output_path = Path(output_path) if output_path else get_html_output_path()
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

    # generate preview
    preview_path = dst_img / "preview.png"
    generate_preview(output_path, preview_path)

    return output_path


def generate_preview(html_path: Path, output_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto(f"file:///{html_path.resolve()}")
        page.screenshot(path=str(output_path))
        browser.close()