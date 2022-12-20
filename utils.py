import dataclasses
import json
from typing import Any, Dict, Union


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Union[Dict[str, Any], Any]:
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        return super().default(obj)


def dict_to_dataclass(klass, obj) -> Any:
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dict_to_dataclass(fieldtypes[f], obj[f]) for f in obj})
    except:
        return obj
