from comment_tree.factories import CreateTablesFlag, factories
from comment_tree.postgres.storage import Storage
from comment_tree.postgres.tables import metadata

test_factories = factories.copy()


@test_factories.override(CreateTablesFlag)
async def drop_before_create_tables(storage: Storage):
    async with storage.engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
