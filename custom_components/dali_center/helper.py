"""Helper functions for Dali Center."""


def find_set_differences(
    list1: list, list2: list, attr_name: str
) -> tuple[list, list]:
    """
    Calculate the difference between two object lists.

    Args:
        - list1: First list of objects
        - list2: Second list of objects  
        - attr_name: Name of attribute to compare (e.g. "unique_id")

    Returns:
        - unique1: List of objects that exist in list1 but not in list2
        - unique2: List of objects that exist in list2 but not in list1
    """
    set1_keys = {obj[attr_name] for obj in list1}
    set2_keys = {obj[attr_name] for obj in list2}
    unique1 = [obj for obj in list1 if obj[attr_name] not in set2_keys]
    unique2 = [obj for obj in list2 if obj[attr_name] not in set1_keys]
    return unique1, unique2
