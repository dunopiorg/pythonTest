class CasterQueue:
    q = []
    async_flag = 0

    def put(self, data):
        self.q.extend(data)

    def get(self, q_index=None):
        if q_index is None:
            q_index = 0

        if self.size() > 0:
            item = self.q[q_index]
            return item
        else:
            return None

    def set(self, q_index, data):
        self.q[q_index] = data

    def delete_none(self):
        if self.size() > 0:
            self.q = [x for x in self.q if x is not None]

    def remove(self, priority):
        if self.size() > 0:
            for i, v in enumerate(self.q):
                if v[0] < priority:
                    del self.q[i]

    def size(self):
        return len(self.q)

    def sort(self):
        if self.size() > 2:
            self.q.sort(key=lambda x: x[0], reverse=True)

    def decrease_q(self, dnum):
        if self.size() > 0:
            for i in range(self.size()):
                self.q[i][0] = (self.q[i][0] - dnum)
