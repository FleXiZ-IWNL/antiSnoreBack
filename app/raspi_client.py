import httpx
import logging
from typing import Dict, Any
from .config import settings

logger = logging.getLogger(__name__)


class RaspberryPiClient:
    """Client for communicating with Raspberry Pi API"""
    
    def __init__(self):
        self.base_url = settings.RASPI_API_URL
        self.api_key = settings.RASPI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = 10.0
    
    async def trigger_pump_on(self) -> Dict[str, Any]:
        """
        Send request to turn pump ON
        
        Returns:
            Response from Raspberry Pi
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/pump/on",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to trigger pump ON: {e}")
            raise Exception(f"Failed to communicate with Raspberry Pi: {str(e)}")
    
    async def trigger_pump_off(self) -> Dict[str, Any]:
        """
        Send request to turn pump OFF
        
        Returns:
            Response from Raspberry Pi
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/pump/off",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to trigger pump OFF: {e}")
            raise Exception(f"Failed to communicate with Raspberry Pi: {str(e)}")
    
    async def get_pump_status(self) -> Dict[str, Any]:
        """
        Get current pump status
        
        Returns:
            Status from Raspberry Pi
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/pump/status",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get pump status: {e}")
            raise Exception(f"Failed to communicate with Raspberry Pi: {str(e)}")
    
    # async def trigger_pump_sequence(self, duration: float = 3.0) -> Dict[str, Any]:
    #     """
    #     Trigger pump for a specific duration
        
    #     Args:
    #         duration: Duration in seconds (default 3.0)
        
    #     Returns:
    #         Combined response
    #     """
    #     try:
    #         # Turn pump ON
    #         on_response = await self.trigger_pump_on()
    #         logger.info(f"Pump turned ON: {on_response}")
            
    #         # In production, you might want to add a delay here
    #         # For now, we'll immediately turn it off
    #         # The Raspberry Pi can handle the timing internally
            
    #         return {
    #             "status": "success",
    #             "message": f"Pump triggered for {duration} seconds",
    #             "pump_on_response": on_response
    #         }
        
    #     except Exception as e:
    #         logger.error(f"Failed to trigger pump sequence: {e}")
    #         raise
    async def trigger_pump_sequence(self, duration: float = 3.0) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=...) as client:
            response = await client.post(
                f"{self.base_url}/pump/trigger",
                headers=self.headers,
                json={"duration": duration},
            )
        response.raise_for_status()
        return response.json()


    async def trigger_full_sequence(self) -> Dict[str, Any]:
        """
        Trigger full pump sequence for snoring detection
        Pump 1: Inflate 50 seconds
        Pump 2: Deflate 30 seconds
        Total: 80 seconds
        
        Returns:
            Response from Raspberry Pi
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout for long operation
                response = await client.post(
                    f"{self.base_url}/pump/sequence",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to trigger full pump sequence: {e}")
            raise Exception(f"Failed to communicate with Raspberry Pi: {str(e)}")
    
    async def set_pillow_level(self, level: int) -> Dict[str, Any]:
        """
        Set pillow level
        
        Args:
            level: 0-3 (0=Flat, 1=Low, 2=Medium, 3=High)
        
        Returns:
            Response from Raspberry Pi
        """
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.base_url}/pillow/level",
                    headers=self.headers,
                    json={"level": level}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to set pillow level: {e}")
            raise Exception(f"Failed to communicate with Raspberry Pi: {str(e)}")


# Global client instance
_raspi_client_instance = None


def get_raspi_client() -> RaspberryPiClient:
    """Get or create the global Raspberry Pi client instance"""
    global _raspi_client_instance
    if _raspi_client_instance is None:
        _raspi_client_instance = RaspberryPiClient()
    return _raspi_client_instance

