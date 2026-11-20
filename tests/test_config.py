from config import normalize_database_url


def test_railway_style_url_is_converted():
    assert (
        normalize_database_url("postgres://u:p@host:5432/db")
        == "postgresql+psycopg://u:p@host:5432/db"
    )


def test_plain_postgresql_url_is_converted():
    assert (
        normalize_database_url("postgresql://u:p@host:5432/db")
        == "postgresql+psycopg://u:p@host:5432/db"
    )


def test_explicit_driver_is_kept():
    url = "postgresql+psycopg://u:p@host:5432/db"
    assert normalize_database_url(url) == url


def test_sqlite_is_kept():
    assert normalize_database_url("sqlite://") == "sqlite://"
