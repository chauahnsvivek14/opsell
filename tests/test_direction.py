import unittest

from services.direction import extract_atm_straddle_premium


class ExtractATMStraddlePremiumTests(unittest.TestCase):
    def test_extracts_straddle_from_option_chain_payload(self):
        payload = {
            "data": [
                {
                    "strikePrice": 24000,
                    "ce": {"ltp": 120.5},
                    "pe": {"ltp": 121.0},
                }
            ]
        }

        self.assertEqual(extract_atm_straddle_premium(payload, 24000), 241.5)

    def test_handles_nested_option_chain_data(self):
        payload = {
            "data": {
                "records": [
                    {
                        "strikePrice": 23950,
                        "CE": {"lastPrice": 110.25},
                        "PE": {"lastPrice": 111.0},
                    }
                ]
            }
        }

        self.assertEqual(extract_atm_straddle_premium(payload, 23950), 221.25)


if __name__ == "__main__":
    unittest.main()
