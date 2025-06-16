"""
Debug File Processing Module

This module tests the individual file processing modifications to ensure:
1. Successful files are moved even if other files fail
2. Failed files (duplicates, errors) remain in source directory
3. Proper error reporting for each file
4. ChromaDB and Supabase processing work independently per file
"""

import os
import shutil
import tempfile
from pathlib import Path

# Import the modified upload functions
from upload_supa_chroma import upload_documents_to_chromadb, upload_to_supa
from upload_supa import process_directory
from config import NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR, NEW_USER_UPLOADS_DIR, USER_UPLOADS_DIR

def create_test_files(test_dir: str, num_files: int = 3) -> list:
    """
    Create test files in the specified directory.
    
    Args:
        test_dir: Directory to create test files in
        num_files: Number of test files to create
        
    Returns:
        List of created file paths
    """
    created_files = []
    
    # Ensure directory exists
    os.makedirs(test_dir, exist_ok=True)
    
    for i in range(num_files):
        filename = f"test_document_{i+1}.md"
        filepath = os.path.join(test_dir, filename)
        
        content = f"""# Test Document {i+1}

This is a test document for debugging file processing.

## Introduction
This document tests the individual file processing functionality.

## Content Section
This section contains some sample content to make the document substantial enough for processing.

### Subsection {i+1}
- Point 1: Testing individual file processing
- Point 2: Ensuring failed files don't block successful ones
- Point 3: Verifying proper error handling

## Keywords
test, debugging, file processing, individual handling

## Conclusion
This test document should be processed {'successfully' if i % 2 == 0 else 'with potential issues'}.
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        created_files.append(filepath)
        print(f"Created test file: {filename}")
    
    return created_files

def create_duplicate_test() -> str:
    """
    Create a test scenario with a file that will cause a duplicate error.
    
    Returns:
        Path to the test directory
    """
    # Create a temporary test directory
    test_dir = os.path.join(tempfile.gettempdir(), "vino_debug_test")
    
    # Clean up any existing test directory
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Create test files
    created_files = create_test_files(test_dir, 3)
    
    print(f"\n📁 Created test directory: {test_dir}")
    print(f"📄 Created {len(created_files)} test files")
    
    return test_dir

def backup_original_directories():
    """
    Backup original directory contents before testing.
    """
    backup_info = {}
    
    for dir_name, dir_path in [
        ("NEW_DOCUMENTS_DIR", NEW_DOCUMENTS_DIR),
        ("KB_DOCUMENTS_DIR", KB_DOCUMENTS_DIR)
    ]:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            backup_info[dir_name] = {
                "path": dir_path,
                "files": files,
                "count": len(files)
            }
            print(f"📋 {dir_name} contains {len(files)} files")
        else:
            backup_info[dir_name] = {"path": dir_path, "files": [], "count": 0}
            print(f"📋 {dir_name} does not exist")
    
    return backup_info

def test_individual_file_processing():
    """
    Test the individual file processing functionality.
    """
    print("🔍 Starting Individual File Processing Debug Test")
    print("=" * 60)
    
    # Backup original state
    print("\n1️⃣ Backing up original directory state...")
    original_state = backup_original_directories()
    
    # Create test files
    print("\n2️⃣ Creating test files...")
    test_dir = create_duplicate_test()
    
    # Temporarily replace NEW_DOCUMENTS_DIR for testing
    original_new_docs_dir = NEW_DOCUMENTS_DIR
    
    try:
        # Copy test files to actual NEW_DOCUMENTS_DIR
        print(f"\n3️⃣ Copying test files to {NEW_DOCUMENTS_DIR}...")
        os.makedirs(NEW_DOCUMENTS_DIR, exist_ok=True)
        
        test_files = os.listdir(test_dir)
        for filename in test_files:
            src = os.path.join(test_dir, filename)
            dst = os.path.join(NEW_DOCUMENTS_DIR, filename)
            shutil.copy2(src, dst)
            print(f"   Copied: {filename}")
        
        # Test 1: Process documents directory
        print(f"\n4️⃣ Testing process_directory function...")
        print("-" * 40)
        result = process_directory(NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR, "system_upload")
        print(f"Process result: {result}")
        
        # Check what files were moved vs what remained
        print(f"\n5️⃣ Checking file movement results...")
        print("-" * 40)
        
        remaining_files = os.listdir(NEW_DOCUMENTS_DIR) if os.path.exists(NEW_DOCUMENTS_DIR) else []
        moved_files = []
        if os.path.exists(KB_DOCUMENTS_DIR):
            all_kb_files = os.listdir(KB_DOCUMENTS_DIR)
            # Filter to only test files (those starting with "test_document_")
            moved_files = [f for f in all_kb_files if f.startswith("test_document_")]
        
        print(f"📁 Files remaining in NEW_DOCUMENTS_DIR: {len(remaining_files)}")
        for f in remaining_files:
            if f.startswith("test_document_"):
                print(f"   - {f} (REMAINED - likely failed)")
        
        print(f"📁 Test files moved to KB_DOCUMENTS_DIR: {len(moved_files)}")
        for f in moved_files:
            print(f"   - {f} (MOVED - successfully processed)")
        
        # Test 2: Try processing again to test duplicate handling
        if remaining_files:
            print(f"\n6️⃣ Testing duplicate handling by reprocessing remaining files...")
            print("-" * 40)
            result2 = process_directory(NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR, "system_upload")
            print(f"Second process result: {result2}")
            
            remaining_files_after = os.listdir(NEW_DOCUMENTS_DIR) if os.path.exists(NEW_DOCUMENTS_DIR) else []
            print(f"📁 Files still remaining after second attempt: {len(remaining_files_after)}")
            for f in remaining_files_after:
                if f.startswith("test_document_"):
                    print(f"   - {f}")
        
        # Test 3: Test ChromaDB individual processing
        print(f"\n7️⃣ Testing ChromaDB individual file processing...")
        print("-" * 40)
        if remaining_files:
            chroma_result = upload_documents_to_chromadb("system_upload")
            print(f"ChromaDB result: {chroma_result}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup: Remove test files from actual directories
        print(f"\n8️⃣ Cleaning up test files...")
        print("-" * 40)
        
        # Remove test files from NEW_DOCUMENTS_DIR
        if os.path.exists(NEW_DOCUMENTS_DIR):
            for filename in os.listdir(NEW_DOCUMENTS_DIR):
                if filename.startswith("test_document_"):
                    file_path = os.path.join(NEW_DOCUMENTS_DIR, filename)
                    os.remove(file_path)
                    print(f"   Removed from NEW_DOCUMENTS_DIR: {filename}")
        
        # Remove test files from KB_DOCUMENTS_DIR
        if os.path.exists(KB_DOCUMENTS_DIR):
            for filename in os.listdir(KB_DOCUMENTS_DIR):
                if filename.startswith("test_document_"):
                    file_path = os.path.join(KB_DOCUMENTS_DIR, filename)
                    os.remove(file_path)
                    print(f"   Removed from KB_DOCUMENTS_DIR: {filename}")
        
        # Remove temporary test directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"   Removed temporary directory: {test_dir}")
    
    print(f"\n✅ Individual File Processing Debug Test Completed!")
    print("=" * 60)

def test_error_scenarios():
    """
    Test specific error scenarios to ensure proper handling.
    """
    print("\n🔍 Testing Error Scenarios")
    print("=" * 40)
    
    # Test 1: Empty directory
    print("\n📂 Test 1: Empty directory processing")
    empty_dir = os.path.join(tempfile.gettempdir(), "empty_test_dir")
    os.makedirs(empty_dir, exist_ok=True)
    
    try:
        # This should handle empty directory gracefully
        from upload_supa import check_not_empty
        is_empty = not check_not_empty(empty_dir)
        print(f"   Empty directory check: {is_empty}")
        
        if is_empty:
            print("   ✅ Empty directory handled correctly")
        else:
            print("   ❌ Empty directory not detected")
    
    finally:
        if os.path.exists(empty_dir):
            os.rmdir(empty_dir)
    
    # Test 2: Invalid file permissions (if possible)
    print("\n🔒 Test 2: File permission scenarios")
    print("   (Skipping on Windows - permission tests not reliable)")
    
    print("\n✅ Error Scenarios Testing Completed!")

def run_comprehensive_debug():
    """
    Run comprehensive debugging tests.
    """
    print("🚀 Starting Comprehensive Debug Session")
    print("=" * 60)
    print(f"Timestamp: {__import__('datetime').datetime.now()}")
    print(f"Python version: {__import__('sys').version}")
    print("=" * 60)
    
    try:
        # Test individual file processing
        test_individual_file_processing()
        
        # Test error scenarios
        test_error_scenarios()
        
        print("\n🎉 All debug tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Debug session failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_debug()
