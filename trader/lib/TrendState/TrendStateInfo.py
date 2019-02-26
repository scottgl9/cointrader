class TrendStateInfo(object):
    STATE_UNKNOWN                   = 0
    STATE_INIT                      = 1
    STATE_NON_TREND_NO_DIRECTION    = 2
    STATE_NON_TREND_UP_VERY_SLOW    = 3
    STATE_NON_TREND_UP_SLOW         = 4
    STATE_NON_TREND_UP_FAST         = 5
    STATE_NON_TREND_DOWN_VERY_SLOW  = 6
    STATE_NON_TREND_DOWN_SLOW       = 7
    STATE_NON_TREND_DOWN_FAST       = 8
    STATE_TRENDING_UP_VERY_SLOW     = 9
    STATE_TRENDING_UP_SLOW          = 10
    STATE_TRENDING_UP_FAST          = 11
    STATE_TRENDING_DOWN_VERY_SLOW   = 12
    STATE_TRENDING_DOWN_SLOW        = 13
    STATE_TRENDING_DOWN_FAST        = 14
    STATE_CONT_TREND_UP_VERY_SLOW   = 15
    STATE_CONT_TREND_UP_SLOW        = 16
    STATE_CONT_TREND_UP_FAST        = 17
    STATE_CONT_TREND_DOWN_VERY_SLOW = 18
    STATE_CONT_TREND_DOWN_SLOW      = 19
    STATE_CONT_TREND_DOWN_FAST      = 20
    # trend classification
    TYPE_NON_TREND                  = 21
    TYPE_TRENDING                   = 22
    TYPE_CONT_TREND                 = 23
    # direction and speed classification
    DIR_NONE_NONE                   = 24
    DIR_UP_VERY_SLOW                = 25
    DIR_UP_SLOW                     = 26
    DIR_UP_FAST                     = 27
    DIR_DOWN_VERY_SLOW              = 28
    DIR_DOWN_SLOW                   = 29
    DIR_DOWN_FAST                   = 30

    def __init__(self, state):
        self.state = state
        self.prev_state = TrendStateInfo.STATE_UNKNOWN

    def is_state(self, state):
        return self.state == state

    def get_trend_string(self, state):
        if state == TrendStateInfo.STATE_UNKNOWN:
                return "STATE_UNKNOWN"
        elif state == TrendStateInfo.STATE_INIT:
                return "STATE_INIT"
        elif state == TrendStateInfo.STATE_NON_TREND_NO_DIRECTION:
                return "STATE_NON_TREND_NO_DIRECTION"
        elif state == TrendStateInfo.STATE_NON_TREND_UP_VERY_SLOW:
                return "STATE_NON_TREND_UP_VERY_SLOW"
        elif state == TrendStateInfo.STATE_NON_TREND_UP_SLOW:
                return "STATE_NON_TREND_UP_SLOW"
        elif state == TrendStateInfo.STATE_NON_TREND_UP_FAST:
                return "STATE_NON_TREND_UP_FAST"
        elif state == TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW:
                return "STATE_NON_TREND_DOWN_VERY_SLOW"
        elif state == TrendStateInfo.STATE_NON_TREND_DOWN_SLOW:
                return "STATE_NON_TREND_DOWN_SLOW"
        elif state == TrendStateInfo.STATE_NON_TREND_DOWN_FAST:
                return "STATE_NON_TREND_DOWN_FAST"
        elif state == TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW:
                return "STATE_TRENDING_UP_VERY_SLOW"
        elif state == TrendStateInfo.STATE_TRENDING_UP_SLOW:
                return "STATE_TRENDING_UP_SLOW"
        elif state == TrendStateInfo.STATE_TRENDING_UP_FAST:
                return "STATE_TRENDING_UP_FAST"
        elif state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW:
                return "STATE_TRENDING_DOWN_VERY_SLOW"
        elif state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW:
                return "STATE_TRENDING_DOWN_SLOW"
        elif state == TrendStateInfo.STATE_TRENDING_DOWN_FAST:
                return "STATE_TRENDING_DOWN_FAST"
        elif state == TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW:
                return "STATE_CONT_TREND_UP_VERY_SLOW"
        elif state == TrendStateInfo.STATE_CONT_TREND_UP_SLOW:
                return "STATE_CONT_TREND_UP_SLOW"
        elif state == TrendStateInfo.STATE_CONT_TREND_UP_FAST:
                return "STATE_CONT_TREND_UP_FAST"
        elif state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW:
                return "STATE_CONT_TREND_DOWN_VERY_SLOW"
        elif state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW:
                return "STATE_CONT_TREND_DOWN_SLOW"
        elif state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST:
                return "STATE_CONT_TREND_DOWN_FAST"

    def is_state(self, state):
        return self.state == state

    # encode trend state given type and direction info
    @staticmethod
    def get_trend_state_from_type_and_direction(type, dir):
        state = TrendStateInfo.STATE_UNKNOWN
        if dir == TrendStateInfo.DIR_NONE_NONE:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_NO_DIRECTION
        elif dir == TrendStateInfo.DIR_UP_VERY_SLOW:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_UP_VERY_SLOW
            elif type == TrendStateInfo.TYPE_TRENDING:
                state = TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW
            elif type == TrendStateInfo.TYPE_CONT_TREND:
                state = TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW
        elif dir == TrendStateInfo.DIR_UP_SLOW:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_UP_SLOW
            elif type == TrendStateInfo.TYPE_TRENDING:
                state = TrendStateInfo.STATE_TRENDING_UP_SLOW
            elif type == TrendStateInfo.TYPE_CONT_TREND:
                state = TrendStateInfo.STATE_CONT_TREND_UP_SLOW
        elif dir == TrendStateInfo.DIR_UP_FAST:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_UP_FAST
            elif type == TrendStateInfo.TYPE_TRENDING:
                state = TrendStateInfo.STATE_TRENDING_UP_FAST
            elif type == TrendStateInfo.TYPE_CONT_TREND:
                state = TrendStateInfo.STATE_CONT_TREND_UP_FAST
        elif dir == TrendStateInfo.DIR_DOWN_VERY_SLOW:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW
            elif type == TrendStateInfo.TYPE_TRENDING:
                state = TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW
            elif type == TrendStateInfo.TYPE_CONT_TREND:
                state = TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW
        elif dir == TrendStateInfo.DIR_DOWN_SLOW:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_DOWN_SLOW
            elif type == TrendStateInfo.TYPE_TRENDING:
                state = TrendStateInfo.STATE_TRENDING_DOWN_SLOW
            elif type == TrendStateInfo.TYPE_CONT_TREND:
                state = TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW
        elif dir == TrendStateInfo.DIR_DOWN_FAST:
            if type == TrendStateInfo.TYPE_NON_TREND:
                state = TrendStateInfo.STATE_NON_TREND_DOWN_FAST
            elif type == TrendStateInfo.TYPE_TRENDING:
                state = TrendStateInfo.STATE_TRENDING_DOWN_FAST
            elif type == TrendStateInfo.TYPE_CONT_TREND:
                state = TrendStateInfo.STATE_CONT_TREND_DOWN_FAST
        return state

    # decode direction speed from trend state
    @staticmethod
    def get_direction_speed_from_trend_state(state):
        dir = 0
        if (state == TrendStateInfo.STATE_NON_TREND_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW):
            dir = TrendStateInfo.DIR_UP_VERY_SLOW
        elif (state == TrendStateInfo.STATE_NON_TREND_UP_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_SLOW):
            dir = TrendStateInfo.DIR_UP_SLOW
        elif (state == TrendStateInfo.STATE_NON_TREND_UP_FAST or
            state == TrendStateInfo.STATE_TRENDING_UP_FAST or
            state == TrendStateInfo.STATE_CONT_TREND_UP_FAST):
            dir = TrendStateInfo.DIR_UP_SLOW
        if (state == TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW):
            dir = TrendStateInfo.DIR_DOWN_VERY_SLOW
        elif (state == TrendStateInfo.STATE_NON_TREND_DOWN_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW):
            dir = TrendStateInfo.DIR_DOWN_SLOW
        elif (state == TrendStateInfo.STATE_NON_TREND_DOWN_FAST or
            state == TrendStateInfo.STATE_TRENDING_DOWN_FAST or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
            dir = TrendStateInfo.DIR_DOWN_FAST
        return dir

    # decode type from trend state
    @staticmethod
    def get_type_from_trend_state(state):
        type = 0
        if (state == TrendStateInfo.STATE_NON_TREND_NO_DIRECTION or
            state == TrendStateInfo.STATE_NON_TREND_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_NON_TREND_UP_SLOW or
            state == TrendStateInfo.STATE_NON_TREND_UP_FAST or
            state == TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_NON_TREND_DOWN_SLOW or
            state == TrendStateInfo.STATE_NON_TREND_DOWN_FAST):
            type = TrendStateInfo.TYPE_NON_TREND
        elif (state == TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_FAST or
            state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_FAST):
            type = TrendStateInfo.TYPE_TRENDING
        elif (state == TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_FAST or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
            type = TrendStateInfo.TYPE_CONT_TREND
        return type

    # return true if is in trend state
    @staticmethod
    def is_in_trend_state(state):
        if (state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_FAST or
            state == TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_FAST):
            return True
        elif (state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST or
            state == TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_FAST):
            return True
        return False

    @staticmethod
    def get_trend_direction(state):
        direction = 0
        if (state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_FAST):
            direction = -1
        elif (state == TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW or
             state == TrendStateInfo.STATE_TRENDING_UP_SLOW or
             state == TrendStateInfo.STATE_TRENDING_UP_FAST):
            direction = 1
        elif (state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
            direction = -1
        elif (state == TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW or
             state == TrendStateInfo.STATE_CONT_TREND_UP_SLOW or
             state == TrendStateInfo.STATE_CONT_TREND_UP_FAST):
            direction = 1
        return direction
