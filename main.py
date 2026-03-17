import typer
import click
import shlex
from click.testing import CliRunner
from rich import print as rprint
from pathlib import Path
from store import Store, StoreError
from pretty_printers.pet import print_pet

app = typer.Typer(name="mt2petctl")
store: Store = None

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, path: Path = typer.Option("./store.json")):
    global store
    store = Store(path)
    if ctx.invoked_subcommand is None:
        click_app = typer.main.get_command(app)
        runner = CliRunner()
        while True:
            try:
                raw = input(">> ")
                if raw.strip() in ("exit", "quit"):
                    break
                args = shlex.split(raw)
                result = runner.invoke(click_app, args, catch_exceptions=False)
                typer.echo(result.output, nl=False)
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
