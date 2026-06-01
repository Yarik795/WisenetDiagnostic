from app.models import CheckStatus, Recorder
from app.ui.grouping import (
    aggregate_status,
    effective_status,
    group_by_object,
    problem_count,
)


def _rec(
    object_name: str = "Obj",
    rec_id: str = "nvr-1",
    last_status: CheckStatus | None = None,
) -> Recorder:
    return Recorder(
        id=rec_id,
        object_name=object_name,
        name="NVR",
        host="10.0.0.1",
        port=80,
        use_https=False,
        last_status=last_status,
    )


def test_effective_status_excluded() -> None:
    r = _rec(last_status=CheckStatus.ONLINE)
    assert effective_status(r, excluded_ids={"nvr-1"}) == "excluded"


def test_effective_status_unknown() -> None:
    assert effective_status(_rec()) == "unknown"


def test_aggregate_worst_offline() -> None:
    a = _rec(last_status=CheckStatus.ONLINE)
    b = _rec(rec_id="nvr-2", last_status=CheckStatus.OFFLINE)
    assert aggregate_status([a, b]) == "error"


def test_group_by_object_search() -> None:
    r1 = Recorder(
        id="nvr-1",
        object_name="Москва",
        name=None,
        host="10.1.1.1",
        port=80,
        use_https=False,
    )
    r2 = Recorder(
        id="nvr-2",
        object_name="Казань",
        name=None,
        host="10.2.2.2",
        port=80,
        use_https=False,
    )
    groups = group_by_object([r1, r2], search="10.1", sort="name")
    assert len(groups) == 1
    assert groups[0].object_name == "Москва"


def test_problem_count() -> None:
    a = _rec(last_status=CheckStatus.ONLINE)
    b = _rec(rec_id="nvr-2", last_status=CheckStatus.OFFLINE)
    assert problem_count([a, b]) == 1
