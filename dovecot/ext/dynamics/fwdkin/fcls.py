from .. import fcl


class FclSpace(object):

    def __init__(self):
        self._bodies = []
        self.contacts = []
        self._bodymap = {}
        self._bodydict = {}
        self._pyfcl = fcl.Fcl()

    def register_body(self, body):
        if body.meta is not None:
            self._bodydict[body.meta] = body # just as a convenience, no collision checking
        self._bodies.append(body)

    def body(self, meta):
        return self._bodydict[meta]


    def collisions(self):
        self.contacts = []

        self._pyfcl.reset()

        self._keymap = {}
        for body in self._bodies:
            geom = list(body.geom) + list(body.trans) + list(body.quat)
            key = self._pyfcl.add_box_quat(*geom)
            self._bodymap[key] = body


        self._pyfcl.collide()

        keys_1st = self._pyfcl.get_first_keys()
        keys_2nd = self._pyfcl.get_second_keys()

        for k1, k2 in zip(keys_1st, keys_2nd):
            body1 = self._bodymap[k1]
            body2 = self._bodymap[k2]

            if len(body1.groups.intersection(body2.groups)) == 0:
                    self.contacts.append((None, body1, body2))

        return self.contacts
