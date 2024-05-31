import time
import uuid
from dataclasses import dataclass
from typing import Dict


@dataclass
class Chatter:
    """
    Data class representing a user currently in chat
    """

    id: str
    login: str
    name: str
    seen: float

    @classmethod
    def from_data(cls, val: Dict[str, str]):
        """
        Creates a Chatter object from a provided Dict, defaults to unique unknown
        otherwise
        Args:
            val: Dict[str, str] containing chatter information
                {
                  "user_id": "128393656",
                  "user_login": "smittysmithers",
                  "user_name": "smittysmithers"
                }
        Returns:
            Chatter
        """
        fall_back_uuid: str = str(uuid.uuid4())
        return Chatter(
            id=val.get("user_id", f"UNKNOWN-{fall_back_uuid}"),
            login=val.get("user_login", f"UNKNOWN-{fall_back_uuid}"),
            name=val.get("user_name", f"UNKNOWN-{fall_back_uuid}"),
            seen=time.time(),
        )
