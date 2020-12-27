from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404

from wwwhero.models import Character, CharacterAttributes
from wwwhero.forms import CharacterCreateForm


def index(request):
    user = request.user
    if request.user.is_authenticated:
        characters = Character.objects.filter(user=user).order_by('-updated_at')
        context = {"characters": characters}
    else:
        context = {}

    return render(request, 'wwwhero/index.html', {'user': user, 'context': context})


@login_required
def character_detail(request, character_id):
    character = get_object_or_404(
        Character,
        pk=character_id,
        user=request.user
    )
    attributes = CharacterAttributes.objects.get(character=character)
    context = {"character": character, "attributes": attributes}

    return render(request, 'wwwhero/character_detail.html', context)


@login_required
def character_level_up(request, character_id):
    character = get_object_or_404(
        Character,
        pk=character_id,
        user=request.user
    )
    character.level_up()
    messages.success(request, f"Congrats! now you're level {character.level}.")

    return redirect('character_detail', character_id=character.id)


@login_required
def character_create_view(request):
    user = request.user
    form = CharacterCreateForm(user=user, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data["name"]
            char, _ = Character.objects.get_or_create(name=name, user=user)
            CharacterAttributes.objects.get_or_create(character=char)
            messages.success(request, "Character created!")
            return redirect('character_detail', character_id=char.id)
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
            return redirect('index')
    else:
        form = AuthenticationForm()

    return render(request, 'wwwhero/login.html', {'form': form})


def logout_view(request):
    logout(request)

    return redirect('index')


def signup_view(request):
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


def check_character_exist(request, character_id):
    try:
        character = Character.objects.get(id=character_id, user=request.user)
    except Character.DoesNotExist:
        messages.warning(request, 'There is no such page.')
        return redirect('index')

    return character
