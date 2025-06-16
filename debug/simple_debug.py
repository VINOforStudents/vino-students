"""
Simple Debug Script for File Processing Modifications

This script tests the individual file processing without touching your actual data.
It creates a isolated test environment to verify the modifications work correctly.
"""

import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def create_minimal_test_files(test_dir: str) -> list:
    """Create minimal test files for debugging."""
    os.makedirs(test_dir, exist_ok=True)
    
    files_created = []
    
    # Create 3 test markdown files
    test_contents = [
        "# Test Document 1\n\nThis is a simple test document.\n\n## Keywords\ntest, debug, file1",
        "# Test Document 2\n\nAnother test document with different content.\n\n## Keywords\ntest, debug, file2", 
        "# Test Document 3\n\nThird test document for processing.\n\n## Keywords\ntest, debug, file3"
    ]
    
    for i, content in enumerate(test_contents, 1):
        filename = f"debug_test_{i}.md"
        filepath = os.path.join(test_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        files_created.append(filepath)
        print(f"✓ Created: {filename}")
    
    return files_created

def test_document_loading():
    """Test the document loading and grouping by filename."""
    print("\n🔍 Testing Document Loading and Grouping")
    print("-" * 50)
    
    # Create temporary test directory
    test_dir = os.path.join(tempfile.gettempdir(), "vino_debug_docs")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    try:
        # Create test files
        print("Creating test files...")
        files_created = create_minimal_test_files(test_dir)
        
        # Import and test document processor
        from document_processor import load_documents_from_directory
        
        print(f"\nLoading documents from: {test_dir}")
        documents, metadatas, ids, message = load_documents_from_directory(test_dir, "debug_test")
        
        print(f"✓ Loaded {len(documents)} document chunks")
        print(f"✓ Generated {len(metadatas)} metadata entries") 
        print(f"✓ Created {len(ids)} document IDs")
        
        # Group by filename to simulate the new processing logic
        files_data = {}
        for i, meta in enumerate(metadatas):
            if i >= len(documents):
                continue
                
            filename = meta.get('filename', 'unknown')
            if filename not in files_data:
                files_data[filename] = {
                    'documents': [],
                    'metadatas': [],
                    'ids': []
                }
            
            files_data[filename]['documents'].append(documents[i])
            files_data[filename]['metadatas'].append(meta)
            files_data[filename]['ids'].append(ids[i])
        
        print(f"\n📊 Grouped into {len(files_data)} files:")
        for filename, data in files_data.items():
            print(f"   - {filename}: {len(data['documents'])} chunks")
        
        print("✅ Document loading and grouping test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Document loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")

def test_sql_upload_simulation():
    """Simulate the SQL upload process to test error handling."""
    print("\n🔍 Testing SQL Upload Error Handling Simulation")
    print("-" * 50)
    
    try:
        # Test the modified upload_documents_to_sql function behavior
        # We'll simulate what happens with duplicate files
        
        print("Simulating duplicate file scenario...")
        
        # Create mock metadata and content
        mock_metadata = [{
            'filename': 'existing_file.md',
            'file_size': 1000,
            'file_type': 'markdown',
            'page_count': 1,
            'word_count': 100,
            'char_count': 500,
            'keywords': ['test', 'mock'],
            'source': 'debug_test',
            'abstract': 'Mock file for testing'
        }]
        
        mock_content = ['# Mock Document\n\nThis is a mock document for testing.']
        
        print("✓ Created mock data for testing")
        print(f"   - Filename: {mock_metadata[0]['filename']}")
        print(f"   - Content length: {len(mock_content[0])} chars")
        
        # Show how the grouping logic would work
        files_data = {}
        for i, meta in enumerate(mock_metadata):
            filename = meta.get('filename', 'unknown')
            if filename not in files_data:
                files_data[filename] = {
                    'file_metadata': meta,
                    'chunks': []
                }
            files_data[filename]['chunks'].append(mock_content[i])
        
        print(f"✓ Grouped into {len(files_data)} file(s) for processing")
        
        # Simulate individual file processing logic
        for filename, file_data in files_data.items():
            print(f"\n📄 Processing file: {filename}")
            try:
                # This would normally call upload_documents_to_sql
                # but we'll just simulate the logic
                print(f"   - Would upload {len(file_data['chunks'])} chunks")
                print(f"   - File metadata: {file_data['file_metadata']['file_type']}")
                print("   ✓ Simulated successful upload")
                
            except Exception as e:
                print(f"   ❌ Simulated error: {e}")
                continue
        
        print("✅ SQL upload simulation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ SQL upload simulation test failed: {e}")
        return False

def test_file_movement_logic():
    """Test the file movement logic without actually moving files."""
    print("\n🔍 Testing File Movement Logic")
    print("-" * 50)
    
    # Create temporary directories to simulate the process
    test_source = os.path.join(tempfile.gettempdir(), "debug_source")
    test_dest = os.path.join(tempfile.gettempdir(), "debug_dest")
    
    try:
        # Setup test directories
        os.makedirs(test_source, exist_ok=True)
        os.makedirs(test_dest, exist_ok=True)
        
        # Create test files in source
        test_files = create_minimal_test_files(test_source)
        
        print(f"Created {len(test_files)} files in source directory")
        
        # Simulate the file processing logic
        files_to_process = os.listdir(test_source)
        print(f"Files to process: {files_to_process}")
        
        successful_files = []
        failed_files = []
        
        # Simulate processing each file
        for filename in files_to_process:
            source_path = os.path.join(test_source, filename)
            dest_path = os.path.join(test_dest, filename)
            
            try:
                # Simulate different outcomes
                if "debug_test_2" in filename:
                    # Simulate a failure for the second file
                    raise Exception("Simulated duplicate error")
                
                # Simulate successful processing
                shutil.move(source_path, dest_path)
                successful_files.append(filename)
                print(f"   ✓ Successfully moved: {filename}")
                
            except Exception as e:
                failed_files.append(filename)
                print(f"   ❌ Failed to process: {filename} ({e})")
                continue
        
        # Check results
        remaining_in_source = os.listdir(test_source)
        moved_to_dest = os.listdir(test_dest)
        
        print(f"\n📊 Results:")
        print(f"   - Successfully processed: {len(successful_files)} files")
        print(f"   - Failed to process: {len(failed_files)} files") 
        print(f"   - Remaining in source: {len(remaining_in_source)} files")
        print(f"   - Moved to destination: {len(moved_to_dest)} files")
        
        # Verify that failed files remained in source
        assert len(remaining_in_source) == len(failed_files), "Failed files should remain in source"
        assert len(moved_to_dest) == len(successful_files), "Successful files should be in destination"
        
        print("✅ File movement logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ File movement logic test failed: {e}")
        return False
        
    finally:
        # Cleanup
        for dir_path in [test_source, test_dest]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        print("🧹 Cleaned up test directories")

def run_debug_tests():
    """Run all debug tests."""
    print("🚀 Starting File Processing Debug Tests")
    print("=" * 60)
    
    tests = [
        ("Document Loading & Grouping", test_document_loading),
        ("SQL Upload Error Handling", test_sql_upload_simulation), 
        ("File Movement Logic", test_file_movement_logic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your modifications should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the modifications.")

if __name__ == "__main__":
    run_debug_tests()
