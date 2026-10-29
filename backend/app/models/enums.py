"""Enumeraciones compartidas por los modelos y los esquemas de Pydantic.

Viven en su propio módulo porque sus valores forman parte del esquema de la base de datos
(una restricción CHECK) y los esquemas de la API las reutilizan sin depender de los modelos.
"""

from enum import StrEnum


class UserRole(StrEnum):
    CLIENT = "client"
    ADMIN = "admin"
