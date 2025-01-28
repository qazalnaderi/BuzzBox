import random
from ...core.redis.redis_client import redis_client


import json
import logging

class OTPService:
    @staticmethod
    def generate_otp() -> str:
        return str(random.randint(100000, 999999))


    async def verify_otp(self, redis_key: str, otp: str) -> dict:
        try:
            temp_data = redis_client.get(redis_key)
            if not temp_data:
                logging.error(f"OTP not found in Redis for key: {redis_key}")
                return {"status_code": 400, "message": "OTP has expired or registration data not found"}

            temp_data = json.loads(temp_data)
            logging.info(f"temp data: {temp_data}")
            stored_otp = temp_data.get("otp")
            logging.info(f"Entered OTP: {otp}, Stored OTP: {stored_otp}")

            if stored_otp != otp:
                return {"status_code": 400, "message": "Invalid OTP"}
            user_data = temp_data.get("user_data")
            logging.info(f"user_data : {user_data}")

            account_data = temp_data.get("account_data")
            logging.info(f"account_data: {account_data}")


            if not user_data or not account_data:
                logging.error("User or account data is missing")  # Log if data is missing
                return {"status_code": 500, "message": "User or account data is missing"}

            return {
                "status_code": 200,
                "message": "OTP verified successfully",
                "user_data": user_data,
                "account_data": account_data
            }

        except Exception as e:
            logging.error(f"Error during OTP verification: {e}")
            return {"status_code": 500, "message": "An error occurred during OTP verification"}

    async def delete_otp(self, redis_key: str):
        try:
            await redis_client.delete(redis_key)
        except Exception as redis_error:
            logging.warning(f"Failed to delete Redis key: {redis_key}")
