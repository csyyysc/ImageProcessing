#!/usr/bin/env python3
"""
Script to clean all images from the database
"""
import os
import sys
import logging

from backend.database import image_repo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_all_images():
    """Remove all images from the database"""
    print("🧹 Cleaning all images from database...")

    try:
        # Get all images first to show what we're deleting
        all_images = image_repo.get_images_by_user(
            1, 1, 1000)  # Get all images
        print(f"📋 Found {len(all_images)} images in database")

        if len(all_images) == 0:
            print("✅ Database is already clean - no images to delete")
            return

        # Show what we're about to delete
        print("\n🗑️  Images to be deleted:")
        for i, img in enumerate(all_images[:5]):  # Show first 5
            print(f"  {i+1}. {img['filename']} - {img['original_name']}")

        if len(all_images) > 5:
            print(f"  ... and {len(all_images) - 5} more")

        # Confirm deletion
        confirm = input(
            f"\n⚠️  Are you sure you want to delete ALL {len(all_images)} images? (yes/no): ")

        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return

        # Delete all images
        deleted_count = 0
        for img in all_images:
            success = image_repo.delete_image(img['id'], img['user_id'])
            if success:
                deleted_count += 1
                # Also delete the physical file
                from backend.utils.file_handler import delete_file
                delete_file(img['file_path'])

        print(
            f"✅ Successfully deleted {deleted_count} images from database and filesystem")

    except Exception as e:
        print(f"❌ Error cleaning images: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    clean_all_images()
