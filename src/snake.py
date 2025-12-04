class Snake:
    def __init__(self, start_pos):
        self.body = [start_pos]
        self.direction = (1, 0)  # Default moving right
        self.grow_pending = 3

    def get_head(self):
        return self.body[0]

    def move(self, new_head):
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1
    
    def check_self_collision(self, head):
        # Check if head collides with any part of the body (excluding the tail if it's about to move)
        # However, for simplicity in this step, we just check if it's in the body.
        # Since we insert head first in move, we check against body[1:] if called after move,
        # or body if called before move with a hypothetical head.
        # Let's assume this is called with the *new* head position before moving.
        return head in self.body[:-1] # Tail will move, so it's safe? Actually standard snake rules say yes.
