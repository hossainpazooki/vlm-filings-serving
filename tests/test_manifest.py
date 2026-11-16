from pathlib import Path

from traverse.manifest import Item, Manifest, file_item

def test_round_trip_and_sha_stable(tmp_path: Path):
    m = Manifest(stage="fetch", run_id="r1", items=[Item("a", "a.pdf", 3, "abc", {})],
                 created_at="2026-09-06T00:00:00Z", meta={"source": "file:///x"})
    p = tmp_path / "m.json"
    sha = m.save(p)
    back = Manifest.load(p)
    assert back == m
    assert back.sha() == sha
    assert sha.startswith("sha256:")

def test_sha_changes_when_item_changes(tmp_path: Path):
    m1 = Manifest("fetch", "r1", [Item("a", "a.pdf", 3, "abc", {})], "t", {})
    m2 = Manifest("fetch", "r1", [Item("a", "a.pdf", 4, "abc", {})], "t", {})
    assert m1.sha() != m2.sha()

def test_equality_is_content_identity_not_item_order(tmp_path: Path):
    # A stage may hold its items in its own order (serve lists every cell, then
    # every cell's outputs), while to_dict() sorts them by id. Equality follows
    # the sha, so the in-memory manifest equals its saved-and-loaded copy and
    # keeps its own order.
    cells = [Item(f"cell-{mode}", f"cell-{mode}.json", n, "h", {}) for n, mode in
             enumerate(("isolated", "shared", "shared-evicting"), start=1)]
    outs = [Item(i.id + ".outputs", i.id + ".outputs.json", i.bytes, "o", {}) for i in cells]
    m = Manifest("serve", "r1", cells + outs, "t", {"k": 1})
    p = tmp_path / "m.json"
    sha = m.save(p)
    back = Manifest.load(p)
    assert [i.id for i in m.items] == ["cell-isolated", "cell-shared", "cell-shared-evicting",
                                      "cell-isolated.outputs", "cell-shared.outputs",
                                      "cell-shared-evicting.outputs"]
    assert [i.id for i in back.items] == sorted(i.id for i in m.items)
    assert back == m
    assert back.sha() == sha == m.sha()
    # Equality still bites on content: a dropped item, a different run, a changed
    # extra, and a meta value equal in Python but different in canonical bytes.
    assert Manifest("serve", "r1", cells + outs[:2], "t", {"k": 1}) != m
    assert Manifest("serve", "r2", cells + outs, "t", {"k": 1}) != m
    changed = outs[:2] + [Item(outs[2].id, outs[2].path, outs[2].bytes, "o", {"n": 1})]
    assert Manifest("serve", "r1", cells + changed, "t", {"k": 1}) != m
    assert Manifest("serve", "r1", cells + outs, "t", {"k": True}) != m
    assert m != m.to_dict()

def test_file_item_hashes_and_relativises(tmp_path: Path):
    d = tmp_path / "data"
    d.mkdir()
    f = d / "page.pdf"
    f.write_bytes(b"xyz")
    it = file_item("page", f, rel_to=tmp_path, dpi=150)
    assert it.path == "data/page.pdf"
    assert it.bytes == 3
    assert it.sha256 == "3608bca1e44ea6c4d268eb6db02260269892c0b42b86bbf1e77a6fa16c3c9282"
    assert it.extra == {"dpi": 150}
