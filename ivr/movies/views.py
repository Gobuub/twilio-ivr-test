from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse

from .models import Theater, Movie, Show
import datetime
from django.utils import timezone
# First we will create a new view that accepts an HttpRequest object and returns an HttpResponse


@csrf_exempt
# we use the csrf decorator to disabled Django´s CSRF protection, without this we can't use twilio on our website
def choose_theater(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Bienvenido a tu guía personal de cines', language='es')

    with vr.gather(
        action=reversed('choose-movie'),
        finish_on_key='#',
        timeout=20,
    ) as gather:
        gather.say('Por favor elige una película y presiona #', language='es')
        theaters = (
            Theater.objects
            .filter(digits__isnull = False)
            .order_by('digits')
        )
        for theater in theaters:
            gather.say(f'Para {theater.name} en {theater.address} presiona {theater.digits}',
                       language='es')

        vr.say('No he entendido tu petición', language='es')
        vr.redirect('')

        return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def choose_movie(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()

    digits = request.POST.get('Digits')
    try:
        theater = Theater.objects.get(digits=digits)

    except Theater.DoesNotExist:
        vr.say('Por favor seleccione un cine de la lista', language='es')
        vr.redirect(reversed('choose-theater'))
    else:
        with vr.gather(
            action=f'{reversed("list-showtimes")}?theater={theater.id}',
            finish_on_key='#',
            timeout=20,
        ) as gather:
            gather.say('Por favor elige una película y pulsa #', language='es')
            movies = (
                Movie.objects
                .filter(digits__isnull=False)
                .order_by('digits')
                )
            for movie in movies:
                gather.say(f'Para {movie.title} presiona {movie.digits}', language='es')

        vr.say('No he recibido su elección', language='es')
        vr.redirect(reversed('choose-theater'))

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def list_showtimes(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()

    digits = request.POST.get('Digits')
    theather = Theater.objects.get(id=request.GET['theater'])

    try:
        movie = Movie.objects.get(id=digits)

    except Movie.DoesNotExit:
        vr.say('Por favor, elige una película de la lista', language='es')
        vr.redirect(f'{reversed("choose-movie")}?theater={theather.id}')

    else:

        from_time = timezone.now()
        until_time = from_time + datetime.timedelta(hours=12)
        shows = list(
            Show.objects.filter(
                theather=theather,
                movie=movie,
                starts_at__range=(from_time, until_time),
            ).order_by('starts_at')
        )
        if len(shows) == 0:
            vr.say('Lo sentimos, la pelicula no está disponible en esta franja horaria en este cine',
                   language='es')
        else:
            showtimes = ', '.join(shows.starts_at.time().strftime('%I:$M%p') for show in shows)
            vr.say(f'La película {movie.title} está disponible en {theather.name} a las {showtimes}',
                   language='es')

        vr.say('Gracias por utilizar nuestro servicio', language='es')
        vr.hangup()

    return HttpResponse(str(vr), content_type='text/xml')