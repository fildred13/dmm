"""
Tag Dependency Manager
Handles analysis of tag dependencies and ordering for proper tag presentation
"""

import re
from typing import List, Dict, Set, Any
from collections import defaultdict


class TagDependencyManager:
    """Manages tag dependencies and ordering"""
    
    def __init__(self):
        self.tag_dependencies: Dict[str, Set[str]] = {}
        self.tag_config: Dict[str, Any] = {}
    
    def analyze_dependencies(self, tag_config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze dependencies for all tags in the configuration"""
        self.tag_config = tag_config
        self.tag_dependencies = {}
        
        if 'tags' not in tag_config:
            return {}
        
        # Analyze each tag's dependencies
        for tag_name, tag_info in tag_config['tags'].items():
            dependencies = []
            seen_deps = set()
            
            # Check tag-level requirements
            if 'req' in tag_info:
                deps = self._extract_variables_from_condition(tag_info['req'])
                for dep in deps:
                    if dep not in seen_deps:
                        dependencies.append(dep)
                        seen_deps.add(dep)
            
            # Check value-level requirements
            if 'values' in tag_info:
                for value_item in tag_info['values']:
                    if isinstance(value_item, dict) and 'req' in value_item:
                        deps = self._extract_variables_from_condition(value_item['req'])
                        for dep in deps:
                            if dep not in seen_deps:
                                dependencies.append(dep)
                                seen_deps.add(dep)
            
            self.tag_dependencies[tag_name] = set(dependencies)
        
        # Return dependencies as lists, preserving order as they appear in conditions
        return {tag: list(deps) for tag, deps in self.tag_dependencies.items()}
    
    def get_ordered_tags(self, tag_order: List[str]) -> List[str]:
        """Get tags in the correct order based on dependencies"""
        if not tag_order:
            return []
        
        # Start with the original order
        ordered_tags = tag_order.copy()
        
        # Keep looping until no changes are made
        while True:
            previous_order = ordered_tags.copy()
            
            # Loop through the current list of tags
            for i, tag_name in enumerate(ordered_tags):
                # Get dependencies for this tag
                dependencies = self.tag_dependencies.get(tag_name, set())
                
                # Find the latest position of any dependency
                latest_dep_index = -1
                for dep in dependencies:
                    for j, check_tag in enumerate(ordered_tags):
                        if check_tag == dep:
                            latest_dep_index = max(latest_dep_index, j)
                            break
                
                # If any dependency comes after this tag, move this tag to after the latest dependency
                if latest_dep_index > i:
                    # Remove this tag from its current position
                    ordered_tags.pop(i)
                    # Insert it after the latest dependency (adjust index since we removed an item)
                    if latest_dep_index >= i:
                        latest_dep_index -= 1
                    ordered_tags.insert(latest_dep_index + 1, tag_name)
                    break  # Start over since we modified the list
            
            # If no changes were made, we're done
            if ordered_tags == previous_order:
                break
        
        return ordered_tags
    
    def _extract_variables_from_condition(self, condition: str) -> List[str]:
        """Extract variable names from a condition string in order of appearance"""
        if not condition:
            return []
        
        # Remove string literals first to avoid picking them up as variables
        # This removes anything between quotes
        condition_without_strings = re.sub(r'"[^"]*"', '', condition)
        condition_without_strings = re.sub(r"'[^']*'", '', condition_without_strings)
        
        # Find identifiers (variable names) - sequences of letters, numbers, and underscores
        # that are not at the start of a string literal
        pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        matches = re.findall(pattern, condition_without_strings)
        
        # Filter out operators and keywords, preserving order
        operators = {'and', 'or', 'not', 'true', 'false', 'null', 'undefined'}
        variables = []
        seen = set()
        for match in matches:
            if match.lower() not in operators and match not in seen:
                variables.append(match)
                seen.add(match)
        
        return variables
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the tag configuration"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(tag_name: str, path: List[str]) -> None:
            """Depth-first search to detect cycles"""
            if tag_name in rec_stack:
                # Found a cycle
                cycle_start = path.index(tag_name)
                cycle = path[cycle_start:] + [tag_name]
                cycles.append(cycle)
                return
            
            if tag_name in visited:
                return
            
            visited.add(tag_name)
            rec_stack.add(tag_name)
            path.append(tag_name)
            
            # Visit all dependencies
            for dep in self.tag_dependencies.get(tag_name, set()):
                dfs(dep, path.copy())
            
            rec_stack.remove(tag_name)
        
        # Check for cycles starting from each tag
        for tag_name in self.tag_dependencies:
            if tag_name not in visited:
                dfs(tag_name, [])
        
        return cycles
