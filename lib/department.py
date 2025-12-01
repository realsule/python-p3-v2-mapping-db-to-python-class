from __init__ import CURSOR, CONN


class Department:
    # registry of loaded Department instances keyed by id
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Department instances """
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Department instances """
        sql = """
            DROP TABLE IF EXISTS departments;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the name and location values of the current Department instance.
        Update object id attribute using the primary key value of new row.
        """
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """

        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()

        self.id = CURSOR.lastrowid
        # register this instance in the in-memory cache
        Department.all[self.id] = self

    @classmethod
    def create(cls, name, location):
        """ Initialize a new Department instance and save the object to the database """
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the table row corresponding to the current Department instance."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()
        # ensure in-memory cache reflects current attribute values
        if self.id in Department.all:
            Department.all[self.id] = self

    def delete(self):
        """Delete the table row corresponding to the current Department instance"""
        sql = """
            DELETE FROM departments
            WHERE id = ?
        """
        # capture id for cache removal after deletion
        id_to_delete = self.id
        CURSOR.execute(sql, (id_to_delete,))
        CONN.commit()

        # remove from in-memory cache and clear object's id
        Department.all.pop(id_to_delete, None)
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Given a DB row tuple (id, name, location), return a Department instance.
        If an instance with the id already exists in the in-memory cache, return it.
        Otherwise, create, cache, and return a new instance.
        """
        if row is None:
            return None

        id_, name, location = row[0], row[1], row[2]
        if id_ in cls.all:
            return cls.all[id_]

        department = cls(name, location, id=id_)
        cls.all[id_] = department
        return department

    @classmethod
    def get_all(cls):
        """Return a list of Department instances for every row in the departments table."""
        sql = """
            SELECT * FROM departments
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id_):
        """Return a Department instance for the row with the given id, or None."""
        # check cache first
        if id_ in cls.all:
            return cls.all[id_]

        sql = """
            SELECT * FROM departments
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id_,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_name(cls, name):
        """Return a Department instance for the row with the given name, or None."""
        sql = """
            SELECT * FROM departments
            WHERE name = ?
        """
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row)
