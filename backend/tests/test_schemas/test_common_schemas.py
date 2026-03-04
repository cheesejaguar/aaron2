from app.schemas.common import MessageResponse, PaginationParams, TokenResponse


class TestPaginationParams:
    def test_defaults(self):
        p = PaginationParams()
        assert p.skip == 0
        assert p.limit == 50

    def test_custom_values(self):
        p = PaginationParams(skip=10, limit=25)
        assert p.skip == 10
        assert p.limit == 25


class TestMessageResponse:
    def test_message(self):
        m = MessageResponse(message="Item deleted")
        assert m.message == "Item deleted"


class TestTokenResponse:
    def test_token_response(self):
        t = TokenResponse(access_token="abc", refresh_token="def")
        assert t.token_type == "bearer"
        assert t.access_token == "abc"
