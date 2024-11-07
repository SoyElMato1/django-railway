# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import json
from typing import Any, Dict, List, Text
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker


class ActionGetPlantInfo(Action):
    def name(self) -> Text:
        return "action_get_plant_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        plant_name = tracker.get_slot('plant_name')
        if not plant_name:
            dispatcher.utter_message(text="No mencionaste el nombre de la planta.")
            return [SlotSet("plant_name", None)]

        try:
            # Cargar datos del JSON
            with open('data/plantas.json', encoding="utf-8") as f:
                plantas_data = json.load(f)

            # Búsqueda exacta de la planta
            planta_encontrada = next(
                (plant for plant in plantas_data.get('plants', [])
                if plant['name'].strip().lower() == plant_name.strip().lower()),
                None
            )

            if planta_encontrada:
                details = planta_encontrada['details']
                
                # Formatear la respuesta
                response = self.format_plant_info(
                    plant_name,
                    details['description'],
                    details['care']['requirements'],
                    details['care']['water_frequency'],
                    details['special_needs'],
                    details['sunlight'],
                    details['climate']
                )
                
                dispatcher.utter_message(text=response)
            else:
                dispatcher.utter_message(text=f"No tengo información sobre la planta '{plant_name}'.")

        except Exception as e:
            dispatcher.utter_message(text=f"Ocurrió un error inesperado: {e}")

        # Reinicia el slot plant_name después de cada consulta
        return [SlotSet("plant_name", None)]

    def format_plant_info(self, plant_name: str, description: str, care: str, watering: str, special_needs: str, sun_exposure: str, climate: str) -> str:
        response = (
            f"🌿 **Información sobre {plant_name.capitalize()}** 🌿\n\n"
            f"🌱 **Descripción:** {description}\n\n"
            f"🛠️ **Cuidados básicos:**\n   - {care}\n"
            f"💧 **Riego:**\n   - {watering}\n"
            f"🌞 **Exposición al sol:**\n   - {sun_exposure}\n"
            f"🌡️ **Clima adecuado:**\n   - {climate}\n"
            f"✨ **Necesidades especiales:**\n   - {special_needs}\n\n"
            f"¡Espero que esta información te sea útil! 🌻"
        )
        return response