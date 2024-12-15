from typing import List, Dict, Any, Tuple, Union, Optional

def parse_json(json : Dict[str, Any], keys : List[str], verbose : bool = False) -> Dict[str, Any]:
    """get the values of the keys in the json

    Args:
        json (Dict[str, Any]): the original json
        keys (List[str]): the keys to get the values from the json (if the key is nested, use '.' to separate the keys)

    Returns:
        Dict[str, Any]: the values of the keys in the json
    """
    res = {}
    for key in keys:
        path = key.split(".")
        val = json
        if verbose:
            print(f"parsing {key} : {val}")
        for p in path:
            if verbose:
                print(f"\tparsing {p}")
            try:
                val = val[p]
            except KeyError:
                if verbose:
                    print(f"\tkey {p} not found")
                    print(f"\t{val}")
                val = None
                break
        res["_".join(path)] = val
    return res

class JsonToObject:
        
    def setattr(self, json : Dict[str, Any], keys : List[str], verbose : bool = False):
        """set the attributes of the object from the json

        Args:
            json (Dict[str, Any]): the json to get the values from
            keys (List[str]): the keys to get the values from the json (if the key is nested, use '.' to separate the keys)
        """
        for key, value in parse_json(json, keys, verbose=verbose).items():
            if verbose:
                print(f"setting {key} to {value}")
            self.__setattr__(key, value)
            
    def renameAttribute(self, old_attr, new_attr):
        """rename an attribute of the object

        Args:
            old_attr (str): the old attribute name
            new_attr (str): the new attribute name
        """
        self.__setattr__(new_attr, self.__getattribute__(old_attr))
        delattr(self, old_attr)
        
    def stripAttribute(self, name:str, verbose : bool = False):
        """strip a part of the attribute name

        Args:
            name (str): the part to strip
        """
        keys = list(self.__dict__.keys())
        for key in keys:
            if name in key:
                if verbose:
                    print(f"stripping {name} from {key} -> {key.replace(name, '')}")
                self.renameAttribute(key, key.replace(name, ''))
    
    def addPrefix(self, prefix:str, verbose : bool = False):
        """add a prefix to all the attributes

        Args:
            prefix (str): the prefix to add
        """
        keys = list(self.__dict__.keys())
        for key in keys:
            if verbose:
                print(f"adding {prefix} to {key} -> {prefix + key}")
            self.renameAttribute(key, prefix + key)
    
    def to_dict(self) -> Dict[str, Any]:
        """convert the object to a dictionary

        Returns:
            Dict[str, Any]: the dictionary representation of the object
        """
        return self.__dict__