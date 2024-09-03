from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_core.utils import is_request_type, is_intent_name

sb = SkillBuilder()

# Função para calcular IMC
def calculate_bmi(weight, height):
    return weight / (height ** 2)

# Função para determinar a categoria de peso
def bmi_category(bmi):
    if bmi < 18.5:
        return "underweight"
    elif 18.5 <= bmi < 24.9:
        return "normal weight"
    elif 25 <= bmi < 29.9:
        return "overweight"
    else:
        return "obese"

# Cardápios diários
daily_menus = {
    '1': "Day 1 Menu: Breakfast: Oatmeal with fruits. Lunch: Chicken salad. Dinner: Grilled fish with vegetables.",
    '2': "Day 2 Menu: Breakfast: Greek yogurt with honey. Lunch: Turkey sandwich. Dinner: Beef stir-fry with broccoli.",
    '3': "Day 3 Menu: Breakfast: Smoothie with spinach and banana. Lunch: Quinoa salad. Dinner: Baked chicken with sweet potatoes.",
    '4': "Day 4 Menu: Breakfast: Scrambled eggs with avocado. Lunch: Lentil soup. Dinner: Salmon with asparagus.",
    '5': "Day 5 Menu: Breakfast: Whole grain toast with almond butter. Lunch: Chickpea salad. Dinner: Turkey meatballs with zucchini noodles.",
    '6': "Day 6 Menu: Breakfast: Cottage cheese with berries. Lunch: Grilled chicken wrap. Dinner: Shrimp stir-fry with mixed vegetables.",
    '7': "Day 7 Menu: Breakfast: Fruit smoothie bowl. Lunch: Spinach and feta stuffed chicken. Dinner: Veggie pizza with cauliflower crust."
}

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = (
            "Welcome to Daily Diet Coach! To provide you with personalized advice, I need to collect some information. "
            "First, please tell me your height in meters."
        )
        handler_input.attributes_manager.session_attributes['step'] = 'height'
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class HeightIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("HeightIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Acessando slots
        slots = handler_input.request_envelope.request.intent.slots
        height = float(slots['height']['value'])

        # Armazenando o valor em session_attributes
        handler_input.attributes_manager.session_attributes['height'] = height
        handler_input.attributes_manager.session_attributes['step'] = 'age'

        speech_text = "Got it! Now, please tell me your age."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class AgeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AgeIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Acessando slots
        slots = handler_input.request_envelope.request.intent.slots
        age = int(slots['age']['value'])

        handler_input.attributes_manager.session_attributes['age'] = age
        handler_input.attributes_manager.session_attributes['step'] = 'sex'

        speech_text = "Great! Now, please tell me your sex."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class SexIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("SexIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Acessando slots
        slots = handler_input.request_envelope.request.intent.slots
        sex = slots['sex']['value']

        handler_input.attributes_manager.session_attributes['sex'] = sex
        handler_input.attributes_manager.session_attributes['step'] = 'weight'

        speech_text = "Thank you. Finally, please tell me your weight in kilograms."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


class WeightIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("WeightIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Acessando slots
        slots = handler_input.request_envelope.request.intent.slots
        weight = float(slots['weight']['value'])

        # Verificando se a altura foi armazenada corretamente
        session_attributes = handler_input.attributes_manager.session_attributes
        height = session_attributes.get('height')

        if height is None:
            speech_text = "Sorry, I couldn't find your height. Please start over and provide your height first."
            return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

        # Calculando o IMC e a categoria
        bmi = calculate_bmi(weight, height)
        category = bmi_category(bmi)

        speech_text = f"Your BMI is {bmi:.2f}, which is classified as {category}. "
        if category in ["overweight", "obese"]:
            speech_text += (
                "It looks like you could benefit from a structured diet plan. "
                "We offer a weekly meal plan with daily menus to help you get on track. "
                "Would you like to get access to this weekly meal plan?"
            )
            session_attributes['step'] = 'plan_access'
        else:
            speech_text += "You have a healthy BMI. Would you like to get a daily diet tip?"
            session_attributes['step'] = 'daily_tip'

        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class PlanAccessIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("PlanAccessIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Simular verificação de assinatura premium
        is_premium_user = True  # Em uma aplicação real, você verificaria o status de assinatura do usuário

        if is_premium_user:
            speech_text = (
                "You are already subscribed to the premium plan. Please tell me which day's menu you would like to hear: "
                "Day 1, Day 2, Day 3, Day 4, Day 5, Day 6, or Day 7."
            )
            handler_input.attributes_manager.session_attributes['step'] = 'menu_selection'
        else:
            speech_text = (
                "To access our weekly meal plan, we need to process a small payment. "
                "Please complete the purchase through the In-Skill Purchase options in the Alexa app."
            )

        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class MenuSelectionIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MenuSelectionIntent")(handler_input)

    def handle(self, handler_input):
        # Acessando slots
        slots = handler_input.request_envelope.request.intent.slots
        day = slots['day']['value']

        # Obtendo o menu para o dia selecionado
        menu = daily_menus.get(day, "Sorry, I don't have a menu for that day.")

        speech_text = f"Here is the menu for day {day}: {menu}"
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = (
            "You can tell me your height, age, sex, and weight to receive personalized diet advice. "
            "I can also provide a daily diet tip or offer a weekly meal plan. Just ask me for help if you need it!"
        )
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

# Registre todos os handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HeightIntentHandler())
sb.add_request_handler(AgeIntentHandler())
sb.add_request_handler(SexIntentHandler())
sb.add_request_handler(WeightIntentHandler())
sb.add_request_handler(PlanAccessIntentHandler())
sb.add_request_handler(MenuSelectionIntentHandler())
sb.add_request_handler(HelpIntentHandler())

lambda_handler = sb.lambda_handler()
