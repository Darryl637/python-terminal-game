import uuid
from typing import TypeVar, List, Callable, Any, TYPE_CHECKING
from src.constants import STATS
import asyncio

if TYPE_CHECKING:
    from src.models import Statistics
T = TypeVar("T")


def generate_id():
    return str(uuid.uuid4())


# Using to check if index value is there, if not default value provided
def get_index(list: List[T], index: int, default: T) -> T:
    if index < 0:
        raise IndexError
    if index < len(list):
        return list[index]
    return default


def is_valid(*args):
    return True


def is_non_negative(number: int):
    return number >= 0


def is_positive(number: int):
    return number > 0


def add_stats(destination: dict[str, int], source: "Statistics"):
    for stat in STATS:
        destination_value = destination.get(stat, 0) or 0
        source_value = getattr(source, stat)
        destination[stat] = destination_value + source_value


def validate_campaign_player_count(number: int) -> bool:
    return number > 0 and number < 5
