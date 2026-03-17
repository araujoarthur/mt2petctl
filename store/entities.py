from enum import Enum

class Rarities(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class StoreQuantities(Enum):
    OWNED = "owned"
    AVAILABLE = "available"
    WANT = "want"

class StoreQuantity:
    def __init__(self, title: str):
        self._title = title
        self._owned = 0
        self._available = 0
        self._want = 0

    def __str__(self):
        return f"{self._title}<{self._owned},{self._available},{self._want}>"

    def __repr__(self):
        return self.__str__()

    def _update(self, field: str, value: int, mode: str = "set") -> "StoreQuantity":
        attr = f"_{field}"
        if not hasattr(self, attr):
            raise AttributeError(f"Unknown field: '{field}'")
        match mode:
            case "set":      setattr(self, attr, value)
            case "add":      setattr(self, attr, getattr(self, attr) + value)
            case "sub":   setattr(self, attr, getattr(self, attr) - value)
            case _: raise ValueError(f"Unknown mode: '{mode}'")
        return self

    def set(self, field: str, value: int) -> "StoreQuantity":
        return self._update(field, value, mode="set")

    def add(self, field: str, value: int) -> "StoreQuantity":
        return self._update(field, value, mode="add")
    
    def sub(self, field: str, value: int) -> "StoreQuantity":
        return self._update(field, value, mode="sub")
    
    def zero(self, field: str = "all") -> "StoreQuantity":
        if field == "all":
            for f in ("owned", "available", "want"):
                self._update(f, 0, mode="set")
            return self
        return self._update(field, 0, mode="set")

    def with_owned(self, val: int) -> "StoreQuantity":
        self.set("owned", val)
        return self
    
    def with_available(self, val: int) -> "StoreQuantity":
        self.set("available", val)
        return self
    
    def with_want(self, val: int) -> "StoreQuantity":
        self.set("want", val)
        return self
    
    def to_dict(self) -> dict:
        return {qty.value: getattr(self, f"_{qty.value}") for qty in StoreQuantities}
    

class Pet:
    def __init__(self, id, dn: str):
        self.id = id
        self.display_name = dn

        for rarity in Rarities:
            setattr(self, rarity.value, StoreQuantity(rarity.value).zero())

    def __str__(self):
        return f"{self.id}({self.display_name}) <{self.common}, {self.uncommon}, {self.rare}, {self.epic}, {self.legendary}, {self.mythic}>"
    
    def __repr__(self):
        return self.__str__()
    
    def set_quantity(self, rarity: Rarities, field: StoreQuantities, value: int) -> "Pet":
        qty: StoreQuantity = getattr(self, rarity.value)
        qty.set(field.value, value)
        return self
    
    def add(self, rarity: Rarities, field: StoreQuantities, value: int) -> "Pet":
        qty: StoreQuantity = getattr(self, rarity.value)
        qty.add(field.value, value)
        return self
    
    def sub(self, rarity: Rarities, field: StoreQuantities, value: int) -> "Pet":
        qty: StoreQuantity = getattr(self, rarity.value)
        qty.sub(field.value, value)
        return self
    
    def zero(self, rarity: str = "all", field: str = "all") -> "Pet":
        rarities = [r for r in Rarities if r.value == rarity] if rarity != "all" else list(Rarities)
        for r in rarities:
            getattr(self, r.value).zero(field)
        return self
    
    def to_dict(self) -> dict:
        return {
            "displayName": self.display_name,
            **{rarity.value: getattr(self, rarity.value).to_dict() for rarity in Rarities}
        }
