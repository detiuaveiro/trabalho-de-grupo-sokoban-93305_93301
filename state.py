class State:
    def __init__(self, keeper, boxes):
        self.keeper = keeper
        self.boxes = boxes

    def __eq__(self, other):
        if isinstance(other, State):    
            return self.keeper == other.keeper and self.boxes == other.boxes
        return False