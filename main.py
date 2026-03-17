import typer
import click
import shlex
from click.testing import CliRunner
from pathlib import Path
from store import Store, StoreError
from rich import print as rprint
from rich.console import Console
from pretty_printers.pet import print_pet

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
                raw = input(">> ").strip()
                if raw in ("exit", "quit"):
                    break
                if raw in ("clr", "clear"):
                    clear_screen()
                    continue
                args = shlex.split(raw)
                ctx = click_app.make_context("mt2petctl", args)
                click_app.invoke(ctx)
            except click.exceptions.UsageError as e:
                rprint(f"[red]{e}[/red]")
            except click.exceptions.Exit:
                pass
            except (KeyboardInterrupt, EOFError):
                break

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
def help():
    """Show available commands"""
    click_app = typer.main.get_command(app)
    typer.echo(click_app.get_help(click.Context(click_app)))

if __name__ == "__main__":
    app()
