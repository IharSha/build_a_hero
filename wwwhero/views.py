from django.db import transaction
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404

from wwwhero.models import Character, CharacterAttributes, UserVisit, CharacterSelection
from wwwhero.forms import CharacterCreateForm


def index(request):
    count_user_visit(request)

    user = request.user
    if request.user.is_authenticated:
        characters = Character.objects.filter(user=user).order_by('-updated_at')
        selected_char = CharacterSelection.objects.filter(user=user).first()
        context = {'characters': characters, 'selected_char': selected_char}
    else:
        context = {}

    return render(request, 'wwwhero/index.html', {'user': user, 'context': context})


@login_required
def character_select(request, character_id):
    count_user_visit(request)

    user = request.user
    character = get_object_or_404(
        Character,
        pk=character_id,
        user=user
    )
    with transaction.atomic():
        selected, _ = CharacterSelection.objects.get_or_create(user=user)
        selected.character = character
        selected.save()

    return redirect('character_detail')


@login_required
def character_detail(request):
    count_user_visit(request)

    user = request.user
    selected_char = get_object_or_404(CharacterSelection, user=user)
    character = get_object_or_404(Character, pk=selected_char.character_id)

    attributes = CharacterAttributes.objects.get(character=character)

    context = {'character': character, 'attributes': attributes}

    return render(request, 'wwwhero/character_detail.html', context)


@login_required
def character_level_up(request):
    count_user_visit(request)

    user = request.user
    selected_char = get_object_or_404(CharacterSelection, user=user)
    character = get_object_or_404(Character, pk=selected_char.character_id)

    character.level_up()
    messages.success(request, f"Congrats! now you're level {character.level}.")

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
        visitor.view += 1
        visitor.save()
