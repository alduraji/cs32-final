import typer  
from rich.console import Console  
from rich.table import Table  
from model import Medicine  
from database import get_all_medicines, delete_medicine, insert_medicine, take_medicine, update_medicine  
  
console = Console()  
  
app = typer.Typer()  
  
  
@app.command(short_help='adds a pill')  
def add(medicine_name: str, dosage: str, time: str):  
    typer.echo(f"adding {medicine_name}, {dosage}, {time}")  
    medicine = Medicine(medicine_name, dosage, time)  
    insert_medicine(medicine)  
    show()  
  
  
@app.command()  
def delete(position: int):  
    typer.echo(f"deleting {position}")  
    delete_medicine(position-1)  
    show()  
  
  
@app.command()  
def update(position: int, medicine_name: str = None, dosage: str = None, time: str = None):  
    typer.echo(f"updating {position}")  
    update_medicine(position-1, medicine_name, dosage, time)  
    show()  
  
  
@app.command()  
def take(position: int):  
    typer.echo(f"taking {position}")  
    take_medicine(position-1)  
    show()  
  
  
@app.command()  
def show():  
    medicines = get_all_medicines()  
    console.print("[bold magenta]Pill Aid[/bold magenta]!", "💊")  
  
    table = Table(show_header=True, header_style="bold blue")  
    table.add_column("#", style="dim", width=5)  
    table.add_column("Pill", min_width=27)  
    table.add_column("Dosage", min_width=10, justify="right")  
    table.add_column("Time", min_width=10, justify="right")  
    table.add_column("Taken", min_width=10, justify="right")  
  
    for idx, medicine in enumerate(medicines, start=1):  
        is_taken_str = '✅' if medicine.status == 2 else '❌'  
        table.add_row(str(idx), medicine.medicine_name, medicine.dosage, medicine.time, is_taken_str)  
    console.print(table)  
  
  
if __name__ == "__main__":  
    app()