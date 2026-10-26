import unittest
from smartattend_face_matching.matching import cosine_similarity, normalize_embedding

class MatchingTests(unittest.TestCase):
    def test_cosine_geometry(self):
        self.assertAlmostEqual(cosine_similarity([1,0],[1,0]),1)
        self.assertAlmostEqual(cosine_similarity([1,0],[0,1]),0)
        self.assertAlmostEqual(cosine_similarity([1,0],[-1,0]),-1)
    def test_invalid_vectors_are_rejected(self):
        with self.assertRaises(ValueError): cosine_similarity([1,2],[1])
        with self.assertRaises(ValueError): cosine_similarity([float('nan')],[1])
        with self.assertRaises(ValueError): normalize_embedding([float('inf')])
    def test_zero_vectors_do_not_match(self):
        self.assertEqual(cosine_similarity([0,0],[1,0]),0)
        self.assertEqual(list(normalize_embedding([0,0])),[0,0])
    def test_normalization_is_scale_independent(self):
        self.assertAlmostEqual(cosine_similarity(normalize_embedding([3,4]),[6,8]),1)

if __name__ == '__main__': unittest.main()
