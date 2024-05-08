import json


class DB:
    __instance = None

    __datafile = None
    __data = None

    class DBException(Exception):
        def __init__(self, message: str):
            self._message = message

        def __str__(self):
            return f"DB error: {self._message}"

    def __new__(cls, datafile):
        if cls.__instance is None:
            cls.__datafile = datafile
            cls.__instance = super().__new__(cls)
        return cls

    @staticmethod
    def LoadedCheck() -> None:
        if DB.__data is None:
            raise DB.DBException("data base not loaded.")

    @staticmethod
    def _load(file) -> None:
        DB.__data = json.load(file)

    @staticmethod
    def Load():
        try:
            with open(DB.__datafile, 'r') as f:
                DB._load(f)
        except:
            raise DB.DBException("load error: source file.")
        return DB

    @staticmethod
    def _dump(file) -> None:
        file.seek(0)
        json.dump(DB.__data, file)
        file.truncate()

    @staticmethod
    def Dump() -> None:
        DB.LoadedCheck()

        try:
            with open(DB.__datafile, 'w') as f:
                DB._dump(f)
        except:
            raise DB.DBException("dump error: source file.")

    @staticmethod
    def getUser(user_id) -> dict:
        DB.LoadedCheck()
        user_id = str(user_id)

        if user_id not in list(DB.__data.keys()):
            raise DB.DBException("User not found.")

        return DB.__data[user_id]

    @staticmethod
    def addUser(user_id: int) -> None:
        DB.LoadedCheck()
        user_id = str(user_id)

        if user_id not in list(DB.__data.keys()):
            DB.__data[user_id] = {}

    @staticmethod
    def updateUser(user_id: int, new_data: dict) -> None:
        DB.LoadedCheck()
        user_id = str(user_id)

        if not isinstance(new_data, dict):
            raise DB.DBException("new user data type is not dict")

        DB.__data[user_id] = new_data


if __name__ == "__main__":
    db = DB("data.json").Load()
    user = db.getUser(123)
    db.Dump()
