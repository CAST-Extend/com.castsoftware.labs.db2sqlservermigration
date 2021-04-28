import unittest
from cast.application.test import run
from cast.application import create_postgres_engine
import logging

logging.root.setLevel(logging.DEBUG)

class TestIntegration(unittest.TestCase):

    def test2(self):
        
        run(kb_name='dbmsql_local', application_name='msql', engine=create_postgres_engine(port=2282))
#        
       

if __name__ == "__main__":
    unittest.main()
