from enum import Enum


class Rarities(Enum):
    """Rarity tiers for pets, ordered from most common to most rare."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class StoreQuantities(Enum):
    """Quantity fields tracked per rarity tier."""
    OWNED = "owned"          # How many the user currently owns
    AVAILABLE = "available"  # How many are available to trade
    WANT = "want"            # How many the user wants to acquire


class StoreQuantity:
    """
    Tracks owned, available, and want counts for a single rarity tier.

    Attributes:
        _title (str): The rarity label this quantity belongs to.
        _owned (int): Number of pets owned.
        _available (int): Number of pets available.
        _want (int): Number of pets wanted.
    """

    def __init__(self, title: str):
        """
        Args:
            title: The rarity label (e.g. 'common', 'rare').
        """
        self._title = title
        self._owned = 0
        self._available = 0
        self._want = 0

    def __str__(self):
        return f"{self._title}<{self._owned},{self._available},{self._want}>"

    def __repr__(self):
        return self.__str__()

    def _update(self, field: str, value: int, mode: str = "set") -> "StoreQuantity":
        """
        Internal method to mutate a quantity field.

        Args:
            field: One of 'owned', 'available', 'want'.
            value: The value to apply.
            mode: 'set', 'add', or 'sub'.

        Returns:
            self, for chaining.

        Raises:
            AttributeError: If the field does not exist.
            ValueError: If the mode is unknown.
        """
        attr = f"_{field}"
        if not hasattr(self, attr):
            raise AttributeError(f"Unknown field: '{field}'")
        match mode:
            case "set": new = value
            case "add": new = getattr(self, attr) + value
            case "sub": new = getattr(self, attr) - value
            case _: raise ValueError(f"Unknown mode: '{mode}'")
        if new < 0:
            raise ValueError(f"'{field}' cannot go below zero")
        setattr(self, attr, new)
        return self

    def set(self, field: str, value: int) -> "StoreQuantity":
        """Set a field to an exact value."""
        return self._update(field, value, mode="set")

    def add(self, field: str, value: int) -> "StoreQuantity":
        """Add to a field."""
        return self._update(field, value, mode="add")

    def sub(self, field: str, value: int) -> "StoreQuantity":
        """Subtract from a field."""
        return self._update(field, value, mode="sub")

    def zero(self, field: str = "all") -> "StoreQuantity":
        """
        Zero out one or all fields.

        Args:
            field: Field to zero, or 'all' to zero every field.
        """
        if field == "all":
            for f in ("owned", "available", "want"):
                self._update(f, 0, mode="set")
            return self
        return self._update(field, 0, mode="set")

    def with_owned(self, val: int) -> "StoreQuantity":
        """Set owned and return self for chaining."""
        self.set("owned", val)
        return self

    def with_available(self, val: int) -> "StoreQuantity":
        """Set available and return self for chaining."""
        self.set("available", val)
        return self

    def with_want(self, val: int) -> "StoreQuantity":
        """Set want and return self for chaining."""
        self.set("want", val)
        return self

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict keyed by StoreQuantities values."""
        return {qty.value: getattr(self, f"_{qty.value}") for qty in StoreQuantities}


class Pet:
    """
    Represents a pet and its quantity breakdown across all rarity tiers.

    Each rarity tier (common, uncommon, ..., mythic) is stored as a
    StoreQuantity attribute on the instance.

    Attributes:
        id (str): Unique identifier for the pet.
        display_name (str): Human-readable name.
        common (StoreQuantity): Quantities for the common tier.
        uncommon (StoreQuantity): Quantities for the uncommon tier.
        rare (StoreQuantity): Quantities for the rare tier.
        epic (StoreQuantity): Quantities for the epic tier.
        legendary (StoreQuantity): Quantities for the legendary tier.
        mythic (StoreQuantity): Quantities for the mythic tier.
    """

    def __init__(self, id: str, dn: str):
        """
        Args:
            id: Unique pet identifier.
            dn: Display name.
        """
        self.id = id
        self.display_name = dn
        for rarity in Rarities:
            setattr(self, rarity.value, StoreQuantity(rarity.value).zero())

    def __str__(self):
        return (
            f"{self.id}({self.display_name}) "
            f"<{self.common}, {self.uncommon}, {self.rare}, "
            f"{self.epic}, {self.legendary}, {self.mythic}>"
        )

    def __repr__(self):
        return self.__str__()

    def set_quantity(self, rarity: Rarities, field: StoreQuantities, value: int) -> "Pet":
        """
        Set a quantity field for a specific rarity tier.

        Args:
            rarity: The rarity tier.
            field: The quantity field to set.
            value: The value to assign.
        """
        qty: StoreQuantity = getattr(self, rarity.value)
        qty.set(field.value, value)
        return self

    def add(self, rarity: Rarities, field: StoreQuantities, value: int) -> "Pet":
        """
        Add to a quantity field for a specific rarity tier.

        Args:
            rarity: The rarity tier.
            field: The quantity field to add to.
            value: The amount to add.
        """
        qty: StoreQuantity = getattr(self, rarity.value)
        qty.add(field.value, value)
        return self

    def sub(self, rarity: Rarities, field: StoreQuantities, value: int) -> "Pet":
        """
        Subtract from a quantity field for a specific rarity tier.

        Args:
            rarity: The rarity tier.
            field: The quantity field to subtract from.
            value: The amount to subtract.
        """
        qty: StoreQuantity = getattr(self, rarity.value)
        qty.sub(field.value, value)
        return self

    def zero(self, rarity: str = "all", field: str = "all") -> "Pet":
        """
        Zero out quantities for one or all rarity tiers.

        Args:
            rarity: Rarity tier to zero, or 'all' for every tier.
            field: Field to zero, or 'all' for every field.
        """
        rarities = [r for r in Rarities if r.value == rarity] if rarity != "all" else list(Rarities)
        for r in rarities:
            getattr(self, r.value).zero(field)
        return self

    def to_dict(self) -> dict:
        """Serialize the pet to a JSON-compatible dict."""
        return {
            "displayName": self.display_name,
            **{rarity.value: getattr(self, rarity.value).to_dict() for rarity in Rarities}
        }