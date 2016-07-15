import unittest
import test_authorization
import test_recipes
import test_images
import test_bulks
import test_products
import test_purchased_product_historys
import test_dishs

if __name__ == '__main__':
    allsuite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromModule(test_authorization)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_recipes)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_images)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_bulks)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_products)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_purchased_product_historys)
    allsuite.addTest(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_dishs)
    allsuite.addTest(suite)

    unittest.TextTestRunner(verbosity=2).run(allsuite)
    