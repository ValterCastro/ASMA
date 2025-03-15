from announcement_types import AnnouncementType

class Announcement:
    def __init__(self, announcement_type, variable_name=None, threshold=None):
        """
        Initialize an announcement.
        - announcement_type: Type of announcement (from AnnouncementType Enum).
        - variable_name: Name of the variable to set (for SET_VARIABLE_LESS_THAN_OR_EQUAL).
        - threshold: The value x that the variable should be <= (for SET_VARIABLE_LESS_THAN_OR_EQUAL).
        """
        self.announcement_type = announcement_type
        self.variable_name = variable_name
        self.threshold = threshold

    def __str__(self):
        if self.announcement_type == AnnouncementType.SET_VARIABLE_LESS_THAN_OR_EQUAL:
            return f"Announcement: Set variable '{self.variable_name}' to a value <= {self.threshold}"
        return f"Announcement: {self.announcement_type}"