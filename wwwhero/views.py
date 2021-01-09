from django.db import transaction
from django.db.models import F
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

from wwwhero.models import (
    Character,
    CharacterAttributes,
    CharacterCooldown,
    CharacterLocation,
    CharacterSelection,
    Location,
    UserVisit,
)
from wwwhero.forms import CharacterCreateForm
from wwwhero.exceptions import LevelUpCooldownError, MaxLevelError


def index(request):
    count_user_visit(request)
    context = {}

    user = request.user
    if request.user.is_authenticated:
        characters = Character.objects.filter(user=user).order_by('-updated_at')
        character_id = request.session.get('character_id')
        selected_char = Character.objects.filter(id=character_id).first()
        location = CharacterLocation.objects.filter(character_id=character_id).first()

        context = {
            'characters': characters,
            'selected_char': selected_char,
            'location': location,
        }

    return render(request, 'wwwhero/index.html', context)


@login_required
def character_select(request, character_id):
    count_user_visit(request)

    user = request.user
    character = get_object_or_404(
        Character,
        pk=character_id,
        user=user
    )

    CharacterSelection.objects.update_or_create(
        user=user,
        defaults={'character': character}
    )
    request.session['character_id'] = character.id

    if CharacterLocation.objects.filter(character=character).first():
        return redirect('story')

    return redirect('map')


@login_required
def character_detail_view(request):
    count_user_visit(request)

    user = request.user
    character = get_object_or_404(CharacterSelection, user=user).character

    attributes = CharacterAttributes.objects.get(character=character)
    cooldown = CharacterCooldown.objects.filter(
        character=character,
        type=CharacterCooldown.Type.LEVEL,
    ).first()
    if cooldown and cooldown.until > timezone.now():
        cooldown_until = cooldown.until - timezone.now()
        cooldown_until = cooldown_until.seconds + 1  # round to the next second
    else:
        cooldown_until = 0

    context = {
        'character': character,
        'attributes': attributes,
        'cooldown_s': cooldown_until
    }

    return render(request, 'wwwhero/character_detail.html', context)


@login_required
def map_view(request):
    count_user_visit(request)

    character = get_object_or_404(CharacterSelection, user=request.user).character

    locations = Location.objects.filter(is_active=True).order_by('min_level')
    character_location = CharacterLocation.objects.filter(character=character).first()

    context = {
        'character_location': character_location,
        'locations': locations,
        'character_level': character.level
    }

    return render(request, 'wwwhero/map.html', context)


@login_required
def location_select(request, location_id):
    character = get_object_or_404(CharacterSelection, user=request.user).character
    location = get_object_or_404(Location, id=location_id)

    if not location.is_active or character.level < location.min_level:
        messages.error(request, "Your are not allowed to go here :(")
        return redirect('map')

    CharacterLocation.objects.update_or_create(
        character=character,
        defaults={'location': location}
    )
    messages.success(request, f"Now you are here: {location}")

    return redirect('story')


@login_required
def story_view(request):
    count_user_visit(request)

    character_id = request.session.get('character_id')
    if not character_id:
        messages.warning(request, "Please select or create a new character")
        return redirect('index')

    character_location = CharacterLocation.objects.filter(character_id=character_id).first()
    context = {'character_location': character_location}

    return render(request, 'wwwhero/story.html', context)


@login_required
def character_level_up(request):
    count_user_visit(request)

    user = request.user
    selected_char = get_object_or_404(CharacterSelection, user=user)
    character = selected_char.character

    try:
        character.level_up()
        messages.success(request, f"Congrats! Now you're level {character.level}.")
    except LevelUpCooldownError:
        messages.error(request, "Nice try, but no! You have a level up cooldown.")
    except MaxLevelError:
        messages.error(
            request,
            f"You are too strong already. Max level {character.MAX_LEVEL} reached."
        )

    return redirect('character_detail')


@login_required
def character_create_view(request):
    count_user_visit(request)

    user = request.user
    form = CharacterCreateForm(user=user, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data['name']
            with transaction.atomic():
                char, _ = Character.objects.get_or_create(name=name, user=user)
                CharacterAttributes.objects.get_or_create(character=char)

            messages.success(request, "Character created!")
            return redirect('character_select', character_id=char.id)
        else:
            for _, er in form.errors.items():
                messages.error(request, er.as_text())

    return render(request, 'wwwhero/character_create.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            selected_char = CharacterSelection.objects.filter(user=request.user).first()
            if selected_char:
                request.session['character_id'] = selected_char.character.id
            return redirect('index')
    else:
        form = AuthenticationForm()

    return render(request, 'wwwhero/login.html', {'form': form})


def logout_view(request):
    count_user_visit(request)
    logout(request)

    return redirect('index')


def signup_view(request):
    count_user_visit(request)

    if request.user.is_authenticated:
        return redirect('index')

    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')

    return render(request, 'wwwhero/signup.html', {'form': form})


def count_user_visit(request):
    user = request.user
    if user.is_authenticated:
        visitor, _ = UserVisit.objects.get_or_create(
            user=user,
            url=request.path,
            method=request.method,
        )
        visitor.view = F('view') + 1
        visitor.save()
