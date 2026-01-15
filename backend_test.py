#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class COMEAPITester:
    def __init__(self, base_url="https://cricketapp-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                    self.log_test(name, True, details)
                    return True, response_data
                except:
                    self.log_test(name, True, details)
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Error: {response.text[:100]}"
                self.log_test(name, False, details)
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_login_valid(self):
        """Test login with valid credentials"""
        success, response = self.run_test(
            "Login - Valid Credentials",
            "POST",
            "auth/login",
            200,
            data={"username": "aryan", "password": "726339"}
        )
        if success and 'token' in response:
            self.token = response['token']
            return True
        return False

    def test_login_invalid(self):
        """Test login with invalid credentials"""
        return self.run_test(
            "Login - Invalid Credentials",
            "POST",
            "auth/login",
            401,
            data={"username": "invalid", "password": "wrong"}
        )[0]

    def test_auth_me(self):
        """Test authenticated user info"""
        return self.run_test("Get User Info", "GET", "auth/me", 200)[0]

    def test_get_stats(self):
        """Test stats endpoint"""
        return self.run_test("Get Dashboard Stats", "GET", "stats", 200)[0]

    def test_seed_logos(self):
        """Test seeding default logos"""
        return self.run_test("Seed Default Logos", "POST", "seed-logos", 200)[0]

    def test_get_logos(self):
        """Test getting all logos"""
        success, response = self.run_test("Get All Logos", "GET", "logos", 200)
        if success and isinstance(response, list):
            print(f"    Found {len(response)} logos")
        return success

    def test_get_team_logos(self):
        """Test getting team logos"""
        return self.run_test("Get Team Logos", "GET", "logos?category=team", 200)[0]

    def test_get_tournament_logos(self):
        """Test getting tournament logos"""
        return self.run_test("Get Tournament Logos", "GET", "logos?category=tournament", 200)[0]

    def test_create_logo(self):
        """Test creating a new logo"""
        logo_data = {
            "name": "Test Team",
            "short_name": "TT",
            "logo_url": "https://via.placeholder.com/50",
            "category": "team"
        }
        success, response = self.run_test("Create New Logo", "POST", "logos", 200, data=logo_data)
        if success and 'id' in response:
            return response['id']
        return None

    def test_delete_logo(self, logo_id):
        """Test deleting a logo"""
        if logo_id:
            return self.run_test(f"Delete Logo {logo_id}", "DELETE", f"logos/{logo_id}", 200)[0]
        return False

    def test_create_campaign(self):
        """Test creating a new campaign"""
        campaign_data = {
            "winner_name": "Test Winner",
            "winner_email": "test@example.com",
            "winning_amount": "50000",
            "contests_won": 1,
            "team1_name": "India",
            "team1_logo": "https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
            "team2_name": "Australia",
            "team2_logo": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Flag_of_Australia.svg",
            "match_date": "15/01/2025",
            "prize_pool": "30 Lakhs",
            "spots": "14,76,906",
            "entry_fee": "0",
            "rank": 1,
            "tournament_name": "World Cup",
            "tournament_logo": "https://upload.wikimedia.org/wikipedia/en/b/bd/2023_Cricket_World_Cup_Logo.svg"
        }
        success, response = self.run_test("Create Campaign", "POST", "campaigns", 200, data=campaign_data)
        if success and 'id' in response:
            return response['id']
        return None

    def test_get_campaigns(self):
        """Test getting all campaigns"""
        success, response = self.run_test("Get All Campaigns", "GET", "campaigns", 200)
        if success and isinstance(response, list):
            print(f"    Found {len(response)} campaigns")
        return success

    def test_get_campaign(self, campaign_id):
        """Test getting a specific campaign"""
        if campaign_id:
            return self.run_test(f"Get Campaign {campaign_id}", "GET", f"campaigns/{campaign_id}", 200)[0]
        return False

    def test_preview_campaign(self, campaign_id):
        """Test campaign email preview"""
        if campaign_id:
            success, response = self.run_test(f"Preview Campaign {campaign_id}", "POST", f"campaigns/{campaign_id}/preview", 200)
            if success and 'html' in response:
                print(f"    Preview HTML length: {len(response['html'])} characters")
            return success
        return False

    def test_send_campaign_email(self, campaign_id):
        """Test sending campaign email (will actually send email)"""
        if campaign_id:
            print("    WARNING: This will send a real email!")
            # For testing, we'll skip actual sending to avoid spam
            # return self.run_test(f"Send Campaign {campaign_id}", "POST", f"campaigns/{campaign_id}/send", 200)[0]
            print("    Skipping actual email send for testing")
            return True
        return False

    def test_delete_campaign(self, campaign_id):
        """Test deleting a campaign"""
        if campaign_id:
            return self.run_test(f"Delete Campaign {campaign_id}", "DELETE", f"campaigns/{campaign_id}", 200)[0]
        return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting COME Email Campaign Manager API Tests")
        print("=" * 60)

        # Test root endpoint
        self.test_root_endpoint()

        # Test authentication
        if not self.test_login_valid():
            print("❌ Login failed - stopping tests")
            return False

        self.test_login_invalid()
        self.test_auth_me()

        # Test stats
        self.test_get_stats()

        # Test logo management
        self.test_seed_logos()
        self.test_get_logos()
        self.test_get_team_logos()
        self.test_get_tournament_logos()

        # Test logo CRUD
        logo_id = self.test_create_logo()
        self.test_delete_logo(logo_id)

        # Test campaign management
        campaign_id = self.test_create_campaign()
        self.test_get_campaigns()
        self.test_get_campaign(campaign_id)
        self.test_preview_campaign(campaign_id)
        self.test_send_campaign_email(campaign_id)
        self.test_delete_campaign(campaign_id)

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")

        return self.tests_passed == self.tests_run

def main():
    tester = COMEAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/test_reports/backend_api_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())