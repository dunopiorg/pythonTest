class ScoreTable(object):

    def __init__(self):
        self._SCORE_TABLE = []
        self._ASYNC_FLAG = 0

    def put(self, data):
        self._SCORE_TABLE.extend(data)

    def get(self, table_index=None):
        index = table_index
        if index is None:
            index = 0

        if self.get_size() > 0:
            item = self._SCORE_TABLE[index]
            return item
        else:
            return None

    def set(self, table_index, data):
        self._SCORE_TABLE[table_index] = data

    def clear_none(self):
        if self.get_size() > 0:
            self._SCORE_TABLE = [x for x in self._SCORE_TABLE if x is not None]

    def get_size(self):
        if self._SCORE_TABLE is None:
            return 0
        else:
            return len(self._SCORE_TABLE)

    def sort(self):
        if self.get_size() > 2:
            self._SCORE_TABLE.sort(key=lambda x: x[0], reverse=True)

    def decrease_q(self, num):
        if self.get_size() > 0:
            for i in range(self.get_size()):
                self._SCORE_TABLE[i][0] = (self._SCORE_TABLE[i][0] - num)

    def get_async(self):
        return self._ASYNC_FLAG

    def set_async(self, flag):
        self._ASYNC_FLAG = flag

    def is_ready(self):
        if self.get_async() == 0 and self.get_size() > 0:
            self.set_async(1)
            self.sort()
            self.set_async(0)
            return True
        else:
            return False

    def get_group(self):
        parameter_list = []
        event_group = ''
        event = ''
        grouping_event = 0

        for i in range(self.get_size()):
            if i == 0:
                selected_row = self.get(i)
                if selected_row[1] == "HIT_EVENT":
                    grouping_event = 1
                else:
                    grouping_event = 3
                event_group = selected_row[grouping_event]
                event = selected_row[1]
                parameter_list.append(selected_row)
                self.set(i, None)
            else:
                relative_row = self.get(i)
                if event_group == relative_row[grouping_event]:
                    parameter_list.append(relative_row)
                    self.set(i, None)

        self.clear_none()
        return event, event_group, parameter_list
