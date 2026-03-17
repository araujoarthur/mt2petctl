from store import Rarities, StoreQuantities

RARITY_MAP = {r.value[0]: r.value for r in Rarities}   # c, u, r, e, l, m
FIELD_MAP  = {f.value[0]: f.value for f in StoreQuantities}  # o, a, w

def expand_args(args: list[str]) -> list[str]:
    if not args or args[0] not in ("add", "sub", "set"):
        return args
    # args: [cmd, pet_id, rarity, field, value]
    if len(args) >= 3:
        args[2] = RARITY_MAP.get(args[2], args[2])
    if len(args) >= 4:
        args[3] = FIELD_MAP.get(args[3], args[3])
    return args