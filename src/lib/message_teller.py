class MsgTeller(object):

    def __init__(self):
        self.q = []
        self.async_flag = 0

    def put_back(self, data):
        self.q.append(data)

    def put_front(self, data):
        self.q.insert(0, data)

    def pop(self, q_index=None):
        index = q_index
        if index is None:
            index = 0

        if self.get_size() > 0:
            item = self.q.pop(index)
            return item
        else:
            return None

    def get(self, q_index=None):
        index = q_index
        if index is None:
            index = 0

        if self.get_size() > 0:
            item = self.q[index]
            return item
        else:
            return None

    def set(self, q_index, data):
        self.q[q_index] = data

    def delete_none(self):
        if self.get_size() > 0:
            self.q = [x for x in self.q if x is not None]

    def get_size(self):
        return len(self.q)

    def sort(self):
        if self.get_size() > 2:
            self.q.sort(key=lambda x: x[0], reverse=True)

    def decrease_q(self, num):
        if self.get_size() > 0:
            for i in range(self.get_size()):
                self.q[i][0] = (self.q[i][0] - num)

    def say(self):
        if self.get_size() > 0:
            message = self.pop()
            print("캐스터: ", message.rstrip('\n'))
