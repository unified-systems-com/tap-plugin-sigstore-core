"""Delete edges of the three edge types renamed in sigstore-core#4.

Edge ids derive from the slug (`decompose._edge_id`), so a renamed type is a NEW edge on the
consumer's next collection and the old rows would linger as unregistered types nothing reads.
This removes them (with their spine rows) so a grid upgraded in place is not left carrying two
generations of the same relation; the next collection repopulates the new types. Nodes are
untouched.

Direct ORM access is the sanctioned path in migrations.
"""

from typing import Any

from django.db import migrations

_RETIRED_EDGE_TYPES = (
    "ATTESTED_BY__sigstore_core",
    "CERT_ISSUED_BY__sigstore_core",
    "IDENTITY_VOUCHED_BY__sigstore_core",
)


def delete_retired_edges(apps: Any, schema_editor: Any) -> None:
    Edge = apps.get_model("tap_grid", "Edge")
    Entity = apps.get_model("tap_grid", "Entity")
    edges = Edge.objects.filter(edge_type__in=_RETIRED_EDGE_TYPES)
    entity_ids = list(edges.values_list("entity_id", flat=True))
    edges.delete()
    Entity.objects.filter(pk__in=entity_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("sigstore_core", "0002_initial"),
        ("tap_grid", "0001_initial"),
    ]

    operations = [migrations.RunPython(delete_retired_edges, migrations.RunPython.noop)]
