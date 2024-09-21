import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


class TestPurchaseFlow(unittest.TestCase):

    def setUp(self):
        self.url = "saucedemo.com"
        self.user = "standard_user"
        self.password = "secret_sauce"
        self.product_to_buy = "Sauce Labs Backpack".lower()
        self.first_name = "John"
        self.last_name = "Doe"
        self.postal_code = "123456"

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")
        options.page_load_strategy = 'none'
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.close()

    def wait_for_elem(self, parameter, value, timeout=30):
        timeout = time.time() + timeout
        while time.time() < timeout:
            element = self.get_elem(parameter, value)
            if element:
                return element
            time.sleep(0.1)

    # @if_exception
    def get_elem(self, parameter, value, search_where=False):
        if self.driver:
            if not search_where:
                search_where = self.driver
            try:
                element = search_where.find_element(parameter, value)
                return element
            except:
                return None
        else:
            raise Exception("Tried to check_elem without active driver")

    def login(self):
        self.assertTrue(
            self.wait_for_elem(By.ID, "login_button_container", timeout=20),
            "Login page is not loaded"
        )

        username_field = self.get_elem(By.ID, "user-name")
        self.assertTrue(username_field, "Failed to find username field")
        username_field.clear()
        username_field.send_keys(self.user)

        password_field = self.get_elem(By.ID, "password")
        self.assertTrue(password_field, "Failed to find password field")
        password_field.clear()
        password_field.send_keys(self.password)

        login_button = self.get_elem(By.ID, "login-button")
        self.assertTrue(password_field, "Failed to find login button")
        login_button.click()

        self.assertTrue(
            self.wait_for_elem(By.CLASS_NAME, "shopping_cart_link", timeout=20),
            "Failed to load page after login"
        )

    # Function to find products
    def products_catalog_find_req_item(self):
        required_item = None
        inventory_list = self.wait_for_elem(By.CLASS_NAME, "inventory_list")
        self.assertTrue(inventory_list, "Failed to find inventory_list")

        item_elems = inventory_list.find_elements(By.CLASS_NAME, "inventory_item")
        for item_elem in item_elems:
            product_name = item_elem.find_element(By.CLASS_NAME, "inventory_item_name").text
            if product_name.lower() == self.product_to_buy:
                required_item = item_elem
                break

        self.assertTrue(required_item, "Failed to find any items in inventory_list")

        return required_item

    def cart_find_req_item(self):
        required_item = None
        inventory_list = self.wait_for_elem(By.CLASS_NAME, "cart_list")
        self.assertTrue(inventory_list, "Failed to find cart_list")

        item_elems = inventory_list.find_elements(By.CLASS_NAME, "cart_item")
        for item_elem in item_elems:
            product_name = item_elem.find_element(By.CLASS_NAME, "inventory_item_name").text
            if product_name.lower() == self.product_to_buy:
                required_item = item_elem
                break

        self.assertTrue(required_item, "Failed to find any items in cart_list")

        return required_item

    def add_to_cart(self):
        element = self.products_catalog_find_req_item()
        add_to_cart_button = self.get_elem(By.CLASS_NAME, "btn_inventory", search_where=element)
        self.assertEqual(
            "add to cart",
            add_to_cart_button.text.lower(), f"Button says: {add_to_cart_button.text} instead of Add to cart"
        )
        add_to_cart_button.click()
        time.sleep(0.1)
        element = self.products_catalog_find_req_item()
        add_to_cart_button = self.get_elem(By.CLASS_NAME, "btn_inventory", search_where=element)
        self.assertNotEqual(
            "add to cart",
            add_to_cart_button.text.lower(), f"Add to cart button were clicked but not changed"
        )

    def checkout_req_item(self):
        cart_button = self.get_elem(By.CLASS_NAME, "shopping_cart_link")
        self.assertTrue(cart_button, "Failed to find cart button")
        cart_button.click()
        item = self.cart_find_req_item()
        self.assertTrue(item, "Failed to confirm item in cart")

        checkout_button = self.get_elem(By.ID, "checkout")
        checkout_button.click()

        checkout_form = self.wait_for_elem(By.CLASS_NAME, "checkout_info", timeout=20)
        self.assertTrue(checkout_form, "Failed to find checkout_form")

        first_name_field = self.get_elem(By.ID, "first-name")
        self.assertTrue(first_name_field, "Failed to find first-name field")
        first_name_field.clear()
        first_name_field.send_keys(self.first_name)

        last_name_field = self.get_elem(By.ID, "last-name")
        self.assertTrue(last_name_field, "Failed to find last-name field")
        last_name_field.clear()
        last_name_field.send_keys(self.last_name)

        postal_code_field = self.get_elem(By.ID, "postal-code")
        self.assertTrue(postal_code_field, "Failed to find postal-code field")
        postal_code_field.clear()
        postal_code_field.send_keys(self.postal_code)

        submit_button = self.get_elem(By.CLASS_NAME, "submit-button")
        self.assertTrue(submit_button, "Failed to find submit-button")
        submit_button.click()

        finish_button = self.wait_for_elem(By.ID, "finish")
        self.assertTrue(finish_button, "Failed to find finish button")
        finish_button.click()

        success = self.wait_for_elem(By.CLASS_NAME, "complete-header")
        self.assertTrue(success, "Failed to find success confirmation")
        self.assertEqual(success.text.lower(), "thank you for your order!", "Success message has unexpected text")

    # Helper function to proceed to checkout with assertions
    def checkout(self):
        cart_button = self.driver.find_element(By.ID, "cart")
        cart_button.click()

        # Assertion to ensure the cart page is displayed
        self.assertIn("Your Cart", self.driver.title)

        checkout_button = self.driver.find_element(By.ID, "checkout")
        checkout_button.click()

        # Assertion to ensure the checkout page is displayed
        time.sleep(2)
        self.assertIn("Checkout", self.driver.title)

    # Helper function to enter payment details with assertions
    def enter_payment_details(self, card_number, expiry_date, cvv):
        card_number_field = self.driver.find_element(By.ID, "card-number")
        expiry_date_field = self.driver.find_element(By.ID, "expiry-date")
        cvv_field = self.driver.find_element(By.ID, "cvv")

        card_number_field.send_keys(card_number)
        expiry_date_field.send_keys(expiry_date)
        cvv_field.send_keys(cvv)

        submit_payment_button = self.driver.find_element(By.ID, "submit-payment")
        submit_payment_button.click()

        # Assertion to ensure payment is processed (check for order confirmation or success message)
        time.sleep(2)
        self.assertIn("Order Confirmation", self.driver.page_source)

    # Test function that goes through the entire process with assertions
    def test_purchase_flow(self):
        self.driver.get("https://www.saucedemo.com/")
        self.assertTrue(self.driver, "Driver is not set up")
        self.assertTrue(
            self.wait_for_elem(By.ID, "login_button_container", timeout=20),
            "Login form not found or page is failed to load"
        )
        self.login()
        self.add_to_cart()
        self.checkout_req_item()


if __name__ == "__main__":
    unittest.main()
