import click
from flask import Blueprint
from uuid import uuid4

from ....application.usecases.product.repository import ProductRepository
from ....infrastructure.main.ioc_factory import create_ioc_container
from ....infrastructure.repositories.sqlrepository.models import Base
from ....infrastructure.repositories.sqlrepository.models.stubs import (
    TerminalCategoryOrmModelStub,
    LoadedProductOrmModelStub,
    DiscountOrmModelStub,
)


bp = Blueprint("dev", __name__, cli_group="dev")
ioc = create_ioc_container()


@bp.get("/ping")
def ping():
    return "pong"


@bp.cli.group()
def db():
    """Setup the database for development"""
    ...


@db.command("populate")
@click.option(
    "-n", "--num-of-products", "n", default=30, help="Number of products to generate."
)
@click.option(
    "-r",
    "--return-id",
    default=True,
    help="Whether to return the id of the product category.",
)
def populate_db(
    n,
    return_id: bool,
    repo: ProductRepository = ioc.provide(ProductRepository),
):
    """Populates the db with dummy data"""
    click.echo("Populating the database...")
    category_id = uuid4()
    category = TerminalCategoryOrmModelStub(id=category_id)
    discount = DiscountOrmModelStub()
    products = LoadedProductOrmModelStub.build_batch(
        n, discount=discount, category=category
    )

    with repo._session as s:
        s.add_all(products)
        s.commit()

    click.echo("Database populated.")

    if return_id:
        click.echo(f"Category id: {category_id.hex}")


@db.command("clean")
@click.option("-y", "--yes", "skip", default=False, help="Skip confirmation prompt.")
def clean_db(skip: bool, repo: ProductRepository = ioc.provide(ProductRepository)):
    if not skip:
        confirm = click.confirm(
            "You are about to erase all the database records.",
            default=False,
            prompt_suffix="Do you really wish to proceed?",
            show_default=True,
        )
        if not confirm:
            return click.echo("Aborting...")

    Base.metadata.drop_all(repo._engine)
    Base.metadata.create_all(repo._engine)

    click.echo("Database cleaned. Exiting...")
