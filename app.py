from flask import Flask, render_template, request, session, jsonify
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import datetime
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load Google Ads API client
GOOGLE_ADS_CLIENT = GoogleAdsClient.load_from_storage(version="v18")


def get_customer_id():
    """Retrieves the Customer ID from google-ads.yaml configuration file."""
    try:
        customer_id = GOOGLE_ADS_CLIENT.login_customer_id
        if not customer_id:
            raise ValueError("❌ No Customer ID found in google-ads.yaml.")
        return str(customer_id)  
    except Exception as e:
        print(f"❌ Error retrieving Customer ID from google-ads.yaml: {e}")
        return None


@app.route("/")
def index():
    session.clear()  
    session["conversation"] = []
    session["step"] = 1  
    session["customer_id"] = get_customer_id()  
    session["campaign_details"] = {}  
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"response": "❌ Please enter a valid response."})

    step = session.get("step", 1)

    if step == "confirm":
        if user_input.lower() == "yes":
            customer_id = session.get("customer_id")
            campaign_details = session.get("campaign_details")
            campaign_id = create_google_ads_campaign(GOOGLE_ADS_CLIENT, customer_id, campaign_details)

            if campaign_id:
                session.clear()  
                return jsonify({"response": f"✅ Campaign created successfully! 🎉 Campaign ID: {campaign_id}", "reset": True})
            else:
                return jsonify({"response": "❌ Failed to create campaign. Please try again.", "reset": False})

        elif user_input.lower() == "no":
            session.clear()
            session["step"] = 1
            return jsonify({"response": "📝 What would you like to edit? Please enter a new response for any question."})

        else:
            return jsonify({"response": "❌ Invalid response. Please enter: yes or no."})

    else:
        response = process_campaign_questions(user_input)
        return jsonify({"response": response})


def process_campaign_questions(user_input):
    """Handles campaign questions and ensures valid responses."""
    step = session.get("step", 1)
    campaign_details = session.get("campaign_details")

    QUESTIONS = [
        "What is the name of your campaign?",
        "What is your daily budget in INR?",
        "What type of advertising do you want? (Search, Display, Shopping)?",
        "Do you want to enable Google Search Partners? (yes or no)?",
        "What is your campaign start date? (YYYY-MM-DD)?",
        "What is your campaign end date? (YYYY-MM-DD)?"
    ]

    if step == 1:  
        campaign_details["Campaign Name"] = user_input

    elif step == 2:  
        if not user_input.replace('.', '', 1).isdigit():
            return "❌ Invalid budget. Please enter a numeric value in INR."
        campaign_details["Daily Budget"] = f"₹{user_input}"

    elif step == 3:  
        if user_input.lower() not in ["search", "display", "shopping"]:
            return "❌ Invalid advertising type. Please enter: Search, Display, or Shopping."
        campaign_details["Advertising Type"] = user_input.capitalize()

    elif step == 4:  
        if user_input.lower() not in ["yes", "no"]:
            return "❌ Invalid response. Please enter: yes or no."
        campaign_details["Google Search Partners"] = "Enabled" if user_input.lower() == "yes" else "Disabled"

    elif step == 5:  
        if not validate_date_format(user_input):
            return "❌ Invalid date format. Please enter Start Date in YYYY-MM-DD format."
        if not validate_future_date(user_input):
            return "❌ Start Date cannot be in the past. Please enter a future date."
        campaign_details["Start Date"] = user_input

    elif step == 6:  
        if not validate_date_format(user_input):
            return "❌ Invalid date format. Please enter End Date in YYYY-MM-DD format."
        if not validate_future_date(user_input):
            return "❌ End Date cannot be in the past. Please enter a future date."
        if not validate_date_order(campaign_details["Start Date"], user_input):
            return "❌ End Date must be after Start Date. Please enter a valid End Date."
        campaign_details["End Date"] = user_input

    session["campaign_details"] = campaign_details

    if step < len(QUESTIONS):
        session["step"] += 1
        return QUESTIONS[step]

    else:
        return review_campaign(campaign_details)


def validate_date_format(date_str):
    """Checks if input is a valid YYYY-MM-DD date format."""
    try:
        datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_future_date(date_str):
    """Ensures the given date is in the future."""
    input_date = datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    return input_date >= datetime.date.today()


def validate_date_order(start_date, end_date):
    """Ensures Start Date is before End Date."""
    return datetime.datetime.strptime(start_date, "%Y-%m-%d") < datetime.datetime.strptime(end_date, "%Y-%m-%d")

def review_campaign(campaign_details):
    """Summarizes the campaign details and asks for confirmation before creation."""
    summary = (
        f"📋 Here is your campaign summary:\n\n"
        f"📌 Campaign Name: {campaign_details.get('Campaign Name', 'N/A')}\n"
        f"💰 Daily Budget: {campaign_details.get('Daily Budget', 'N/A')}\n"
        f"🎯 Advertising Type: {campaign_details.get('Advertising Type', 'N/A')}\n"
        f"🔍 Google Search Partners: {campaign_details.get('Google Search Partners', 'N/A')}\n"
        f"📅 Start Date: {campaign_details.get('Start Date', 'N/A')}\n"
        f"⏳ End Date: {campaign_details.get('End Date', 'N/A')}\n\n"
        f"✅ Does everything look correct? Type 'yes' to confirm!."
    )
    
    session["step"] = "confirm"  # Move to confirmation step
    return summary

import datetime
import uuid
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def create_google_ads_campaign(client: GoogleAdsClient, customer_id: str, campaign_details):
    """Creates a Google Ads campaign with a budget and applies the correct settings."""
    customer_id = "4852899962"  
    try:
        campaign_budget_service = client.get_service("CampaignBudgetService")
        campaign_service = client.get_service("CampaignService")

        
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = f"Budget for {campaign_details['Campaign Name']} {uuid.uuid4()}"
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        campaign_budget.amount_micros = int(float(campaign_details["Daily Budget"].replace("₹", "")) * 1_000_000)
        campaign_budget.explicitly_shared = False 

        campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
        budget_resource_name = campaign_budget_response.results[0].resource_name

        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = f"{campaign_details['Campaign Name']} {uuid.uuid4()}"  
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.campaign_budget = budget_resource_name  

        campaign.network_settings.target_google_search = True
        campaign.network_settings.target_search_network = True
        campaign.network_settings.target_partner_search_network = False
        campaign.network_settings.target_content_network = True

        campaign.start_date = campaign_details["Start Date"].replace("-", "")
        campaign.end_date = campaign_details["End Date"].replace("-", "")

        campaign.manual_cpc = client.get_type("ManualCpc")  

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )

        return campaign_response.results[0].resource_name

    except GoogleAdsException as ex:
        return f"❌ Failed to create campaign: {ex}"



if __name__ == "__main__":
    app.run(debug=True)
