import math

import natnet

def dist(a, b):
    assert len(a) == len(b)
    return math.sqrt(sum(abs(a_i - b_i)**2 for a_i, b_i in zip(a, b)))

class MarkerTracker(object):
    """Class for tracking a robustly tracking a single marker"""

    def __init__(self, rb_name, ref_position):
        """The marker must be member of a given rigid body, and its position known in the first frame"""
        self.nnclient = natnet.NatNetClient()
        self.rb_name = rb_name
        self._ref_position = ref_position
        self._last_pos = None
        self._setup()

    def _update_frame(self):
        raw_frame = self.nnclient.receive_frame()
        self._frame = raw_frame.unpack_data()

    def _find_rbid(self):
        """We assume the frame has been updated"""
        rb_markers = self._frame['markersets'][self.rb_name]
        for idx, rb2 in enumerate(self._frame['rb']):
            if (len(rb2['markers']) == len(rb_markers)
                and all(m_rb_pos == m_rb2['position'] for m_rb_pos, m_rb2 in zip(rb_markers, rb2['markers']))):
                return idx, rb2['id']

        assert False # something is really wrong with the frame if we get here.

    def _setup(self):
        self._update_frame()
        self._rb_idx_id = self._find_rbid() # this won't ever change

        # we want to find the marker of the rb closest to our ref pos
        rb_markers = self._frame['markersets'][self.rb_name]
        d_ref   = [dist(self._ref_position, p) for p in rb_markers]
        min_ref = min(d_ref)
        assert min_ref < 0.02, "closest marker is at {} mm too far.".format(int(min_ref*1000)) # if the marker has moved by more than 2cm, something's up.
        self._m_idx = d_ref.index(min_ref) # this won't ever change
        self._last_pos = rb_markers[self._m_idx]

        assert self._update_marker_id() is not None

    def _update_marker_id(self):
        """This only can be done if the rigid body is visible"""
        try:
            rb_markers = self._frame['markersets'][self.rb_name]
        except KeyError:
            return None

        rb_idx, rb_id = self._rb_idx_id
        for rb in self._frame['rb']:
            if rb['id'] == rb_id:
                marker = rb['markers'][self._m_idx]
                assert marker['position'] == rb_markers[self._m_idx]

                #return rb['markers'][self._m_idx]['id']

        marker = self._frame['rb'][rb_idx]['markers'][self._m_idx]
        assert marker['position'] == rb_markers[self._m_idx]

        self._m_id = marker['id']
        return self._m_id

    def update(self):
        self._update_frame()
        try:
            rb_markers = self._frame['markersets'][self.rb_name]
            # the rigid body is detected, good
            self._update_marker_id() # if it changed
            self._last_pos = rb_markers[self._m_idx]
            return rb_markers[self._m_idx]
        except KeyError:
            # no rigid body, many be the marker is still labelled ?
            for marker in self._frame['lb_markers']:
                if marker['id'] == self._m_id:
                    self._last_pos = marker['position']
                    return marker['position']

            # we don't know which marker it is. If the closest is at less than
            # 10mm from its last dsfsfsafafpos *and* no other is closer than 20mm, then we
            # heuristically decide it is the marker we are looking for,HGTLO9..LO9LO9.LO9........L.R4ih
            for marker in self._frame['lb_markers']:
                if dist(marker['position'], self._last_pos) < 0.01:
                    self._m_id = marker['id']
                    self._last_pos = marker['position']
                    return self._last_pos
            return None

if __name__ == "__main__":
    import time, sys
    from toolbox import gfx

    ref_point = (-0.1096, 0.1100,-0.2106) # compliant stem
#    ref_point = (-0.1036, 0.2461, 0.1383) # init pose
    rb_name   = 'Rigid Body 1'
    mt = MarkerTracker(rb_name, ref_point)

    last_pos = ref_point
    while True:
        pos = mt.update()
        if pos is None:
            color = gfx.red
        else:
            last_pos = pos
            color = gfx.green
        print('{}{}{}\r'.format(color, ', '.join('{:+5.4f}'.format(e) for e in last_pos), gfx.end)),
        sys.stdout.flush()
        time.sleep(0.01)