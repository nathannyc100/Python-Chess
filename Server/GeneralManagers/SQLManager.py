import mysql.connector
import threading

from icecream import ic

class SQLManager:

    def __init__(self):
        self.database = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "1234", 
            database = "finalSqlDatabase"
        )

        self.cursor = self.database.cursor()
        self.sqlLock = threading.Lock()
    #end

    def SqlSelect(self, query: str, condition: tuple, fetchall: bool):
        with self.sqlLock:
            if condition == None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, condition)
            #end

            if fetchall:
                queryResult = self.cursor.fetchall() 
            else:
                queryResult = self.cursor.fetchone()
            #end
        #end

        return queryResult
    #end

    def SqlEdit(self, query: str, values):
        with self.sqlLock:
            self.cursor.execute(query, values)
            self.database.commit()
        #end
    #end


class AccountSQLManager:

    def __init__(self, sqlManager: SQLManager):
        self.sqlManager = sqlManager
    #end

    def CheckUsername(self, username: str) -> bool:
        query = "SELECT id FROM users WHERE username = %s OR email = %s"
        queryResult = self.sqlManager.SqlSelect(query, (username, username), False)

        if not queryResult:
            return False
        else:
            return True
        #end
    #end

    def GetId(self, username: str) -> int:
        query = "SELECT id FROM users WHERE username = %s OR email = %s"
        queryResult = self.sqlManager.SqlSelect(query, (username, username), False)
    
        return queryResult[0]
    #end

    def GetUsername(self, id: int) -> str:
        query = "SELECT username FROM users WHERE id = %s"

        queryResult = self.sqlManager.SqlSelect(query, (id,), False)

        return queryResult[0]
    #end

    def GetSalt(self, username: str) -> bytes:
        query = "SELECT salt FROM users WHERE username = %s OR email = %s"
        queryResult = self.sqlManager.SqlSelect(query, (username, username), False)

        if not queryResult:
            return False
        else:
            return queryResult[0]
        #end
    #end

    def GetPassword(self, id: int):
        query = "SELECT passwordHash FROM users WHERE id = %s"
        queryResult = self.sqlManager.SqlSelect(query, (id,), False)

        return queryResult[0]
    #end

    def CreateAccount(self, username: str, password: bytes, salt: bytes):
        query = "INSERT INTO users (username, passwordHash, salt) VALUES (%s, %s, %s)"
        values = (username, password, salt)

        self.sqlManager.SqlEdit(query, values)
    #end