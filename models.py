"""TODO: user model
username (Имя)
uni_id (номер студенческого)
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# class User(Base):
#     __tablename__ = "user"
#     # TODO: user model
#     id = Column(Integer, primary_key=True)
#     is_bot = Column(Boolean)
#     first_name = Column(String)
#     last_name = Column(String, nullable=True)
#     username = Column(String, nullable=True)
#     is_premium = Column(Boolean, nullable=True)
#     added_to_attachment_menu = Column(Boolean, nullable=True)
#     is_admin = Column(Boolean)

#     answer = relationship("Answer", back_populates="user")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    folder_id = Column(Integer, ForeignKey("folders.id"))

    # Document = relationship("Document", back_populates="documents")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    folder_id = Column(Integer, ForeignKey("folders.id"))
    name = Column(String)

    # user = relationship("Folder", back_populates="docunents")
