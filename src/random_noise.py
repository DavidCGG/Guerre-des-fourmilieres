import random

## Tout le crédit pour cette classe va à l'utilisateur 'wtf_that_guy' sur Reddit.
## lien: https://www.reddit.com/r/Python/comments/a45779/terrain_generation_in_python/?rdt=49532


class RandomNoise:
    def __init__(self, width=32, height=32, bit_depth=255, extra=32):
        self.w = width + extra
        self.h = height + extra
        self.bit_depth = bit_depth
        self.extra = extra
        self.n = []

    def randomize(self):
        self.n = [[random.randint(0, self.bit_depth) / self.bit_depth for y in range(self.h)] for x in range(self.w)]

    def noise2d(self, x, y):
        return self.n[x][y]

    def smoothNoise2d(self, bit_depth=255, smoothing_passes=15, upper_value_limit=1):
        """
        Smooths the random grid and returns the smoothed noise values
        """
        # If not enough grid size
        if self.extra < smoothing_passes:
            print(
                "Warning, to maintain intial grid, call the RandomNoise object with a larger 'extra' value; i.e. RandomNoise(extra=your_extra)")
            self.extra = smoothing_passes
            self.__init__(extra=smoothing_passes)
            self.randomize()

        # Convert the grid to values between 0 and the upper_value_limit
        values = [[upper_value_limit * self.noise2d(x, y) for y in range(self.h - self.extra + smoothing_passes)] for x
                  in range(self.w - self.extra + smoothing_passes)]

        # Smoothing the random grid
        for _pass in range(smoothing_passes):
            self.largest_delta = float(max(map(max, values)) - min(map(min, values))) ** 2
            values = [
                [((values[x][y] + values[x + 1][y] + values[x][y + 1] + values[x - 1][y] + values[x][y - 1]) / 5) for y
                 in range(len(values[x]) - 1)] for x in range(len(values) - 1)]

        return values