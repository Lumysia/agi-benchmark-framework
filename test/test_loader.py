import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import yaml
from src.loader import load_benchmarks_from_dir

def test_load_benchmarks_from_dir_valid_files(mocker):
    mock_path_instance = MagicMock()
    mocker.patch('src.loader.Path', return_value=mock_path_instance)

    mock_yaml_file = MagicMock(spec=Path)
    mock_yaml_file.name = 'test1.yaml'
    
    mock_yml_file = MagicMock(spec=Path)
    mock_yml_file.name = 'test2.yml'
    
    mock_path_instance.glob.side_effect = [
        [mock_yaml_file],  
        [mock_yml_file]    
    ]
    
    mock_data_1 = {'name': 'test1'}
    mock_data_2 = {'name': 'test2'}
    
    mock_file_content = {
        str(mock_yaml_file): yaml.dump(mock_data_1),
        str(mock_yml_file): yaml.dump(mock_data_2)
    }

    def mock_open_side_effect(filepath, mode, encoding):
        content = mock_file_content[str(filepath)]
        return mock_open(read_data=content)()

    with patch('builtins.open', side_effect=mock_open_side_effect):
        benchmarks = load_benchmarks_from_dir('dummy_dir')
        
        assert len(benchmarks) == 2
        assert benchmarks[0]['name'] == 'test1'
        assert benchmarks[0]['__filepath__'] == 'test1.yaml'
        assert benchmarks[1]['name'] == 'test2'
        assert benchmarks[1]['__filepath__'] == 'test2.yml'

def test_load_benchmarks_empty_dir(mocker):
    mock_path_instance = MagicMock()
    mocker.patch('src.loader.Path', return_value=mock_path_instance)
    mock_path_instance.glob.return_value = []
    
    benchmarks = load_benchmarks_from_dir('empty_dir')
    assert len(benchmarks) == 0

def test_load_benchmarks_yaml_error(mocker, capsys):
    mock_path_instance = MagicMock()
    mocker.patch('src.loader.Path', return_value=mock_path_instance)
    
    mock_file = MagicMock(spec=Path)
    mock_file.name = 'bad.yaml'
    
    mock_path_instance.glob.side_effect = [[mock_file], []]
    
    with patch('builtins.open', mock_open(read_data='name: test\ninvalid: yaml: syntax')):
        benchmarks = load_benchmarks_from_dir('dummy_dir')
        
        assert len(benchmarks) == 0
        captured = capsys.readouterr()
        assert "Error parsing YAML file bad.yaml" in captured.out

def test_load_benchmarks_other_exception(mocker, capsys):
    mock_path_instance = MagicMock()
    mocker.patch('src.loader.Path', return_value=mock_path_instance)
    
    mock_file = MagicMock(spec=Path)
    mock_file.name = 'error.yaml'
    
    mock_path_instance.glob.side_effect = [[mock_file], []]
    
    with patch('builtins.open', side_effect=IOError("File not found")):
        benchmarks = load_benchmarks_from_dir('dummy_dir')
        
        assert len(benchmarks) == 0
        captured = capsys.readouterr()
        assert "Error loading file error.yaml: File not found" in captured.out