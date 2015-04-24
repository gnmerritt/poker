import unittest
import pokeher.cython_random as random


class RandomTest(unittest.TestCase):
    """Tests that the crappy bootleg random functions I wrote match up
    reasonably well to the python random API"""
    def test_uniform(self):
        for i in range(1, 50):
            uniform = random.uniform(0, i)
            self.assertTrue(uniform >= 0, "uniform output too small")
            self.assertTrue(uniform <= i, "uniform output too big")

    def test_randint(self):
        saw = {}
        for _ in range(50):
            result = random.randint(0, 1)
            count = saw.get(result, 0)
            saw[result] = count + 1
        self.assertEqual(len(saw), 2)
        for n, c in saw.iteritems():
            self.assertTrue(n in [0,1])
            self.assertTrue(c > 10)

    def test_randint_range(self):
        min = 30
        max = 3911
        saw = {}
        for _ in range(500):
            result = random.randint(min, max)
            count = saw.get(result, 0)
            saw[result] = count + 1

        for n, c in saw.iteritems():
            self.assertTrue(n >= min)
            self.assertTrue(n <= max)

    def test_sample(self):
        population = ['a', 'b', 'c', 1, 2, 3, 4]
        for i in range(0, len(population)):
            sample = random.sample(population, i)
            self.assertEqual(len(sample), i, "sample wrong length")
            counts = {}
            for p in sample:
                self.assertTrue(p in population,
                                "member in sample not from population")
                count = counts.get(p, 0)
                counts[p] = count + 1

            for p, count in counts.iteritems():
                self.assertEqual(count, 1, "saw duplicates from sample")
