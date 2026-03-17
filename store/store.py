import json
from pathlib import Path
from .entities import Pet, Rarities, StoreQuantities


class StoreError(Exception):
    """Raised when a Store operation fails due to invalid state or input."""
    pass


class Store:
    """
    Manages a collection of pets and their quantities, backed by a JSON file.

    The store automatically persists to disk after every mutating operation.

    Attributes:
        Pets (dict[str, Pet]): Map of pet id to Pet object.
    """

    def __init__(self, path: Path):
        """
        Initialize the store from a JSON file.

        Args:
            path: Path to the JSON store file. Must exist and have a 'pets' key.

        Raises:
            FileNotFoundError: If the file does not exist.
            StoreError: If the file format is unexpected.
        """
        self.Pets = dict()
        self._path = Path(path)
        self._initialize_from_file(self._path)

    def _save(self):
        """Serialize and write the current state to disk."""
        with open(self._path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def _initialize_from_file(self, path: Path):
        """
        Parse the JSON file and populate self.Pets.

        Args:
            path: Path to the JSON store file.

        Raises:
            FileNotFoundError: If the file does not exist.
            StoreError: If the 'pets' key is missing.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError
        with open(path, "r") as f:
            data = json.load(f)
        if "pets" not in data:
            raise StoreError("unexpected store format")

        pets = data["pets"]
        for pet in pets:
            newpet = Pet(pet, pets[pet]["displayName"])
            for rarity in Rarities:
                for qty in StoreQuantities:
                    newpet.set_quantity(rarity, qty, pets[pet][rarity.value][qty.value])
            self.Pets[pet] = newpet

    def get_pet(self, pet_id: str) -> Pet | None:
        """
        Retrieve a pet by id.

        Args:
            pet_id: The pet's id.

        Returns:
            The Pet object, or None if not found.
        """
        return self.Pets.get(pet_id)

    def create_pet(self, pet_id: str, display_name: str) -> Pet:
        """
        Create and register a new pet.

        Args:
            pet_id: Unique identifier for the pet.
            display_name: Human-readable name.

        Returns:
            The newly created Pet.

        Raises:
            StoreError: If a pet with the same id already exists.
        """
        if pet_id in self.Pets:
            raise StoreError(f"pet '{pet_id}' already exists")
        pet = Pet(pet_id, display_name)
        self.Pets[pet_id] = pet
        self._save()
        return pet

    def delete_pet(self, pet_id: str) -> None:
        """
        Delete a pet by id.

        Args:
            pet_id: The pet's id.

        Raises:
            StoreError: If the pet does not exist.
        """
        if pet_id not in self.Pets:
            raise StoreError(f"pet '{pet_id}' not found")
        del self.Pets[pet_id]
        self._save()

    def set_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> "Store":
        """
        Set a quantity field for a pet to an exact value.

        Args:
            pet_name: The pet's id.
            rarity: The rarity tier.
            field: The quantity field (owned, available, want).
            value: The value to set.

        Raises:
            StoreError: If the pet does not exist.
        """
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")
        self.Pets[pet_name].set(rarity, field, value)
        self._save()
        return self

    def add_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> "Store":
        """
        Add to a quantity field for a pet.

        Args:
            pet_name: The pet's id.
            rarity: The rarity tier.
            field: The quantity field (owned, available, want).
            value: The amount to add.

        Raises:
            StoreError: If the pet does not exist.
        """
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")
        self.Pets[pet_name].add(rarity, field, value)
        self._save()
        return self

    def sub_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> "Store":
        """
        Subtract from a quantity field for a pet.

        Args:
            pet_name: The pet's id.
            rarity: The rarity tier.
            field: The quantity field (owned, available, want).
            value: The amount to subtract.

        Raises:
            StoreError: If the pet does not exist.
        """
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")
        self.Pets[pet_name].sub(rarity, field, value)
        self._save()
        return self

    def zero_pet_quantity(self, pet_name: str, rarity: str = "all", field: str = "all") -> "Store":
        """
        Zero out quantity fields for a pet.

        Args:
            pet_name: The pet's id.
            rarity: Rarity tier to zero, or 'all' for every tier.
            field: Field to zero, or 'all' for every field.

        Raises:
            StoreError: If the pet does not exist.
        """
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")
        self.Pets[pet_name].zero(rarity, field)
        self._save()
        return self

    def zero_all(self) -> "Store":
        """Zero out all quantity fields for every pet."""
        for pet in self.Pets.values():
            pet.zero()
        self._save()
        return self

    def to_dict(self) -> dict:
        """Serialize the store to a JSON-compatible dict."""
        return {"pets": {pet.id: pet.to_dict() for pet in self.Pets.values()}}

    def save(self, path: Path = None) -> None:
        """
        Persist the store to disk.

        Args:
            path: Optional new path to save to. Updates the store's path if provided.
        """
        self._path = Path(path) if path else self._path
        self._save()