class CasterQueue:
    q = []

    def put(self, data):
        for item in data:
            self.q.append(item)

    def get(self):
        if self.size() > 0:
            item = self.q[0]
            del self.q[0]
            return item
        else:
            return None

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