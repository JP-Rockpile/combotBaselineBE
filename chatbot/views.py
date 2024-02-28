from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from transformers import pipeline
from django.utils.safestring import mark_safe
from .models import Conversation
import random
from openai import OpenAI
client = OpenAI()


class ChatAPIView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        user_input = data.get('message', '')
        conversation_index = data.get('index', 0)
        time_spent = data.get('timer', 0)
        chat_log = data.get('chatLog', '')
        class_type = data.get('classType', '')

        if conversation_index in (0, 1, 2):
            if conversation_index == 0:
                classifier = pipeline("text-classification", model="jpsteinhafel/complaints_classifier")
                class_response = classifier(user_input)[0]
                class_type = class_response["label"]
                confidence = class_response["score"]
                if class_type == "Other":
                    conversation_index += 10
                chat_response = self.conversation_index_0_response(class_type, user_input)

                if chat_response.startswith("Paraphrased: "):
                    chat_response = chat_response[len("Paraphrased: "):]
                    conversation_index += 2
            elif conversation_index in (1, 2):
                print("inside of convo index 1 or 2")
                chat_response = self.conversation_index_1_response(class_type, chat_log)
        elif conversation_index == 3:
            chat_response = self.conversation_index_3_response()
        elif conversation_index == 4:
            chat_response = self.save_conversation(user_input, time_spent, chat_log)
        else:
            chat_response = ""

        conversation_index += 1
        return Response({"reply": chat_response, "index": conversation_index, "classType": class_type}, status=status.HTTP_200_OK)

    def conversation_index_0_response(self, class_type, user_input):

        A_responses_high = [
            "Can you describe the problem in more detail?",
            "When did you first notice the issue?",
            "Have you tried to resolve the problem on your own?",
            "Have you used the product as intended and followed any instructions provided?",
            "Is there a specific resolution or solution you are hoping for?",
        ]

        B_responses_high = [
            "What was the expected delivery date?",
            "Have you received any updates or notifications regarding your delivery?",
            "Have you tried reaching out to the carrier or delivery service?",
            "Would you like to receive a refund or store credit for the inconvenience?",
            "Are you still hoping to receive the order or would you like to cancel it?",
        ]

        C_responses_high = [
            "Can you provide us with more details about the interaction with the employee?",
            "When and where did the interaction take place?",
            "Was there a specific instance or series of incidents that led to you feeling mistreated?",
            "How did the employee behave in a rude or disrespectful manner?",
        ]

        if class_type == "A":
            chat_response = random.choice([
                random.choice(A_responses_high),
                self.paraphrase_response(user_input)
            ])
        elif class_type == "B":
            chat_response = random.choice([
                random.choice(B_responses_high),
                self.paraphrase_response(user_input)
            ])
        elif class_type == "C":
            chat_response = random.choice([
                random.choice(C_responses_high),
                self.paraphrase_response(user_input)
            ])
        elif class_type == "Other":
            completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "assistant", "content": user_input}],
            )
            chat_response = completion.choices[0].message.content

        return chat_response

    def conversation_index_1_response(self, class_type, chat_log):

        A_responses_high = [
            "Can you describe the problem in more detail?",
            "When did you first notice the issue?",
            "Have you tried to resolve the problem on your own?",
            "Have you used the product as intended and followed any instructions provided?",
            "Is there a specific resolution or solution you are hoping for?",
        ]

        B_responses_high = [
            "What was the expected delivery date?",
            "Have you received any updates or notifications regarding your delivery?",
            "Have you tried reaching out to the carrier or delivery service?",
            "Would you like to receive a refund or store credit for the inconvenience?",
            "Are you still hoping to receive the order or would you like to cancel it?",
        ]

        C_responses_high = [
            "Can you provide us with more details about the interaction with the employee?",
            "When and where did the interaction take place?",
            "Was there a specific instance or series of incidents that led to you feeling mistreated?",
            "How did the employee behave in a rude or disrespectful manner?",
        ]
        print(chat_log)
        print(class_type)
        if class_type == "A":
            chat_response = self.select_next_response(chat_log, A_responses_high.copy())
        elif class_type == "B":
            chat_response = self.select_next_response(chat_log, B_responses_high.copy())
        elif class_type == "C":
            chat_response = self.select_next_response(chat_log, C_responses_high.copy())

        return chat_response

    def select_next_response(self, chat_log, response_options):
        print("do we make it here? ")
        # Collect all messages from 'combot'
        combot_messages = [message['text'] for message in chat_log if message['sender'] == 'combot']

        # Exclude all messages that have already been used by 'combot'
        updated_response_options = [option for option in response_options if option not in combot_messages]

        # Randomly select the next response from the remaining options
        if updated_response_options:  # Ensure the list is not empty
            return random.choice(updated_response_options)

    def conversation_index_3_response(self):
        feel_response_high = "I understand how frustrating this must be for you. That’s definitely not what we expect."
        feel_response_low = ""

        return random.choice([feel_response_high, feel_response_low])

    def conversation_index_10_response(self, user_input):
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "assistant", "content": user_input}],
        )
        return completion.choices[0].message.content

    def paraphrase_response(self, user_input):
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "assistant", "content": "Paraphrase what I am about to say in the next sentence" +
                                                       " and then ask me if that is correct. " + user_input}],
        )
        return "Paraphrased: " + completion.choices[0].message.content

    def save_conversation(self, email, time_spent, chat_log):
        conversation = Conversation(email=email, time_spent=time_spent, chat_log=chat_log)
        conversation.save()
        return "Thank you for providing your email!"


class InitialMessageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        initial_message_high = {
            "message": "Hi there! I'm Combot, and it's great to meet you. I'm here to help with any product or " +
                       "service problems you may have encountered in the past few months. My goal is to make sure you receive " +
                       "the best guidance from me. Let's work together to resolve your issue!"
        }

        initial_message_low = {
            "message": "The purpose of Combot is to assist with resolution of product/service problems. " +
                       "If you have experienced any issues in the past few months, Combot is designed to guide you through " +
                       "finding the optimal solution."
        }

        initial_message = random.choice([initial_message_high, initial_message_low])

        return Response(initial_message)


class ClosingMessageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        html_message = mark_safe(
            "THANK YOU for sharing your experience with me! I will send you a set of comprehensive "
            "suggestions via email. "
            "Please provide your email address below. <br><br> As part of this study, please follow this link to answer a few follow-up questions: "
            "<a href='https://mylmu.co1.qualtrics.com/jfe/form/SV_bjCEGqlJL9LUFX8' target='_blank' rel='noopener noreferrer'>Survey Link</a>."
        )
        return Response({"message": html_message})
