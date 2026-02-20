from src.db.main_db import get_session_factory


def get_session(db: str):
    """_summary_

    Args:
        db (str): _description_

    Returns:
        _type_: _description_
    """
    return get_session_factory(db=db)()
