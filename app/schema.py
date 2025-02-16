import strawberry
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post, User

@strawberry.type
class UserType:
    id: int
    username: str
    email: str

@strawberry.type
class PostType:
    id: int
    title: str
    content: str
    author: UserType

@strawberry.type
class Query:
    @strawberry.field
    def get_posts(self) -> List[PostType]:
        db = next(get_db())  # Correctly retrieve session
        posts = db.query(Post).all()
        return [PostType(id=p.id, title=p.title, content=p.content, author=UserType(id=p.author.id, username=p.author.username, email=p.author.email)) for p in posts]

@strawberry.input
class CreateUserInput:
    username: str
    email: str
    password_hash: str  # Ideally, hash this before saving

@strawberry.input
class CreatePostInput:
    title: str
    content: str
    author_id: int

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> UserType:
        db = next(get_db())  # Get database session
        try:
            user = User(username=input.username, email=input.email, password_hash=input.password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            return UserType(id=user.id, username=user.username, email=user.email)
        finally:
            db.close()  # Always close DB connection

    @strawberry.mutation
    def create_post(self, input: CreatePostInput) -> PostType:
        db = next(get_db())  # Get database session
        try:
            post = Post(title=input.title, content=input.content, author_id=input.author_id)
            db.add(post)
            db.commit()
            db.refresh(post)
            return PostType(id=post.id, title=post.title, content=post.content, author=UserType(id=post.author.id, username=post.author.username, email=post.author.email))
        finally:
            db.close()  # Always close DB connection

schema = strawberry.Schema(query=Query, mutation=Mutation)
