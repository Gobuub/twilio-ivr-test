from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse

# First we will create a new view that accepts an HttpRequest object and returns an HttpResponse


@csrf_exempt
# we use the csrf decorator to disabled Django´s CSRF protection, without this we can't use twilio on our website
def answer(request: HttpRequest) -> HttpResponse:
    # with this create an instance of VoiceResponse
    vr = VoiceResponse()
    # then use the 'say' function of the VoiceResponse object to create a TwiML markup to greet the user 'Hello'
    # using text-to-speech
    vr.say('Hello Yonatan')
    return HttpResponse(str(vr), content_type='text/xml')
