from rich.table import Table
from rich import print as rprint
from rich.text import Text
from store.entities import Pet, Rarities

def print_pet(pet: Pet, diff: dict = None):
    """
    diff format: { "common": { "owned": +3 }, "rare": { "want": -1 } }
    """
    rprint(f"[bold]{pet.id}[/bold] [dim]({pet.display_name})[/dim]")

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("Rarity")
    table.add_column("Owned",     justify="right")
    table.add_column("Available", justify="right")
    table.add_column("Want",      justify="right")

    colors = {
        "common":    "white",
        "uncommon":  "green",
        "rare":      "blue",
        "epic":      "magenta",
        "legendary": "yellow",
        "mythic":    "red",
    }

    for rarity in Rarities:
        qty = getattr(pet, rarity.value)
        color = colors[rarity.value]
        rarity_diff = diff.get(rarity.value, {}) if diff else {}

        def fmt(field, val):
            d = rarity_diff.get(field, 0)
            base = str(val)
            if d > 0:
                return f"{base} [green](+{d})[/green]"
            elif d < 0:
                return f"{base} [red]({d})[/red]"
            return base

        table.add_row(
            f"[{color}]{rarity.value}[/{color}]",
            fmt("owned",     qty._owned),
            fmt("available", qty._available),
            fmt("want",      qty._want),
        )

    rprint(table)