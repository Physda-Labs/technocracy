import os
from openai import OpenAI
import string 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cleanAnswers():
    for i in range(1, 1001):
        # ID should be padded on the left with 0s.
        char_id = str(i)
        while (len(char_id) < 4): char_id = "0" + char_id

        # Empty the answer and short-answer files
        dir_path = f"char_x1000/character_{char_id}"
        full_path = os.path.join(dir_path, "answer.txt")
        short_path = os.path.join(dir_path, "short-answer.txt")

        # Empty the files
        open(full_path, 'w').close()
        open(short_path, 'w').close()



def query_gpt(prompt, model = "gpt-3.5-turbo"):
    response = client.chat.completions.create(model=model,
    messages=[
        {"role": "system", "content": prompt}
    ],
    max_tokens=150,       # limit the response length
    temperature=0.8       # randomness of output
    )

    # Extract the assistant’s reply
    message = response.choices[0].message.content
    return message

def considerQuestion(question, char_id):
    # ID should be padded on the left with 0s.
    char_id = str(char_id)
    while (len(char_id) < 4): char_id = "0" + char_id

    with (
        open(f'char_x1000/character_{char_id}/description.txt', 'r') as desc_f,
        open('prompts/introduction.txt', 'r') as intro_f,
        open('prompts/pre.txt', 'r') as pre_f,
        open('prompts/post.txt', 'r') as post_f,
    ):
        character_description = desc_f.read()
        introduction_prompt = intro_f.read()
        pre_prompt = pre_f.read()
        post_prompt = post_f.read()

    response_1 = query_gpt(character_description + introduction_prompt)
    prompt_2 = character_description + introduction_prompt + response_1 + pre_prompt + question + post_prompt
    response_2 = query_gpt(prompt_2)

    print(prompt_2)
    print("-----")
    print(response_2)

    return response_2

def getAnswer(prompt):
    short = prompt[-30:-1]
    if "yes" in short or "Yes" in short:
        return True
    else:
        return False
    
def writeOut(answer, char_id):
    # ID should be padded on the left with 0s.
    char_id = str(char_id)
    while (len(char_id) < 4): char_id = "0" + char_id

    # Build the directory path
    dir_path = f"char_x1000/character_{char_id}"
    os.makedirs(dir_path, exist_ok=True)

    # Paths for the full and short answer files
    full_path = os.path.join(dir_path, "answer.txt")
    short_path = os.path.join(dir_path, "short-answer.txt")

    # Write full answer
    # with open(full_path, "w", encoding="utf-8") as f:
    #     f.write(answer)

    # Generate and write short answer
    short_answer = getAnswer(answer)
    if short_answer: short_answer = "Yes"
    else: short_answer = "No"
    print(short_answer)
    with open(short_path, "w", encoding="utf-8") as f:
        f.write(short_answer)

def promptCharacters(question, num):

    count_yes = 0
    count_no  = 0

    # Paralellse the for loop?
    for i in range(1, num+1):
        answer = considerQuestion(question, i)
        ans_yes = getAnswer(answer)
        if ans_yes: count_yes = count_yes + 1
        else: count_no = count_no + 1

        writeOut(answer, i)

    print("Yes count:")
    print(count_yes)
    print("No count:")
    print(count_no)


promptCharacters("I have some university coursework deadlines next week, but this weekend there is a hackathon that I want to go to. Should I go to the Hackathon?", 10)

# writeOut("I understand the pull of the hackathon, the excitement of new challenges. But remember, your university deadlines are crucial. Prioritize your coursework; it's the foundation of your future success. The hackathon will come again, but missed deadlines can have lasting consequences. Focus on your responsibilities now. No.", 1)

