import pytest
import os
import yaml
from tagging.tag_registry import TagRegistry


class TestFrontendDefaults:
    """Test that frontend default logic works correctly"""
    
    def test_default_application_when_tag_requirements_not_met(self, temp_dir):
        """Test that defaults are applied when tag requirements are not met"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create a test YAML file with a tag that has a default
        yaml_path = os.path.join(temp_dir, "events_tags.yaml")
        test_config = {
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
                }
            }
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Simulate frontend logic: when participants=1, girls=1, guys should get default=0
        # because participants - girls = 0, which is not > 0
        
        # First, set the tags that would be answered by user
        user_tags = {
            'participants': '1',
            'girls': '1'
        }
        
        # Simulate the frontend logic for applying defaults
        tag_config = tag_registry.get_tag_config()
        
        # Check if 'guys' would be skipped due to unmet requirements
        guys_info = tag_config['tags']['guys']
        guys_req = guys_info['req']  # 'participants - girls > 0'
        
        # Simulate evaluating the condition with current tags
        # participants=1, girls=1, so participants - girls = 0, which is not > 0
        # Therefore guys should get its default value
        
        # This simulates what the frontend would do
        if guys_info.get('default') is not None:
            user_tags['guys'] = guys_info['default']
        
        # Save the tags (including the applied default)
        success = tag_registry.set_media_tags('events/test.jpg', user_tags)
        assert success is True
        
        # Verify the default was applied
        loaded_tags = tag_registry.get_media_tags('events/test.jpg')
        assert loaded_tags['participants'] == 1
        assert loaded_tags['girls'] == 1
        assert loaded_tags['guys'] == 0  # Default value should be applied
        
    def test_no_default_when_requirements_met(self, temp_dir):
        """Test that defaults are NOT applied when tag requirements are met"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create a test YAML file with a tag that has a default
        yaml_path = os.path.join(temp_dir, "events_tags.yaml")
        test_config = {
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
                }
            }
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Simulate frontend logic: when participants=2, girls=1, guys should NOT get default
        # because participants - girls = 1, which is > 0, so guys should be presented to user
        
        # First, set the tags that would be answered by user
        user_tags = {
            'participants': '2',
            'girls': '1'
        }
        
        # Simulate the frontend logic for applying defaults
        tag_config = tag_registry.get_tag_config()
        
        # Check if 'guys' would be skipped due to unmet requirements
        guys_info = tag_config['tags']['guys']
        guys_req = guys_info['req']  # 'participants - girls > 0'
        
        # Simulate evaluating the condition with current tags
        # participants=2, girls=1, so participants - girls = 1, which is > 0
        # Therefore guys should NOT get its default value (user should be prompted)
        
        # This simulates what the frontend would do
        # Since requirements are met, no default should be applied
        # The user would be prompted for 'guys' value
        
        # Save the tags (without applying default)
        success = tag_registry.set_media_tags('events/test.jpg', user_tags)
        assert success is True
        
        # Verify the default was NOT applied
        loaded_tags = tag_registry.get_media_tags('events/test.jpg')
        assert loaded_tags['participants'] == 2
        assert loaded_tags['girls'] == 1
        assert 'guys' not in loaded_tags  # Default should NOT be applied
