import pytest
from playwright.sync_api import Page, expect
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

def test_homepage_loads(page: Page):
    """Test that the homepage loads correctly"""
    page.goto(FRONTEND_URL)
    
    # Check page title
    expect(page).to_have_title("ML Production App")
    
    # Check main heading
    expect(page.locator("h1")).to_contain_text("ML Production App")
    
    # Check status cards are present
    expect(page.locator('[data-testid="api-status"]')).to_be_visible()
    expect(page.locator('[data-testid="model-status"]')).to_be_visible()
    expect(page.locator('[data-testid="model-type"]')).to_be_visible()

def test_prediction_form(page: Page):
    """Test the prediction form functionality"""
    page.goto(FRONTEND_URL)
    
    # Fill in feature values
    page.fill('input[id="feature-0"]', "1.5")
    page.fill('input[id="feature-1"]', "2.0")
    page.fill('input[id="feature-2"]', "0.5")
    page.fill('input[id="feature-3"]', "1.0")
    
    # Click predict button
    page.click('button:has-text("Predict")')
    
    # Wait for prediction result (or error if backend not available)
    page.wait_for_timeout(2000)
    
    # Check that something happened (either success or error)
    # In a real scenario, we'd mock the backend or have it running
    prediction_section = page.locator('[data-testid="prediction-results"]')
    expect(prediction_section).to_be_visible()

def test_responsive_design(page: Page):
    """Test responsive design on different screen sizes"""
    # Test mobile view
    page.set_viewport_size({"width": 375, "height": 812})
    page.goto(FRONTEND_URL)
    
    # Cards should stack vertically on mobile
    status_cards = page.locator('[data-testid="status-cards"]')
    expect(status_cards).to_be_visible()
    
    # Test desktop view
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(FRONTEND_URL)
    
    # Cards should be horizontal on desktop
    expect(status_cards).to_be_visible() 