class State:
    def __init__(self,normalized_keeper, keeper, boxes):
        self.normalized_keeper = normalized_keeper
        self.keeper = keeper
        self.boxes = boxes

    def __eq__(self, other):
        if isinstance(other, State):
            return self.normalized_keeper == other.normalized_keeper and self.boxes == other.boxes
        return False

    def __str__(self):
        return f"Keeper: {self.keeper}, Boxes: {self.boxes}, Normalized: {self.normalized_keeper})"
