"""
Unit tests for TagDependencyManager
"""

import pytest
from tagging.tag_dependency_manager import TagDependencyManager


class TestTagDependencyManager:
    """Test cases for TagDependencyManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = TagDependencyManager()
    
    def test_extract_variables_from_condition(self):
        """Test variable extraction from condition strings"""
        # Test basic variable extraction
        condition = "participants >= 1"
        variables = self.manager._extract_variables_from_condition(condition)
        assert variables == ["participants"]
        
        # Test arithmetic expressions
        condition = "participants - girls > 0"
        variables = self.manager._extract_variables_from_condition(condition)
        assert variables == ["participants", "girls"]
        
        # Test complex conditions
        condition = "(girls > 0 && guys > 0) && scene == 'gym'"
        variables = self.manager._extract_variables_from_condition(condition)
        assert variables == ["girls", "guys", "scene"]
        
        # Test with string literals
        condition = 'action == "dancing"'
        variables = self.manager._extract_variables_from_condition(condition)
        assert variables == ["action"]
        
        # Test empty condition
        variables = self.manager._extract_variables_from_condition("")
        assert variables == []
        
        # Test None condition
        variables = self.manager._extract_variables_from_condition(None)
        assert variables == []
    
    def test_analyze_dependencies_simple(self):
        """Test dependency analysis with simple configuration"""
        config = {
            'tags': {
                'participants': {
                    'desc': 'Number of people',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'girls': {
                    'desc': 'Number of girls',
                    'req': 'participants >= 1',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'guys': {
                    'desc': 'Number of guys',
                    'req': 'participants - girls > 0',
                    'type': 'int',
                    'default': 0,
                    'values': ['0', '1', '2', '3', 'many']
                }
            }
        }
        
        dependencies = self.manager.analyze_dependencies(config)
        
        assert dependencies['participants'] == []
        assert dependencies['girls'] == ['participants']
        assert set(dependencies['guys']) == {'participants', 'girls'}
    
    def test_analyze_dependencies_with_value_conditions(self):
        """Test dependency analysis with value-level conditions"""
        config = {
            'tags': {
                'action': {
                    'desc': 'Action type',
                    'values': ['existing', 'dancing', 'climbing']
                },
                'dance_style': {
                    'desc': 'Dance style',
                    'req': 'action == "dancing"',
                    'values': [
                        {'value': 'shuffle', 'req': 'girls >= 1'},
                        {'value': 'swing', 'req': 'girls + guys > 0'},
                        {'value': 'salsa', 'req': 'girls > 0 && guys > 0'}
                    ]
                }
            }
        }
        
        dependencies = self.manager.analyze_dependencies(config)
        
        assert dependencies['action'] == []
        assert set(dependencies['dance_style']) == {'action', 'girls', 'guys'}
    
    def test_get_ordered_tags_simple(self):
        """Test tag ordering with simple dependencies"""
        # Set up dependencies
        config = {
            'tags': {
                'participants': {},
                'girls': {'req': 'participants >= 1'},
                'guys': {'req': 'participants - girls > 0'}
            }
        }
        self.manager.analyze_dependencies(config)
        
        # Test with original order that should be preserved
        original_order = ['participants', 'girls', 'guys']
        ordered = self.manager.get_ordered_tags(original_order)
        assert ordered == ['participants', 'girls', 'guys']
        
        # Test with mixed order that should be corrected
        mixed_order = ['girls', 'participants', 'guys']
        ordered = self.manager.get_ordered_tags(mixed_order)
        assert ordered == ['participants', 'girls', 'guys']
    
    def test_get_ordered_tags_complex(self):
        """Test tag ordering with complex dependencies"""
        # Set up complex configuration
        config = {
            'tags': {
                'participants': {},
                'girls': {'req': 'participants >= 1'},
                'guys': {'req': 'participants - girls > 0'},
                'action': {},
                'scene': {},
                'dance_style': {'req': 'action == "dancing"'}
            }
        }
        self.manager.analyze_dependencies(config)
        
                # Test with the actual YAML order
        yaml_order = ['dance_style', 'participants', 'girls', 'guys', 'action', 'scene']
        ordered = self.manager.get_ordered_tags(yaml_order)

        # Expected order: minimal moves to satisfy dependencies
        expected_order = ['participants', 'girls', 'guys', 'action', 'dance_style', 'scene']
        assert ordered == expected_order
    
    def test_detect_circular_dependencies(self):
        """Test circular dependency detection"""
        # Set up circular dependencies
        config = {
            'tags': {
                'tag1': {'req': 'tag2'},
                'tag2': {'req': 'tag3'},
                'tag3': {'req': 'tag1'}  # Creates a cycle
            }
        }
        self.manager.analyze_dependencies(config)
        
        cycles = self.manager.detect_circular_dependencies()
        assert len(cycles) > 0
        assert any('tag1' in cycle and 'tag2' in cycle and 'tag3' in cycle for cycle in cycles)
    
    def test_no_circular_dependencies(self):
        """Test that no cycles are detected in valid configuration"""
        config = {
            'tags': {
                'participants': {},
                'girls': {'req': 'participants >= 1'},
                'guys': {'req': 'participants - girls > 0'}
            }
        }
        self.manager.analyze_dependencies(config)
        
        cycles = self.manager.detect_circular_dependencies()
        assert cycles == []
    
    def test_empty_config(self):
        """Test handling of empty configuration"""
        config = {}
        dependencies = self.manager.analyze_dependencies(config)
        assert dependencies == {}
        
        ordered = self.manager.get_ordered_tags([])
        assert ordered == []
    
    def test_simple_ordering_issue(self):
        """Test simple ordering issue: a depends on c, expect [c, a, b]"""
        config = {
            'tags': {
                'a': {
                    'desc': 'Tag A depends on C',
                    'req': 'c > 0',
                    'values': ['yes', 'no']
                },
                'b': {
                    'desc': 'Tag B is independent',
                    'values': ['yes', 'no']
                },
                'c': {
                    'desc': 'Tag C is independent',
                    'values': ['0', '1', '2']
                }
            }
        }
        
        dependencies = self.manager.analyze_dependencies(config)
        
        # Verify dependencies
        assert dependencies['a'] == ['c']
        assert dependencies['b'] == []
        assert dependencies['c'] == []
        
        # Test ordering with YAML order [a, b, c]
        yaml_order = ['a', 'b', 'c']
        ordered = self.manager.get_ordered_tags(yaml_order)
        
        # Expected order: [b, c, a] because a depends on c, so a gets moved after c
        expected_order = ['b', 'c', 'a']
        assert ordered == expected_order, f"Expected {expected_order}, got {ordered}"
    
    def test_real_world_config(self):
        """Test with the actual events_tags.yaml configuration"""
        config = {
            'tags': {
                'participants': {
                    'desc': 'Number of people in the scene.',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'girls': {
                    'desc': 'Number of girls in the scene.',
                    'req': 'participants >= 1',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'guys': {
                    'desc': 'Number of guys in the scene.',
                    'req': 'participants - girls > 0',
                    'type': 'int',
                    'default': 0,
                    'values': ['0', '1', '2', '3', 'many']
                },
                'action': {
                    'desc': 'High level category of what the main person is doing.',
                    'values': ['existing', 'dancing', 'climbing']
                },
                'dance_style': {
                    'desc': 'What style of dance is the main person doing?',
                    'req': 'action == "dancing"',
                    'values': [
                        {'value': 'shuffle', 'req': 'girls >= 1'},
                        {'value': 'swing', 'req': 'girls + guys > 0'},
                        {'value': 'salsa', 'req': 'girls > 0 && guys > 0'},
                        {'value': 'tango', 'req': '(girls > 0 && guys > 0) && scene == "gym"'},
                        {'value': 'breakdance', 'req': 'guys > 0'}
                    ]
                },
                'scene': {
                    'desc': 'Should this media be restricted to occurring in a certain location?',
                    'values': ['gym', 'office', 'club']
                }
            }
        }
        
        dependencies = self.manager.analyze_dependencies(config)
        
        # Verify dependencies
        assert dependencies['participants'] == []
        assert dependencies['girls'] == ['participants']
        assert set(dependencies['guys']) == {'participants', 'girls'}
        assert dependencies['action'] == []
        assert dependencies['scene'] == []
        assert set(dependencies['dance_style']) == {'action', 'girls', 'guys', 'scene'}
        
                # Test ordering
        yaml_order = ['dance_style', 'participants', 'girls', 'guys', 'action', 'scene']
        ordered = self.manager.get_ordered_tags(yaml_order)

        # Expected order: minimal moves to satisfy dependencies
        expected_order = ['participants', 'girls', 'guys', 'action', 'scene', 'dance_style']
        assert ordered == expected_order
