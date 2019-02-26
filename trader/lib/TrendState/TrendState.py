from .TrendStateInfo import TrendStateInfo


class TrendState(object):
    def __init__(self, state, percent_slow_cutoff, percent_very_slow_cutoff):
        self.percent_slow_cutoff = percent_slow_cutoff
        self.percent_very_slow_cutoff = percent_very_slow_cutoff
        self.trend_state = TrendStateInfo(state)
        self.seg_down_list = []
        self.seg_up_list = []

    def get_state(self):
        return self.trend_state.state

    def get_direction_speed_movement(self, percent, direction):
        if direction == 1:
            if percent < self.percent_very_slow_cutoff:
                return TrendStateInfo.DIR_UP_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendStateInfo.DIR_UP_SLOW
            else:
                return TrendStateInfo.DIR_UP_FAST
        elif direction == -1:
            if percent < self.percent_very_slow_cutoff:
                return TrendStateInfo.DIR_DOWN_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendStateInfo.DIR_DOWN_SLOW
            else:
                return TrendStateInfo.DIR_DOWN_FAST
        return TrendStateInfo.DIR_NONE_NONE

    def process_trend_segment_state(self, seg_down, seg_up, ts):
        self.seg_down_list.append(seg_down)
        self.seg_up_list.append(seg_up)

        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if seg_down_percent == seg_up_percent:
            self.trend_state.set_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION)
            return self.trend_state

        # determine which direction update is most recent
        direction = self.process_trend_direction(seg_down, seg_up)

        if not direction:
            self.trend_state.set_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION)
            return self.trend_state

        if self.trend_state.is_state(TrendStateInfo.STATE_INIT):
            if direction == 1:
                dir = self.get_direction_speed_movement(seg_up_percent, 1)
                new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
                self.trend_state.set_state(new_state)
            elif direction == -1:
                dir = self.get_direction_speed_movement(seg_down_percent, -1)
                new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
                self.trend_state.set_state(new_state)

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
        if not self.trend_state.has_state_changed() and len(self.seg_down_list) > 2 and len(self.seg_up_list) > 2:
            self.process_potential_upward_reversal(seg_down, seg_up, direction)
            self.process_potential_downward_reversal(seg_down, seg_up, direction)

        return self.trend_state

    def process_trend_direction(self, seg_down, seg_up):
        seg_down_start_ts = int(seg_down['start_ts'])
        seg_up_start_ts = int(seg_up['start_ts'])
        seg_down_end_ts = int(seg_down['end_ts'])
        seg_up_end_ts = int(seg_up['end_ts'])

        direction = 0

        # determine which direction update is most recent
        if seg_down_end_ts > seg_up_end_ts or seg_down_start_ts > seg_up_end_ts:
            direction = -1
        elif seg_up_end_ts > seg_down_end_ts or seg_up_start_ts > seg_down_end_ts:
            direction = 1

        return direction

    def process_potential_downward_reversal(self, seg_down, seg_up, direction):
        seg_down_prev = self.seg_down_list[-2]
        seg_up_prev = self.seg_up_list[-2]
        seg_down_prev_percent = abs(float(seg_down_prev['percent']))
        seg_up_prev_percent = abs(float(seg_up_prev['percent']))
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        # check if could be downward trend reversal
        if seg_up_percent < seg_up_prev_percent and seg_down_percent > seg_down_prev_percent:
            if TrendStateInfo.get_trend_direction(self.trend_state.state) != 1:
                return
        else:
            return

        type = TrendStateInfo.get_type_from_trend_state(self.trend_state.state)

        if type == TrendStateInfo.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, newdir)
            self.trend_state.set_state(new_state)

    def process_potential_upward_reversal(self, seg_down, seg_up, direction):
        seg_down_prev = self.seg_down_list[-2]
        seg_up_prev = self.seg_up_list[-2]
        seg_down_prev_percent = abs(float(seg_down_prev['percent']))
        seg_up_prev_percent = abs(float(seg_up_prev['percent']))
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        # check if could be upward trend reversal
        if seg_up_percent > seg_up_prev_percent and seg_down_percent < seg_down_prev_percent:
            if TrendStateInfo.get_trend_direction(self.trend_state.state) != -1:
                return
        else:
            return

        type = TrendStateInfo.get_type_from_trend_state(self.trend_state.state)

        if type == TrendStateInfo.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, newdir)
            self.trend_state.set_state(new_state)

    def process_state_non_trend_no_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_non_trend_up_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(state)

    def process_state_non_trend_down_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            self.trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_trending_up_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_trending_down_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_cont_trend_up_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # possible that trend is about to switch direction, so set to trend up slow
            self.trend_state.set_state(TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW)

        elif direction == 1 and seg_down_percent < seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)

    def process_state_cont_trend_down_direction(self, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # self.trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            self.trend_state.set_state(state)

        elif direction == 1 and seg_down_percent < seg_up_percent:
            # possible that trend is about to switch direction, so set to trend down slow
            self.trend_state.set_state(TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW)
