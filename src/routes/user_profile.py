from routes.chatbot import get_bot_response

users = {'name': None, 'age': None, 'interests': None, 'intro_sent': False}

def update_user_profile(name=None, age=None, interests=None):
    if name: users['name'] = name
    if age: users['age'] = age
    if interests:
        # take only the first interest if it's a list
        if isinstance(interests, list):
            users['interests'] = interests[0]
        else:
            users['interests'] = interests
    users['intro_sent'] = False


tone_templates = {
    "friendly": "Hey {name}! As a {age}-year-old interested in {interests}, I think you'll love this: {answer}",
    "professional": "Hello {name}, considering your age of {age} and your interests in {interests}, here's a professional insight: {answer}",
    "humorous": "Haha {name}! At {age}, with interests like {interests}, here's something funny: {answer}"
}

def get_dynamic_response(user_input: str):
    """Return a personalised answer only the first time."""
    answer = get_bot_response(user_input)

   
    if not users['intro_sent'] and users['interests'] in tone_templates:
        response_text = tone_templates[users['interests']].format(
            name=users['name'],
            age=users['age'],
            interests=", ".join(users['interests']) if isinstance(users['interests'], list) else users['interests'],
            answer=answer
        )
        users['intro_sent'] = True
    else:
        
        response_text = answer

    return response_text