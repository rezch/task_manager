import json


class DB:
    __instance = None

    __datafile = None
    __data = None

    class Error(Exception):
        def __init__(self, message: str):
            self._message = message

        def __str__(self):
            return f"DB Error: {self._message}"

    def __new__(cls, datafile):
        if cls.__instance is None:
            cls.__datafile = datafile
            cls.__instance = super().__new__(cls)
        return cls

    def LoadedCheck() -> None:
        if DB.__data is None:
            raise DB.Error("data base not loaded.")

    def _load(file) -> None:
        DB.__data = json.load(file)

    def Load() -> None:
        try:
            with open(DB.__datafile, 'r') as f:
                DB._load(f)
        except:
            raise DB.Error("load error: source file.")
        return DB

    def _dump(file) -> None:
        file.seek(0)
        json.dump(DB.__data, file)
        file.truncate()

    def Dump() -> None:
        DB.LoadedCheck()

        try:
            with open(DB.__datafile, 'w') as f:
                DB._dump(f)
        except:
            raise DB.Error("dump error: source file.")
        
    def getUser(user_id) -> dict:
        DB.LoadedCheck()

        user_id = str(user_id)

        if user_id not in list(DB.__data.keys()):
            raise DB.Error("User not found.")

        return DB.__data[user_id]

    def addUser(used_id: int) -> None:
        DB.LoadedCheck()

        if used_id not in list(DB.__data.keys()):
            DB.__data[used_id] = {}


if __name__ == "__main__":
    db = DB("data.json").Load()
    user = db.getUser(123)
    db.Dump()
