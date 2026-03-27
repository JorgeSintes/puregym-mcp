from types import SimpleNamespace

from puregym_mcp.mcp.tools import register_tools


class FakeMCP:
    def __init__(self):
        self.tools: dict[str, object] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class FakeService:
    def __init__(self, *, authenticated: bool):
        self.is_authenticated = authenticated

    async def get_center_live_status(self, center_id: int):
        return SimpleNamespace(model_dump=lambda mode="json": {"center_id": center_id})

    async def get_center_open_hours(self, center_id: int):
        return [SimpleNamespace(model_dump=lambda mode="json": {"center_id": center_id})]


def test_register_tools_only_exposes_read_only_tools_in_anonymous_mode():
    mcp = FakeMCP()
    service = FakeService(authenticated=False)

    register_tools(mcp, service)  # type: ignore[arg-type]

    assert set(mcp.tools) == {"get_capabilities", "list_class_types", "list_centers", "search_classes"}


def test_register_tools_exposes_booking_tools_in_authenticated_mode():
    mcp = FakeMCP()
    service = FakeService(authenticated=True)

    register_tools(mcp, service)  # type: ignore[arg-type]

    assert set(mcp.tools) == {
        "get_capabilities",
        "list_class_types",
        "list_centers",
        "search_classes",
        "list_my_bookings",
        "book_class",
        "cancel_booking",
        "get_center_live_status",
        "get_center_open_hours",
    }
