from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.4-mini",
    input="Give me one short travel tip for Goa."
)

print(response.output_text)