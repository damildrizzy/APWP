from sqlalchemy import Table, Integer, Column, String
from sqlalchemy.orm import registry

import model

mapper_registry = registry()

order_lines = Table(
    'order_lines',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),

)


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)
