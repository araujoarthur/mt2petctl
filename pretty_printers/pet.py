from rich.table import Table
from rich import print as rprint
from rich.text import Text
from store.entities import Pet, Rarities

def print_pet(pet: Pet):
    rprint(f"[bold]{pet.display_name}[/bold] [dim]({pet.id})[/dim]")
    
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
        table.add_row(
            f"[{color}]{rarity.value}[/{color}]",
            str(qty._owned),
            str(qty._available),
            str(qty._want),
        )
    
    rprint(table)