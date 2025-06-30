import requests

def send_otp_sms(number, otp):
    url = "https://bulksmsbd.net/api/smsapi"
    payload = {
        "api_key": "YOUR_API_KEY",         # BulkSMSBD API key
        "senderid": "YOUR_SENDER_ID",      # Sender ID (DEMO or Verified)
        "number": number,                  # 8801XXXXXXXXX format
        "message": f"Your OTP code is {otp}. It will expire in 10 minutes."
    }

    try:
        response = requests.post(url, data=payload)
        print("SMS response:", response.text)
        return response.json()
    except Exception as e:
        print("SMS sending failed:", e)
        return {"success": False, "error": str(e)}
