import pydash as _
import json
import os


class Database:
    """
    Starts the MIDB client
    ### Parameters:
    - path: `str` (The path to save te tables, this must be a directory path)
    - tables: `list[str]` (The tables to checkout)
    """

    def __init__(self, path: str, tables: list = ["Main"]) -> None:
        self.path = path
        self.document = {}
        self.tables = tables

    def set(self, key: str, value: any, table: str = "Main"):
        """
        Set a key value in the database
        ### Parameters:
        - key: `str` (The key to change its value)
        - value: `any` (The new value of this key)
        - table: `str` (The table of the database to set)
        ### Returns:
        None
        """
        if not self._validate_table(table):
            raise SyntaxError("MIDB: Invalid table provided.")
        content = self.load_table(table) or {}
        _.set_(content, key, value)
        self.insert(table, content)
        self.document[table] = self._fetch_table(table)

    def get(self, key: str, table: str = "Main"):
        """
        Get a key value from the database
        ### Parameters:
        - key: `str` (The key from the table to get the value)
        - table: `str` (The table of the database to get)
        ### Returns:
        any
        """
        if not self._validate_table(table):
            raise SyntaxError("MIDB: Invalid table provided.")
        content = self.load_table(table) or {}
        return _.get(content, key)

    def append(self, key: str, value: any, table: str = "Main"):
        if not self._validate_table(table):
            raise SyntaxError("MIDB: Invalid table provided.")
        
    def delete(self, key: str, table: str = "Main"):
        """
        Delete a key value from the database
        ### Parameters:
        - key: `str` (The key from the table to delete the value)
        - table: `str` (The table of the database)
        ### Returns:
        None
        """
        if not self._validate_table(table):
            raise SyntaxError("MIDB: Invalid table provided.")
        content = self.load_table(table)
        if not content:
            return
        _.unset(content, key)
        self.insert(table, content)
        self.document[table] = self._fetch_table(table)

    def load_table(self, name: str):
        """
        Loads a database table
        ### Parameters:
        - name: `str` (The table name)
        ### Returns:
        dict | None
        """
        if not self._validate_table(name):
            raise SyntaxError("MIDB: Invalid table provided.")
        if not hasattr(self.document, name):
            v = self._fetch_table(name)
            self.document[name] = v
            return v
        else:
            return self.document[name] if hasattr(self.document, name) else None

    # def attend(self, name: str, data: dict):
    # 	pass

    def insert(self, name: str, data: dict):
        """
        Insert a new content into a table database
        ### Parameters:
        - name: `str` (The table name to edit)
        - data: `dict` (The new table content)
        ### Returns:
        None
        """
        if not self._validate_table(name):
            raise SyntaxError("MIDB: Invalid table provided.")
        if not os.path.exists(self.path):
            os.mkdir(os.path.abspath(self.path))
        with open(f"{self.path}/{name}.json", "w") as document:
            document.write(json.dumps(data))

    def _fetch_table(self, name: str):
        """
        Force to fetch a table database
        ### Parameters:
        - name: `str` (The table name)
        ### Returns:
        None
        """
        try:
            with open(f"{self.path}/{name}.json", "r") as document:
                if not document:
                    return None
                else:
                    return json.loads(document.read())
        except:
            return None

    def _validate_table(self, name: str):
        """
        Validate if this is a database table
        ### Parameters:
        - name: `str` (The possible table name)
        ### Returns:
        bool
        """
        return name in self.tables
