
#
# Source for the AnimationCurve math: unity forums.
#

class KeyFrame:

    def __init__(self, time, value, in_tangent, out_tangent):
        self.time = time
        self.value = value
        self.in_tangent = in_tangent
        self.out_tangent = out_tangent

class AnimationCurve:

    def __init__(self, keys):
        self.keys = keys

    def evaluate(self, time):
        value = 0.0
        for i in range(len(self.keys) - 1):
            kf1 = self.keys[i]
            kf2 = self.keys[(i + 1)]
            min_check = (0.0, 1.0)[(time > kf1.time)]
            max_check = (0.0, 1.0)[(time <= kf2.time)]
            check = min_check * max_check
            value += self.__evaluate(time, kf1, kf2) * check
        else:
            return value

    def __evaluate(self, t, kf1, kf2):
        p1x = kf1.time
        p1y = kf1.value
        p1s = kf1.out_tangent
        p2x = kf2.time
        p2y = kf2.value
        p2s = kf2.in_tangent
        e = 1 / (p2x - p1x)
        f = e * (p1s - p2s)
        a = (p1s + p2s + 2 * e * (p1y - p2y)) * e ** 2
        b = (a * 3 * (p2x + p1x) + f) / -2
        c = p2x * (a * 3 * p1x + f) + p2s
        d = p1x / 2 * (a * p1x * (p1x - p2x * 3) + f * (p1x - p2x * 2) - p2s * 2) + p1y
        return t * (t ** 2 * a + t * b + c) + d