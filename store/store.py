import json
from pathlib import Path
from .entities import Pet, Rarities, StoreQuantities

class StoreError(Exception):
    pass

class Store:
    def __init__(self, path: Path):
        self.Pets = dict()
        self._path = Path(path)
        self._initialize_from_file(self._path)
    
    def _save(self):
        with open(self._path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
    def _initialize_from_file(self, path: Path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError

        with open(path, "r") as f:
            data = json.load(f)

        if not "pets" in data:
            raise StoreError("unexpected store format")
        
        pets = data["pets"]
        for pet in pets:
            newpet = Pet(pet, pets[pet]["displayName"])
            for rarity in Rarities:
                for qty in StoreQuantities:
                    newpet.set_quantity(rarity, qty, pets[pet][rarity.value][qty.value])
            self.Pets[pet] = newpet
    

    def add_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> Store:
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")
        
        pet: Pet = self.Pets[pet_name]
        pet.add(rarity, field, value)
        return self

    def sub_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> Store:
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")
    
        pet: Pet = self.Pets[pet_name]
        pet.sub(rarity, field, value)
        return self
    
    def set_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> Store:
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")

        pet: Pet = self.Pets[pet_name]
        pet.set(rarity, field, value)
        return self
    
    def zero_pet_quantity(self, pet_name: str, rarity: Rarities, field: StoreQuantities, value: int) -> Store:
        if pet_name not in self.Pets:
            raise StoreError(f"pet '{pet_name}' not found")

        pet: Pet = self.Pets[pet_name]
        pet.zero(rarity, field)
        return self

    def zero_all(self) -> Store:
        for pet in self.Pets.values():
            pet.zero()
        return self

    def get_pet(self, pet_id: str) -> Pet | None:
        return self.Pets.get(pet_id)
    
    def create_pet(self, pet_id: str, display_name: str) -> Pet:
        if pet_id in self.Pets:
            raise StoreError(f"pet '{pet_id}' already exists")
        pet = Pet(pet_id, display_name)
        self.Pets[pet_id] = pet
        return pet

    def delete_pet(self, pet_id: str) -> None:
        if pet_id not in self.Pets:
            raise StoreError(f"pet '{pet_id}' not found")
        del self.Pets[pet_id]

    def to_dict(self) -> dict:
        return {"pets": {pet.id:pet.to_dict() for pet in self.Pets.values()}}
    
    def save(self, path: Path):
        path = Path(path)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
