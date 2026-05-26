import maya.cmds as cmds
from Blue_Pipeline.Checks.base_check import BaseCheck


class DuplicateNames(BaseCheck):
    """Check for duplicate names in the scene."""

    name        = "Duplicate Names"
    description = "Scene should not contain nodes with duplicate names."
    can_fix     = True

    # ------------------------------------------------------------------ helpers

    def _get_all_nodes(self):
        """Get all DAG nodes in the scene."""
        return cmds.ls(dag=True, long=True) or []

    def _find_duplicates(self):
        """Find all nodes with duplicate short names.
        
        Returns
        -------
        dict : {short_name: [full_paths]}
            Groups nodes by their short name. Only includes groups with > 1 node.
        """
        nodes = self._get_all_nodes()
        name_map = {}
        
        for node in nodes:
            short_name = node.split('|')[-1]
            if short_name not in name_map:
                name_map[short_name] = []
            name_map[short_name].append(node)
        
        # Filter to only duplicates
        duplicates = {k: v for k, v in name_map.items() if len(v) > 1}
        return duplicates

    def _rename_duplicates(self, duplicates):
        """Rename duplicate nodes by appending numbers."""
        for short_name, nodes in duplicates.items():
            for i, node in enumerate(nodes[1:], start=1):
                try:
                    # Get the base name components
                    parent_path = '|'.join(node.split('|')[:-1])
                    new_name = f"{short_name}_{i}"
                    
                    if parent_path:
                        full_new_name = f"{parent_path}|{new_name}"
                    else:
                        full_new_name = new_name
                    
                    cmds.rename(node, new_name)
                except Exception as e:
                    print(f"Warning: Could not rename {node}: {e}")

    # ------------------------------------------------------------------ api

    def check(self):
        """Check if there are duplicate names."""
        duplicates = self._find_duplicates()
        has_duplicates = len(duplicates) > 0
        
        if has_duplicates:
            dup_names = ', '.join(duplicates.keys())
            print(f"Duplicate names found: {dup_names}")
        
        return not has_duplicates

    def autofix(self):
        """Rename duplicate nodes by appending numbers."""
        duplicates = self._find_duplicates()
        if duplicates:
            self._rename_duplicates(duplicates)
