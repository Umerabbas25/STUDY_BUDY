from groq import Groq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from .models import Room, Messages

# Initialize Groq Client
client = Groq(api_key=settings.GROQ_API_KEY)
MODEL_NAME = 'llama-3.1-8b-instant' # Fast and reliable Groq model

class RoomSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=404)

        messages = room.messages_set.all().order_by('created')
        if not messages.exists():
            return Response({'summary': 'No messages to summarize yet.'})

        # Build context
        chat_history = ""
        for msg in messages:
            chat_history += f"{msg.user.username}: {msg.body}\n"

        prompt = f"""
        Summarize the following discussion in the room titled '{room.name}' (Topic: {room.topic.name}).
        Provide a concise bullet-point summary of the key takeaways and main points discussed.
        Keep it professional and easy to read.
        
        Chat History:
        {chat_history}
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes chat room discussions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=MODEL_NAME,
            )
            return Response({'summary': chat_completion.choices[0].message.content})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class SmartReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            message = Messages.objects.get(pk=pk)
        except Messages.DoesNotExist:
            return Response({'error': 'Message not found'}, status=404)

        prompt = f"""
        Context: The user '{message.user.username}' posted the following message in a study room titled '{message.room.name}' (Topic: {message.room.topic.name}):
        Message: "{message.body}"

        Task: Suggest exactly 3 short, relevant, and helpful replies that another user could send to this message. 
        Format your response as a simple JSON list of strings. Do not include markdown formatting, backticks, or any other text.
        Example: ["That's a great point!", "I agree, can you explain more?", "I had the same issue."]
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=MODEL_NAME,
            )
            text = chat_completion.choices[0].message.content.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            import json
            suggestions = json.loads(text.strip())
            return Response({'suggestions': suggestions})
        except Exception as e:
            # Fallback
            return Response({'suggestions': ["Interesting!", "I agree completely.", "Can you elaborate?"]})


class AIChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        query = request.data.get('query')
        context_room = request.data.get('room_name', 'General Study')
        context_topic = request.data.get('topic_name', 'General')
        
        if not query:
            return Response({'error': 'Query is required'}, status=400)

        prompt = f"""
        You are an AI Study Assistant for a platform called StudyBud.
        The user is currently in the room '{context_room}' discussing '{context_topic}'.
        They ask: "{query}"
        
        Provide a helpful, clear, and concise answer. Keep the tone friendly and encouraging.
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=MODEL_NAME,
            )
            return Response({'response': chat_completion.choices[0].message.content})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
