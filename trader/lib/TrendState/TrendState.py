from .TrendStateInfo import TrendStateInfo

class TrendState(object):
    def __init__(self, state):
        self.state = state
        self.prev_state = TrendStateInfo.STATE_UNKNOWN
        self.direction = 0
        self.prev_direction = 0
        self.direction_count = 0
        self.prev_direction_count = 0
        self.direction_speed = TrendStateInfo.DIR_NONE_NONE
        self.prev_direction_speed = TrendStateInfo.DIR_NONE_NONE
        self.direction_speed_count = 0
        self.prev_direction_speed_count = 0
        self.start_ts = 0
        self.cur_ts = 0
        self.end_ts = 0
        self.start_price = 0
        self.cur_price = 0
        self.end_price = 0
        self.start_volume = 0
        self.cur_volume = 0
        self.end_volume = 0

    def is_state(self, state):
        return self.state == state

    def has_state_changed(self):
        return self.state != self.prev_state

    def has_direction_speed_changed(self):
        return self.direction_speed != self.prev_direction_speed

    def has_direction_speed_count_changed(self):
        return self.direction_speed_count != self.prev_direction_speed_count

    def has_direction_changed(self):
        return self.direction != self.prev_direction

    def has_direction_count_changed(self):
        return self.direction_count != self.prev_direction_count

    # conditional set state
    def set_state_conditional(self, cond, cond_true_state, cond_false_state):
        if cond:
            self.set_state(cond_true_state)
        else:
            self.set_state(cond_false_state)

    def set_state(self, state):
        # update direction from state
        direction = TrendStateInfo.get_trend_direction(state)
        self.set_direction(direction)
        self.set_direction_speed_from_state(state)
        # update state
        self.prev_state = self.state
        self.state = state

    def set_direction_speed_from_state(self, state):
        dir = TrendStateInfo.get_direction_speed_from_trend_state(state)
        self.prev_direction_speed = self.direction_speed
        self.direction_speed = dir
        self.prev_direction_speed_count = self.direction_speed_count
        if self.direction_speed != self.prev_direction_speed:
            self.direction_speed_count = 0
        else:
            self.direction_speed_count += 1

    def set_direction(self, direction):
        self.prev_direction = self.direction
        self.direction = direction
        # determine if direction changed or not
        self.prev_direction_count = self.direction_count
        if self.direction != self.prev_direction:
            self.direction_count = 0
        else:
            self.direction_count += 0
