class Snake:
  def __init__(self, start_pos, start_width):
    self.body = [start_pos]
    self.direction = (1, 0)  # Default moving right
    # Maintain a parallel list of movement directions for each body segment.
    # directions[i] represents the unit vector that segment i followed when it
    # moved into its current position.
    self.directions = [self.direction]
    self.grow_pending = start_width

  def get_head(self):
    return self.body[0]

  def move(self, new_head):
    """Move snake by inserting a new head and optionally removing the tail.

    This method also keeps the ``directions`` list in sync with the body so that
    ``directions[i]`` always corresponds to ``body[i]``.
    """
    # Insert new head & its direction vector at the front
    self.body.insert(0, new_head)
    self.directions.insert(0, self.direction)

    if self.grow_pending > 0:
      # Growing – keep the tail; just decrease the counter.
      self.grow_pending -= 1
    else:
      # Normal move – remove tail segment and its direction entry.
      self.body.pop()
      self.directions.pop()

  def grow(self):
    self.grow_pending += 1

  def check_self_collision(self, head):
    # Check if head collides with any part of the body (excluding the tail if it's about to move)
    # However, for simplicity in this step, we just check if it's in the body.
    # Since we insert head first in move, we check against body[1:] if called after move,
    # or body if called before move with a hypothetical head.
    # Let's assume this is called with the *new* head position before moving.
    return head in self.body[:-1]  # Tail will move, so it's safe? Actually standard snake rules say yes.
