import unittest
import test_authorization
import test_recipes


if __name__ == '__main__':
    allsuite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromModule(test_authorization)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_recipes)
    allsuite.addTest(suite)  
    unittest.TextTestRunner(verbosity=2).run(allsuite)