import pytest
from app.retrieval.fusion import rrf_fuse


def test_rrf_fuse_single_list():
    rankings = [["p1", "p2", "p3"]]
    fused = rrf_fuse(rankings, k=60)
    assert len(fused) == 3
    assert fused[0][0] == "p1"
    assert fused[0][1] == pytest.approx(1.0 / 61)
    assert fused[1][0] == "p2"
    assert fused[1][1] == pytest.approx(1.0 / 62)


def test_rrf_fuse_combined_lists():
    # List 1: p1 (rank 1), p2 (rank 2)
    # List 2: p2 (rank 1), p1 (rank 2)
    rankings = [["p1", "p2"], ["p2", "p1"]]
    fused = rrf_fuse(rankings, k=60)
    assert len(fused) == 2
    # Both p1 and p2 should have equal score: 1/61 + 1/62
    expected_score = (1.0 / 61) + (1.0 / 62)
    assert fused[0][1] == pytest.approx(expected_score)
    assert fused[1][1] == pytest.approx(expected_score)


def test_rrf_fuse_distinct_items():
    rankings = [["p1"], ["p2"]]
    fused = rrf_fuse(rankings, k=60)
    assert len(fused) == 2
    assert fused[0][1] == pytest.approx(1.0 / 61)
    assert fused[1][1] == pytest.approx(1.0 / 61)
