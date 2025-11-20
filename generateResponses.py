import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def query_gpt(prompt, model = "gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,       # limit the response length
        temperature=0.7       # randomness of output
    )

    # Extract the assistant’s reply
    message = response.choices[0].message.content
    return message


def considerQuestion(prompt, id):
    with (
        open(f'char_x1000/character_{id}/description.txt', 'r') as desc_f,
        open('prompts/introduction.txt', 'r') as intro_f,
        open('prompts/context.txt', 'r') as context_f,
        open('prompts/post.txt', 'r') as post_f,
    ):
        character_description = desc_f.read()
        introduction_prompt = intro_f.read()
        context_prompt = context_f.read()
        post_prompt = post_f.read()

    full_prompt = character_description + introduction_prompt + context_prompt + prompt + post_prompt
    print(f"Full prompt for character:\n{full_prompt}\n")



considerQuestion("Should I go for a walk today?", "0042")
