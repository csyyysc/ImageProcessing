"""
Database setup and configuration for SQLite
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, List
from contextlib import contextmanager

from backend.utils.file_handler import ensure_upload_directory

logger = logging.getLogger(__name__)


DB_PATH = Path("data/app.db")


class DatabaseManager:
    """SQLite database manager"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self.ensure_database_exists()
        self.init_tables()

    def ensure_database_exists(self):
        """Ensure database directory and file exist"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(exist_ok=True)

        if not db_file.exists():
            logger.info(f"Creating new database at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""

        logger.info(f"Getting database connection to {self.db_path}...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access

        logger.info(f"Database connection established to {self.db_path}")

        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def init_tables(self):
        """Initialize database tables"""

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Images table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    mime_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id)")

            conn.commit()
            logger.info("Database tables initialized successfully")


# Global database instance
db_manager = DatabaseManager()


class UserRepository:
    """User database operations"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create_user(self, username: str, email: Optional[str], password_hash: str) -> Dict:
        """Create a new user"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))

            user_id = cursor.lastrowid
            conn.commit()

            # Return the created user
            return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, username, email, password_hash, is_active, 
                       last_login, created_at, updated_at
                FROM users WHERE id = ?
            """, (user_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, username, email, password_hash, is_active, 
                       last_login, created_at, updated_at
                FROM users WHERE username = ?
            """, (username,))

            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, username, email, password_hash, is_active, 
                       last_login, created_at, updated_at
                FROM users WHERE email = ?
            """, (email,))

            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """Update user fields"""
        if not kwargs:
            return self.get_user_by_id(user_id)

        # Build dynamic UPDATE query
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['username', 'email', 'password_hash', 'is_active', 'last_login']:
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return self.get_user_by_id(user_id)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

            return self.get_user_by_id(user_id)

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

            return cursor.rowcount > 0

    def user_exists(self, username: str) -> bool:
        """Check if username already exists"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None


class ImageRepository:
    """Image database operations"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

        ensure_upload_directory()

    def get_image_by_id(self, image_id: int, user_id: int = None) -> Optional[Dict]:
        """Get image by ID with optional user ownership check"""

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            if user_id is not None:
                # Check ownership
                cursor.execute("""
                    SELECT id, user_id, filename, original_name, file_path, 
                           file_size, mime_type, created_at
                    FROM images WHERE id = ? AND user_id = ?
                """, (image_id, user_id))
            else:
                # No ownership check
                cursor.execute("""
                    SELECT id, user_id, filename, original_name, file_path, 
                           file_size, mime_type, created_at
                    FROM images WHERE id = ?
                """, (image_id,))

            row = cursor.fetchone()

            return dict(row) if row else None

    def get_images_by_user(self, user_id: int, page: int = 1, limit: int = 10) -> List[Dict]:
        """Use pagination to reduce the overload of getting images for a user"""

        with self.db.get_connection() as conn:
            offset = (page - 1) * limit

            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, filename, original_name, file_path, 
                       file_size, mime_type, created_at
                FROM images 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))

            logger.info(
                f"Image Repository: images for user_id={user_id}, page={page}, limit={limit}, offset={offset}")

            rows = cursor.fetchall()
            images = [dict(row) for row in rows]
            return images

    def create_image(self, user_id: int, filename: str, original_name: str,
                     file_path: str, file_size: int, mime_type: str) -> Dict:
        """Create a new image record specified to a user"""

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO images (user_id, filename, original_name, file_path, file_size, mime_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, filename, original_name, file_path, file_size, mime_type))

            image_id = cursor.lastrowid
            conn.commit()

            logger.info(
                f"Image Repository: Created image with id={image_id} for user_id={user_id}")

            return self.get_image_by_id(image_id)

    def delete_image(self, image_id: int, user_id: int) -> bool:
        """Delete an image (only if owned by the user)"""

        with self.db.get_connection() as conn:

            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM images 
                WHERE id = ? AND user_id = ?
            """, (image_id, user_id))

            conn.commit()

            logger.info(
                f"Image Repository: Deleted image with id={image_id} and user_id={user_id}")

            return cursor.rowcount > 0

    def get_user_image_count(self, user_id: int) -> int:
        """Get total number of images for a user"""

        with self.db.get_connection() as conn:

            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM images WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()
            print(row)
            return row['count'] if row else 0


# Global repository instances
user_repo = UserRepository(db_manager)
image_repo = ImageRepository(db_manager)
