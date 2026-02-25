import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from glpi_mcp_server.tools.folder_tools import list_folders

@pytest.mark.asyncio
async def test_list_folders_exists(tmp_path):
    # Create some folders
    root1 = tmp_path / "root1"
    root1.mkdir()
    success_dir = tmp_path / "success"
    success_dir.mkdir()
    error_dir = tmp_path / "error"
    error_dir.mkdir()
    non_existent = tmp_path / "non_existent"
    
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.allowed_roots_list = [root1, non_existent]
    mock_settings.folder_success_path = success_dir
    mock_settings.folder_errores_path = error_dir
    
    with patch("glpi_mcp_server.tools.folder_tools.settings", mock_settings):
        folders = await list_folders()
        
        # Should include existing folders
        assert str(root1.resolve()) in folders
        assert str(success_dir.resolve()) in folders
        assert str(error_dir.resolve()) in folders
        
        # Should NOT include non-existent folder
        assert str(non_existent.resolve()) not in folders
        
        # Should return sorted list of 3 folders
        assert len(folders) == 3
        assert folders == sorted([str(root1.resolve()), str(success_dir.resolve()), str(error_dir.resolve())])

@pytest.mark.asyncio
async def test_list_folders_duplicates(tmp_path):
    # Create one folder
    root1 = tmp_path / "root1"
    root1.mkdir()
    
    # Mock settings where same folder is root and success
    mock_settings = MagicMock()
    mock_settings.allowed_roots_list = [root1]
    mock_settings.folder_success_path = root1
    mock_settings.folder_errores_path = None
    
    with patch("glpi_mcp_server.tools.folder_tools.settings", mock_settings):
        folders = await list_folders()
        
        # Should only have one entry
        assert len(folders) == 1
        assert folders == [str(root1.resolve())]

@pytest.mark.asyncio
async def test_list_folders_no_processing_folders(tmp_path):
    root1 = tmp_path / "root1"
    root1.mkdir()
    
    # Mock settings with only roots
    mock_settings = MagicMock()
    mock_settings.allowed_roots_list = [root1]
    mock_settings.folder_success_path = None
    mock_settings.folder_errores_path = None
    
    with patch("glpi_mcp_server.tools.folder_tools.settings", mock_settings):
        folders = await list_folders()
        assert folders == [str(root1.resolve())]
