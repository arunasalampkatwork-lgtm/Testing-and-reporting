from pathlib import Path

from app.services.asset_manager import AssetManager


def test_asset_creation(tmp_path):

    manager = AssetManager(tmp_path)

    substation = manager.create_node(
        "REF-2",
        "SUBSTATION"
    )

    switchboard = manager.create_node(
        "PCC-1",
        "SWITCHBOARD",
        substation.node_id
    )

    panel = manager.create_node(
        "1FA",
        "PANEL",
        switchboard.node_id
    )

    equipment = manager.create_node(
        "14G1A",
        "FEED_EQUIPMENT",
        panel.node_id
    )

    expected = (
        tmp_path
        / "REF-2"
        / "PCC-1"
        / "1FA"
        / "14G1A"
    )

    assert expected.exists()