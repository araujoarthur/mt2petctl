import typer
import click
import shlex
from pathlib import Path
from store import Store, StoreError, Rarities, StoreQuantities
from rich import print as rprint
from rich.console import Console
from pretty_printers.pet import print_pet
from exporter import export

from parser import expand_args

app = typer.Typer(name="mt2petctl")
store: Store = None

console = Console()

def clear_screen():
    console.clear()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, path: Path = typer.Option("./store.json")):
    global store
    store = Store(path)
    if ctx.invoked_subcommand is None:
        click_app = typer.main.get_command(app)
        while True:
            try:
                #raw = input("mt2petctl >> ").strip()
                raw = console.input("[yellow]mt2petctl[/yellow] [red]>>[/red] ").strip()
                if raw in ("exit", "quit"):
                    break
                if raw in ("clr", "clear"):
                    clear_screen()
                    continue
                args = shlex.split(raw)
                args = expand_args(args)
                ctx = click_app.make_context("mt2petctl", args)
                click_app.invoke(ctx)
            except click.exceptions.UsageError as e:
                rprint(f"[red]{e}[/red]")
            except click.exceptions.Exit:
                pass
            except (KeyboardInterrupt, EOFError):
                break


# COMMANDS

from exporter import export

@app.command()
def export_catalog(output: Path = typer.Option("./output/catalog.html", help="Output path")):
    """Export pet catalog as HTML"""
    try:
        path = export(store, output)
        rprint(f"[green]Exported catalog to[/green] [bold]{path}[/bold]")
    except Exception as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)

@app.command()
def show(pet_id: str = typer.Argument(None)):
    """Show all pets or a single one"""
    if pet_id is None:
        for pet in store.Pets.values():
            print_pet(pet)
    else:
        pet_id = pet_id.lower()
        pet = store.get_pet(pet_id)
        if pet is None:
            typer.echo(f"Pet '{pet_id}' not found")
            raise typer.Exit(1)
        print_pet(pet)

@app.command()
def create(pet_id: str, display_name: str):
    """Create a new pet"""
    try:
        pet = store.create_pet(pet_id, display_name)
        rprint(f"[green]Created pet[/green] [bold]{pet_id}[/bold] ({display_name})")
    except StoreError as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)

@app.command()
def delete(pet_id: str):
    """Delete a pet"""
    try:
        store.delete_pet(pet_id)
        rprint(f"[green]Deleted pet[/green] [bold]{pet_id}[/bold]")
    except StoreError as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)
    
@app.command()
def set(pet_id: str, rarity: Rarities, field: StoreQuantities, value: int):
    """Set a quantity field for a pet"""
    try:
        store.set_pet_quantity(pet_id, rarity, field, value)
        rprint(f"[green]Set[/green] {pet_id} {rarity.value} {field.value} = {value}")
    except StoreError as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)

@app.command()
def add(pet_id: str, rarity: Rarities, field: StoreQuantities, value: int):
    """Add to a quantity field for a pet"""
    try:
        store.add_pet_quantity(pet_id, rarity, field, value)
        pet = store.get_pet(pet_id)
        print_pet(pet, diff={rarity.value: {field.value: +value}})
    except StoreError as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)

@app.command()
def sub(pet_id: str, rarity: Rarities, field: StoreQuantities, value: int):
    """Subtract from a quantity field for a pet"""
    try:
        store.sub_pet_quantity(pet_id, rarity, field, value)
        pet = store.get_pet(pet_id)
        print_pet(pet, diff={rarity.value: {field.value: -value}})
    except StoreError as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)
    
@app.command()
def help():
    """Show available commands"""
    click_app = typer.main.get_command(app)
    typer.echo(click_app.get_help(click.Context(click_app)))

if __name__ == "__main__":
    app()
