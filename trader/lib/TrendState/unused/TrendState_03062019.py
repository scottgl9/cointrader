from .TrendStateInfo import TrendStateInfo


class TrendState(object):
    def __init__(self, state, percent_slow_cutoff, percent_very_slow_cutoff):
        self.percent_slow_cutoff = percent_slow_cutoff
        self.percent_very_slow_cutoff = percent_very_slow_cutoff
        self.trend_state = TrendStateInfo(state)
        self.seg_down_list = []
        self.seg_up_list = []
        self.value = 0
        self.prev_value = 0
        self.ts = 0
        self.prev_ts = 0

    def get_state(self):
        return self.trend_state.state

    def state_changed(self):
        return self.trend_state.state != self.trend_state.prev_state

    def is_in_trend_state(self):
        return TrendStateInfo.is_in_trend_state(self.trend_state.state)

    def is_in_up_trend_state(self):
        return TrendStateInfo.is_in_up_trend_state(self.trend_state.state)

    def is_in_down_trend_state(self):
        return TrendStateInfo.is_in_down_trend_state(self.trend_state.state)

    def is_in_up_trend_very_slow_state(self):
        return TrendStateInfo.is_in_up_trend_very_slow_state(self.trend_state.state)

    def is_in_down_trend_very_slow_state(self):
        return TrendStateInfo.is_in_down_trend_very_slow_state(self.trend_state.state)

    def get_direction(self):
        return self.trend_state.direction

    def get_direction_speed_movement(self, percent, direction):
        if direction == TrendStateInfo.DIRECTION_UP:
            if percent < self.percent_very_slow_cutoff:
                return TrendStateInfo.DIR_UP_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendStateInfo.DIR_UP_SLOW
            else:
                return TrendStateInfo.DIR_UP_FAST
        elif direction == TrendStateInfo.DIRECTION_DOWN:
            if percent < self.percent_very_slow_cutoff:
                return TrendStateInfo.DIR_DOWN_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendStateInfo.DIR_DOWN_SLOW
            else:
                return TrendStateInfo.DIR_DOWN_FAST
        return TrendStateInfo.DIR_NONE_NONE

    def process_trend_state(self, seg_down, seg_up, value, ts):
        self.prev_value = self.value
        self.value = value

        self.prev_ts = self.ts
        self.ts = ts

        self.seg_down_list.append(seg_down)
        self.seg_up_list.append(seg_up)

        if abs(seg_down.percent) == abs(seg_up.percent):
            self.trend_state.set_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION)
            return self.trend_state

        # determine which direction update is most recent
        direction = self.process_trend_direction(seg_down, seg_up)

        if not direction:
            self.trend_state.set_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION)
            return self.trend_state

        if self.trend_state.is_state(TrendStateInfo.STATE_INIT):
            if direction == TrendStateInfo.DIRECTION_UP:
                dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
                new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
                self.trend_state.set_state(new_state)
                return self.trend_state
            elif direction == TrendStateInfo.DIRECTION_DOWN:
                dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
                new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
                self.trend_state.set_state(new_state)
                return self.trend_state

        if self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION):
            self.process_state_non_trend_no_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW):
            self.process_state_non_trend_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_DOWN_SLOW):
            self.process_state_non_trend_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_DOWN_FAST):
            self.process_state_non_trend_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_UP_VERY_SLOW):
            self.process_state_non_trend_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_UP_SLOW):
            self.process_state_non_trend_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_NON_TREND_UP_FAST):
            self.process_state_non_trend_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW):
            self.process_state_trending_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_TRENDING_DOWN_SLOW):
            self.process_state_trending_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_TRENDING_DOWN_FAST):
            self.process_state_trending_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW):
            self.process_state_trending_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_TRENDING_UP_SLOW):
            self.process_state_trending_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_TRENDING_UP_FAST):
            self.process_state_trending_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW):
            self.process_state_cont_trend_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW):
            self.process_state_cont_trend_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
            self.process_state_cont_trend_down_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW):
            self.process_state_cont_trend_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_UP_SLOW):
            self.process_state_cont_trend_up_direction(seg_down, seg_up, direction)
        elif self.trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_UP_FAST):
            self.process_state_cont_trend_up_direction(seg_down, seg_up, direction)

        # check if the state hasn't changed, and trend could be changing
        if not self.trend_state.has_state_changed() and len(self.seg_down_list) != 1 and len(self.seg_up_list) != 1:
            self.process_potential_upward_reversal(seg_down, seg_up)
            self.process_potential_downward_reversal(seg_down, seg_up)

        return self.trend_state

    def process_trend_direction(self, seg_down, seg_up):
        direction = 0

        # determine which direction update is most recent
        if seg_down.end_ts > seg_up.end_ts or seg_down.start_ts > seg_up.end_ts:
            direction = -1
        elif seg_up.end_ts > seg_down.end_ts or seg_up.start_ts > seg_down.end_ts:
            direction = 1

        return direction

    # process if current trend direction is up, seg_up_percent is shrinking, and seg_down_percent is growing
    def process_potential_downward_reversal(self, seg_down, seg_up):
        seg_down_prev = self.seg_down_list[-2]
        seg_up_prev = self.seg_up_list[-2]

        # check if could be downward trend reversal
        if abs(seg_up.percent) < abs(seg_up_prev.percent) and abs(seg_down.percent) > abs(seg_down_prev.percent):
            if TrendStateInfo.get_trend_direction(self.trend_state.state) != TrendStateInfo.DIRECTION_UP:
                return
        else:
            return

        type = TrendStateInfo.get_type_from_trend_state(self.trend_state.state)

        if type == TrendStateInfo.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, newdir)
            self.trend_state.set_state(new_state)

    # process if current trend direction is up, seg_down_percent is shrinking, and seg_up_percent is growing
    def process_potential_upward_reversal(self, seg_down, seg_up):
        seg_down_prev = self.seg_down_list[-2]
        seg_up_prev = self.seg_up_list[-2]

        # check if could be upward trend reversal
        if abs(seg_up.percent) > abs(seg_up_prev.percent) and abs(seg_down.percent) < abs(seg_down_prev.percent):
            if TrendStateInfo.get_trend_direction(self.trend_state.state) != TrendStateInfo.DIRECTION_DOWN:
                return
        else:
            return

        type = TrendStateInfo.get_type_from_trend_state(self.trend_state.state)

        if type == TrendStateInfo.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, newdir)
            self.trend_state.set_state(new_state)

    def process_state_non_trend_no_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_non_trend_up_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(state)

    def process_state_non_trend_down_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_trending_up_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_trending_down_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_cont_trend_up_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_cont_trend_down_direction(self, seg_down, seg_up, direction):
        if direction == TrendStateInfo.DIRECTION_DOWN and abs(seg_down.percent) > abs(seg_up.percent):
            if self.value > self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_down.percent), TrendStateInfo.DIRECTION_DOWN)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == TrendStateInfo.DIRECTION_UP and abs(seg_down.percent) < abs(seg_up.percent):
            if self.value < self.prev_value:
                return
            dir = self.get_direction_speed_movement(abs(seg_up.percent), TrendStateInfo.DIRECTION_UP)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(state)
